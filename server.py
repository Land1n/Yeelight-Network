from __future__ import annotations

import os
import socket
import subprocess
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
    port = int(os.getenv("YEELIGHT_PORT", "8000"))
    if host in {"0.0.0.0", "::"}:
        lan_ip = _lan_ipv4()
        if lan_ip:
            print(f"Phone app server address: http://{lan_ip}:{port}")
        else:
            print(f"Server listens on all interfaces at port {port}.")
        print("Enter this address and YEELIGHT_API_TOKEN in the Flet app.")
    uvicorn.run(app, host=host, port=port)


def _lan_ipv4() -> str | None:
    if os.name == "nt":
        command = (
            "$physical = Get-NetAdapter -Physical | "
            "Where-Object Status -eq 'Up' | "
            "Select-Object -ExpandProperty Name; "
            "Get-NetIPConfiguration | "
            "Where-Object { $_.InterfaceAlias -in $physical -and $_.IPv4DefaultGateway } | "
            "ForEach-Object { $_.IPv4Address | ForEach-Object IPAddress }"
        )
        try:
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command", command],
                capture_output=True,
                check=True,
                text=True,
                timeout=10,
            )
            for line in result.stdout.splitlines():
                address = line.strip()
                if address and not address.startswith("127."):
                    return address
        except (OSError, subprocess.SubprocessError):
            pass

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
            probe.connect(("192.0.2.1", 80))
            address = probe.getsockname()[0]
            return address if not address.startswith("127.") else None
    except OSError:
        return None


if __name__ == "__main__":
    main()
