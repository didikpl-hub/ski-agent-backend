from playwright.sync_api import sync_playwright

def fetch_html(url: str, wait_for: str = None, timeout: int = 15000) -> str:
    """
    Fetch fully rendered HTML using headless Chromium.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(url, timeout=timeout)

        if wait_for:
            page.wait_for_selector(wait_for, timeout=timeout)

        html = page.content()
        browser.close()
        return html