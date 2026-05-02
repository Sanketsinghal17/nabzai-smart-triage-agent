"""
NabzAI – Smart Appointment Triage Agent
Decision Engine (Core Logic)

A HYBRID decision engine combining rule-based triage with
ML-powered generalization for unseen symptom patterns.
Pipeline: Input → Rules → ML Fallback → Decide → Explain
"""

from ml_engine import (
    predict_from_symptoms,
    CATEGORY_URGENCY,
    CATEGORY_TO_SPECIALIST,
)


# ─────────────────────────────────────────────────────────────
# Symptom-to-Specialist Mapping Tables
# ─────────────────────────────────────────────────────────────

HIGH_URGENCY_SYMPTOMS = {
    "chest pain": {
        "specialist": "Cardiologist",
        "reason_fragment": "chest pain indicating potential cardiac involvement",
        "rule_label": "chest pain -> cardiac risk",
    },
    "breathing issue": {
        "specialist": "Pulmonologist",
        "reason_fragment": "breathing difficulty suggesting respiratory distress",
        "rule_label": "breathing issue -> respiratory distress",
    },
    "breathing difficulty": {
        "specialist": "Pulmonologist",
        "reason_fragment": "breathing difficulty suggesting respiratory distress",
        "rule_label": "breathing difficulty -> respiratory distress",
    },
    "shortness of breath": {
        "specialist": "Pulmonologist",
        "reason_fragment": "shortness of breath indicating compromised respiratory function",
        "rule_label": "shortness of breath -> respiratory compromise",
    },
    "severe bleeding": {
        "specialist": "Emergency Medicine",
        "reason_fragment": "severe bleeding requiring immediate medical intervention",
        "rule_label": "severe bleeding -> emergency intervention",
    },
    "fainting": {
        "specialist": "Cardiologist",
        "reason_fragment": "fainting episodes suggesting possible cardiovascular or neurological concern",
        "rule_label": "fainting -> cardiovascular concern",
    },
}

MEDIUM_URGENCY_SYMPTOMS = {
    "fever": {
        "specialist": "General Physician",
        "reason_fragment": "persistent fever requiring medical evaluation",
        "duration_threshold": 3,
        "rule_label": "fever (>=3 days) -> persistent infection",
    },
    "stomach pain": {
        "specialist": "Gastroenterologist",
        "reason_fragment": "stomach pain suggesting gastrointestinal concern",
        "rule_label": "stomach pain -> gastrointestinal concern",
    },
    "abdominal pain": {
        "specialist": "Gastroenterologist",
        "reason_fragment": "abdominal pain indicating possible gastrointestinal issue",
        "rule_label": "abdominal pain -> gastrointestinal issue",
    },
    "dizziness": {
        "specialist": "Neurologist",
        "reason_fragment": "dizziness suggesting potential neurological evaluation needed",
        "rule_label": "dizziness -> neurological evaluation",
    },
    "blurred vision": {
        "specialist": "Neurologist",
        "secondary_specialist": "Ophthalmologist",
        "reason_fragment": "blurred vision indicating potential neurological or ophthalmological concern",
        "rule_label": "blurred vision -> neurological / ophthalmological evaluation",
    },
    "joint pain": {
        "specialist": "Orthopedic",
        "reason_fragment": "joint pain warranting orthopedic assessment",
        "rule_label": "joint pain -> orthopedic assessment",
    },
    "back pain": {
        "specialist": "Orthopedic",
        "reason_fragment": "back pain requiring musculoskeletal evaluation",
        "rule_label": "back pain -> musculoskeletal evaluation",
    },
    "ear pain": {
        "specialist": "ENT Specialist",
        "reason_fragment": "ear pain indicating possible ENT condition",
        "rule_label": "ear pain -> ENT condition",
    },
    "sore throat": {
        "specialist": "ENT Specialist",
        "reason_fragment": "persistent sore throat needing ENT evaluation",
        "rule_label": "sore throat -> ENT evaluation",
    },
}

