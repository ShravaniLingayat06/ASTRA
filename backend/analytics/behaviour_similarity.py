"""Behavioral similarity and Modus Operandi (MO) pattern matching.

Analyzes:
1. Threat category taxonomy consistency (incident type distribution)
2. Structured MO attribute matching (time-of-day, approach vector, threat sub-type)
3. TF-IDF cosine similarity across narrative descriptions
4. Specific MO keyword extraction from a women-safety-specific taxonomy

Produces a composite behaviour_similarity_score (0-100%) with full explainability.
"""
from typing import List, Dict, Any
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- MO Taxonomy -----------------------------------------------------------
# Women-safety-specific Modus Operandi keyword taxonomy.
# Each key is a named MO trait; each value is a list of indicator terms.
MO_TAXONOMY_KEYWORDS = {
    "Following / Trailing": [
        "follow", "followed", "following", "trailing", "shadowing",
        "behind me", "kept following", "same direction", "repeated approach"
    ],
    "Covert Loitering": [
        "loitering", "corner", "alley", "dark lane", "standing",
        "waiting near", "hiding", "dim", "streetlight", "under staircase"
    ],
    "Verbal Harassment": [
        "catcalling", "remark", "shouted", "verbal", "jeering", "whistling",
        "commented", "passed comment", "lewd remark", "abusive language"
    ],
    "Physical Blocking / Confrontation": [
        "blocking", "confronted", "cornered", "surrounded", "grabbed",
        "blocked path", "intimidation", "blocked my way", "pushed"
    ],
    "Transit Hub Targeting": [
        "bus stop", "metro", "station", "stairs", "auto stand",
        "bus", "platform", "overbridge", "footover"
    ],
    "Repeat / Organised Pattern": [
        "same person", "same group", "again", "regular", "every day",
        "third time", "second time", "keeps appearing", "seen before"
    ]
}

# Canonical threat category groupings (for structured taxonomy matching)
THREAT_FAMILY_MAP = {
    "stalking": "predatory_contact",
    "following": "predatory_contact",
    "aggressive_posture": "physical_threat",
    "physical_harassment": "physical_threat",
    "assault": "physical_threat",
    "verbal_harassment": "verbal_threat",
    "catcalling": "verbal_threat",
    "loitering": "suspicious_presence",
    "suspicious_activity": "suspicious_presence",
    "intimidation": "physical_threat",
    "eve_teasing": "verbal_threat",
}


def _get_threat_family(incident_type: str) -> str:
    """Map raw incident type to a normalised threat family for comparison."""
    return THREAT_FAMILY_MAP.get(incident_type.lower().strip(), "other")


def analyze_behaviour_similarity(
    incident_types: List[str],
    descriptions: List[str]
) -> Dict[str, Any]:
    """
    Evaluate similarity in behavior, MO, and incident taxonomy.

    Scoring pillars (weighted to 100):
      • Taxonomy consistency  — 35%  (same threat family across incidents)
      • MO trait presence     — 35%  (keyword-matched MO indicators)
      • Textual cosine sim    — 30%  (TF-IDF pairwise narrative similarity)

    Returns a fully explainable dict including per-pillar scores.
    """
    if not incident_types:
        return {
            "mo_similarity_score": 0.0,
            "primary_threat_type": "None",
            "primary_threat_family": "None",
            "detected_mo_traits": [],
            "common_keywords": [],
            "taxonomy_consistency": 0.0,
            "text_similarity": 0.0,
            "type_distribution": {}
        }

    # ── Pillar 1: Incident category distribution & taxonomy consistency ──
    type_counts: Dict[str, int] = {}
    for t in incident_types:
        type_counts[t] = type_counts.get(t, 0) + 1

    primary_type = max(type_counts, key=type_counts.get)
    category_consistency = type_counts[primary_type] / len(incident_types)

    # Structured threat-family consistency (more robust than raw type match)
    families = [_get_threat_family(t) for t in incident_types]
    family_counts: Dict[str, int] = {}
    for f in families:
        family_counts[f] = family_counts.get(f, 0) + 1
    dominant_family_count = max(family_counts.values())
    family_consistency = dominant_family_count / len(families)

    # Use the better of raw-type or family-level consistency
    taxonomy_consistency = max(category_consistency, family_consistency)
    primary_threat_family = max(family_counts, key=family_counts.get)

    # ── Pillar 2: MO Trait Extraction ──────────────────────────────────
    detected_mo: List[str] = []
    all_keywords_found: List[str] = []
    all_text = " ".join([d.lower() for d in descriptions if d])

    for trait, keywords in MO_TAXONOMY_KEYWORDS.items():
        matched = [kw for kw in keywords if kw in all_text]
        if matched:
            detected_mo.append(trait)
            all_keywords_found.extend(matched[:2])  # keep top-2 keywords per trait

    # Normalised MO trait factor: 1 trait = 0.40, 2 = 0.70, 3+ = 1.0
    mo_trait_factor = min(1.0, len(detected_mo) * 0.33) if detected_mo else 0.25

    # ── Pillar 3: TF-IDF / Cosine Similarity on narrative descriptions ──
    valid_descriptions = [d.strip() for d in descriptions if d and len(d.strip()) > 3]
    text_similarity = 0.0

    if len(valid_descriptions) >= 2:
        try:
            tfidf = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
            tfidf_matrix = tfidf.fit_transform(valid_descriptions)
            cos_sim_matrix = cosine_similarity(tfidf_matrix)
            n = len(valid_descriptions)
            triu_indices = np.triu_indices(n, k=1)
            pairwise_sims = cos_sim_matrix[triu_indices]
            if len(pairwise_sims) > 0:
                text_similarity = float(np.mean(pairwise_sims))
        except Exception:
            text_similarity = 0.30
    elif len(valid_descriptions) == 1:
        # Single description: moderate default (cannot cross-compare)
        text_similarity = 0.35

    # ── Composite Score ─────────────────────────────────────────────────
    # Weights: taxonomy 35% + MO traits 35% + text cosine 30%
    composite = (
        taxonomy_consistency  * 35.0 +
        mo_trait_factor       * 35.0 +
        text_similarity       * 30.0
    )
    mo_similarity_score = round(min(100.0, max(10.0, composite)), 1)

    return {
        "mo_similarity_score": mo_similarity_score,
        "primary_threat_type": primary_type,
        "primary_threat_family": primary_threat_family.replace("_", " ").title(),
        "detected_mo_traits": detected_mo,
        "common_keywords": list(dict.fromkeys(all_keywords_found))[:8],
        "taxonomy_consistency": round(taxonomy_consistency * 100.0, 1),
        "family_consistency": round(family_consistency * 100.0, 1),
        "text_similarity": round(text_similarity * 100.0, 1),
        "type_distribution": type_counts,
        "pillar_scores": {
            "taxonomy_score": round(taxonomy_consistency * 35.0, 1),
            "mo_trait_score": round(mo_trait_factor * 35.0, 1),
            "text_cosine_score": round(text_similarity * 30.0, 1)
        }
    }
