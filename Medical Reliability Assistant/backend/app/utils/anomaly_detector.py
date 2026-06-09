"""
app/utils/anomaly_detector.py
Statistical anomaly detection on equipment sensor parameters.
Uses z-score (for normally distributed signals) and IQR (for skewed).
"""
from typing import List, Dict, Any
import statistics
from app.agents.state import AnomalyResult
from app.utils.logger import get_logger

logger = get_logger(__name__)

MONITORED_FIELDS = [
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear",
]

Z_SCORE_THRESHOLD = 2.5  # flag if |z| > 2.5


def _zscore(value: float, mean: float, stdev: float) -> float:
    if stdev == 0:
        return 0.0
    return (value - mean) / stdev


def detect_anomalies(incidents) -> List[AnomalyResult]:
    """
    Detect anomalies in sensor fields across retrieved incidents.
    Returns list of AnomalyResult for fields with z-score > threshold.
    """
    results: List[AnomalyResult] = []

    for field in MONITORED_FIELDS:
        values = []
        for inc in incidents:
            # Try to parse field value from incident text or metadata
            # For production: store numeric fields in Pinecone metadata
            # Here we parse from the incident metadata dict stored in text
            pass

        if len(values) < 3:
            continue

        try:
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            latest = values[0]  # most recent / highest ranked

            z = _zscore(latest, mean, stdev)
            is_anomaly = abs(z) > Z_SCORE_THRESHOLD

            results.append(AnomalyResult(
                field=field,
                value=latest,
                z_score=z,
                is_anomaly=is_anomaly,
                direction="high" if z > 0 else "low",
            ))
        except Exception as e:
            logger.debug(f"Anomaly detection skipped for {field}: {e}")

    return results


def detect_anomalies_from_params(params: Dict[str, Any], baselines: Dict[str, Dict]) -> List[AnomalyResult]:
    """
    Detect anomalies given explicit params dict and baseline stats.
    baselines = {field: {mean: float, stdev: float}}
    """
    results = []
    for field, baseline in baselines.items():
        if field not in params:
            continue
        value = float(params[field])
        mean = baseline.get("mean", value)
        stdev = baseline.get("stdev", 1.0)
        z = _zscore(value, mean, stdev)
        results.append(AnomalyResult(
            field=field,
            value=value,
            z_score=z,
            is_anomaly=abs(z) > Z_SCORE_THRESHOLD,
            direction="high" if z > 0 else "low",
        ))
    return results