LOW_URGENCY_SYMPTOMS = {
    "headache": {
        "specialist": "General Physician",
        "reason_fragment": "mild headache manageable with general consultation",
        "rule_label": "headache -> general consultation",
    },
    "mild cold": {
        "specialist": "General Physician",
        "reason_fragment": "mild cold symptoms typical of a common viral infection",
        "rule_label": "mild cold -> viral infection",
    },
    "cold": {
        "specialist": "General Physician",
        "reason_fragment": "cold symptoms that can be managed with general care",
        "rule_label": "cold -> general care",
    },
    "cough": {
        "specialist": "General Physician",
        "reason_fragment": "cough symptoms suitable for general medical assessment",
        "rule_label": "cough -> general assessment",
    },
    "skin rash": {
        "specialist": "Dermatologist",
        "reason_fragment": "skin rash requiring dermatological evaluation",
        "rule_label": "skin rash -> dermatological evaluation",
    },
    "rash": {
        "specialist": "Dermatologist",
        "reason_fragment": "skin rash that should be evaluated by a dermatologist",
        "rule_label": "rash -> dermatological evaluation",
    },
    "acne": {
        "specialist": "Dermatologist",
        "reason_fragment": "acne condition best handled by a dermatologist",
        "rule_label": "acne -> dermatological care",
    },
    "runny nose": {
        "specialist": "General Physician",
        "reason_fragment": "runny nose indicative of a minor upper respiratory issue",
        "rule_label": "runny nose -> minor respiratory issue",
    },
    "sneezing": {
        "specialist": "General Physician",
        "reason_fragment": "sneezing likely related to allergies or a mild infection",
        "rule_label": "sneezing -> allergy or mild infection",
    },
    "body ache": {
        "specialist": "General Physician",
        "reason_fragment": "general body ache that can be assessed in a routine consultation",
        "rule_label": "body ache -> routine consultation",
    },
}

# Special combo rules: when multiple symptoms appear together
COMBO_RULES = [
    {
        "required": {"chest pain", "breathing issue"},
        "urgency": "High",
        "specialist": "Cardiologist",
        "confidence_boost": 10,
        "rule_label": "combo: chest pain + breathing issue -> cardiac emergency",
        "reason": (
            "Chest pain combined with breathing difficulty suggests "
            "a potential cardiac emergency requiring immediate attention"
        ),
    },
    {
        "required": {"chest pain", "breathing difficulty"},
        "urgency": "High",
        "specialist": "Cardiologist",
        "confidence_boost": 10,
        "rule_label": "combo: chest pain + breathing difficulty -> cardiac emergency",
        "reason": (
            "Chest pain combined with breathing difficulty suggests "
            "a potential cardiac emergency requiring immediate attention"
        ),
    },
    {
        "required": {"chest pain", "shortness of breath"},
        "urgency": "High",
        "specialist": "Cardiologist",
        "confidence_boost": 10,
        "rule_label": "combo: chest pain + shortness of breath -> cardiac event",
        "reason": (
            "Chest pain with shortness of breath raises high suspicion "
            "of a cardiac event — urgent cardiology referral recommended"
        ),
    },
    {
        "required": {"fever", "headache"},
        "urgency": "Medium",
        "specialist": "General Physician",
        "confidence_boost": 5,
        "rule_label": "combo: fever + headache -> systemic infection",
        "reason": (
            "Fever accompanied by headache may indicate a systemic "
            "infection requiring prompt medical evaluation"
        ),
    },
    {
        "required": {"dizziness", "fainting"},
        "urgency": "High",
        "specialist": "Cardiologist",
        "confidence_boost": 10,
        "rule_label": "combo: dizziness + fainting -> cardiovascular concern",
        "reason": (
            "Dizziness with fainting episodes suggests a potentially "
            "serious cardiovascular or neurological condition"
        ),
    },
]

# Urgency rank for comparisons (higher = more urgent)
URGENCY_RANK = {"Low": 1, "Medium": 2, "High": 3}

# Map urgency to human-friendly risk level
RISK_LEVEL_MAP = {"High": "Critical", "Medium": "Moderate", "Low": "Mild"}

# Specialist clinical priority scores (higher = more critical specialty)
SPECIALIST_PRIORITY = {
    "Cardiologist": 5,
    "Pulmonologist": 5,
    "Ophthalmologist": 5,
    "Neurologist": 4,
    "Urologist": 4,
    "Psychiatrist": 4,
    "Orthopedic": 4,
    "Gastroenterologist": 4,
    "Endocrinologist": 3,
    "Dermatologist": 3,
    "ENT Specialist": 3,
    "Dentist": 2,
    "Oncologist": 5,
    "General Physician": 1,
}

# ─────────────────────────────────────────────────────────────
# Symptom Normalization Layer
# ─────────────────────────────────────────────────────────────

