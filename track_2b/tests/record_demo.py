"""Record the real CPU model and coordinator workflow with optional Playwright."""

import json
import os
from pathlib import Path
import time

from playwright.sync_api import sync_playwright


output = Path(os.environ.get("HAUSPOST_ARTIFACT_DIR", "temp/onprem-smoke/demo"))
output.mkdir(parents=True, exist_ok=True)
events = []
started = time.monotonic()


def event(name, **details):
    events.append({"name": name, "seconds": round(time.monotonic() - started, 3), **details})
    (output / "events.json").write_text(json.dumps(events, ensure_ascii=False, indent=2) + "\n")


with sync_playwright() as playwright:
    browser = playwright.chromium.launch()
    context = browser.new_context(viewport={"width": 1600, "height": 1000},
                                  record_video_dir=str(output),
                                  record_video_size={"width": 1600, "height": 1000},
                                  reduced_motion="reduce")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    started = time.monotonic()
    try:
        page.goto("http://127.0.0.1:4377", wait_until="networkidle")
        page.wait_for_function("state.mode === 'live' && state.cases.length === 6")
        event("desk_loaded")
        page.wait_for_timeout(2500)
        event("analysis_requested")
        with page.expect_response(lambda response: response.url.endswith("/api/analyse"), timeout=480000) as pending:
            page.locator("#analyseButton").click()
        response = pending.value
        result = response.json()
        (output / "live-response.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        assert response.status == 200, result
        page.wait_for_function("state.result?.origin === 'live'")
        event("model_result", model=result["model"], elapsed_ms=result["elapsed_ms"])
        page.screenshot(path=str(output / "live-result.png"), full_page=True)
        page.wait_for_timeout(4000)
        for key, label in (("active_issue", "Current repair"), ("resolved_issue", "Already resolved"),
                           ("cancelled_visit", "Cancelled visit"),
                           ("requested_visit", "Requested visit · awaiting confirmation")):
            page.get_by_role("button", name=label, exact=True).click()
            event("source_review", field=key)
            page.wait_for_timeout(2800)
        for key, field in result["fields"].items():
            expected = page.evaluate("key => state.selected.example.fields[key]", key)
            needs_entry = bool(expected["value"]) and not field.get("value")
            needs_link = bool(field.get("value")) and field.get("evidence_status") != "matched"
            if (needs_entry or needs_link) and expected["quote"]:
                # Each correction is a visible scripted coordinator action.
                page.locator(f".field-row.{key} button[aria-label^='Edit ']").click()
                if needs_entry:
                    page.locator("#fieldValue").fill(expected["value"])
                page.locator("#operatorEntry").uncheck()
                page.locator("#fieldQuote").fill(expected["quote"])
                page.wait_for_timeout(2000)
                page.get_by_role("button", name="Save detail", exact=True).click()
                event("coordinator_correction", field=key, added_value=needs_entry)
                page.wait_for_timeout(2000)
        page.locator("#confirmAll").click()
        page.get_by_role("button", name="Draft clarification", exact=True).click()
        assert "Wohnungsnummer" in page.locator("#handoffText").inner_text()
        event("clarification_draft")
        page.wait_for_timeout(7000)
        page.get_by_role("button", name="Close handoff", exact=True).click()
        page.get_by_role("button", name="Edit Apartment / unit", exact=True).click()
        page.locator("#fieldValue").fill("3B")
        page.wait_for_timeout(2500)
        page.get_by_role("button", name="Save detail", exact=True).click()
        event("coordinator_adds_unit")
        page.wait_for_timeout(2500)
        page.locator("#confirmAll").click()
        page.get_by_role("button", name="Create repair brief", exact=True).click()
        brief = page.locator("#handoffText").inner_text()
        assert "awaiting coordinator confirmation" in brief and "Coordinator entry" in brief
        event("repair_handoff")
        (output / "handoff.txt").write_text(brief)
        page.screenshot(path=str(output / "handoff.png"))
        page.wait_for_timeout(7000)
        assert not errors, errors
        event("completed", page_errors=errors)
    finally:
        context.close()
        event("video_saved", path=Path(page.video.path()).name)
        browser.close()
