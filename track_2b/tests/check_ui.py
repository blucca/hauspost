"""Optional browser smoke: pip install playwright; playwright install chromium.

Start the application, then run this file. CDP_URL can reuse an existing browser.
Artifacts go to ./temp/hauspost-ui (or HAUSPOST_ARTIFACT_DIR).
"""

import json
import os
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright


base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4377"
output = Path(os.environ.get("HAUSPOST_ARTIFACT_DIR", "temp/hauspost-ui"))
output.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    cdp = os.environ.get("CDP_URL")
    browser = playwright.chromium.connect_over_cdp(cdp) if cdp else playwright.chromium.launch()
    context = browser.contexts[0] if cdp else browser.new_context()
    page = context.new_page()
    page.set_viewport_size({"width": 1440, "height": 1050})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(base, wait_until="networkidle")
    page.wait_for_function("state.cases.length === 6")
    # Use authored inputs to check UI state independently of model variability.
    page.evaluate("acceptResult(state.selected.example, 'example')")
    page.get_by_role("button", name="Confirm sourced details", exact=True).click()
    page.get_by_role("button", name="Draft clarification", exact=True).click()
    assert "Wohnungsnummer" in page.locator("#handoffText").inner_text()
    page.get_by_role("button", name="Close handoff", exact=True).click()
    page.get_by_role("button", name="Edit Apartment / unit", exact=True).click()
    page.locator("#fieldValue").fill("3B")
    page.get_by_role("button", name="Save detail", exact=True).click()
    page.get_by_role("button", name="Confirm sourced details", exact=True).click()
    page.get_by_role("button", name="Create repair brief", exact=True).click()
    brief = page.locator("#handoffText").inner_text()
    assert "awaiting coordinator confirmation" in brief and "Coordinator entry" in brief
    page.get_by_role("button", name="Close handoff", exact=True).click()

    page.evaluate("""() => {
      const bad = structuredClone(state.selected.example);
      bad.fields.active_issue.quote = 'A reordered quotation that is absent from the thread.';
      acceptResult(bad, 'example');
    }""")
    page.get_by_role("button", name="Confirm sourced details", exact=True).click()
    assert page.locator("#handoffButton").is_disabled()
    page.get_by_role("button", name="Edit Current repair", exact=True).click()
    quote = page.evaluate("state.selected.example.fields.active_issue.quote")
    page.locator("#fieldQuote").fill(quote)
    page.get_by_role("button", name="Save detail", exact=True).click()
    page.get_by_role("button", name="Confirm sourced details", exact=True).click()
    assert page.locator("#handoffButton").is_enabled()

    page.locator("#casePicker").select_option("de-archive-only")
    page.evaluate("acceptResult(state.selected.example, 'example')")
    page.get_by_role("button", name="Confirm sourced details", exact=True).click()
    page.get_by_role("button", name="Create routing note", exact=True).click()
    assert "property administration inbox" in page.locator("#handoffText").inner_text()
    page.get_by_role("button", name="Close handoff", exact=True).click()
    page.locator("#casePicker").select_option("it-heating-closure")
    page.evaluate("acceptResult(state.selected.example, 'example')")
    page.get_by_role("button", name="Confirm sourced details", exact=True).click()
    page.get_by_role("button", name="Draft closure reply", exact=True).click()
    assert "risolto" in page.locator("#handoffText").inner_text()
    page.get_by_role("button", name="Close handoff", exact=True).click()
    page.locator("#casePicker").select_option("de-doorbell-reschedule")
    page.evaluate("acceptResult(state.selected.example, 'example')")
    page.screenshot(path=str(output / "desktop.png"), full_page=True)
    page.set_viewport_size({"width": 390, "height": 844})
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
    page.screenshot(path=str(output / "mobile.png"), full_page=True)
    assert not errors, errors
    (output / "result.json").write_text(json.dumps({"passed": True, "page_errors": errors}))
    page.close()
    if not cdp:
        browser.close()

print("PASS: source correction gate, clarification, coordinator entry, unconfirmed visit, general routing, closure, mobile layout")
