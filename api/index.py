import os
import sys
import traceback

# Ensure project root directory is in sys.path for Vercel serverless execution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    from main import app
    handler = app
except Exception as e:
    err_tb = traceback.format_exc()
    print("FATAL ERROR ON STARTUP:\n", err_tb)
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse

    app = FastAPI(title="Focus OS - Startup Diagnostics")
    handler = app

    @app.get("/{full_path:path}", response_class=HTMLResponse)
    async def startup_error_page(full_path: str = ""):
        return f"""<!DOCTYPE html>
        <html>
        <head>
            <title>Focus OS - Startup Error</title>
            <style>
                body {{ background: #0b0f17; color: #f87171; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; padding: 2rem; }}
                .card {{ background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 1.5rem; max-width: 900px; margin: 0 auto; }}
                h1 {{ color: #ef4444; font-size: 1.5rem; margin-top: 0; }}
                pre {{ background: #1f2937; padding: 1rem; border-radius: 6px; overflow-x: auto; color: #fca5a5; font-size: 0.9rem; line-height: 1.4; }}
            </style>
        </head>
        <body>
            <div class="card">
                <h1>Focus OS Deployment Diagnostics</h1>
                <p>The application encountered an uncaught exception during startup:</p>
                <pre>{err_tb}</pre>
            </div>
        </body>
        </html>"""