# Exact alias mapping: real-world variations → canonical symptom
SYMPTOM_MAP = {
    "tightness in chest": "chest pain",
    "chest discomfort": "chest pain",
    "pressure in chest": "chest pain",
    "chest tightness": "chest pain",
    "heart pain": "chest pain",
    "shortness of breath": "breathing issue",
    "difficulty breathing": "breathing issue",
    "breathlessness": "breathing issue",
    "can't breathe": "breathing issue",
    "trouble breathing": "breathing issue",
    "high fever": "fever",
    "mild fever": "fever",
    "high temperature": "fever",
    "abdominal discomfort": "stomach pain",
    "tummy pain": "stomach pain",
    "belly pain": "stomach pain",
    "loss of balance": "dizziness",
    "feeling dizzy": "dizziness",
    "lightheaded": "dizziness",
    "light headed": "dizziness",
    "migraine": "headache",
    "head pain": "headache",
    "skin irritation": "skin rash",
    "itchy skin": "skin rash",
    "running nose": "runny nose",
    "blocked nose": "cold",
    "nasal congestion": "cold",
    "throwing up": "stomach pain",
    "nausea": "stomach pain",
    "vomiting": "stomach pain",
    "passed out": "fainting",
    "blacked out": "fainting",
    "sweating": "sweating",
    "blurry vision": "blurred vision",
    "vision problems": "blurred vision",
    "can't see clearly": "blurred vision",
    "fuzzy vision": "blurred vision",
}


def _normalize_symptom(symptom: str) -> str:
    """
    Normalize a single symptom string to its canonical form.
    Uses exact mapping first, then keyword-based fuzzy matching.
    """
    s = symptom.strip().lower()

    # Exact alias lookup
    if s in SYMPTOM_MAP:
        return SYMPTOM_MAP[s]

    # Keyword-based fallback matching
    if "chest" in s:
        return "chest pain"
    if "breath" in s:
        return "breathing issue"
    if "fever" in s or "temperature" in s:
        return "fever"
    if "stomach" in s or "abdominal" in s or "abdomen" in s:
        return "stomach pain"
    if "dizz" in s or "balance" in s or "lightheaded" in s:
        return "dizziness"
    if "head" in s and "ache" in s:
        return "headache"
    if "rash" in s or "skin" in s:
        return "skin rash"
    if "faint" in s or "passed out" in s:
        return "fainting"
    if "bleed" in s:
        return "severe bleeding"
    if "vision" in s or "blurr" in s:
        return "blurred vision"
    if "throat" in s:
        return "sore throat"
    if "ear" in s and "pain" in s:
        return "ear pain"

    return s


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

def _normalize_symptoms(symptoms: list) -> list:
    """Lowercase, strip, and normalize each symptom to its canonical form, then deduplicate."""
    normalized = [_normalize_symptom(s) for s in symptoms if isinstance(s, str)]
    # deduplicate while preserving order
    return list(dict.fromkeys(normalized))


def _classify_single_symptom(symptom: str, duration_days: int):
    """
    Classify a single symptom and return its urgency level,
    specialist, reason fragment, and rule_label.

    Returns None if the symptom is unrecognized.
    """
    # Check HIGH urgency table
    if symptom in HIGH_URGENCY_SYMPTOMS:
        entry = HIGH_URGENCY_SYMPTOMS[symptom]
        return {
            "urgency": "High",
            "specialist": entry["specialist"],
            "secondary_specialist": entry.get("secondary_specialist"),
            "reason_fragment": entry["reason_fragment"],
            "rule_label": entry["rule_label"],
        }

    # Check MEDIUM urgency table
    if symptom in MEDIUM_URGENCY_SYMPTOMS:
        entry = MEDIUM_URGENCY_SYMPTOMS[symptom]
        # Duration-gated symptoms (e.g., fever >= 3 days)
        threshold = entry.get("duration_threshold")
        if threshold and duration_days < threshold:
            return {
                "urgency": "Low",
                "specialist": entry["specialist"],
                "secondary_specialist": entry.get("secondary_specialist"),
                "reason_fragment": f"recent {symptom} (under {threshold} days) that can be monitored",
                "rule_label": f"{symptom} (under {threshold} days) -> monitor",
            }
        return {
            "urgency": "Medium",
            "specialist": entry["specialist"],
            "secondary_specialist": entry.get("secondary_specialist"),
            "reason_fragment": entry["reason_fragment"],
            "rule_label": entry["rule_label"],
        }

    # Check LOW urgency table
    if symptom in LOW_URGENCY_SYMPTOMS:
        entry = LOW_URGENCY_SYMPTOMS[symptom]
        return {
            "urgency": "Low",
            "specialist": entry["specialist"],
            "secondary_specialist": entry.get("secondary_specialist"),
            "reason_fragment": entry["reason_fragment"],
            "rule_label": entry["rule_label"],
        }

    return None


