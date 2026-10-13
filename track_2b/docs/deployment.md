# Reproducing HausPost

Target architecture: **on-premise**, administered by the organisation using the tool.

## Three commands

Run these from the repository root or from `track_2b/`. Docker Engine, Docker Compose v2 and GNU Make are the host prerequisites.

| Command | Model path | Purpose |
| --- | --- | --- |
| `make run` | Real Apertus 1.5 8B Q4_K_M in the internal Compose network | Complete self-managed prototype |
| `make demo` | Empty `LLM_BASE_URL` | Lightweight application and saved-example demonstration |
| `make hosted` | Operator's `.env` endpoint | Hosted model development and evaluation |

The application opens at **http://127.0.0.1:4377**. `make logs` shows the last 80 application/model log lines; `make stop` stops the stack. Switch profiles by running `make stop` before the next start command.

For Docker access through sudo, use `make DOCKER='sudo docker' run`.

## On-prem provisioning and runtime

`make run` first invokes `make provision`. A short-lived Python container downloads the pinned model **directly from its Hugging Face publisher** into `track_2b/models/`. It resumes an interrupted download and checks the expected file size before moving it into place. The repository's existing `*.gguf` rule excludes both the model and its partial download from Git. Model files remain outside the application image and published source.

Provisioning requires access to Docker Hub, GHCR and Hugging Face. At runtime, the model joins the **internal `runtime` network**. The application joins that model network and a regular `ingress` bridge that publishes its browser-facing port on **127.0.0.1:4377**. The shipped on-prem application sends source text and prompts to `http://model:8080/v1`; model port 8080 stays inside the model network. The ingress bridge supplies the application's host-facing connection and an outbound route. The configured application uses the local model endpoint for its LLM requests. Application and model containers receive their artifacts locally at runtime.

For a provisioned host:

```sh
cd track_2b
docker compose -f compose.yaml -f compose.onprem.yaml up --wait --wait-timeout 300 app
```

Images and the GGUF can also be staged on the organisation's machine before startup. A remote workstation can use an SSH port forward to the loopback-bound application. Organisation-wide service publishing, accounts and authentication belong to a subsequent deployment stage.

### Fixed artifacts

- **GGUF:** `Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF`, revision `248ec68a63e219e3f061e4c946fc8a20d63b9975`, file `apertus-v1.5-8b-text-q4_k_m.gguf`, **5,059,027,136 bytes**. [Pinned download](https://huggingface.co/Colby/apertus-v1.5-8b-text-Q4_K_M-GGUF/resolve/248ec68a63e219e3f061e4c946fc8a20d63b9975/apertus-v1.5-8b-text-q4_k_m.gguf).
- **Serving image:** llama.cpp `server-b11561`, source revision `e937b17a2df081e9c7ae380f0dab4341c1585bce`, image index `ghcr.io/ggml-org/llama.cpp@sha256:052888c603894ecfa08deb6714fdc2d7084e491e174d5ab41bfb36b49ee7151c`.
- **Application base:** `python:3.12-slim@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1`. The application uses Python's standard library.

The text-only model card and GGUF identify **Apache-2.0**. The publisher also provides the [Apertus 1.5 Acceptable Use Policy](https://github.com/swiss-ai/apertus-legal/blob/main/apertus_1.5/USAGE_POLICY.pdf). Operators obtain the weights from that source under its terms. Weight redistribution carries the AUP's recipient-assent and onward-propagation obligations.

### Resource budget

- Capacity target: **8 GiB host RAM**, 4 CPU threads and 8 GiB free disk space. A 16 GB machine provides additional operating-system headroom.
- Provisioning container: **1 GiB RAM / 1 CPU** for the downloader and filesystem cache, released before the model starts.
- Model container: **7 GiB RAM / 4 CPU** limit. Application: **512 MiB / 1 CPU** limit; the host shares CPU time between them.
- Context: **4096 tokens**, one parallel slot, 256-token logical batch / 128-token physical batch, thinking disabled in the model's Jinja template.
- Model-response deadline: **420 seconds** in the CPU on-prem profile; hosted development uses the application's 180-second default.
- The model's F16 KV cache at this context is approximately 512 MiB. Its original 262,144-token context needs approximately 32 GiB for that cache, so the Compose file sets the smaller context explicitly.

The 8 GiB capacity target comes from weight size, KV allocation and runtime headroom. Observed memory and timing belong to the attached deployment smoke results, with their recorded host hardware.

## Hosted development

Copy `track_2b/.env.example` to `track_2b/.env`, enter the operator's key, then run `make hosted`.

```dotenv
LLM_NAME=swiss-ai/apertus-v1.5-8b
LLM_BASE_URL=https://api.publicai.co/v1
LLM_API_KEY=your-private-key
```

`LLM_BASE_URL` includes `/v1`; the application adds `/chat/completions`. Public AI requires a descriptive `User-Agent` header. The application sends the source text and prompt to the configured provider in this profile. Development records distinguish that provider's model from the local Q4_K_M conversion. The on-prem profile uses an empty API key within the internal network.

## One real-model CI smoke

The manually dispatched **Apertus on-prem smoke** workflow runs on a standard public-repository `ubuntu-24.04` runner. GitHub documents 4 CPUs, 16 GB RAM and 14 GB SSD for this runner. The job has a 30-minute deadline.

It starts the same `make run` stack and submits a new German repair thread through `POST /api/analyse`. The thread separates a repaired tap, an active broken doorbell, a cancelled Wednesday proposal and a requested Friday visit. Checks cover those four fields and their `evidence_status=matched` source spans. Source offsets use UTF-16 units, matching the browser API contract. Each model call uses the real downloaded Apertus weights.

Artifacts contain the synthetic input, status, complete response, raw model output, check summary, host specifications and bounded container logs. A failed semantic check remains a failed run with its raw result attached. The workflow stops the containers after collecting diagnostics.

This run records **deployment reproduction on GitHub-hosted CI**. The deployment target is an organisation-administered machine running the same Docker configuration. The artifact gives the precise environment and observed outcome for the reproduction attempt.

### Six-case development evaluation

After the independent German smoke passes, `tests/evaluate.py` sends the six existing `data/cases.json` threads sequentially through the same application and model containers. Each request carries the source text. Expected answers are used by the local evaluator to calculate measurements. The shared prompt prefix can remain cached between calls.

The evaluator records `language_match`, `active_presence_match`, `resolved_presence_match`, `expected_missing_match`, `matched_source_count` and `valued_field_count`. Presence checks compare populated versus empty fields. Matched-source counts cover populated fields whose UTF-16 span equals the quoted source. Issue meaning and temporal interpretation receive separate human review. A recorded response can therefore complete evaluation with failed structural measurements; request or parsing errors make the evaluation step fail.

Each case saves its source, request, response, error, elapsed time and measurements under `temp/onprem-smoke/cases/`. JSON and readable field-value/evidence tables are checkpointed after each case. Request timeouts are capped at 480 seconds; the evaluation deadline reserves the final minute for diagnostics and artifacts. A failed first smoke skips these six calls.
