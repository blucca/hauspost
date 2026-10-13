"""Run: python track_2b/tests/check.py. All model responses are local stubs."""

import http.client
import io
import json
import os
from pathlib import Path
import sys
import threading
from tempfile import TemporaryDirectory
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import server as app

example = app.parse_model_output(json.dumps(app.EXAMPLE_OUTPUT, ensure_ascii=False), app.EXAMPLE_EMAIL)
assert all(field["evidence_status"] == "matched" for field in example["fields"].values())
review = app.parse_model_output(json.dumps(app.REVIEW_OUTPUT, ensure_ascii=False), app.REVIEW_EMAIL)
assert review["fields"]["requested_visit"]["value"] is None
assert all(field["evidence_status"] == "matched" for field in review["fields"].values() if field["value"])
empty = app.parse_model_output('{"language":"de","fields":{"apartment":{"value":"null","quote":null}}}', "Address")
assert empty["fields"]["apartment"]["value"] is None
mismatch = app.parse_model_output('{"language":"en","fields":{"apartment":{"value":"99Z","quote":"Apartment 4B"}}}', 'Apartment 4B')
assert mismatch["fields"]["apartment"]["evidence_status"] == 'value_mismatch'
assert mismatch["fields"]["apartment"]["start"] == 0

source = "📨 Bonjour.\nLe chauffage est réparé.\nFuite encore active.\nVendredi 09:00\nVendredi 09:00"
payload = {"language": "fr", "fields": {
    "active_issue": {"value": "Leaking inlet", "quote": "Fuite encore active."},
    "resolved_issue": {"value": "Heating repaired", "quote": "Le chauffage est réparé."},
    "property_address": {"value": "Invented address", "quote": "Somewhere 8"},
    "cancelled_visit": {"value": "Vendredi 09:00", "quote": "Vendredi 09:00"},
    "requested_visit": {"value": None, "quote": "Vendredi 09:00\nVendredi 09:00"},
    "extra_action": {"value": "send email"}}}
raw = "<think>Private reasoning.</think>\n```json\n" + json.dumps(payload, ensure_ascii=False) + "\n```"
parsed = app.parse_model_output(raw, source)
fields = parsed["fields"]
assert set(fields) == set(app.FIELDS)
matched = fields["active_issue"]
assert matched["evidence_status"] == "matched"
assert source.encode("utf-16-le")[matched["start"] * 2:matched["end"] * 2].decode("utf-16-le") == matched["quote"]
assert matched["start"] == source.index(matched["quote"]) + 1
assert fields["cancelled_visit"]["evidence_status"] == "ambiguous"
assert fields["cancelled_visit"]["start"] is None
assert fields["property_address"]["evidence_status"] == "unmatched"
assert fields["contact_name"]["evidence_status"] == "missing"
assert fields["requested_visit"]["evidence_status"] == "missing"
assert fields["requested_visit"]["quote"] == "Vendredi 09:00\nVendredi 09:00"
try:
    app.parse_model_output('{"language":"en","fields":{"active_issue":{"value":7}}}', source)
except app.APIError as error:
    assert error.code == "model_format"
else:
    raise AssertionError("Field types require validation")

httpd = app.ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
thread = threading.Thread(target=httpd.serve_forever, daemon=True)
thread.start()
origin = f"http://127.0.0.1:{httpd.server_port}"


def request(method, route, data=None, headers=None):
    connection = http.client.HTTPConnection("127.0.0.1", httpd.server_port, timeout=3)
    body = json.dumps(data) if data is not None else None
    connection.request(method, route, body, headers or {})
    response = connection.getresponse()
    result = response.status, json.loads(response.read())
    connection.close()
    return result


def upstream(request, timeout):
    assert request.full_url == "http://model.example/v1/chat/completions"
    assert request.get_header("User-agent") == "HausPost/0.1"
    assert request.get_header("Authorization") is None
    assert timeout == 420
    sent = json.loads(request.data)
    assert sent["response_format"]["type"] == "json_schema"
    assert sent["response_format"]["json_schema"]["schema"] == app.OUTPUT_SCHEMA
    assert [message["role"] for message in sent["messages"]] == ["system", "user", "assistant", "user", "assistant", "user"]
    assert sent["messages"][-1]["content"] == app.email_message(source)
    return io.BytesIO(json.dumps({"choices": [{"message": {"content": raw}}],
                                  "usage": {"prompt_tokens": 100, "completion_tokens": 90}}).encode())


