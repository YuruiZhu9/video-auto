"""Web 服务器入口 — clawremote server"""

import os
import sys
import asyncio
import uvicorn
from config import load_config
from handlers.http_handler import create_app


def main():
    config_path = os.environ.get("CLAWREMOTE_CONFIG", "config.yaml")
    config = load_config(config_path if os.path.exists(config_path) else None)

    app = create_app(config)

    host = config.get("server", {}).get("host", "0.0.0.0")
    port = config.get("server", {}).get("port", 8080)
    debug = config.get("server", {}).get("debug", False)

    print(f"[ClawRemote] 启动服务 http://{host}:{port}")
    print(f"[ClawRemote] API 文档 http://{host}:{port}/docs")
    print(f"[ClawRemote] OpenClaw: {config['openclaw']['gateway_url']}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        log_level="info",
    )


if __name__ == "__main__":
    main()
