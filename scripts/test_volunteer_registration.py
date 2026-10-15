"""
Test Suite: Linear Validation of Folk Internal Contacts on Volunteer Registration Form
Target URL: https://folknet.in/volunteer-registration.php
Description:
    Navigates to the volunteer registration page, enters mobile numbers from
    folk_internal sequentially, and validates whether the "Already submitted"
    popup appears upon submission.

Outputs:
    - Console formatted report with status per contact
    - Markdown report (volunteer_registration_report.md)
    - CSV report (volunteer_registration_report.csv)
    - JSON report (volunteer_registration_report.json)
"""

import sys
import os
import time
import json
import csv
import argparse
from datetime import datetime

# Import dictionaries
try:
    import mobile_dict
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
    import mobile_dict

PAGE_URL = "https://folknet.in/volunteer-registration.php"


class TestResult:
    def __init__(self, index, mobile, name, status, popup_title="", popup_text="", is_already_submitted=False, response_time_ms=0, error_message=""):
        self.index = index
        self.mobile = mobile
        self.name = name
        self.status = status  # 'PASS', 'FAIL', 'ERROR'
        self.popup_title = popup_title.strip() if popup_title else ""
        self.popup_text = popup_text.strip() if popup_text else ""
        self.is_already_submitted = is_already_submitted
        self.response_time_ms = response_time_ms
        self.error_message = error_message
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        return {
            "index": self.index,
            "mobile": self.mobile,
            "name": self.name,
            "status": self.status,
            "is_already_submitted": self.is_already_submitted,
            "popup_title": self.popup_title,
            "popup_text": self.popup_text,
            "response_time_ms": round(self.response_time_ms, 2),
            "error_message": self.error_message,
            "timestamp": self.timestamp
        }


