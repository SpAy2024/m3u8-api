import asyncio
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from playwright.async_api import async_playwright

app = FastAPI(title="M3U8 Extractor API", version="1.0")

async def extraer_m3u8(url_embed: str) -> str | None:
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context()
        page = await context.new_page()

        m3u8_urls = []

        async def check_response(response):
            try:
                if ".m3u8" in response.url:
                    print("🔎 Detectado:", response.url)
                    m3u8_urls.append(response.url)
            except:
                pass

        page.on("response", lambda response: asyncio.create_task(check_response(response)))

        try:
            await page.goto(url_embed, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(7)
        except Exception as e:
            print("⚠️ Error al cargar:", e)

        await browser.close()

        if m3u8_urls:
            return m3u8_urls[0]
        return None

@app.get("/extraer")
async def extraer(url: str = Query(..., description="URL de video embebido")):
    m3u8 = await extraer_m3u8(url)
    if m3u8:
        return {"status": "success", "m3u8_url": m3u8}
    return JSONResponse(status_code=404, content={"status": "error", "message": "No se encontró la URL .m3u8"})

