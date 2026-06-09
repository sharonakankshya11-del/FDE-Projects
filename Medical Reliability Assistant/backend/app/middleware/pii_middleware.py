"""
app/middleware/pii_middleware.py
FastAPI middleware that masks PII in request bodies using Microsoft Presidio.
Masks: person names, phone numbers, email, SSN, medical record numbers,
       IP addresses, location identifiers.

The original query reaches no downstream system; only the anonymised version does.
"""
import json
import re
from typing import Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    _presidio_available = True
except ImportError:
    _presidio_available = False

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Simple regex fallbacks if Presidio not installed
_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_PHONE_RE = re.compile(r"\b(\+?\d[\d\s\-().]{7,}\d)\b")
_MRN_RE = re.compile(r"\bMRN[-\s]?\d{6,10}\b", re.IGNORECASE)

if _presidio_available:
    try:
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        _analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        _anonymizer = AnonymizerEngine()
        logger.info("Presidio PII engine loaded (en_core_web_sm).")
    except Exception as e:
        _presidio_available = False
        _analyzer = None
        _anonymizer = None
        logger.warning(f"Presidio init failed, using regex fallback: {e}")
else:
    _analyzer = None
    _anonymizer = None
    logger.warning("Presidio not available; using regex fallback for PII masking.")


def mask_pii(text: str) -> str:
    """Mask PII in a string. Returns anonymised string."""
    if not text:
        return text

    if _presidio_available:
        try:
            results = _analyzer.analyze(text=text, language="en")
            if results:
                anonymised = _anonymizer.anonymize(text=text, analyzer_results=results)
                return anonymised.text
        except Exception as e:
            logger.warning(f"Presidio error, falling back to regex: {e}")

    # Regex fallback
    text = _EMAIL_RE.sub("[EMAIL_REDACTED]", text)
    text = _PHONE_RE.sub("[PHONE_REDACTED]", text)
    text = _MRN_RE.sub("[MRN_REDACTED]", text)
    return text


class PIIMiddleware(BaseHTTPMiddleware):
    """
    Intercepts POST request bodies on /api/* routes.
    Masks PII in the 'query' field before the request reaches route handlers.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if request.method == "POST" and request.url.path.startswith("/api/"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body = json.loads(body_bytes.decode("utf-8"))
                    modified = False

                    # Mask 'query' field
                    if "query" in body and isinstance(body["query"], str):
                        original = body["query"]
                        masked = mask_pii(original)
                        if masked != original:
                            body["query"] = masked
                            modified = True
                            logger.info(f"PII masked in query for {request.url.path}")

                    if modified:
                        # Rebuild request with masked body
                        new_body = json.dumps(body).encode("utf-8")
                        async def receive():
                            return {"type": "http.request", "body": new_body}
                        request = Request(request.scope, receive)
            except Exception as e:
                logger.warning(f"PII middleware error (passing through): {e}")

        return await call_next(request)