def run_playwright_test(contacts, headed=False, slowmo=0, timeout_sec=15):
    """
    Executes linear browser tests using Playwright.
    """
    from playwright.sync_api import sync_playwright

    results = []
    total = len(contacts)

    print("\n" + "=" * 90)
    print(f"🚀 STARTING LINEAR VOLUNTEER REGISTRATION VALIDATION ({total} CONTACTS)")
    print(f"🌐 Target URL: {PAGE_URL}")
    print(f"🕒 Started At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not headed, slow_mo=slowmo)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(timeout_sec * 1000)

        # Initial navigation
        print(f"[*] Navigating to {PAGE_URL} ...")
        page.goto(PAGE_URL, wait_until="domcontentloaded")
        page.wait_for_selector("#otp-mobile", state="visible")
        print("[+] Page loaded successfully.\n")

        header_fmt = "{:<4} | {:<12} | {:<25} | {:<10} | {:<20} | {:<10}"
        print(header_fmt.format("#", "Mobile", "Contact Name", "Status", "Popup Title", "Time (ms)"))
        print("-" * 90)

        for idx, (mobile, name) in enumerate(contacts.items(), start=1):
            start_time = time.time()
            popup_title = ""
            popup_text = ""
            is_already_submitted = False
            status = "FAIL"
            err_msg = ""

            try:
                # Ensure we are ready on the mobile form
                # If mobile input is disabled or hidden, reload page
                mobile_input = page.locator("#otp-mobile")
                if not mobile_input.is_visible() or not mobile_input.is_enabled():
                    page.goto(PAGE_URL, wait_until="domcontentloaded")
                    page.wait_for_selector("#otp-mobile", state="visible")
                    mobile_input = page.locator("#otp-mobile")

                # Clear previous input and fill number
                mobile_input.fill("")
                mobile_input.fill(str(mobile))

                # Submit form
                submit_btn = page.locator("#mobile-form-submit-btn")
                submit_btn.click()

                # Wait for response: either Swal modal or OTP container
                # We poll for swal2-popup or otp-ctn
                matched = False
                for _ in range(int(timeout_sec * 10)):
                    swal_popup = page.locator(".swal2-popup")
                    otp_ctn = page.locator("#otp-ctn")

                    if swal_popup.is_visible():
                        title_el = page.locator(".swal2-title")
                        html_el = page.locator(".swal2-html-container")
                        popup_title = title_el.text_content() or ""
                        popup_text = html_el.text_content() or ""

                        if "Already submitted" in popup_title or "Already submitted" in popup_text:
                            is_already_submitted = True
                            status = "PASS"
                        else:
                            status = "FAIL"
                            err_msg = f"Popup appeared but not 'Already submitted': {popup_title}"

                        matched = True
                        # Dismiss popup cleanly
                        cancel_btn = page.locator(".swal2-cancel")
                        if cancel_btn.is_visible():
                            cancel_btn.click()
                        else:
                            page.evaluate("if (typeof Swal !== 'undefined') Swal.close();")
                        break

                    elif otp_ctn.is_visible():
                        # OTP container opened -> number is NOT already submitted
                        is_already_submitted = False
                        status = "FAIL"
                        err_msg = "OTP container displayed (Form not previously submitted)"
                        matched = True
                        # Reload to reset state for next contact
                        page.goto(PAGE_URL, wait_until="domcontentloaded")
                        page.wait_for_selector("#otp-mobile", state="visible")
                        break

                    time.sleep(0.1)

                if not matched:
                    status = "TIMEOUT"
                    err_msg = f"No popup or OTP form appeared within {timeout_sec}s"
                    page.goto(PAGE_URL, wait_until="domcontentloaded")
                    page.wait_for_selector("#otp-mobile", state="visible")

            except Exception as ex:
                status = "ERROR"
                err_msg = str(ex)
                try:
                    page.goto(PAGE_URL, wait_until="domcontentloaded")
                    page.wait_for_selector("#otp-mobile", state="visible")
                except Exception:
                    pass

            elapsed_ms = (time.time() - start_time) * 1000

            res = TestResult(
                index=idx,
                mobile=mobile,
                name=name,
                status=status,
                popup_title=popup_title,
                popup_text=popup_text,
                is_already_submitted=is_already_submitted,
                response_time_ms=elapsed_ms,
                error_message=err_msg
            )
            results.append(res)

            # Live terminal print
            status_display = f"✅ {status}" if status == "PASS" else f"❌ {status}"
            display_title = popup_title if popup_title else ("OTP Sent" if "OTP container" in err_msg else err_msg[:18])
            print(header_fmt.format(
                idx,
                mobile,
                name[:25],
                status_display,
                display_title[:20],
                f"{elapsed_ms:.1f}"
            ))

        browser.close()

    return results


def run_api_test(contacts):
    """
    Fast direct API validation using requests to backend endpoint:
    https://dashboard.folknet.in/volunteer-web/check-existing
    """
    import requests

    api_url = "https://dashboard.folknet.in/volunteer-web/check-existing"
    results = []
    total = len(contacts)

    print("\n" + "=" * 90)
    print(f"🚀 STARTING FAST API VALIDATION ({total} CONTACTS)")
    print(f"🌐 Backend Endpoint: {api_url}")
    print(f"🕒 Started At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 90 + "\n")

    header_fmt = "{:<4} | {:<12} | {:<25} | {:<10} | {:<20} | {:<10}"
    print(header_fmt.format("#", "Mobile", "Contact Name", "Status", "API Response", "Time (ms)"))
    print("-" * 90)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Origin": "https://folknet.in",
        "Referer": "https://folknet.in/volunteer-registration.php"
    })

    for idx, (mobile, name) in enumerate(contacts.items(), start=1):
        start_time = time.time()
        popup_title = ""
        popup_text = ""
        is_already_submitted = False
        status = "FAIL"
        err_msg = ""

        try:
            resp = session.post(api_url, data={"mobile": mobile}, timeout=10)
            elapsed_ms = (time.time() - start_time) * 1000

            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    if data.get("alreadySubmitted"):
                        is_already_submitted = True
                        status = "PASS"
                        popup_title = "Already submitted"
                        popup_text = "You have already submitted this form. Do you want to edit your response?"
                    else:
                        is_already_submitted = False
                        status = "FAIL"
                        popup_title = "Not Submitted"
                        err_msg = "Volunteer has not submitted registration yet (alreadySubmitted=False)"
                else:
                    status = "ERROR"
                    err_msg = data.get("message", "API returned success=false")
            else:
                status = "ERROR"
                err_msg = f"HTTP {resp.status_code}"

        except Exception as ex:
            elapsed_ms = (time.time() - start_time) * 1000
            status = "ERROR"
            err_msg = str(ex)

        res = TestResult(
            index=idx,
            mobile=mobile,
            name=name,
            status=status,
            popup_title=popup_title,
            popup_text=popup_text,
            is_already_submitted=is_already_submitted,
            response_time_ms=elapsed_ms,
            error_message=err_msg
        )
        results.append(res)

        status_display = f"✅ {status}" if status == "PASS" else f"❌ {status}"
        display_title = popup_title if popup_title else err_msg[:18]
        print(header_fmt.format(
            idx,
            mobile,
            name[:25],
            status_display,
            display_title[:20],
            f"{elapsed_ms:.1f}"
        ))

    return results


