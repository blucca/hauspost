"""Provision the pinned Apertus GGUF directly from its publisher into a local mount."""

import sys
import urllib.request
from pathlib import Path

MODEL_FILE = "apertus-v1.5-8b-text-q4_k_m.gguf"
MODEL_REVISION = "248ec68a63e219e3f061e4c946fc8a20d63b9975"
MODEL_URL = (
    "https://huggingface.co/Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF/resolve/"
    f"{MODEL_REVISION}/{MODEL_FILE}"
)
MODEL_BYTES = 5_059_027_136


def provision(directory):
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / MODEL_FILE
    partial = directory / f".{MODEL_FILE[:-5]}.partial.gguf"
    if target.exists():
        if target.stat().st_size != MODEL_BYTES:
            raise ValueError(f"Model size mismatch: {target}; expected {MODEL_BYTES} bytes")
        print(f"Model ready: {target.name} ({MODEL_BYTES} bytes)", flush=True)
        return target

    offset = partial.stat().st_size if partial.exists() else 0
    if offset > MODEL_BYTES:
        raise ValueError(f"Partial download exceeds expected size: {partial}")
    if offset < MODEL_BYTES:
        headers = {"User-Agent": "HausPost/0.1 (model provisioning)"}
        if offset:
            headers["Range"] = f"bytes={offset}-"
        print(f"Provisioning Apertus from {MODEL_URL}", flush=True)
        print(f"Download begins at {offset}/{MODEL_BYTES} bytes", flush=True)
        request = urllib.request.Request(MODEL_URL, headers=headers)
        with urllib.request.urlopen(request, timeout=90) as response:
            if offset and response.status != 206:
                offset = 0
            elif offset:
                content_range = response.headers.get("Content-Range", "")
                if not content_range.startswith(f"bytes {offset}-"):
                    raise ValueError(f"Unexpected download range: {content_range}")
            next_progress = offset + 512 * 1024 * 1024
            with partial.open("ab" if offset else "wb") as stream:
                while chunk := response.read(1024 * 1024):
                    stream.write(chunk)
                    offset += len(chunk)
                    if offset > MODEL_BYTES:
                        raise ValueError("Downloaded model exceeds expected size")
                    if offset >= next_progress:
                        print(f"Downloaded {offset}/{MODEL_BYTES} bytes", flush=True)
                        next_progress = offset + 512 * 1024 * 1024
    if partial.stat().st_size != MODEL_BYTES:
        raise ValueError(f"Incomplete model: {partial.stat().st_size}/{MODEL_BYTES} bytes")
    partial.replace(target)
    print(f"Model ready: {target.name} ({MODEL_BYTES} bytes)", flush=True)
    return target


if __name__ == "__main__":
    provision(Path(sys.argv[1] if len(sys.argv) > 1 else "models"))
