
"""
scheduler.py  -  NabzAI Scheduling Module
==========================================
Production-ready (hackathon-speed) scheduling layer that:
  - Loads doctors from JSON with in-memory caching
  - Filters, ranks, and assigns slots with conflict-safe logic
  - Is directly importable into FastAPI (JSON-serialisable output)
  - Is designed for easy migration to a real DB (MongoDB / PostgreSQL)

Public API
----------
get_available_doctor(specialist, location=None, top_n=3) -> dict
    Primary entry point called by the decision engine / FastAPI route.

schedule_appointment(specialist, location=None) -> dict
    Backward-compatible alias kept for main.py.

Helper functions (all independently testable)
---------------------------------------------
load_doctors()          - I/O + cache
filter_doctors()        - eligibility gate
rank_doctors()          - priority scoring
assign_slot()           - slot pop + conflict guard
"""

from __future__ import annotations

import copy
import json
import logging
import random
import threading
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  |  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("nabzai.scheduler")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOCTORS_FILE: Path = Path(__file__).parent / "data" / "doctors.json"
FALLBACK_SPECIALIST: str = "General Physician"

# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------
# A single lock guards both the cache and slot-mutation operations so that
# concurrent FastAPI requests cannot double-book the same slot.

_lock = threading.Lock()

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------
# Structure: { doctor_id -> doctor_dict (mutable copy) }
# Using a dict keyed by ID makes O(1) look-ups and avoids list scans when
# a database replaces this layer in the future.

_cache: dict[int, dict] | None = None  # None means "not loaded yet"


# ---------------------------------------------------------------------------
# 1. Data Layer
# ---------------------------------------------------------------------------

def load_doctors(filepath: Path = DOCTORS_FILE, force_reload: bool = False) -> dict[int, dict]:
    """
    Load doctors from JSON into an in-memory cache (dict keyed by doctor ID).

    The cache persists for the lifetime of the process.  Pass
    ``force_reload=True`` to invalidate it (useful in tests or after a
    hot-reload of the JSON file).

    Returns
    -------
    dict[int, dict]
        Mapping of doctor_id -> doctor record.  Empty dict on any error.

    Design note
    -----------
    Swapping to a database later is a one-line change: replace the
    ``json.load`` block with a DB query and keep the same return type.
    """
    global _cache

    with _lock:
        if _cache is not None and not force_reload:
            return _cache

        try:
            with open(filepath, "r", encoding="utf-8") as fh:
                raw: list[dict] = json.load(fh)

            if not isinstance(raw, list):
                logger.error("doctors.json must contain a JSON array.")
                _cache = {}
                return _cache

            # Deep-copy so slot mutations don't corrupt the on-disk representation
            # and so each worker thread gets its own view.
            _cache = {
                int(d["id"]): copy.deepcopy(d)
                for d in raw
                if "id" in d
            }
            logger.info("Cache loaded: %d doctor records from %s", len(_cache), filepath)
            return _cache

        except FileNotFoundError:
            logger.error("doctors.json not found at %s", filepath)
            _cache = {}
            return _cache
        except (json.JSONDecodeError, KeyError, ValueError) as exc:
            logger.error("Failed to parse doctors.json: %s", exc)
            _cache = {}
            return _cache


# ---------------------------------------------------------------------------
# 2. Filter Layer
# ---------------------------------------------------------------------------

def filter_doctors(
    doctors: dict[int, dict],
    specialist: str,
    location: Optional[str] = None,
) -> list[dict]:
    """
    Return eligible doctors matching the given specialist and (optionally)
    location.

    Eligibility rules
    -----------------
    1. ``specialist`` matches (case-insensitive)
    2. ``available`` flag is True  (or absent — defaults to True)
    3. ``slots`` list is non-empty

    If ``location`` is supplied, a location-matching sub-filter is tried first.
    If that yields no results, the location constraint is relaxed so the caller
    always gets the broadest possible match.

    Parameters
    ----------
    doctors : dict[int, dict]
        The full in-memory cache.
    specialist : str
        Specialty string from the decision engine.
    location : str | None
        Optional city / area preference.

    Returns
    -------
    list[dict]
        Mutable copies of eligible doctor records.
    """
    spec_lower = specialist.strip().lower()

    def is_eligible(d: dict) -> bool:
        return (
            d.get("specialist", "").strip().lower() == spec_lower
            and d.get("available", True)  # default True if key missing
            and bool(d.get("slots"))
        )

    eligible = [copy.deepcopy(d) for d in doctors.values() if is_eligible(d)]

    if not eligible:
        return []

    # Soft location filter
    if location:
        loc_lower = location.strip().lower()
        loc_eligible = [d for d in eligible if d.get("location", "").strip().lower() == loc_lower]
        if loc_eligible:
            logger.debug("Location filter '%s' matched %d doctor(s).", location, len(loc_eligible))
            return loc_eligible
        logger.info(
            "No available '%s' doctor in '%s'. Relaxing location constraint.",
            specialist, location,
        )

    return eligible


