from __future__ import annotations

import secrets
from importlib.resources import files
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from yeelight_logic import CommandError, DeviceError, YeelightController


class CommandRequest(BaseModel):
    command: str = Field(min_length=1, max_length=500)


def create_app(
    controller: YeelightController | None = None,
    api_token: str | None = None,
) -> FastAPI:
    app = FastAPI(title="Yeelight Network", version="0.1.0")
    service = controller or YeelightController()

    async def authorize(x_api_token: str | None = Header(default=None)) -> None:
        if api_token and (
            x_api_token is None or not secrets.compare_digest(x_api_token, api_token)
        ):
            raise HTTPException(status_code=401, detail="A valid X-API-Token is required")

    @app.get("/api/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", include_in_schema=False)
    async def web_client() -> FileResponse:
        index = Path(str(files("yeelight_app").joinpath("static", "index.html")))
        if not index.is_file():
            raise HTTPException(status_code=500, detail="Web client files are missing")
        return FileResponse(index, media_type="text/html")

    @app.get("/api/bulbs", dependencies=[Depends(authorize)])
    async def bulbs() -> dict[str, Any]:
        return {"bulbs": service.known_bulbs()}

    @app.post("/api/commands", dependencies=[Depends(authorize)])
    async def command(request: CommandRequest) -> dict[str, Any]:
        try:
            result = await run_in_threadpool(service.execute, request.command)
            return {"ok": True, "result": result}
        except CommandError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        except DeviceError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return app