def generate_reports(results, output_dir="."):
    """
    Generates Markdown, CSV, and JSON report files.
    """
    os.makedirs(output_dir, exist_ok=True)
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status in ("ERROR", "TIMEOUT"))
    pass_percentage = (passed / total * 100) if total > 0 else 0
    avg_time = (sum(r.response_time_ms for r in results) / total) if total > 0 else 0

    # 1. Markdown Report
    md_path = os.path.join(output_dir, "volunteer_registration_report.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# 📋 Volunteer Registration Validation Report\n\n")
        f.write(f"- **Target URL**: [{PAGE_URL}]({PAGE_URL})\n")
        f.write(f"- **Generated At**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **Total Contacts Validated**: {total}\n")
        f.write(f"- **Validation Rule**: Popup modal contains `Already submitted`\n\n")

        f.write("## 📊 Summary Metrics\n\n")
        f.write("| Metric | Value | Percentage |\n")
        f.write("| :--- | :--- | :--- |\n")
        f.write(f"| **Total Checked** | {total} | 100.0% |\n")
        f.write(f"| **✅ Already Submitted (PASS)** | {passed} | {pass_percentage:.1f}% |\n")
        f.write(f"| **❌ Not Submitted / OTP Sent (FAIL)** | {failed} | {(failed / total * 100):.1f}% |\n")
        f.write(f"| **⚠️ Errors / Timeouts** | {errors} | {(errors / total * 100):.1f}% |\n")
        f.write(f"| **⚡ Average Response Time** | {avg_time:.1f} ms | - |\n\n")

        f.write("## 📝 Detailed Results Per Contact\n\n")
        f.write("| # | Mobile | Name | Result | Already Submitted? | Popup Title | Details / Error | Time (ms) |\n")
        f.write("| :--- | :--- | :--- | :--- | :---: | :--- | :--- | :---: |\n")

        for r in results:
            res_badge = "✅ PASS" if r.status == "PASS" else ("❌ FAIL" if r.status == "FAIL" else "⚠️ " + r.status)
            submitted_badge = "Yes" if r.is_already_submitted else "No"
            details = r.popup_text if r.popup_text else r.error_message
            # escape pipes for markdown
            details_clean = details.replace("|", "\\|").replace("\n", " ")
            popup_title_clean = r.popup_title.replace("|", "\\|")
            f.write(f"| {r.index} | `{r.mobile}` | **{r.name}** | {res_badge} | {submitted_badge} | {popup_title_clean} | {details_clean} | {r.response_time_ms:.1f} |\n")

        f.write("\n---\n*Report generated automatically by Antigravity Test Automation Suite.*\n")

    # 2. CSV Report
    csv_path = os.path.join(output_dir, "volunteer_registration_report.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "index", "mobile", "name", "status", "is_already_submitted",
            "popup_title", "popup_text", "response_time_ms", "error_message", "timestamp"
        ])
        writer.writeheader()
        for r in results:
            writer.writerow(r.to_dict())

    # 3. JSON Report
    json_path = os.path.join(output_dir, "volunteer_registration_report.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "pass_percentage": round(pass_percentage, 2),
                "avg_response_time_ms": round(avg_time, 2),
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            "results": [r.to_dict() for r in results]
        }, f, indent=2)

    print("\n" + "=" * 90)
    print("📊 VALIDATION SUMMARY")
    print("=" * 90)
    print(f"Total Contacts Checked: {total}")
    print(f"✅ Already Submitted (PASS): {passed} ({pass_percentage:.1f}%)")
    print(f"❌ Not Submitted (FAIL):      {failed} ({(failed / total * 100):.1f}%)")
    print(f"⚠️ Errors / Timeouts:        {errors} ({(errors / total * 100):.1f}%)")
    print(f"⚡ Average Response Time:    {avg_time:.1f} ms")
    print("-" * 90)
    print(f"📄 Markdown Report : {md_path}")
    print(f"📊 CSV Report      : {csv_path}")
    print(f"💾 JSON Report     : {json_path}")
    print("=" * 90 + "\n")


def main():
    parser = argparse.ArgumentParser(description="Validate mobile numbers on volunteer registration page")
    parser.add_argument("--dict", default="folk_internal", help="Dictionary name from mobile_dict (e.g. folk_internal, hknf, pvnp_contacts)")
    parser.add_argument("--mode", choices=["browser", "api"], default="browser",
                        help="Execution mode: 'browser' (Playwright E2E UI test) or 'api' (Direct HTTP POST check)")
    parser.add_argument("--headed", action="store_true", help="Run browser in headed (visible) mode")
    parser.add_argument("--slowmo", type=int, default=0, help="Slow down Playwright operations by N milliseconds")
    default_reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
    parser.add_argument("--output-dir", default=default_reports_dir, help="Directory to save report artifacts (default: reports/)")

    args = parser.parse_args()

    dict_name = args.dict
    contacts = getattr(mobile_dict, dict_name, None)
    if not contacts or not isinstance(contacts, dict):
        print(f"❌ Error: Dictionary '{dict_name}' not found in mobile_dict.py or is empty!")
        sys.exit(1)

    if args.mode == "browser":
        results = run_playwright_test(
            contacts=contacts,
            headed=args.headed,
            slowmo=args.slowmo,
            timeout_sec=args.timeout
        )
    else:
        results = run_api_test(contacts=contacts)

    generate_reports(results, output_dir=args.output_dir)


if __name__ == "__main__":
    main()
