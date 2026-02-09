import os
import uuid
from playwright.async_api import async_playwright
from jinja2 import Environment, FileSystemLoader

# 🔧 ВАЖНО: иначе Playwright не найдёт браузер на сервере
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HTML_DIR = os.path.join(BASE_DIR, "html")
OUT_DIR = os.path.join(BASE_DIR, "screens")

os.makedirs(OUT_DIR, exist_ok=True)

env = Environment(loader=FileSystemLoader(HTML_DIR))


async def render_html(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    html = template.render(**context)

    file_name = f"{uuid.uuid4()}.png"
    out_path = os.path.join(OUT_DIR, file_name)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu"
            ]
        )

        page = await browser.new_page(
            viewport={"width": 390, "height": 800}
        )

        await page.set_content(html, wait_until="networkidle")
        await page.wait_for_timeout(300)

        await page.screenshot(path=out_path)
        await browser.close()

    return out_path


# ---------- PROGRESS ----------
async def make_progress_screenshot(name: str, age: int, percent: int):
    return await render_html(
        "progress.html",
        {
            "name": name,
            "age": age,
            "percent": percent
        }
    )


# ---------- BALANCE ----------
async def make_balance_screenshot(name: str, balance: int, failed_amount: int):
    return await render_html(
        "balance.html",
        {
            "name": name,
            "balance": balance,
            "failed_amount": failed_amount
        }
    )


# ---------- SUCCESS ----------
async def make_success_screenshot(
    username: str,
    balance: int,
    withdraw: int,
    card: str,
    fullname: str
):
    return await render_html(
        "success.html",
        {
            "username": username,
            "balance": balance,
            "withdraw": withdraw,
            "card": card,
            "fullname": fullname
        }
    )
