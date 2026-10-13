"""Record six-case live evaluation; issue semantics are reviewed separately."""

import argparse
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

FIELDS = ("active_issue", "resolved_issue", "property_address", "apartment",
          "requested_visit", "cancelled_visit", "contact_name")


def save_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def structural_metrics(case, result):
    fields = result["fields"]
    valued = {name: fields[name] for name in FIELDS if fields[name].get("value")}
    source = case["text"].encode("utf-16-le")
    matched = 0
    for field in valued.values():
        start, end, quote = field.get("start"), field.get("end"), field.get("quote")
        valid_span = (type(start) is int and type(end) is int
                      and 0 <= start < end <= len(source) // 2 and isinstance(quote, str))
        if (field.get("evidence_status") == "matched" and valid_span
                and source[2 * start:2 * end] == quote.encode("utf-16-le")):
            matched += 1
    expected = case["expected"]
    return {
        "language_match": result.get("language") == case["language"],
        "active_presence_match": bool(fields["active_issue"].get("value"))
                                 == bool(expected["source_quotes"]["active_issue"]),
        "resolved_presence_match": bool(fields["resolved_issue"].get("value"))
                                   == bool(expected["source_quotes"]["resolved_issue"]),
        "expected_missing_match": all(not fields[name].get("value")
                                      for name in expected.get("required_missing", [])),
        "matched_source_count": matched,
        "valued_field_count": len(valued),
    }


def write_summary(output, records, total):
    save_json(output / "summary.json", {"case_count": total, "cases": records})
    lines = ["# Six-case Apertus development evaluation", "",
             "Automatic measurements cover language, field presence, listed missing fields and literal source spans. "
             "Current-issue meaning and temporal interpretation receive separate human review.", "",
             "`matched_source_count` counts valued fields with an exact UTF-16 source match. "
             "`valued_field_count` counts populated values. Quote-only fields stay outside both counts. "
             "`expected_missing_match` checks the listed missing fields; an empty list satisfies that check.", "",
             f"Recorded cases: {len(records)}/{total}. Case errors: {sum(bool(r['error']) for r in records)}.", "",
             "| Case | language_match | active_presence_match | resolved_presence_match | expected_missing_match (listed) | matched_source_count / valued_field_count | HTTP wall ms |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for record in records:
        metric = record.get("metrics") or {}
        pending = record["status"] if record["error"] else "pending"
        values = [str(metric.get(key, pending)) for key in
                  ("language_match", "active_presence_match", "resolved_presence_match")]
        missing = f"{metric.get('expected_missing_match', pending)} ({len(record['expected_missing_fields'])})"
        ratio = f"{metric.get('matched_source_count', pending)} / {metric.get('valued_field_count', pending)}"
        lines.append(f"| {record['id']} | {' | '.join(values)} | {missing} | {ratio} | {record.get('elapsed_ms', 'pending')} |")
    for record in records:
        lines += ["", f"## {record['id']}", "", f"Status: {record['status']}; expected language: {record['expected_language']}."]
        if record["error"]:
            lines += ["", "Error: " + json.dumps(record["error"], ensure_ascii=False)]
        if record.get("fields"):
            lines += ["", f"Model: {record.get('model')}; model elapsed ms: {record.get('model_elapsed_ms')}.",
                      "Usage: " + json.dumps(record.get("usage"), ensure_ascii=False), "",
                      "| Field | Value | Evidence status | UTF-16 span |", "| --- | --- | --- | --- |"]
            for name in FIELDS:
                field = record["fields"][name]
                value = json.dumps(field.get("value"), ensure_ascii=False).replace("|", "\\|")
                lines.append(f"| {name} | {value} | {field.get('evidence_status')} | {field.get('start')}–{field.get('end')} |")
    (output / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def evaluate(cases, base_url, output, deadline=None):
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for index, case in enumerate(cases, start=1):
        case_dir = output / f"{index:02d}-{case['id']}"
        case_dir.mkdir(parents=True, exist_ok=True)
        request_body = {"text": case["text"]}
        save_json(case_dir / "request.json", request_body)
        (case_dir / "source.txt").write_text(case["text"], encoding="utf-8")
        record = {"id": case["id"], "expected_language": case["language"],
                  "expected_missing_fields": case["expected"].get("required_missing", []),
                  "status": "running", "http_status": None, "http_attempted": False,
                  "error": None, "metrics": None, "directory": case_dir.name}
        records.append(record)
        save_json(case_dir / "record.json", record)
        write_summary(output, records, len(cases))
        started = time.monotonic()
        try:
            remaining = deadline - time.time() if deadline is not None else 480
            if remaining <= 0:
                raise TimeoutError("Evaluation deadline reached before this request")
            request = urllib.request.Request(
                base_url.rstrip("/") + "/api/analyse",
                data=json.dumps(request_body, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            record["http_attempted"] = True
            with urllib.request.urlopen(request, timeout=min(480, remaining)) as response:
                record["http_status"] = response.status
                raw = response.read()
            (case_dir / "result.json").write_bytes(raw)
            result = json.loads(raw)
            if (not isinstance(result, dict) or not isinstance(result.get("fields"), dict)
                    or any(not isinstance(result["fields"].get(name), dict) for name in FIELDS)):
                raise ValueError("Application response requires all seven field objects")
            (case_dir / "raw-model-output.txt").write_text(str(result.get("raw_model_output", "")), encoding="utf-8")
            record.update(fields=result["fields"], model=result.get("model"),
                          usage=result.get("usage"), model_elapsed_ms=result.get("elapsed_ms"),
                          language=result.get("language"))
            record["metrics"] = structural_metrics(case, result)
            record["status"] = "completed"
        except urllib.error.HTTPError as error:
            record["http_status"] = error.code
            (case_dir / "http-error.txt").write_bytes(error.read())
            record["error"] = {"type": "HTTPError", "message": str(error)}
        except Exception as error:
            record["error"] = {"type": type(error).__name__, "message": str(error)}
        record["elapsed_ms"] = round((time.monotonic() - started) * 1000)
        if record["error"]:
            record["status"] = "error" if record["http_attempted"] else "deadline_skipped"
            save_json(case_dir / "error.json", record["error"])
        save_json(case_dir / "record.json", record)
        write_summary(output, records, len(cases))
        print(json.dumps({key: record.get(key) for key in
                          ("id", "status", "http_status", "elapsed_ms", "metrics", "error")}, ensure_ascii=False), flush=True)
    return records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:4377")
    parser.add_argument("--output", type=Path, default=Path("temp/onprem-smoke/cases"))
    parser.add_argument("--deadline", type=float, help="Unix timestamp that ends HTTP evaluation, leaving time for artifact collection")
    args = parser.parse_args()
    cases = json.loads((Path(__file__).resolve().parents[1] / "data/cases.json").read_text(encoding="utf-8"))
    records = evaluate(cases, args.base_url, args.output, args.deadline)
    raise SystemExit(1 if any(record["error"] for record in records) else 0)
