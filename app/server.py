"""
server.py — L6 Production Uvicorn Server Entrypoint

Features:
✔ Loads FastAPI app from api.py
✔ Runs high-performance Uvicorn server
✔ Graceful shutdown (Kubernetes safe)
✔ Config-driven host/port/workers
✔ Logging enabled for production use
✔ Docker-ready, Kubernetes-ready

This file is what you run in production or local dev.
"""

import logging

import uvicorn

from src.utils.config import get_config

logger = logging.getLogger("UvicornServer")
logger.setLevel(logging.INFO)


def start_server():
    """
    Launch Uvicorn FastAPI server using config settings.
    """

    cfg = get_config()
    server_cfg = cfg.get("server", {})

    host = server_cfg.get("host", "127.0.0.1")
    port = int(server_cfg.get("port", 8000))
    reload = bool(server_cfg.get("reload", False))
    workers = int(server_cfg.get("workers", 1))

    logger.info("🚀 Starting Cautious Enigma ML API Server...")
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Workers: {workers}")
    logger.info(f"Reload: {reload}")

    uvicorn.run(
        "app.api:app",
        host=host,
        port=port,
        reload=reload,
        workers=workers,
        log_level="info",
    )


if __name__ == "__main__":
    start_server()
