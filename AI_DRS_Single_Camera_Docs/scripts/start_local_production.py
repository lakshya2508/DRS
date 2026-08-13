"""
Local Production Server Launcher for AI DRS Platform
Starts uvicorn ASGI web server serving Cricbuzz Web UI & REST/WebSocket APIs.
"""

import sys
import uvicorn
from pathlib import Path

# Add src to Python search path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def main():
    print("=" * 70)
    print(" STARTING LOCAL PRODUCTION AI DRS SERVER")
    print("=" * 70)
    print(" [+] Mobile Web App UI : http://127.0.0.1:8000/")
    print(" [+] Interactive Docs   : http://127.0.0.1:8000/docs")
    print(" [+] Minimum DRS API    : http://127.0.0.1:8000/api/v1/drs/health")
    print(" [+] Model Inference API: http://127.0.0.1:8000/api/v1/model/status")
    print(" [+] Local LLM API      : http://127.0.0.1:8000/api/v1/llm/chat")
    print("=" * 70)

    uvicorn.run(
        "ai_drs.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
