# Yeelight-Network

FastAPI server exposing the Yeelight command service over HTTP.

Run with `python -m yeelight_network.server`. Configure the listening address,
port, optional API token and initial bulb IPs with the `YEELIGHT_HOST`,
`YEELIGHT_PORT`, `YEELIGHT_API_TOKEN` and `YEELIGHT_BULBS` environment
variables. In the main project these are loaded from its root `.env` file.

The server also serves the web client at `/`; API endpoints are available under
`/api`.
