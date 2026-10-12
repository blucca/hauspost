"""Run: python track_2b/tests/check.py. All model responses are local stubs."""

import http.client
import io
import json
import os
from pathlib import Path
import sys
import threading
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import server as app

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
    assert json.loads(sent["messages"][1]["content"])["tenant_email"] == source
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
finally:
    httpd.shutdown()
    httpd.server_close()
    thread.join()

print("PASS: model parsing, exact/ambiguous/missing evidence, UTF-16 spans, input and origin boundaries, single model dispatch")
