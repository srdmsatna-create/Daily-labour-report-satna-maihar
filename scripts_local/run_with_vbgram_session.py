"""Run a command with cookies from a dedicated local VBGRAM Chrome profile.

The cookie value is kept in process memory and is never printed or written to
the repository/log. On Windows, a manual run allows the user to sign in once;
scheduled runs reuse that persistent browser profile without prompting.
"""
import argparse
import os
from pathlib import Path
import subprocess
import sys

TARGET = "https://vbgramgrep.dord.gov.in/VBGRAMG/Secure_work.aspx?payload=YQL26U5Cur1To85X_ocjWXCXQLMXsSv9vpIIc7xmJMlIoHwNL91rGCgC1Ke_ie9b-a9DYoKRg3vO-kWZkWUovCx2e_SPYg05SZ3_4ClT8ZY9ygchbWsxx_1p4leHIFjeDMk-R8wcF5-xXfK_qpBS79z0CpYxeVZdsfjdnq1jLvbErn97JtjbZXfgI1-aMpU6RruDmtefzLka-9E1Um66bgotkl52pMOe9oSkJ4l5eo06wc8W3VcGWIDRY-lqu8OV"
HOST = "vbgramgrep.dord.gov.in"


def cookie_header(context):
    pairs = []
    for cookie in context.cookies():
        domain = str(cookie.get("domain", "")).lstrip(".").lower()
        name, value = str(cookie.get("name", "")), str(cookie.get("value", ""))
        if (domain == HOST or HOST.endswith("." + domain)) and name and value and not any(c in name + value for c in "\r\n;"):
            pairs.append(f"{name}={value}")
    return "; ".join(pairs)


def report_available(page):
    try:
        response = page.goto(TARGET, wait_until="domcontentloaded", timeout=90000)
        if response is not None and response.status in (401, 403):
            return False
        text = page.locator("body").inner_text(timeout=15000)
        normalized = " ".join(text.upper().split())
        return "R6.17" in normalized and "SECURE" in normalized and "BHUVAN" in normalized
    except Exception:
        return False


def acquire_cookie(scheduled):
    from playwright.sync_api import sync_playwright

    base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".local" / "share")
    profile = base / "SRDM" / "VBGRAM-Shared-Chrome"
    profile.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        options = {"user_data_dir": str(profile), "headless": os.name != "nt" or scheduled}
        try:
            context = playwright.chromium.launch_persistent_context(channel="chrome", **options)
        except Exception:
            context = playwright.chromium.launch_persistent_context(**options)
        try:
            page = context.pages[0] if context.pages else context.new_page()
            ready = report_available(page)
            if not ready and not scheduled and os.name == "nt":
                print("VBGRAM session expired. Opened Chrome me official portal login karein.", file=sys.stderr)
                print("Login/report khulne ke baad is window me Enter dabayein.", file=sys.stderr)
                input()
                ready = report_available(page)
            header = cookie_header(context) if ready else ""
            if ready:
                print("VBGRAM browser session verified; protected reports will use it.", file=sys.stderr)
            else:
                print("WARNING: VBGRAM session unavailable; public reports will continue and protected reports may retain old data.", file=sys.stderr)
            return header
        finally:
            context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scheduled", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    env = os.environ.copy()
    cookie = acquire_cookie(args.scheduled)
    if cookie:
        env["VBGRAM_COOKIE"] = cookie
    return subprocess.run(command, env=env).returncode


if __name__ == "__main__":
    raise SystemExit(main())
