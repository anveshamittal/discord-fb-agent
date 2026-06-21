"""
Standalone FastAPI app for the Facebook token generator.

This app has no Discord bot, no config validation, and no mappings.json dependency.
Use it as a separate Render Web Service for the /token UI.

Run locally:
    uvicorn token_app:app --host 0.0.0.0 --port 8000
"""

import os

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

from token_refresh import (
    HTML_PAGE,
    exchange_user_token,
    fetch_page_token,
    render_result,
)

app = FastAPI()


@app.get("/", response_class=HTMLResponse)
async def root():
    return HTML_PAGE.format(result="")


@app.get("/token", response_class=HTMLResponse)
async def token_form():
    return HTML_PAGE.format(result="")


@app.post("/token", response_class=HTMLResponse)
async def token_generate(
    app_id: str = Form(...),
    app_secret: str = Form(...),
    short_lived_token: str = Form(...),
    page_id: str = Form(...),
):
    try:
        long_lived_user_token = exchange_user_token(app_id, app_secret, short_lived_token)
        page_token = fetch_page_token(long_lived_user_token, page_id)
        result = render_result("", token=page_token)
    except Exception as e:
        result = render_result(f"Token generation failed: {e}", is_error=True)
    return HTML_PAGE.format(result=result)


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("token_app:app", host="0.0.0.0", port=port)
