from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from dotenv import load_dotenv

from yeelight_logic import YeelightController
from yeelight_network.api import create_app

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def main() -> None:
    host = os.getenv("YEELIGHT_HOST", "127.0.0.1")
    token = os.getenv("YEELIGHT_API_TOKEN")
    if host not in {"127.0.0.1", "localhost", "::1"} and not token:
        raise RuntimeError(
            "YEELIGHT_API_TOKEN is required when binding beyond localhost"
        )
    addresses = filter(None, (part.strip() for part in os.getenv("YEELIGHT_BULBS", "").split(",")))
    app = create_app(YeelightController(addresses), api_token=token)
    uvicorn.run(app, host=host, port=int(os.getenv("YEELIGHT_PORT", "8000")))


if __name__ == "__main__":
    main()
