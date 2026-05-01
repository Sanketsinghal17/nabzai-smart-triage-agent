"""
NabzAI – Smart Appointment Triage Agent
Decision Engine (Core Logic)

A rule-based decision engine that simulates Agentic AI reasoning.
Pipeline: Input → Analyze → Decide → Explain
"""


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
    if "throat" in s:
        return "sore throat"
    if "ear" in s and "pain" in s:
        return "ear pain"

    return s


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

def _normalize_symptoms(symptoms: list) -> list:
    """Lowercase, strip, and normalize each symptom to its canonical form."""
    return [_normalize_symptom(s) for s in symptoms if isinstance(s, str)]


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
                "reason_fragment": f"recent {symptom} (under {threshold} days) that can be monitored",
                "rule_label": f"{symptom} (under {threshold} days) -> monitor",
            }
        return {
            "urgency": "Medium",
            "specialist": entry["specialist"],
            "reason_fragment": entry["reason_fragment"],
            "rule_label": entry["rule_label"],
        }

    # Check LOW urgency table
    if symptom in LOW_URGENCY_SYMPTOMS:
        entry = LOW_URGENCY_SYMPTOMS[symptom]
        return {
            "urgency": "Low",
            "specialist": entry["specialist"],
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
) -> int:
    """
    Compute a confidence percentage (clamped to 60–99).

    Rules:
      - 1 matched symptom  → base 75%
      - 2+ matched symptoms → base 88%
      - combo match adds a boost
      - unmatched symptoms slightly reduce confidence
    """
    if num_matched == 0:
        return 60

    base = 75 if num_matched == 1 else 88
    base += combo_boost

    # Penalize slightly for unmatched symptoms
    unmatched = num_symptoms - num_matched
    base -= unmatched * 3

    return max(60, min(base, 99))


def _build_reason(
    matched_fragments: list,
    combo_reason: str | None,
    severity: str,
    final_urgency: str,
) -> str:
    """
    Generate a clear, human-readable reason string that explains
    the decision in natural language.
    """
    # If a combo rule fired, lead with its reason
    if combo_reason:
        parts = [combo_reason]
    else:
        parts = []
        if matched_fragments:
            parts.append(
                "Patient presents with "
                + ", and ".join(matched_fragments)
            )

    # Mention severity override if applicable
    if severity.strip().lower() == "high" and final_urgency in ("Medium", "High"):
        parts.append(
            "Patient-reported severity is high, reinforcing the urgency of this case"
        )

    # Closing recommendation keyed on urgency
    recommendations = {
        "High": "Immediate specialist consultation is strongly recommended",
        "Medium": "Timely medical evaluation is advised to prevent escalation",
        "Low": "A routine consultation should be sufficient at this time",
    }
    parts.append(recommendations.get(final_urgency, ""))

    return ". ".join(p for p in parts if p) + "."


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
    """Return a secondary specialist if symptoms map to more than one."""
    seen = []
    for c in classifications:
        spec = c["specialist"]
        if spec not in seen:
            seen.append(spec)
    others = [s for s in seen if s != primary]
    return others[0] if others else None


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
    """Build dynamic agent reasoning steps."""
    steps = []

    # Step 1 – always
    steps.append(
        f"Step 1: Parsed {len(clean_symptoms)} symptom(s): "
        + ", ".join(clean_symptoms)
    )

    # Step 2 – severity & duration
    steps.append(
        f"Step 2: Analyzed severity='{severity}' and duration={duration_days} day(s)"
    )

    # Step 3 – rule matching
    matched_count = len(classifications)
    if combo:
        steps.append(
            f"Step 3: Matched {matched_count} individual rule(s) + 1 combo rule"
        )
    elif matched_count:
        steps.append(f"Step 3: Matched {matched_count} medical rule(s)")
    else:
        steps.append("Step 3: No specific medical rules matched — using fallback")

    # Step 4 – urgency
    urgency_detail = f"Step 4: Determined urgency level -> {final_urgency}"
    if severity_changed:
        urgency_detail += " (elevated by patient-reported severity)"
    if escalated:
        urgency_detail += " (escalated due to multiple serious symptoms)"
    steps.append(urgency_detail)

    # Step 5 – specialist
    spec_detail = f"Step 5: Mapped primary specialist -> {best_specialist}"
    if secondary_specialist:
        spec_detail += f" | secondary -> {secondary_specialist}"
    steps.append(spec_detail)

    # Step 6 – recommendation
    steps.append("Step 6: Generated recommendation and confidence score")

    return steps


# ─────────────────────────────────────────────────────────────
# Main Public API
# ─────────────────────────────────────────────────────────────

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
    confidence = _compute_confidence(
        num_symptoms=len(clean_symptoms),
        num_matched=num_matched,
        combo_boost=combo_boost,
    )

    # ── Step 8: Build human-readable reason ──────────────────
    combo_reason = combo["reason"] if combo else None
    reason = _build_reason(
        matched_fragments=matched_fragments,
        combo_reason=combo_reason,
        severity=severity,
        final_urgency=final_urgency,
    )

    # ── Step 9: Collect matched rules ─────────────────────────
    matched_rules = _collect_matched_rules(classifications, combo)

    # ── Step 10: Determine secondary specialist ──────────────
    secondary_specialist = _find_secondary_specialist(
        classifications, best_specialist
    )

    # ── Step 11: Track whether urgency was modified ──────────
    severity_changed = final_urgency != best_urgency
    escalated = serious_count >= 2 and best_urgency == "Medium"

    # ── Step 12: Handle complete fallback ─────────────────────
    if num_matched == 0:
        return {
            "urgency": "Low",
            "risk_level": "Mild",
            "specialist": "General Physician",
            "secondary_specialist": None,
            "confidence": "60%",
            "reason": (
                "Symptoms appear mild and do not match critical conditions, "
                "general consultation recommended."
            ),
            "matched_rules": [],
            "steps": [
                f"Step 1: Parsed {len(clean_symptoms)} symptom(s): "
                + ", ".join(clean_symptoms),
                f"Step 2: Analyzed severity='{severity}' and duration={duration_days} day(s)",
                "Step 3: No specific medical rules matched — using fallback",
                "Step 4: Determined urgency level -> Low",
                "Step 5: Mapped primary specialist -> General Physician",
                "Step 6: Generated recommendation and confidence score",
            ],
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