try:
    with patch.dict(os.environ, {"LLM_BASE_URL": "", "LLM_API_KEY": ""}):
        os.environ.pop("LLM_TIMEOUT_SECONDS", None)
        headers = {"Content-Type": "application/json", "Origin": origin}
        status = request("GET", "/api/status")[1]
        assert status["mode"] == "sample" and status["model_timeout_seconds"] == 180
        assert request("POST", "/api/analyse", {"text": source}, headers)[0] == 409
        assert request("POST", "/api/analyse", {"text": source},
                       {**headers, "Origin": "https://outside.example"})[0] == 403
        assert request("POST", "/api/analyse", {"text": source},
                       {**headers, "Content-Type": "text/plain"})[0] == 415
        assert request("POST", "/api/analyse", {"text": "x" * 16001}, headers)[0] == 413
        assert request("GET", "/data/../../LICENSE")[0] == 404
        os.environ["LLM_BASE_URL"] = "http://model.example/v1"
        os.environ["LLM_TIMEOUT_SECONDS"] = "420"
        status = request("GET", "/api/status")[1]
        assert status["mode"] == "live" and status["model_timeout_seconds"] == 420
        with patch.object(app, "urlopen", upstream):
            status, result = request("POST", "/api/analyse", {"text": source}, headers)
            assert status == 200 and result["fields"] == fields
            assert result["raw_model_output"] == raw and result["usage"]["prompt_tokens"] == 100
            app.MODEL_LOCK.acquire()
            try:
                assert request("POST", "/api/analyse", {"text": source}, headers)[1]["error"] == "analysis_busy"
            finally:
                app.MODEL_LOCK.release()
            raw = '{"language":"fr","fields":'
            status, result = request("POST", "/api/analyse", {"text": source}, headers)
            assert status == 502 and result["error"] == "model_format"
            assert result["raw_model_output"] == raw and result["model"] == app.configuration()["model"]
            assert result["usage"]["completion_tokens"] == 90 and isinstance(result["elapsed_ms"], int)
    Path("temp").mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="hauspost-trial-check-", dir="temp") as directory:
        quota = Path(directory) / "quota.json"
        quota.write_text(json.dumps({"attempts": app.TRIAL_REQUEST_LIMIT - 1}))
        with patch.dict(os.environ, {"LLM_BASE_URL": "https://api.publicai.co/v1",
                                     "LLM_NAME": "swiss-ai/apertus-v1.5-8b",
                                     "HAUSPOST_TRIAL_STATE": str(quota),
                                     "HAUSPOST_TRIAL_END": "2099-01-01T00:00:00Z"}):
            with patch.object(app, "call_model", return_value={"fields": fields, "usage": {"prompt_tokens": 100}}) as model:
                assert request("POST", "/api/analyse", {"text": "x" * 6001}, headers)[0] == 413
                status, result = request("POST", "/api/analyse", {"text": source}, headers)
                assert status == 200 and "usage" not in result
                saved = json.loads(quota.read_text())
                assert saved["attempts"] == app.TRIAL_REQUEST_LIMIT and saved["prompt_tokens"] == 100
                assert request("POST", "/api/analyse", {"text": source}, headers)[1]["error"] == "trial_capacity"
                assert request("GET", "/api/status")[1]["trial_available"] is False
                assert model.call_count == 1
                quota.write_text('{"attempts": 0}')
                os.environ["HAUSPOST_TRIAL_END"] = "2000-01-01T00:00:00Z"
                assert request("POST", "/api/analyse", {"text": source}, headers)[0] == 410
                quota.write_text("interrupted ledger write")
                assert request("POST", "/api/analyse", {"text": source}, headers)[0] == 503
finally:
    httpd.shutdown()
    httpd.server_close()
    thread.join()

print("PASS: model parsing, exact/ambiguous/missing evidence, UTF-16 spans, input and origin boundaries, single model dispatch")