# ---------------------------------------------------------------------------
# 3. Ranking Layer
# ---------------------------------------------------------------------------

def rank_doctors(doctors: list[dict]) -> list[dict]:
    """
    Sort doctors by a composite priority score (descending).

    Scoring formula
    ---------------
        priority = (rating * 0.6) + (experience * 0.4)

    This weighs patient satisfaction (rating) slightly above years of
    practice (experience), making the top result both trusted and skilled.

    Returns
    -------
    list[dict]
        Same list, sorted in-place and returned for chaining.
    """
    def priority(d: dict) -> float:
        rating = float(d.get("rating", 0))
        experience = float(d.get("experience", 0))
        return (rating * 0.6) + (experience * 0.4)

    doctors.sort(key=priority, reverse=True)
    logger.debug(
        "Ranked %d doctor(s). Top: %s (score=%.2f)",
        len(doctors),
        doctors[0].get("name") if doctors else "N/A",
        priority(doctors[0]) if doctors else 0,
    )
    return doctors


# ---------------------------------------------------------------------------
# 4. Slot Allocation Layer
# ---------------------------------------------------------------------------

def assign_slot(
    doctor: dict,
    randomize: bool = False,
) -> Optional[str]:
    """
    Pop and return a slot from the doctor's slot list.

    The slot is removed from the live cache entry to prevent double-booking.
    If ``randomize`` is True, a random slot is chosen instead of the earliest.

    Parameters
    ----------
    doctor : dict
        A single doctor record (must have an ``id`` key).
    randomize : bool
        When True, picks a random slot (bonus feature).

    Returns
    -------
    str | None
        The assigned time string, or None if no slots remain.
    """
    global _cache

    slots: list[str] = doctor.get("slots", [])
    if not slots:
        return None

    # Determine which slot to assign
    chosen: str = random.choice(slots) if randomize else sorted(slots)[0]

    # Remove it from the LIVE cache under the lock to avoid race conditions.
    with _lock:
        if _cache is not None and doctor.get("id") in _cache:
            live_slots: list = _cache[doctor["id"]].get("slots", [])
            if chosen in live_slots:
                live_slots.remove(chosen)
                # If no slots remain, mark as unavailable
                if not live_slots:
                    _cache[doctor["id"]]["available"] = False
                    logger.info(
                        "%s is now fully booked — marked unavailable.",
                        doctor.get("name"),
                    )
            else:
                # Race condition: another request grabbed the same slot
                logger.warning(
                    "Slot %s for %s already taken. Attempting next slot.",
                    chosen, doctor.get("name"),
                )
                remaining = _cache[doctor["id"]].get("slots", [])
                if not remaining:
                    return None
                chosen = random.choice(remaining) if randomize else sorted(remaining)[0]
                remaining.remove(chosen)

    logger.debug("Assigned slot %s to %s", chosen, doctor.get("name"))
    return chosen


# ---------------------------------------------------------------------------
# 5. Core Public Function
# ---------------------------------------------------------------------------

