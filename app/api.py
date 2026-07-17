"""FastAPI inference service with health probes and Prometheus telemetry."""

import logging
import os
import secrets
import time
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, ConfigDict, Field

from src.pipelines.inference_pipeline import run_realtime_inference

logger = logging.getLogger(__name__)

REQUESTS = Counter(
    "cautious_enigma_http_requests_total",
    "HTTP requests handled",
    ("method", "path", "status"),
)
LATENCY = Histogram(
    "cautious_enigma_http_request_duration_seconds",
    "HTTP request latency",
    ("method", "path"),
)

app = FastAPI(
    title="Cautious Enigma Threat Detection API",
    description="Validated real-time and batch anomaly detection.",
    version="1.1.0",
)


class PredictionRequest(BaseModel):
    """Validated real-time feature payload."""

    model_config = ConfigDict(extra="forbid")
    data: dict[str, float] = Field(
        ...,
        min_length=1,
        max_length=64,
        examples=[{"hour": 12, "ip_freq": 3, "suspicious_flag": 1}],
    )


class BatchPredictionRequest(BaseModel):
    """Bounded inline batch; HTTP callers never control server file paths."""

    model_config = ConfigDict(extra="forbid")
    records: list[dict[str, float]] = Field(..., min_length=1, max_length=1_000)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Require a constant-time API-key match when configured by the operator."""
    expected = os.getenv("CAUTIOUS_API_KEY")
    if expected and (x_api_key is None or not secrets.compare_digest(x_api_key, expected)):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.middleware("http")
async def record_metrics(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    """Record bounded-cardinality request count and latency."""
    started = time.perf_counter()
    response = await call_next(request)
    route = request.scope.get("route")
    path = getattr(route, "path", "unmatched")
    REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    LATENCY.labels(request.method, path).observe(time.perf_counter() - started)
    return response


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/live")
async def liveness_probe() -> dict[str, bool]:
    return {"alive": True}


@app.get("/ready")
async def readiness_probe() -> dict[str, bool]:
    return {"ready": True}


@app.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", dependencies=[Depends(require_api_key)])
async def predict(req: PredictionRequest) -> dict[str, Any]:
    try:
        return {"prediction": run_realtime_inference(req.data)}
    except (ValueError, FileNotFoundError) as exc:
        logger.warning("Prediction rejected: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=503, detail="Model unavailable") from exc


@app.post("/batch_predict", dependencies=[Depends(require_api_key)])
async def batch_predict(req: BatchPredictionRequest) -> dict[str, Any]:
    try:
        predictions = run_realtime_inference(req.records)
        return {
            "status": "success",
            "rows_processed": len(predictions),
            "predictions": predictions,
        }
    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Batch prediction failed")
        raise HTTPException(status_code=503, detail="Model unavailable") from exc


@app.get("/")
async def root() -> dict[str, Any]:
    return {
        "service": "cautious-enigma",
        "version": app.version,
        "endpoints": ["/predict", "/batch_predict", "/health", "/ready", "/live"],
    }