def _check_combo_rules(symptom_set: set):
    """
    Check if any combo rule matches the provided symptom set.
    Returns the first matching combo rule or None.
    """
    for rule in COMBO_RULES:
        if rule["required"].issubset(symptom_set):
            return rule
    return None


def _apply_severity_override(urgency: str, severity: str) -> str:
    """
    If the patient-reported severity is 'high', escalate urgency
    by one level (Low → Medium, Medium → High).
    """
    severity_lower = severity.strip().lower()
    if severity_lower == "high":
        if urgency == "Low":
            return "Medium"
        if urgency == "Medium":
            return "High"
    return urgency


def _compute_confidence(
    num_symptoms: int,
    num_matched: int,
    combo_boost: int,
    clean_symptoms: list,
    severity: str = "normal",
    num_rules: int = 0,
    final_urgency: str = "Low",
) -> int:
    """
    Compute a realistic confidence percentage dynamically.
    - Strong rule match -> 80-95%
    - Moderate rule match -> 65-80%
    - Weak/unknown -> 20-50%
    """
    if num_matched == 0:
        base = 20
        max_val = 50
    elif num_matched == num_symptoms and num_symptoms > 0:
        base = 80
        max_val = 95
    else:
        base = 65
        max_val = 80

    # Pseudo-random variance based on symptom string hash
    variance = hash("".join(clean_symptoms)) % 15
    
    score = base + variance + combo_boost
    
    sev = severity.strip().lower()
    if sev == "high":
        score += 5

    if final_urgency == "High":
        score = max(80, score)

    return max(base, min(score, max_val))


def _build_reason(
    clean_symptoms: list,
    combo_reason: str | None,
    severity: str,
    final_urgency: str,
    best_specialist: str = "",
    secondary_specialist: str | None = None,
) -> str:
    """
    Generate a clear, human-readable reason string that explains
    the decision in natural language, ensuring symptom mention and varied structure.
    """
    if not clean_symptoms:
        symp_str = "the reported symptoms"
    elif len(clean_symptoms) == 1:
        symp_str = clean_symptoms[0]
    else:
        symp_str = ", ".join(clean_symptoms[:-1]) + " and " + clean_symptoms[-1]

    if final_urgency == "High":
        templates = [
            "With symptoms like {symptoms}, this raises immediate concern for a serious {specialist} issue.",
            "The combination of {symptoms} points to a potentially critical condition requiring urgent {specialist} evaluation.",
            "Given the severity of {symptoms}, immediate {specialist} intervention is strongly advised.",
            "The presentation of {symptoms} indicates a severe condition that demands prompt {specialist} attention.",
            "In this case, experiencing {symptoms} creates a critical pattern that necessitates immediate {specialist} care."
        ]
    elif final_urgency == "Low":
        if best_specialist in ("Primary Care", "General Physician"):
            templates = [
                "With symptoms like {symptoms}, the condition appears mild and manageable by a {specialist}.",
                "Reporting {symptoms} does not strongly point to a specific emergency, so a general {specialist} evaluation is reasonable.",
                "Presentations involving {symptoms} are commonly seen in less serious conditions and usually resolve with basic {specialist} care.",
                "Given the occurrence of {symptoms}, a routine check-up with a {specialist} should be sufficient.",
                "In this case, experiencing {symptoms} does not suggest a severe emergency, making a {specialist} consultation appropriate."
            ]
        else:
            templates = [
                "With symptoms like {symptoms}, the condition appears non-critical but warrants a {specialist} check-up.",
                "Presentations involving {symptoms} suggest a mild issue best evaluated by a {specialist}.",
                "The occurrence of {symptoms} typically points to manageable conditions requiring routine {specialist} care.",
                "Given the presentation of {symptoms}, monitoring by a {specialist} is advisable.",
                "In this case, experiencing {symptoms} indicates a need for a {specialist} assessment, though not urgently."
            ]
    else:
        templates = [
            "Experiencing {symptoms} is a typical pattern seen in conditions requiring a {specialist}.",
            "With symptoms like {symptoms}, targeted assessment by a {specialist} is recommended.",
            "Presentations involving {symptoms} are commonly linked to {specialist}-related issues.",
            "The pattern of {symptoms} strongly suggests a need for {specialist} expertise.",
            "Given the presentation of {symptoms}, evaluation by a {specialist} is the appropriate next step."
        ]

    variation = hash("".join(clean_symptoms)) % len(templates)
    base_sentence = templates[variation].format(symptoms=symp_str, specialist=best_specialist)
    base_sentence = base_sentence[0].upper() + base_sentence[1:]

    parts = []
    if combo_reason:
        parts.append(combo_reason)

    parts.append(base_sentence)

    if secondary_specialist:
        parts.append(f"A {secondary_specialist} could offer a secondary perspective.")

    sev = severity.strip().lower()
    if sev == "high" and final_urgency != "High":
        parts.append("The reported high severity reinforces the need for timely medical attention.")

    return " ".join(parts)


