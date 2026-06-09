"""
app/data/narrative_generator.py

Transforms AI4I / predictive_maintenance CSV rows into natural-language
incident narrative documents with medical equipment framing.

Column mapping:
  Type (L/M/H)  → quality tier → maps to specific device type
  failure flags → failure_type string
  hospital_unit → derived from Type + UDI hash
  severity      → derived from failure type + sensor thresholds
"""
import hashlib
import random
from typing import Dict, Any, List

# ── Device type mapping ───────────────────────────────────────────────────────
DEVICE_MAP = {
    "L": [
        "Infusion Pump",
        "Patient Monitoring System",
        "Pulse Oximeter",
        "Defibrillator",
    ],
    "M": [
        "Ventilator",
        "Ultrasound Scanner",
        "ECG Monitor",
        "Anaesthesia Machine",
    ],
    "H": [
        "MRI System",
        "CT Scanner",
        "X-Ray Machine",
        "Laboratory Analyser",
    ],
}

HOSPITAL_UNITS = ["ICU", "ER", "OR", "Radiology", "Ward A", "Ward B", "NICU", "CCU"]

FAILURE_TYPE_MAP = {
    "TWF": "Tool Wear Failure (TWF)",
    "HDF": "Heat Dissipation Failure (HDF)",
    "PWF": "Power Failure (PWF)",
    "OSF": "Overstress Failure (OSF)",
    "RNF": "Random Failure (RNF)",
}

SEVERITY_MAP = {
    "TWF": "medium",
    "HDF": "high",
    "PWF": "high",
    "OSF": "medium",
    "RNF": "low",
    "No Failure": "info",
}


def _deterministic_choice(items: List[str], seed: int) -> str:
    rng = random.Random(seed)
    return rng.choice(items)


def _get_failure_flags(row: Dict[str, Any]) -> List[str]:
    flags = []
    for flag in ["TWF", "HDF", "PWF", "OSF", "RNF"]:
        if int(row.get(flag, 0)) == 1:
            flags.append(flag)
    return flags


def _classify_anomaly(row: Dict[str, Any]) -> str:
    """Simple threshold-based anomaly label for enrichment."""
    air_temp = float(row.get("Air temperature [K]", 300))
    proc_temp = float(row.get("Process temperature [K]", 310))
    rpm = float(row.get("Rotational speed [rpm]", 1500))
    torque = float(row.get("Torque [Nm]", 40))
    tool_wear = float(row.get("Tool wear [min]", 0))

    issues = []
    if air_temp > 304:
        issues.append("elevated ambient temperature")
    if proc_temp - air_temp > 12:
        issues.append("high process-to-ambient temperature differential")
    if rpm < 1200:
        issues.append("low rotational speed")
    if torque > 60:
        issues.append("high torque load")
    if tool_wear > 180:
        issues.append("critical component wear")

    return "; ".join(issues) if issues else "within normal operating parameters"


def row_to_narrative(row: Dict[str, Any], source: str = "ai4i") -> Dict[str, Any]:
    """
    Convert a single CSV row to an incident narrative document.
    Returns {id, text, metadata}.
    """
    udi = int(row.get("UDI", 0))
    product_id = str(row.get("Product ID", f"UNKNOWN-{udi}"))
    quality_type = str(row.get("Type", "M"))

    device_type = _deterministic_choice(DEVICE_MAP.get(quality_type, DEVICE_MAP["M"]), udi)
    hospital_unit = _deterministic_choice(HOSPITAL_UNITS, udi + 7)

    air_temp = float(row.get("Air temperature [K]", 300))
    proc_temp = float(row.get("Process temperature [K]", 310))
    rpm = int(row.get("Rotational speed [rpm]", 1500))
    torque = float(row.get("Torque [Nm]", 40))
    tool_wear = int(row.get("Tool wear [min]", 0))

    # Failure detection
    failure_flags = _get_failure_flags(row)

    # Support predictive_maintenance.csv which has 'Failure Type' column
    failure_type_str = str(row.get("Failure Type", ""))
    if failure_type_str and failure_type_str != "No Failure":
        failure_label = failure_type_str
        severity = "high"
        machine_failure = 1
    elif failure_flags:
        failure_label = " + ".join(FAILURE_TYPE_MAP[f] for f in failure_flags)
        severity = max((SEVERITY_MAP.get(f, "low") for f in failure_flags),
                       key=lambda s: ["info", "low", "medium", "high"].index(s))
        machine_failure = 1
    else:
        failure_label = "No Failure"
        severity = "info"
        machine_failure = int(row.get("Machine failure", row.get("Target", 0)))

    anomaly_note = _classify_anomaly(row)

    # ── Build narrative ────────────────────────────────────────────────────────
    if machine_failure == 1:
        narrative = (
            f"INCIDENT REPORT | Device: {device_type} [{product_id}] | Unit: {hospital_unit} | "
            f"Severity: {severity.upper()}\n"
            f"Equipment {product_id} ({device_type}) in {hospital_unit} recorded a maintenance incident. "
            f"Failure classification: {failure_label}. "
            f"At the time of failure: air temperature {air_temp:.1f}K, process temperature {proc_temp:.1f}K, "
            f"rotational speed {rpm} rpm, torque {torque:.1f} Nm, component wear {tool_wear} min. "
            f"Sensor anomalies detected: {anomaly_note}. "
            f"Immediate engineering review required. "
            f"Source dataset: {source}."
        )
    else:
        narrative = (
            f"OPERATIONAL LOG | Device: {device_type} [{product_id}] | Unit: {hospital_unit} | "
            f"Severity: INFO\n"
            f"Equipment {product_id} ({device_type}) in {hospital_unit} operating normally. "
            f"Current readings: air temperature {air_temp:.1f}K, process temperature {proc_temp:.1f}K, "
            f"rotational speed {rpm} rpm, torque {torque:.1f} Nm, component wear {tool_wear} min. "
            f"Status: {anomaly_note}. "
            f"Source dataset: {source}."
        )

    doc_id = f"{source}-{udi}"

    metadata = {
        "id": doc_id,
        "udi": udi,
        "product_id": product_id,
        "equipment_type": device_type,
        "hospital_unit": hospital_unit,
        "severity": severity,
        "failure_type": failure_label,
        "machine_failure": machine_failure,
        "air_temperature": air_temp,
        "process_temperature": proc_temp,
        "rotational_speed": rpm,
        "torque": torque,
        "tool_wear": tool_wear,
        "source": source,
        "text": narrative,  # stored in metadata for BM25 reconstruction
    }

    return {"id": doc_id, "text": narrative, "metadata": metadata}


def generate_narratives(
    rows: List[Dict[str, Any]], source: str = "ai4i"
) -> List[Dict[str, Any]]:
    """Convert all rows to narrative dicts."""
    return [row_to_narrative(row, source) for row in rows]
