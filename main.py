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
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.90 Safari/537.36"
        )
        page = await context.new_page()

        m3u8_urls = []

        async def check_response(response):
            try:
                if ".m3u8" in response.url:
                    print("🔎 Detectado:", response.url)
                    m3u8_urls.append(response.url)
            except Exception as e:
                print("⚠️ Error en check_response:", e)

        page.on("response", lambda response: asyncio.create_task(check_response(response)))

        try:
            await page.goto(url_embed, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000)  # Espera adicional 5 seg
            await asyncio.sleep(25)            # Espera extra para que cargue el video
        except Exception as e:
            print("⚠️ Error al cargar página:", e)

        await browser.close()

        if m3u8_urls:
            base_url = m3u8_urls[0].split("?")[0]  # Limpiar parámetros
            return base_url
        return None

@app.get("/extraer")
async def extraer(url: str = Query(..., description="URL de video embebido")):
    m3u8 = await extraer_m3u8(url)
    if m3u8:
        return {"status": "success", "m3u8_url": m3u8}
    return JSONResponse(status_code=404, content={"status": "error", "message": "No se encontró la URL .m3u8"})

@app.get("/health")
async def health():
    return {"status": "ok"}