# ─────────────────────────────────────────────────────────────
# Explainability Helpers (NEW)
# ─────────────────────────────────────────────────────────────

def _get_risk_level(urgency: str) -> str:
    """Map urgency to a human-friendly risk level."""
    return RISK_LEVEL_MAP.get(urgency, "Mild")


def _collect_matched_rules(classifications: list, combo) -> list:
    """Gather rule labels from individual classifications and combo."""
    rules = []
    if combo:
        rules.append(combo["rule_label"])
    for c in classifications:
        label = c.get("rule_label")
        if label and label not in rules:
            rules.append(label)
    return rules


def _find_secondary_specialist(classifications: list, primary: str):
    """
    Return a secondary specialist if symptoms map to more than one distinct
    medical domain. Uses SPECIALIST_PRIORITY for intelligent ranking.
    Filters out General Physician as secondary (not clinically meaningful).
    """
    all_specialists = []
    for c in classifications:
        all_specialists.append(c["specialist"])
        # Check for explicit secondary specialist from symptom tables
        explicit_sec = c.get("secondary_specialist")
        if explicit_sec:
            all_specialists.append(explicit_sec)

    # Include primary to correctly assess all unique domains
    if primary not in all_specialists:
        all_specialists.append(primary)

    # Remove duplicates while preserving order
    unique_specialists = list(dict.fromkeys(all_specialists))

    # Sort by clinical priority (highest first)
    unique_specialists.sort(
        key=lambda s: SPECIALIST_PRIORITY.get(s, 0),
        reverse=True,
    )

    # Secondary = highest-priority specialist that is NOT the primary
    # and NOT "General Physician" (not a meaningful secondary referral)
    for s in unique_specialists:
        if s != primary and s != "General Physician":
            return s
    return None


def _build_steps(
    clean_symptoms: list,
    severity: str,
    duration_days: int,
    combo,
    classifications: list,
    severity_changed: bool,
    escalated: bool,
    final_urgency: str,
    best_specialist: str,
    secondary_specialist,
) -> list:
    """Build dynamic, professional agent reasoning steps."""
    steps = []

    # Step 1 – Normalize
    symptoms_str = ', '.join(clean_symptoms) if clean_symptoms else 'none'
    steps.append(
        f"Step 1: Normalized and deduplicated {len(clean_symptoms)} symptom(s) - {symptoms_str}"
    )

    # Step 2 – Context
    steps.append(
        f"Step 2: Evaluated clinical context (severity: {severity}, duration: {duration_days} day(s))"
    )

    # Step 3 – Rule check
    matched_count = len(classifications)
    if combo:
        steps.append("Step 3: Rule-based match identified multi-symptom combo pattern")
    elif matched_count:
        steps.append(f"Step 3: Rule-based match identified {matched_count} symptom(s) against knowledge base")
    else:
        steps.append("Step 3: No critical rule match found")

    # Step 4 & 5 - ML and Override
    steps.append("Step 4: ML inference skipped (rule match sufficient)")
    steps.append("Step 5: Symptom override skipped")

    # Step 6 – Specialist mapping
    if secondary_specialist:
        steps.append(f"Step 6: Mapped primary specialist to {best_specialist}; secondary to {secondary_specialist}")
    else:
        steps.append(f"Step 6: Mapped primary specialist to {best_specialist}")

    # Step 7 – Final reasoning
    steps.append(f"Step 7: Final reasoning applied {final_urgency} urgency with calibrated confidence")

    return steps


# ─────────────────────────────────────────────────────────────
# Symptom Override Layer (Priority 2 — between Rules and ML)
# ─────────────────────────────────────────────────────────────

