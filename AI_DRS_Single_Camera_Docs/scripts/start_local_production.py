"""
Local Production Server Launcher for AI DRS Platform
Starts uvicorn ASGI web server serving all live match UIs & REST/WebSocket APIs.
"""

import sys
import uvicorn
from pathlib import Path

# Add src to Python search path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

BASE = "http://127.0.0.1:8000"

def main():
    print("=" * 70)
    print("   AI DRS - LIVE MATCH CRICKET PLATFORM")
    print("=" * 70)
    print(f" SCREENS (open on ground displays / laptops / mobile)")
    print(f"   >> Fulltrack Homepage   : {BASE}/")
    print(f"   >> Match Setup Wizard   : {BASE}/setup")
    print(f"   >> Operator Dashboard   : {BASE}/live")
    print(f"   >> Analytics Engine     : {BASE}/analytics")
    print(f"   >> Ground Scoreboard    : {BASE}/scoreboard")
    print()
    print(f" API")
    print(f"   >> API Docs (Swagger)   : {BASE}/docs")
    print(f"   >> DRS Health           : {BASE}/api/v1/drs/health")
    print(f"   >> Live Leagues         : {BASE}/api/v1/live/leagues")
    print(f"   >> All League Teams     : {BASE}/api/v1/leagues")
    print(f"   >> Pipeline Start       : POST {BASE}/pipeline/start")
    print(f"   >> Calibration          : {BASE}/api/v1/calibration/current")
    print(f"   >> WebSocket Live Feed  : ws://127.0.0.1:8000/ws/live")
    print("=" * 70)
    print()
    print("  QUICK START:")
    print("  1. Open /setup — configure your match + camera")
    print("  2. Click LAUNCH — pipeline starts automatically")
    print("  3. Open /live on operator laptop + /scoreboard on stadium screen")
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