def get_available_doctor(
    specialist: str,
    location: Optional[str] = None,
    top_n: int = 3,
    randomize: bool = False,
) -> dict:
    """
    Find and return the best available doctor for the requested specialist.

    Execution pipeline
    ------------------
    load  ->  filter  ->  rank  ->  (optional) randomize top-N  ->  assign slot

    Parameters
    ----------
    specialist : str
        Specialty from the decision engine (e.g. "Cardiologist").
    location : str | None
        Optional preferred city.  Falls back gracefully if not found.
    top_n : int
        Pool size for optional randomized selection among top doctors.
        Ignored when ``randomize=False``.
    randomize : bool
        If True, picks randomly among the top-``top_n`` ranked doctors and
        assigns a random slot (instead of earliest).

    Returns
    -------
    dict
        Success:  {"doctor": str, "slot": str, "hospital": str,
                   "location": str, "specialist": str, "rating": float}
        Failure:  {"doctor": None, "slot": None, "error": str}
    """
    # -- Load (from cache after first call) --
    doctors = load_doctors()

    if not doctors:
        return {"doctor": None, "slot": None, "error": "Doctor database unavailable."}

    # -- Filter --
    candidates = filter_doctors(doctors, specialist, location)

    # Final location prioritization (prefer same-city doctors when possible)
    if location:
        same_city = [
            d for d in candidates
            if d.get("location", "").strip().lower() == location.strip().lower()
        ]
        if same_city:
            candidates = same_city

    # -- Fallback to General Physician --
    if not candidates and specialist.strip().lower() != FALLBACK_SPECIALIST.strip().lower():
        logger.warning(
            "No available '%s' found. Falling back to '%s'.",
            specialist, FALLBACK_SPECIALIST,
        )
        candidates = filter_doctors(doctors, FALLBACK_SPECIALIST, location)
        if candidates:
            specialist = FALLBACK_SPECIALIST  # update for response

    if not candidates:
        logger.error("No available doctors found for '%s' (or fallback).", specialist)
        return {
            "doctor": None,
            "slot": None,
            "error": f"No '{specialist}' available. Try '{FALLBACK_SPECIALIST}'.",
        }

    # -- Rank --
    ranked = rank_doctors(candidates)

    # -- Optional: randomize among top N --
    pool = ranked[:top_n] if randomize else ranked

    # -- Attempt slot assignment, skipping fully-booked doctors --
    chosen_doctor: Optional[dict] = None
    chosen_slot: Optional[str] = None

    for candidate in pool:
        slot = assign_slot(candidate, randomize=randomize)
        if slot:
            chosen_doctor = candidate
            chosen_slot = slot
            break
        logger.debug("%s had no assignable slot. Trying next.", candidate.get("name"))

    if not chosen_doctor or not chosen_slot:
        logger.error("All '%s' doctors are fully booked.", specialist)
        return {
            "doctor": None,
            "slot": None,
            "error": f"All '{specialist}' doctors are currently fully booked.",
        }

    rating     = float(chosen_doctor.get("rating", 0))
    experience = float(chosen_doctor.get("experience", 0))
    score      = (rating * 0.6) + (experience * 0.4)

    result = {
        "doctor":          chosen_doctor.get("name"),
        "slot":            chosen_slot,
        "hospital":        chosen_doctor.get("hospital"),
        "location":        chosen_doctor.get("location"),
        "specialist":      chosen_doctor.get("specialist"),
        "rating":          rating,
        "experience":      experience,
        "selection_score": round(score, 2),
        "reason":          f"Selected due to high rating ({rating}) and {int(experience)} yrs experience",
    }
    logger.info("Appointment booked -> %s", result)
    return result


# ---------------------------------------------------------------------------
# 6. Backward-compatible alias (keeps main.py unchanged)
# ---------------------------------------------------------------------------

def schedule_appointment(
    specialist: str,
    location: Optional[str] = None,
) -> dict:
    """
    Legacy alias.  Delegates to get_available_doctor.
    Kept so existing callers in main.py / planner.py are unaffected.
    """
    return get_available_doctor(specialist, location=location)


# ---------------------------------------------------------------------------
# 7. Smoke-test  (python scheduler.py)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cases = [
        # (specialist,          location,  randomize)
        ("Cardiologist",        "Delhi",   False),
        ("Cardiologist",        "Delhi",   False),  # round-trips: slot removed
        ("Dermatologist",       None,      True),   # randomised
        ("Neurologist",         "Gurgaon", False),
        ("Pediatrician",        None,      False),
        ("ENT",                 "Delhi",   False),
        ("UnknownSpecialist",   None,      False),  # -> fallback GP
        ("UnknownSpecialist",   None,      False),  # -> fallback GP (next slot)
    ]

    print("\n" + "=" * 60)
    print("  NabzAI Scheduler - Smoke Test")
    print("=" * 60)

    for spec, loc, rnd in cases:
        result = get_available_doctor(spec, location=loc, randomize=rnd)
        tag = f"{spec}" + (f" @ {loc}" if loc else "") + (" [random]" if rnd else "")
        print(f"\n  [{tag}]")
        for k, v in result.items():
            print(f"    {k:12}: {v}")

    print("\n" + "=" * 60)

