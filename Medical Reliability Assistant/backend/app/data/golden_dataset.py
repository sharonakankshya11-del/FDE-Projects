"""
app/data/golden_dataset.py
20 hand-crafted golden Q&A pairs for DeepEval evaluation.
Each entry: {input, expected_output, context_keywords}
"""

GOLDEN_DATASET = [
    {
        "input": "MRI machine in Radiology showing heat dissipation failures after recent maintenance",
        "expected_output": (
            "Heat dissipation failures (HDF) in MRI systems are commonly caused by cooling system "
            "degradation, blocked ventilation, or improper post-maintenance recalibration. Immediate "
            "actions: (1) inspect cooling fans and fluid lines, (2) verify thermal management settings "
            "post-maintenance, (3) reduce scan load until resolved. Monitor process-to-ambient temperature "
            "differential; >12K indicates active thermal stress."
        ),
        "context_keywords": ["HDF", "heat dissipation", "MRI", "cooling", "temperature"],
    },
    {
        "input": "Ventilator power failures recurring in ICU Unit 3",
        "expected_output": (
            "Recurring Power Failures (PWF) in ventilators are a critical safety risk. Root causes "
            "include power supply unit degradation, faulty UPS batteries, or circuit overload. "
            "Immediate actions: (1) test UPS and backup power, (2) inspect power supply unit, "
            "(3) deploy backup ventilator. Escalate to facilities engineering for power circuit audit."
        ),
        "context_keywords": ["PWF", "power failure", "ventilator", "ICU", "UPS"],
    },
    {
        "input": "Infusion pump alerts increasing in Ward B, tool wear above 180 minutes",
        "expected_output": (
            "Tool wear > 180 minutes is a critical threshold for infusion pump drive mechanisms. "
            "This typically precedes Tool Wear Failure (TWF). Immediate replacement of the pump "
            "mechanism is recommended. Similar historical incidents show 87% failure rate within "
            "24 hours past this threshold."
        ),
        "context_keywords": ["TWF", "tool wear", "infusion pump", "Ward B"],
    },
    {
        "input": "CT scanner showing overstress failures with high torque readings",
        "expected_output": (
            "Overstress Failure (OSF) in CT scanners with high torque is consistent with gantry "
            "motor strain or bearing wear. Reduce rotational load immediately. Inspect motor drive "
            "components and bearing assemblies. Torque readings > 60 Nm warrant immediate shutdown "
            "for inspection."
        ),
        "context_keywords": ["OSF", "overstress", "CT scanner", "torque", "gantry"],
    },
    {
        "input": "Patient monitoring device anomaly in NICU — rotational speed low",
        "expected_output": (
            "Low rotational speed in NICU patient monitoring devices suggests drive motor degradation "
            "or mechanical obstruction. This can cause display lag and missed alarm triggers — "
            "critical in NICU environments. Immediate device swap recommended; send unit for "
            "preventive maintenance review."
        ),
        "context_keywords": ["rotational speed", "patient monitoring", "NICU", "alarm"],
    },
    {
        "input": "Which equipment type has the highest failure rate in the dataset?",
        "expected_output": (
            "Based on retrieved incidents, MRI Systems and Ventilators show the highest failure "
            "rates, predominantly Heat Dissipation Failures and Power Failures respectively. "
            "H-type equipment quality grades show concentrated high-severity incidents."
        ),
        "context_keywords": ["failure rate", "MRI", "ventilator", "HDF", "PWF"],
    },
    {
        "input": "Ultrasound scanner in OR showing random failures",
        "expected_output": (
            "Random Failures (RNF) in ultrasound equipment are often caused by intermittent "
            "electrical faults, connector corrosion, or transducer cable damage. Systematic "
            "diagnostic: (1) check all cable connections, (2) run transducer self-test, "
            "(3) review operating room humidity levels. RNF does not follow a deterministic "
            "pattern; exhaustive electrical inspection is required."
        ),
        "context_keywords": ["RNF", "random failure", "ultrasound", "OR", "transducer"],
    },
    {
        "input": "Equipment downtime increasing across all ICU devices this month",
        "expected_output": (
            "Widespread ICU equipment downtime suggests a systemic issue: shared power circuit "
            "instability, environmental factors (temperature/humidity), or deferred maintenance "
            "accumulation. Recommended: (1) audit ICU power infrastructure, (2) review HVAC "
            "maintenance logs, (3) perform simultaneous preventive maintenance sweep across all "
            "ICU assets. Cross-device correlation analysis recommended."
        ),
        "context_keywords": ["ICU", "downtime", "systemic", "power", "maintenance"],
    },
    {
        "input": "Defibrillator in ER showing tool wear failures",
        "expected_output": (
            "Tool Wear Failure in defibrillators typically involves electrode pad wear or internal "
            "switching mechanism degradation. In ER settings this is a critical life-safety issue. "
            "Replace electrode pads immediately, perform full defibrillator functional test, and "
            "keep a backup unit charged and available."
        ),
        "context_keywords": ["TWF", "defibrillator", "ER", "electrode", "life-safety"],
    },
    {
        "input": "Air temperature around lab analyser exceeding 304K",
        "expected_output": (
            "Ambient air temperature above 304K represents elevated thermal stress for laboratory "
            "analysers. This correlates with increased Heat Dissipation Failure risk. Ensure "
            "adequate room ventilation, verify HVAC is operational, and check that the analyser "
            "cooling vents are not obstructed. Continue monitoring; if temperature exceeds 308K, "
            "pause operations."
        ),
        "context_keywords": ["air temperature", "lab analyser", "HDF", "HVAC", "thermal"],
    },
    {
        "input": "How do I interpret failure probability scores?",
        "expected_output": (
            "Failure probability (0.0–1.0) is estimated from historical incident pattern matching "
            "and sensor anomaly z-scores. A score > 0.75 indicates high risk requiring immediate "
            "action. Scores 0.5–0.75 warrant increased monitoring frequency. Below 0.5, standard "
            "maintenance schedules apply. The score is based on retrieved incident similarity; "
            "always corroborate with direct device inspection."
        ),
        "context_keywords": ["failure probability", "z-score", "monitoring", "maintenance"],
    },
    {
        "input": "Anaesthesia machine in OR — process temperature 15K above air temperature",
        "expected_output": (
            "A 15K process-to-ambient temperature differential in anaesthesia machines is a critical "
            "warning sign for Heat Dissipation Failure. The normal differential threshold is ≤12K. "
            "Immediate actions: halt elective procedures, inspect internal cooling, and switch to "
            "backup equipment. Do not resume use until thermal fault is resolved."
        ),
        "context_keywords": ["anaesthesia machine", "HDF", "temperature differential", "OR"],
    },
    {
        "input": "ECG monitor alerts in CCU — torque reading 65 Nm",
        "expected_output": (
            "Torque of 65 Nm exceeds the normal operating range (typically ≤60 Nm) and indicates "
            "mechanical strain in the ECG monitor's recording mechanism. This is consistent with "
            "Overstress Failure (OSF) precursors. Service the drive mechanism promptly. In CCU "
            "environments, immediately replace with a standby unit."
        ),
        "context_keywords": ["ECG monitor", "OSF", "torque", "CCU", "overstress"],
    },
    {
        "input": "What maintenance schedule is recommended for high-wear equipment?",
        "expected_output": (
            "For equipment approaching tool wear > 150 minutes, transition to bi-weekly inspection "
            "cycles. Above 180 minutes, move to daily functional checks and plan component "
            "replacement within the next scheduled maintenance window. Track wear accumulation in "
            "your CMMS and set automated alerts at 160-minute threshold."
        ),
        "context_keywords": ["maintenance schedule", "tool wear", "CMMS", "inspection"],
    },
    {
        "input": "Pulse oximeter random failures in Ward A post midnight",
        "expected_output": (
            "Intermittent failures post-midnight may indicate power fluctuation issues during "
            "low-demand periods causing voltage instability. Also consider sensor fouling from "
            "overnight use patterns. Actions: (1) test during the failure time window, "
            "(2) inspect power conditioning, (3) clean and test optical sensors."
        ),
        "context_keywords": ["pulse oximeter", "RNF", "power", "Ward A", "sensor"],
    },
    {
        "input": "X-ray machine breakdown in Radiology — third failure this quarter",
        "expected_output": (
            "Three failures within a quarter indicates systematic reliability degradation, not "
            "isolated incidents. Likely root cause: aging component nearing end-of-life (tool wear "
            "accumulation) or recurring environmental stress. Recommend: (1) full component "
            "lifecycle audit, (2) review service history for pattern, "
            "(3) evaluate equipment replacement vs. overhaul cost-benefit."
        ),
        "context_keywords": ["X-ray", "Radiology", "recurring failure", "lifecycle", "overhaul"],
    },
    {
        "input": "How does the system detect equipment anomalies?",
        "expected_output": (
            "The system uses z-score statistical analysis on sensor parameters (air temperature, "
            "process temperature, rotational speed, torque, tool wear). A z-score > 2.5 flags an "
            "anomaly. It also applies IQR-based detection for skewed distributions. Anomalies are "
            "correlated across retrieved similar incidents to identify failure patterns."
        ),
        "context_keywords": ["z-score", "anomaly", "sensor", "IQR", "statistical"],
    },
    {
        "input": "ICU ventilator HDF — process temp 318K, air temp 301K",
        "expected_output": (
            "Temperature differential of 17K (318 − 301K) critically exceeds the 12K safe threshold "
            "for ventilators, confirming active Heat Dissipation Failure. Remove device from service "
            "immediately. Provide backup ventilation. Inspect heat exchanger, cooling fan, and "
            "thermal management system before returning to service."
        ),
        "context_keywords": ["HDF", "ventilator", "ICU", "temperature differential", "heat exchanger"],
    },
    {
        "input": "MRI system preventive maintenance checklist",
        "expected_output": (
            "MRI preventive maintenance checklist: (1) Helium level and cryogen system check, "
            "(2) RF shielding integrity test, (3) gradient coil inspection, (4) cooling system "
            "flow rate verification, (5) quench pipe inspection, (6) patient table mechanism test, "
            "(7) emergency stop function test. Schedule quarterly for high-utilisation systems."
        ),
        "context_keywords": ["MRI", "preventive maintenance", "checklist", "helium", "cooling"],
    },
    {
        "input": "Infusion pump OSF — high torque 62 Nm, tool wear 195 min",
        "expected_output": (
            "This combination (Overstress Failure + tool wear 195 min + torque 62 Nm) is a critical "
            "triple-indicator event. Historical data shows > 90% failure probability within 12 hours. "
            "Immediately: (1) replace infusion pump, (2) inspect drive motor and cam mechanism, "
            "(3) file maintenance incident report. Do not return to service without full overhaul."
        ),
        "context_keywords": ["OSF", "infusion pump", "tool wear", "torque", "critical"],
    },
]