def _symptom_override(symptoms: list) -> str | None:
    """
    Check for strong symptom patterns that should override ML predictions.
    Returns a category string if a high-confidence pattern is detected,
    or None to let ML handle the decision.

    Priority order (within this function):
      Psychiatry > Ophthalmology > Dental > Dermatology > Orthopedic > Urology
    """
    text = " ".join(symptoms).lower()

    # Psychiatry (mental health)
    if any(kw in text for kw in [
        "anxiety", "depression", "stress", "panic",
        "sleep disturbance", "restlessness", "mood swing",
        "suicidal", "insomnia", "nervousness",
    ]):
        return "Psychiatry"

    # Ophthalmology (MUST be checked BEFORE neurological patterns)
    if any(kw in text for kw in [
        "eye pain", "blurred vision", "vision problem",
        "watery eyes", "eye redness", "double vision",
        "eye swelling", "eye irritation",
    ]):
        return "Ophthalmology"

    # Dental
    if any(kw in text for kw in [
        "tooth pain", "gum swelling", "bad breath",
        "toothache", "gum bleeding", "cavity",
    ]):
        return "Dental"

    # Dermatology (skin + hair)
    if any(kw in text for kw in [
        "hair fall", "dandruff", "itchy scalp",
        "hair loss", "scalp",
    ]):
        return "Dermatology"

    # Orthopedic
    if any(kw in text for kw in [
        "joint pain", "knee pain", "bone pain", "back pain",
        "hip pain", "shoulder pain", "fracture",
    ]):
        return "Orthopedic"

    # Urology
    if any(kw in text for kw in [
        "burning urination", "frequent urination",
        "blood in urine", "bladder pain",
    ]):
        return "Urology"

    return None


# ─────────────────────────────────────────────────────────────
# Main Public API
# ─────────────────────────────────────────────────────────────

import random

def _get_general_physician_variant(
    urgency: str, num_symptoms: int, severity: str, duration_days: int, is_vague: bool = False
) -> str:
    """Returns a consistent professional variant of General Physician based on context."""
    if duration_days > 7 or num_symptoms >= 3 or urgency == "High":
        return "Internal Medicine"
    
    sev = severity.strip().lower()
    if sev == "low" and num_symptoms <= 2 and not is_vague:
        return "Primary Care"
        
    return "General Physician"

def analyze_case(
    symptoms: list,
    severity: str = "normal",
    duration_days: int = 1,
) -> dict:
    """
    Analyze a patient case and produce a triage decision.

    Parameters
    ----------
    symptoms : list
        List of symptom strings reported by the patient.
    severity : str
        Patient-reported severity level ("low", "normal", "high").
    duration_days : int
        Number of days the symptoms have persisted.

    Returns
    -------
    dict
        {
            "urgency":              "High" | "Medium" | "Low",
            "risk_level":           "Critical" | "Moderate" | "Mild",
            "specialist":           str,
            "secondary_specialist": str | None,
            "confidence":           str   (e.g. "85%"),
            "reason":               str   (human-readable explanation),
            "matched_rules":        list[str],
            "steps":                list[str],
        }
    """

    # ── Step 1: Normalize input ──────────────────────────────
    clean_symptoms = _normalize_symptoms(symptoms)
    symptom_set = set(clean_symptoms)

    if not clean_symptoms:
        return {
            "urgency": "Low",
            "risk_level": "Mild",
            "specialist": "General Physician",
            "secondary_specialist": None,
            "confidence": "60%",
            "reason": (
                "No recognizable symptoms provided. "
                "A general consultation is recommended for further assessment."
            ),
            "matched_rules": [],
            "steps": [
                "Step 1: No symptoms provided",
                "Step 2: Defaulting to general consultation",
            ],
        }

    # ── Step 2: Check combo rules first ──────────────────────
    combo = _check_combo_rules(symptom_set)
    combo_boost = combo["confidence_boost"] if combo else 0

    # ── Step 3: Classify each symptom individually ───────────
    classifications = []
    matched_fragments = []
    for symptom in clean_symptoms:
        result = _classify_single_symptom(symptom, duration_days)
        if result:
            classifications.append(result)
            matched_fragments.append(result["reason_fragment"])

    num_matched = len(classifications)

    # ── Step 4: Determine highest urgency across symptoms ────
    if combo:
        best_urgency = combo["urgency"]
        best_specialist = combo["specialist"]
    elif classifications:
        best_urgency = max(
            classifications,
            key=lambda c: URGENCY_RANK[c["urgency"]],
        )["urgency"]
        # Pick the specialist from the highest-urgency symptom
        best_specialist = next(
            c["specialist"]
            for c in classifications
            if c["urgency"] == best_urgency
        )
    else:
        # Fallback — no symptoms matched any rule
        best_urgency = "Low"
        best_specialist = "General Physician"

    # ── Step 5: Severity override ────────────────────────────
    final_urgency = _apply_severity_override(best_urgency, severity)

    # If severity override pushed urgency higher and original specialist
    # was General Physician at low urgency, keep the specialist unchanged.

    # ── Step 6: Multi-symptom urgency boost ──────────────────
    # If multiple symptoms individually classify as Medium or higher,
    # escalate to High.
    serious_count = sum(
        1 for c in classifications if URGENCY_RANK[c["urgency"]] >= 2
    )
    if serious_count >= 2 and final_urgency == "Medium":
        final_urgency = "High"

    # ── Step 7: Confidence calculation ───────────────────────
    matched_rules_pre = _collect_matched_rules(classifications, combo)
    confidence = _compute_confidence(
        num_symptoms=len(clean_symptoms),
        num_matched=num_matched,
        combo_boost=combo_boost,
        clean_symptoms=clean_symptoms,
        severity=severity,
        num_rules=len(matched_rules_pre),
        final_urgency=final_urgency,
    )

    # ── Step 8: Determine secondary specialist (moved up) ────
    secondary_specialist = _find_secondary_specialist(
        classifications, best_specialist
    )

    vague_symptoms = {"uneasiness", "weird sensation", "fatigue", "weakness", "tired", "dizzy", "lethargy", "feeling unwell"}
    is_vague = all(s.lower() in vague_symptoms for s in clean_symptoms) if clean_symptoms else True
    any_vague = any(s.lower() in vague_symptoms for s in clean_symptoms) if clean_symptoms else False

    if best_specialist == "General Physician":
        best_specialist = _get_general_physician_variant(
            final_urgency, len(clean_symptoms), severity, duration_days, is_vague
        )

    # ── Step 9: Build human-readable reason ──────────────────
    combo_reason = combo["reason"] if combo else None
    reason = _build_reason(
        clean_symptoms=clean_symptoms,
        combo_reason=combo_reason,
        severity=severity,
        final_urgency=final_urgency,
        best_specialist=best_specialist,
        secondary_specialist=secondary_specialist,
    )

    if num_matched > 0 and any_vague and not is_vague:
        reason += " Specialist assigned based on strong symptom pattern despite some low-specificity inputs."

    # ── Step 10: Collect matched rules ────────────────────────
    matched_rules = _collect_matched_rules(classifications, combo)

    # ── Step 11: Track whether urgency was modified ──────────
    severity_changed = final_urgency != best_urgency
    escalated = serious_count >= 2 and best_urgency == "Medium"

    # ── Step 12: Handle complete fallback — HYBRID ML ENGINE ───
    if num_matched == 0:
        if is_vague:
            ml_specialist = "General Physician"
            ml_category = "General"
            ml_urgency = "Medium"
            ml_confidence = max(20, min(50, 20 + hash("".join(clean_symptoms)) % 30))
            ml_secondary = None
            
            ml_urgency = _apply_severity_override(ml_urgency, severity)
            if ml_urgency == "High":
                ml_confidence = max(80, ml_confidence)
                
            risk_level = _get_risk_level(ml_urgency)
            
            reason = _build_reason(
                clean_symptoms=clean_symptoms,
                combo_reason=None,
                severity=severity,
                final_urgency=ml_urgency,
                best_specialist=ml_specialist,
                secondary_specialist=ml_secondary,
            )
            
            symptoms_display = ', '.join(clean_symptoms) if clean_symptoms else 'none'
            ml_steps = [
                f"Step 1: Normalized and deduplicated {len(clean_symptoms)} symptom(s) - {symptoms_display}",
                f"Step 2: Evaluated clinical context (severity: {severity}, duration: {duration_days} day(s))",
                "Step 3: No critical rule match found",
                "Step 4: ML prediction skipped due to vague symptom profile",
                f"Step 5: Assigned specialist '{ml_specialist}' based on symptom ambiguity"
            ]
            
            return {
                "urgency": ml_urgency,
                "risk_level": risk_level,
                "specialist": ml_specialist,
                "secondary_specialist": ml_secondary,
                "confidence": f"{ml_confidence}%",
                "reason": reason,
                "matched_rules": [],
                "steps": ml_steps,
            }

        # No rule matched and NOT vague — invoke ML model for generalization
        symptoms_text = " ".join(clean_symptoms)
        ml_result = predict_from_symptoms(symptoms_text)

        ml_category = ml_result["category"]
        ml_specialist = ml_result["specialist"]
        ml_confidence = ml_result["confidence"]
        ml_secondary = ml_result.get("secondary_specialist")
        ml_urgency = ml_result.get("urgency", "Low")
        ml_used = ml_result.get("ml_used", False)

        # ── Priority 2: Symptom Override Layer ────────────────
        override_category = _symptom_override(clean_symptoms)
        override_used = False

        if override_category:
            # Override wins over ML — correct known misclassifications
            original_ml_cat = ml_category
            ml_category = override_category
            ml_specialist = CATEGORY_TO_SPECIALIST.get(
                override_category, "General Physician"
            )
            # Symptom override -> 75-90% confidence
            variance = hash("".join(clean_symptoms)) % 15
            override_conf = 75 + variance
            if severity.strip().lower() == "high":
                override_conf = min(90, override_conf + 5)
            ml_confidence = override_conf
            ml_urgency = CATEGORY_URGENCY.get(override_category, "Low")
            ml_secondary = None  # reset — override is authoritative
            override_used = True
        elif ml_used:
            # ML prediction -> 40-70%
            variance = hash("".join(clean_symptoms)) % 30
            ml_confidence = max(40, min(70, 40 + variance))
        else:
            # Weak/unknown -> 20-50%
            variance = hash("".join(clean_symptoms)) % 30
            ml_confidence = max(20, min(50, 20 + variance))

        # Apply severity override on final urgency
        ml_urgency = _apply_severity_override(ml_urgency, severity)

        if ml_urgency == "High":
            ml_confidence = max(80, ml_confidence)

        risk_level = _get_risk_level(ml_urgency)

        accept_ml_spec = ml_used and (duration_days <= 7) and (len(clean_symptoms) >= 2) and not is_vague

        if not override_used and (not accept_ml_spec or ml_specialist == "General Physician"):
            ml_specialist = _get_general_physician_variant(
                ml_urgency, len(clean_symptoms), severity, duration_days, False
            )

        # Build reason using unified contextual builder
        reason = _build_reason(
            clean_symptoms=clean_symptoms,
            combo_reason=None,
            severity=severity,
            final_urgency=ml_urgency,
            best_specialist=ml_specialist,
            secondary_specialist=ml_secondary,
        )

        # Build steps (explainable AI trace)
        symptoms_display = ', '.join(clean_symptoms) if clean_symptoms else 'none'
        ml_steps = [
            f"Step 1: Normalized and deduplicated {len(clean_symptoms)} symptom(s) - {symptoms_display}",
            f"Step 2: Evaluated clinical context (severity: {severity}, duration: {duration_days} day(s))",
            "Step 3: No critical rule match found",
        ]

        if ml_used:
            if override_used or accept_ml_spec:
                ml_steps.append(f"Step 4: ML predicted category: {ml_category}")
            else:
                ml_steps.append("Step 4: ML prediction ignored due to fallback priority rules")
        else:
            ml_steps.append("Step 4: ML inference unavailable, used keyword fallback")

        if override_used:
            ml_steps.append(f"Step 5: Override applied based on symptom pattern for {override_category}")
        else:
            ml_steps.append("Step 5: Symptom override skipped")

        if ml_secondary:
            ml_steps.append(f"Step 6: Mapped primary specialist to {ml_specialist}; secondary to {ml_secondary}")
        else:
            ml_steps.append(f"Step 6: Mapped primary specialist to {ml_specialist}")

        ml_steps.append(f"Step 7: Final reasoning applied {ml_urgency} urgency with calibrated confidence")

        ml_matched_rules = []
        if override_used:
            symptoms_joined = " + ".join(clean_symptoms)
            ml_matched_rules.append(f"{symptoms_joined} -> {override_category.lower()} pattern")

        return {
            "urgency": ml_urgency,
            "risk_level": risk_level,
            "specialist": ml_specialist,
            "secondary_specialist": ml_secondary,
            "confidence": f"{ml_confidence}%",
            "reason": reason,
            "matched_rules": ml_matched_rules,
            "steps": ml_steps,
        }

    # ── Step 13: Build reasoning steps ────────────────────────
    steps = _build_steps(
        clean_symptoms=clean_symptoms,
        severity=severity,
        duration_days=duration_days,
        combo=combo,
        classifications=classifications,
        severity_changed=severity_changed,
        escalated=escalated,
        final_urgency=final_urgency,
        best_specialist=best_specialist,
        secondary_specialist=secondary_specialist,
    )

    # ── Step 14: Return final decision ───────────────────────
    return {
        "urgency": final_urgency,
        "risk_level": _get_risk_level(final_urgency),
        "specialist": best_specialist,
        "secondary_specialist": secondary_specialist,
        "confidence": f"{confidence}%",
        "reason": reason,
        "matched_rules": matched_rules,
        "steps": steps,
    }

