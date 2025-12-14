#!/usr/bin/env python3
import streamlit as st
import pandas as pd
import base64
import json
import os
from collections import Counter

st.set_page_config(page_title="FM26 Squad Helper", layout="wide")

STATE_FILE = "fm26_state.json"

# =========================
# FIXED INDONESIA STRUCTURE
# =========================

SUPER_LEAGUE_TEAMS = [
    "Arema",
    "Bali United",
    "Barito Putera",
    "Borneo Samarinda",
    "Dewa United",
    "Madura United",
    "Malut United",
    "Persebaya",
    "Persib",
    "Persija",
    "Persik",
    "Persis",
    "PSBS",
    "PSM",
    "PSIS",
    "PSS",
    "Semen Padang",
    "Persita",
]

CHAMPIONSHIP_TEAMS = [
    "Adhyaksa",
    "Bekasi City",
    "Bhayangkara Presisi",
    "Dejan",
    "Deltras",
    "Gresik United",
    "Nusantara United",
    "Persekat",
    "Persela",
    "Persewar",
    "Persibo",
    "Persijap",
    "Persikabo 1973",
    "Persikas",
    "Persikota",
    "Persiku",
    "Persipa",
    "Persipal",
    "Persipura",
    "Persiraja",
    "PSIM",
    "PSKC",
    "PSMS",
    "PSPS",
    "Sriwijaya",
    "RANS Nusantara",
]

LIGA_NUSANTARA_TEAMS = [
    "Persipa",
    "Nusantara United",
    "Persikabo 1973",
    "Batavia FC",
    "Dejan FC",
    "PSDS Deli Serdang",
    "Pekanbaru FC",
    "PSGC Ciamis",
    "Persikota Tangerang",
    "Perserang Serang",
    "Tri Brata Rafflesia FC",
    "Persitara Jakarta Utara",
    "Persibo Bojonegoro",
    "Persika Karanganyar",
    "Persewar Waropen",
    "Persikutim United",
    "Rans Nusantara FC",
    "Sang Maestro FC",
    "Persiba Bantul",
    "Perseden Denpasar",
    "Gresik United",
    "Persebata Lembata",
    "Waanal Brothers",
    "Persekabpas Pasuruan",
]

FM_STRUCTURE = {
    "Indonesia": {
        "Super League": SUPER_LEAGUE_TEAMS,
        "Championship": CHAMPIONSHIP_TEAMS,
        "Liga Nusantara": LIGA_NUSANTARA_TEAMS,
    }
}

CUSTOM_TEAM_LABEL = "Custom club name"

# =========================
# ONLINE IMAGES FOR FLAG & LEAGUES
# =========================

FLAG_URLS = {
    "Indonesia": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/800px-Flag_of_Indonesia.svg.png",
}

LEAGUE_LOGO_URLS = {
    ("Indonesia", "Super League"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/BRI_Super_League_Indonesia.png/960px-BRI_Super_League_Indonesia.png",
    ("Indonesia", "Championship"): "https://upload.wikimedia.org/wikipedia/id/thumb/9/99/Logo_Terbaru_Liga_2_Indonesia.png/600px-Logo_Terbaru_Liga_2_Indonesia.png",
    ("Indonesia", "Liga Nusantara"): "https://upload.wikimedia.org/wikipedia/id/thumb/9/9a/PNM_Liga_Nusantara_Logo.png/500px-PNM_Liga_Nusantara_Logo.png",
}


def get_flag_url(country: str) -> str:
    return FLAG_URLS.get(country or "", "")


def get_league_logo_url(country: str, league: str) -> str:
    return LEAGUE_LOGO_URLS.get((country or "", league or ""), "")


def bytes_to_data_uri(png_bytes: bytes | None) -> str:
    if not png_bytes:
        return ""
    b64 = base64.b64encode(png_bytes).decode("utf-8")
    return f"data:image/png;base64,{b64}"


# =========================
# POSITIONS, FAMILIES & ROLES
# =========================

POSITION_CHOICES = [
    "GK",
    "LB", "LWB", "CB", "RB", "RWB",
    "CDM", "CM",
    "LM", "LW", "RM", "RW",
    "CAM", "ST",
]

PITCH_ORDER = [
    "GK",
    "LB", "LWB",
    "CB",
    "RB", "RWB",
    "CDM",
    "CM",
    "LM", "LW",
    "RM", "RW",
    "CAM",
    "ST",
]


def position_sort_key(pos: str) -> int:
    pos_u = (pos or "").upper()
    return PITCH_ORDER.index(pos_u) if pos_u in PITCH_ORDER else 999

POSITION_FAMILIES = {
    "GK": ["GK"],
    "CB": ["CB"],
    "FULLBACK": ["LB", "RB"],
    "WINGBACK": ["LWB", "RWB"],
    "DM": ["CDM"],
    "CM": ["CM"],
    "WIDE_MID": ["LM", "RM"],
    "WIDE_AM": ["LW", "RW"],
    "AMC": ["CAM"],
    "ST": ["ST"],
}


def family_for_position(pos: str) -> str:
    pos = (pos or "").upper()
    for fam, members in POSITION_FAMILIES.items():
        if pos in members:
            return fam
    return ""


IN_POSSESSION_ROLES = {
    "GK": [
        "Goalkeeper",
        "Ball-Playing Goalkeeper",
        "No-Nonsense Goalkeeper",
    ],
    "CB": [
        "Centre-Back",
        "Ball-Playing Centre-Back",
        "No-Nonsense Centre-Back",
        "Wide Centre-Back",
        "Advanced Centre-Back",
    ],
    "FULLBACK": [
        "Full-Back",
        "Inverted Full-Back",
        "Wing-Back",
        "Inverted Wing-Back",
        "Playmaking Wing-Back",
    ],
    "WINGBACK": [
        "Wing-Back",
        "Playmaking Wing-Back",
        "Advanced Wing-Back",
        "Inside Wing-Back",
        "Holding Wing-Back",
    ],
    "DM": [
        "Defensive Midfielder",
        "Deep-Lying Playmaker",
        "Half Back",
        "Box-to-Box Midfielder",
        "Midfield Playmaker",
    ],
    "CM": [
        "Central Midfielder",
        "Attacking Midfielder",
        "Advanced Playmaker",
        "Channel Midfielder",
        "Box-to-Box Midfielder",
    ],
    "WIDE_MID": [
        "Wide Midfielder",
        "Winger",
        "Playmaking Winger",
        "Inside Winger",
        "Wide Playmaker",
    ],
    "WIDE_AM": [
        "Winger",
        "Inside Forward",
        "Wide Forward",
        "Playmaking Winger",
        "Wide Playmaker",
    ],
    "AMC": [
        "Attacking Midfielder",
        "Advanced Playmaker",
        "Free Role",
        "Second Striker",
        "Channel Midfielder",
    ],
    "ST": [
        "Centre Forward",
        "Deep-Lying Forward",
        "Target Forward",
        "Poacher",
        "False Nine",
    ],
}

OUT_OF_POSSESSION_ROLES = {
    "GK": [
        "Goalkeeper",
        "Sweeper Keeper",
        "Line-Holding Keeper",
    ],
    "CB": [
        "Centre-Back",
        "Stopping Centre-Back",
        "Covering Centre-Back",
        "Stopping Wide Centre-Back",
        "Covering Wide Centre-Back",
    ],
    "FULLBACK": [
        "Full-Back",
        "Holding Full-Back",
        "Pressing Full-Back",
        "Holding Wing-Back",
        "Pressing Wing-Back",
    ],
    "WINGBACK": [
        "Wing-Back",
        "Holding Wing-Back",
        "Pressing Wing-Back",
    ],
    "DM": [
        "Defensive Midfielder",
        "Dropping Defensive Midfielder",
        "Screening Defensive Midfielder",
        "Pressing Defensive Midfielder",
        "Wide Covering Defensive Midfielder",
    ],
    "CM": [
        "Central Midfielder",
        "Pressing Central Midfielder",
        "Screening Central Midfielder",
        "Wide Covering Central Midfielder",
    ],
    "WIDE_MID": [
        "Wide Midfielder",
        "Tracking Wide Midfielder",
        "Wide Outlet Wide Midfielder",
    ],
    "WIDE_AM": [
        "Winger",
        "Tracking Winger",
        "Inside Outlet Winger",
        "Wide Outlet Winger",
    ],
    "AMC": [
        "Attacking Midfielder",
        "Tracking Attacking Midfielder",
        "Central Outlet Attacking Midfielder",
    ],
    "ST": [
        "Centre Forward",
        "Tracking Centre Forward",
        "Central Outlet Centre Forward",
        "Splitting Outlet Centre Forward",
    ],
}

# =========================
# STAR & RATING HELPERS
# =========================

STAR_VALUES = [i / 2 for i in range(0, 11)]          # for position ratings (0.0–5.0)
CP_STAR_VALUES = [i / 2 for i in range(1, 11)]        # for Current/Potential only (0.5–5.0)
RATING_BANDS = ["Leading", "Good", "Decent", "Standard"]
POTENTIAL_EXTRA = ["Unlikely to improve", "Could improve a lot", "Could improve slightly", "Could improve significantly"]
RATING_LEAGUES = ["Super League", "Championship", "Liga Nusantara"]

# Sorting helpers for potential
POTENTIAL_BAND_SORT = {band: idx for idx, band in enumerate(RATING_BANDS)}
POTENTIAL_LEAGUE_SORT = {lg: idx for idx, lg in enumerate(RATING_LEAGUES)}

def potential_tiebreak_tuple(player: dict) -> tuple[float, int]:
    """
    Tiebreaker for players when ratings are equal:
      1) potential_stars (higher first)
      2) age (younger first)
    """
    try:
        pot = float(player.get("potential_stars", 0.0) or 0.0)
    except Exception:
        pot = 0.0

    try:
        age = int(player.get("age", 0) or 0)
    except Exception:
        age = 0

    return (-pot, age)


def stars_to_label(value: float) -> str:
    full = int(value)
    half = 1 if value - full >= 0.5 else 0
    full_part = "⭐" * full
    half_part = "½" if half else ""
    return full_part + half_part


def rating_text(band: str, league_level: str | None) -> str:
    if not band:
        return ""
    if band in POTENTIAL_EXTRA:
        if league_level:
            return f"{band} ({league_level})"
        return band
    lg = league_level if league_level else "this level"
    return f"{band} {lg}"


def single_pos_rating(player: dict, pos: str) -> float:
    """
    Strict rating for a specific position (in possession).
    If the player doesn't have a rating for `pos`, return 0.0.
    """
    pos_ratings = player.get("position_ratings") or {}
    if pos in pos_ratings:
        return float(pos_ratings[pos])
    return 0.0


def single_pos_rating_oop(player: dict, pos: str) -> float:
    """Out-of-possession rating for a given position (falls back to IP if missing)."""
    pos_ratings_oop = player.get("position_ratings_oop") or {}
    if pos in pos_ratings_oop:
        return float(pos_ratings_oop[pos])
    return single_pos_rating(player, pos)


def combined_rating_for_position(player: dict, base_pos: str) -> float:
    """
    Rating used in the position overview table.
    We keep this as the *in-possession* rating so the stars stay on a 0–5 scale.
    """
    return single_pos_rating(player, base_pos)


def combined_ip_oop_for_pos(player: dict, pos: str) -> float:
    """
    Combined IP+OOP rating for a single position, using your rules:

    - If player has both IP and OOP rating for this position:
        score = (IP + OOP) / 2
    - If player only has one side (IP or OOP):
        treat the missing side as 0.5⭐
        score = (present + 0.5) / 2
    - If both are 0:
        score = 0
    """
    pos = (pos or "").upper()
    if not pos:
        return 0.0

    ip = single_pos_rating(player, pos)
    oop = single_pos_rating_oop(player, pos)

    # No rating at all
    if ip <= 0 and oop <= 0:
        return 0.0

    # Has both → straight average
    if ip > 0 and oop > 0:
        return (ip + oop) / 2.0

    # Only one side is playable → missing side = 0.5⭐
    present = ip if ip > 0 else oop
    return (present + 0.5) / 2.0


def best_position_rating(player: dict) -> float:
    pos_ratings = player.get("position_ratings") or {}
    if not pos_ratings:
        return 0.0
    return float(max(pos_ratings.values()))

def single_pos_rating_oop(player: dict, pos: str) -> float:
    """Out-of-possession rating for a given position (falls back to IP if missing)."""
    pos_ratings_oop = player.get("position_ratings_oop") or {}
    if pos in pos_ratings_oop:
        return float(pos_ratings_oop[pos])
    return single_pos_rating(player, pos)


def best_ip_rating(player: dict) -> float:
    """Best in-possession rating."""
    return best_position_rating(player)


def best_oop_rating(player: dict) -> float:
    """Best out-of-possession rating (falls back to IP if OOP not set)."""
    pos_ratings_oop = player.get("position_ratings_oop") or {}
    if pos_ratings_oop:
        return float(max(pos_ratings_oop.values()))
    return best_position_rating(player)


def best_ip_position(player: dict):
    """Best IP position (tie-broken by pitch order)."""
    pos_ratings = player.get("position_ratings") or {}
    if not pos_ratings:
        return None
    best_val = max(pos_ratings.values())
    best_positions = [pos for pos, val in pos_ratings.items() if val == best_val]
    best_positions.sort(key=position_sort_key)
    return best_positions[0] if best_positions else None


def best_oop_position(player: dict):
    """Best OOP position (tie-broken by pitch order, falls back to IP)."""
    pos_ratings_oop = player.get("position_ratings_oop") or {}
    if not pos_ratings_oop:
        return best_ip_position(player)
    best_val = max(pos_ratings_oop.values())
    best_positions = [pos for pos, val in pos_ratings_oop.items() if val == best_val]
    best_positions.sort(key=position_sort_key)
    return best_positions[0] if best_positions else None

def best_cover_pos_for_formation(player: dict, formation_mode: str | None = None) -> str | None:
    """
    Return the best cover position for this player given the active formation.

    - Allowed positions are derived from the formation's IP slots (unique).
    - Uses combined IP + OOP for scoring.
    """
    if formation_mode is None:
        formation_mode = st.session_state.get("formation_mode")

    formations = st.session_state.get("formations", {}) or {}
    fdef = formations.get(formation_mode or "", {}) or {}

    allowed_raw = fdef.get("ip") or []
    allowed = []
    for p in allowed_raw:
        pu = (p or "").upper()
        if pu in POSITION_CHOICES and pu not in allowed:
            allowed.append(pu)

    # If formation missing/invalid, fall back to anywhere they can actually play
    if not allowed:
        pos_r_ip = player.get("position_ratings") or {}
        pos_r_oop = player.get("position_ratings_oop") or {}
        allowed = [
            p for p in POSITION_CHOICES
            if pos_r_ip.get(p, 0) > 0 or pos_r_oop.get(p, 0) > 0
        ]
        if not allowed:
            allowed = POSITION_CHOICES

    best_pos = None
    best_score = 0.0
    for pos in allowed:
        score = combined_ip_oop_for_pos(player, pos)
        if score > best_score + 1e-6:
            best_score = score
            best_pos = pos

    return best_pos if best_score > 0 else None

def compute_primary_position(player: dict) -> str | None:
    """Return the player's primary position based on the highest rating."""
    pos_ratings = player.get("position_ratings") or {}
    if not pos_ratings:
        return None

    # highest rating
    best_val = max(pos_ratings.values())
    best_positions = [pos for pos, val in pos_ratings.items() if val == best_val]

    # tie-break with pitch order
    best_positions.sort(key=position_sort_key)
    return best_positions[0] if best_positions else None

def current_rating_display_overall(player: dict) -> str:
    try:
        stars = float(player.get("current_stars", 0.0) or 0.0)
    except Exception:
        stars = 0.0
    return stars_to_label(stars)

def current_rating_for_position_display(player: dict, pos: str) -> str:
    stars = combined_rating_for_position(player, pos)
    star_str = stars_to_label(stars)
    band = player.get("current_band", "")
    lvl = player.get("current_level_league", "")
    text = rating_text(band, lvl)
    return f"{star_str} | {text}" if text else star_str

def potential_rating_display(player: dict) -> str:
    try:
        stars = float(player.get("potential_stars", 0.0) or 0.0)
    except Exception:
        stars = 0.0
    return stars_to_label(stars)

# =========================
# STATE LOAD / SAVE
# =========================

def load_state_from_disk():
    if not os.path.exists(STATE_FILE):
        return
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return

    for key in ["positions", "players", "known_nationalities", "formations", "formation_mode"]:
        if key in data:
            st.session_state[key] = data[key]

    for key in ["country_select", "league_select", "team_select", "team_custom_name"]:
        if key in data:
            st.session_state[key] = data[key]

    logo_b64 = data.get("club_logo_b64", "")
    if logo_b64:
        try:
            st.session_state.club_logo_bytes = base64.b64decode(logo_b64)
        except Exception:
            st.session_state.club_logo_bytes = None


def save_state_to_disk():
    try:
        logo_b64 = ""
        if st.session_state.get("club_logo_bytes"):
            logo_b64 = base64.b64encode(st.session_state["club_logo_bytes"]).decode(
                "utf-8"
            )

        data = {
            "positions": st.session_state.get("positions", []),
            "players": st.session_state.get("players", []),
            "known_nationalities": st.session_state.get("known_nationalities", []),
            "country_select": st.session_state.get("country_select", ""),
            "league_select": st.session_state.get("league_select", ""),
            "team_select": st.session_state.get("team_select", ""),
            "team_custom_name": st.session_state.get("team_custom_name", ""),
            "club_logo_b64": logo_b64,
            "formations": st.session_state.get("formations", {}),
            "formation_mode": st.session_state.get("formation_mode", "4-2-3-1"),
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# =========================
# SESSION STATE DEFAULTS
# =========================

if "positions" not in st.session_state:
    st.session_state.positions = []

if "players" not in st.session_state:
    st.session_state.players = []

if "known_nationalities" not in st.session_state:
    st.session_state.known_nationalities = ["Indonesia"]

if "club_logo_bytes" not in st.session_state:
    st.session_state.club_logo_bytes = None

if "rules_tracker" not in st.session_state:
    st.session_state.rules_tracker = {}

if "reset_player_form" not in st.session_state:
    st.session_state.reset_player_form = False

if "reset_position_form" not in st.session_state:
    st.session_state.reset_position_form = False

if "xi_variants" not in st.session_state:
    st.session_state.xi_variants = []
if "xi_variant_count" not in st.session_state:
    st.session_state.xi_variant_count = 0
if "xi_variant_choice" not in st.session_state:
    st.session_state.xi_variant_choice = 0

if "formation_mode" not in st.session_state:
    st.session_state.formation_mode = "4-2-3-1"

if "formations" not in st.session_state:
    st.session_state.formations = {
        "4-2-3-1": {
            "ip": [
                "GK",
                "LB", "CB", "CB", "RB",
                "CDM", "CM",
                "CAM",
                "LW", "RW",
                "ST",
            ],
            "oop": [
                "GK",
                "LB", "CB", "CB", "RB",
                "CDM", "CDM",
                "CM",
                "LM", "RM",
                "ST",
            ],
        },
        "5-2-1-2": {
            "ip": [
                "GK",
                "LWB", "CB", "CB", "RWB",
                "CDM", "CM", "CM",
                "CAM",
                "ST", "ST",
            ],
            "oop": [
                "GK",
                "LWB", "CB", "CB", "CB",
                "RWB", "CDM", "CDM",
                "CAM",
                "ST", "ST",
            ],
        },
    }

FORMATION_MAX_COUNTS = {"CB": 3, "CM": 3, "CDM": 3, "CAM": 3, "ST": 3}

def formation_max_for_pos(pos: str) -> int:
    pos = (pos or "").upper()
    return int(FORMATION_MAX_COUNTS.get(pos, 1))

def validate_formation_positions(ip_11: list[str], oop_11: list[str]) -> tuple[bool, str]:
    if len(ip_11) != 11 or len(oop_11) != 11:
        return False, "Formation must have exactly 11 IP positions and 11 OOP positions."

    def _validate_one(label: str, positions_11: list[str]) -> tuple[bool, str]:
        counts = Counter()
        for p in positions_11:
            pu = (p or "").upper().strip()
            if pu not in POSITION_CHOICES:
                return False, f"Invalid position in {label}: {pu}"
            counts[pu] += 1
            if counts[pu] > formation_max_for_pos(pu):
                return False, f"Too many {pu} in {label}: max {formation_max_for_pos(pu)}"
        return True, "OK"

    ok, msg = _validate_one("IP", ip_11)
    if not ok:
        return ok, msg

    ok, msg = _validate_one("OOP", oop_11)
    if not ok:
        return ok, msg

    return True, "OK"

if "state_loaded" not in st.session_state:
    load_state_from_disk()
    st.session_state.state_loaded = True


# =========================
# HELPER FUNCTIONS
# =========================

def is_domestic(nationality: str, club_country: str) -> bool:
    if not nationality or not club_country:
        return False
    return nationality.strip().casefold() == club_country.strip().casefold()


def is_under23_domestic(player: dict, club_country: str) -> bool:
    try:
        age = int(player.get("age", 0))
    except Exception:
        age = 0
    return age < 23 and is_domestic(player.get("nationality", ""), club_country)


def add_or_update_player(player: dict):
    name = player["name"].strip()
    for p in st.session_state.players:
        if p["name"].strip().lower() == name.lower():
            p.update(player)
            return
    st.session_state.players.append(player)

def best_rating_for_allowed_positions(player: dict, allowed_positions: list[str]):
    """
    Among allowed_positions, return (best_rating, best_position) for this player.
    Uses single_pos_rating, so 0.0 means 'cannot play this'.
    """
    best_score = 0.0
    best_pos = None
    for pos in allowed_positions:
        score = single_pos_rating(player, pos)
        if score > best_score:
            best_score = score
            best_pos = pos
    return best_score, best_pos

def best_combined_for_allowed_positions(player: dict, allowed_positions: list[str]):
    """
    Among allowed_positions, return (best_score, best_position) where
    score = (IP + OOP) + tiny potential bonus so ties favour higher-upside players.
    """
    # Tiny potential bonus used only as tie-breaker (won't beat real star gaps)
    band = player.get("potential_band", "") or ""
    league = player.get("potential_level_league", "") or ""

    band_rank = POTENTIAL_BAND_SORT.get(band, len(POTENTIAL_BAND_SORT))
    league_rank = POTENTIAL_LEAGUE_SORT.get(league, len(POTENTIAL_LEAGUE_SORT))

    max_band = max(len(POTENTIAL_BAND_SORT) - 1, 1)
    max_league = max(len(POTENTIAL_LEAGUE_SORT) - 1, 1)

    band_score = (max_band - band_rank) / max_band
    league_score = (max_league - league_rank) / max_league
    potential_bonus = 0.01 * (band_score + league_score)

    best_score = 0.0
    best_pos: str | None = None

    for pos in allowed_positions:
        ip = single_pos_rating(player, pos)
        oop = single_pos_rating_oop(player, pos)
        base = ip + oop
        score = base + potential_bonus
        if score > best_score:
            best_score = score
            best_pos = pos

    return best_score, best_pos

def lineup_ip_score(players, xi_indices, assignment: dict[int, str]) -> float:
    """Total IP score for this XI + position assignment."""
    total = 0.0
    for idx in xi_indices:
        pos = assignment.get(idx)
        if not pos:
            return 0.0
        total += single_pos_rating(players[idx], pos)
    return total


def lineup_oop_score(players, xi_indices, assignment: dict[int, str]) -> float:
    """Total OOP score for this XI + position assignment."""
    total = 0.0
    for idx in xi_indices:
        pos = assignment.get(idx)
        if not pos:
            return 0.0
        total += single_pos_rating_oop(players[idx], pos)
    return total


def optimize_xi_positions_ip(
    players,
    xi_indices: list[int],
    use_fullbacks: bool,
    use_back_three: bool,
) -> tuple[list[dict[int, str]], float]:
    """
    For a fixed XI find all IP assignments that give the highest total IP rating
    under all the structural rules.

    Returns (list_of_assignments, best_total_score).
    If no valid assignment exists, returns ([], 0.0).
    """
    if not xi_indices:
        return [], 0.0

    xi_list = list(xi_indices)

    # For IP we only require a mid if at least one XI player
    # can actually play CDM/CM.
    mid_required = any(
        single_pos_rating(players[i], "CDM") > 0
        or single_pos_rating(players[i], "CM") > 0
        for i in xi_list
    )

    best_score = -1.0
    best_assignments: list[dict[int, str]] = []

    def backtrack(k: int, assignment: dict[int, str], counts: dict[str, int]):
        nonlocal best_score, best_assignments

        if k == len(xi_list):
            gk = counts.get("gk", 0)
            cb = counts.get("cb", 0)
            lb_like = counts.get("lb_like", 0)
            rb_like = counts.get("rb_like", 0)
            lm_like = counts.get("lm_like", 0)
            rm_like = counts.get("rm_like", 0)
            mid_like = counts.get("mid_like", 0)
            st_count = counts.get("st", 0)
            fullback = counts.get("fullback", 0)

            if gk != 1:
                return
            if st_count > 2:
                return

            if use_back_three:
                if fullback != 0:
                    return
                if cb != 3:
                    return
            else:
                if use_fullbacks:
                    if lb_like != 1 or rb_like != 1:
                        return
                    if cb < 2:
                        return

            if lm_like > 1 or rm_like > 1:
                return
            # Wide symmetry rule:
            if (lm_like > 0 and rm_like == 0) or (rm_like > 0 and lm_like == 0):
                return

            if mid_required and mid_like < 1:
                return

            score = lineup_ip_score(players, xi_list, assignment)
            if score > best_score + 1e-6:
                best_score = score
                best_assignments = [assignment.copy()]
            elif abs(score - best_score) <= 1e-6:
                best_assignments.append(assignment.copy())
            return

        idx = xi_list[k]
        p = players[idx]

        for pos in POSITION_CHOICES:
            rating = single_pos_rating(p, pos)
            if rating <= 0:
                continue

            up = pos.upper()

            if up == "GK" and counts["gk"] >= 1:
                continue
            if use_back_three and up in ("LB", "LWB", "RB", "RWB"):
                continue

            gk = counts["gk"]
            cb = counts["cb"]
            lb_like = counts["lb_like"]
            rb_like = counts["rb_like"]
            lm_like = counts["lm_like"]
            rm_like = counts["rm_like"]
            mid_like = counts["mid_like"]
            st_count = counts["st"]
            fullback = counts["fullback"]

            if up == "GK":
                gk += 1
            if up == "CB":
                cb += 1
            if up in ("LB", "LWB", "RB", "RWB"):
                fullback += 1
            if up in ("LB", "LWB"):
                lb_like += 1
            if up in ("RB", "RWB"):
                rb_like += 1
            if up in ("LM", "LW"):
                lm_like += 1
            if up in ("RM", "RW"):
                rm_like += 1
            if up in ("CDM", "CM"):
                mid_like += 1
            if up == "ST":
                st_count += 1

            if gk > 1:
                continue
            if st_count > 2:
                continue
            if lm_like > 1 or rm_like > 1:
                continue
            if not use_back_three and use_fullbacks:
                if lb_like > 1 or rb_like > 1:
                    continue
            if use_back_three and cb > 3:
                continue

            new_counts = {
                "gk": gk,
                "cb": cb,
                "lb_like": lb_like,
                "rb_like": rb_like,
                "lm_like": lm_like,
                "rm_like": rm_like,
                "mid_like": mid_like,
                "st": st_count,
                "fullback": fullback,
            }

            assignment[idx] = up
            backtrack(k + 1, assignment, new_counts)
            del assignment[idx]

    init_counts = {
        "gk": 0,
        "cb": 0,
        "lb_like": 0,
        "rb_like": 0,
        "lm_like": 0,
        "rm_like": 0,
        "mid_like": 0,
        "st": 0,
        "fullback": 0,
    }
    backtrack(0, {}, init_counts)

    if best_score < 0 or not best_assignments:
        return [], 0.0

    return best_assignments, best_score

def optimize_xi_positions_oop(
    players,
    xi_indices: list[int],
    use_fullbacks: bool,
    use_back_three: bool,
) -> tuple[list[dict[int, str]], float]:
    """
    For a fixed XI find all OOP assignments that give the highest total OOP rating
    under all the structural rules.

    Returns (list_of_assignments, best_total_score).
    If no valid assignment exists, returns ([], 0.0).
    """
    if not xi_indices:
        return [], 0.0

    xi_list = list(xi_indices)

    # For OOP we always demand at least one CDM/CM in the XI.
    mid_required = True

    best_score = -1.0
    best_assignments: list[dict[int, str]] = []

    def backtrack(k: int, assignment: dict[int, str], counts: dict[str, int]):
        nonlocal best_score, best_assignments

        if k == len(xi_list):
            gk = counts.get("gk", 0)
            cb = counts.get("cb", 0)
            lb_like = counts.get("lb_like", 0)
            rb_like = counts.get("rb_like", 0)
            lm_like = counts.get("lm_like", 0)
            rm_like = counts.get("rm_like", 0)
            mid_like = counts.get("mid_like", 0)
            st_count = counts.get("st", 0)
            fullback = counts.get("fullback", 0)

            if gk != 1:
                return
            if st_count > 2:
                return

            if use_back_three:
                if fullback != 0:
                    return
                if cb != 3:
                    return
            else:
                if use_fullbacks:
                    if lb_like != 1 or rb_like != 1:
                        return
                    if cb < 2:
                        return

            if lm_like > 1 or rm_like > 1:
                return
            if (lm_like > 0 and rm_like == 0) or (rm_like > 0 and lm_like == 0):
                return

            if mid_required and mid_like < 1:
                return

            score = lineup_oop_score(players, xi_list, assignment)
            if score > best_score + 1e-6:
                best_score = score
                best_assignments = [assignment.copy()]
            elif abs(score - best_score) <= 1e-6:
                best_assignments.append(assignment.copy())
            return

        idx = xi_list[k]
        p = players[idx]

        for pos in POSITION_CHOICES:
            rating = single_pos_rating_oop(p, pos)
            if rating <= 0:
                continue

            up = pos.upper()

            if up == "GK" and counts["gk"] >= 1:
                continue
            if use_back_three and up in ("LB", "LWB", "RB", "RWB"):
                continue

            gk = counts["gk"]
            cb = counts["cb"]
            lb_like = counts["lb_like"]
            rb_like = counts["rb_like"]
            lm_like = counts["lm_like"]
            rm_like = counts["rm_like"]
            mid_like = counts["mid_like"]
            st_count = counts["st"]
            fullback = counts["fullback"]

            if up == "GK":
                gk += 1
            if up == "CB":
                cb += 1
            if up in ("LB", "LWB", "RB", "RWB"):
                fullback += 1
            if up in ("LB", "LWB"):
                lb_like += 1
            if up in ("RB", "RWB"):
                rb_like += 1
            if up in ("LM", "LW"):
                lm_like += 1
            if up in ("RM", "RW"):
                rm_like += 1
            if up in ("CDM", "CM"):
                mid_like += 1
            if up == "ST":
                st_count += 1

            if gk > 1:
                continue
            if st_count > 2:
                continue
            if lm_like > 1 or rm_like > 1:
                continue
            if not use_back_three and use_fullbacks:
                if lb_like > 1 or rb_like > 1:
                    continue
            if use_back_three and cb > 3:
                continue

            new_counts = {
                "gk": gk,
                "cb": cb,
                "lb_like": lb_like,
                "rb_like": rb_like,
                "lm_like": lm_like,
                "rm_like": rm_like,
                "mid_like": mid_like,
                "st": st_count,
                "fullback": fullback,
            }

            assignment[idx] = up
            backtrack(k + 1, assignment, new_counts)
            del assignment[idx]

    init_counts = {
        "gk": 0,
        "cb": 0,
        "lb_like": 0,
        "rb_like": 0,
        "lm_like": 0,
        "rm_like": 0,
        "mid_like": 0,
        "st": 0,
        "fullback": 0,
    }
    backtrack(0, {}, init_counts)

    if best_score < 0 or not best_assignments:
        return [], 0.0

    return best_assignments, best_score

def build_xi_variants(
    players,
    base_xi_indices: list[int],
    available_indices: list[int],
    club_country: str,
    use_fullbacks: bool,
    use_back_three: bool,
    max_variants: int = 200,
) -> list[dict]:
    """
    Build XI variants by allowing 1- and 2-player swaps in/out of the XI while respecting:
    - foreigner limit in XI (<=7)
    - at least one U23 domestic in XI if baseline has one
    - structural rules via the IP/OOP optimisers
    IP & OOP always share the same XI players per variant.

    Each variant stores:
      - xi_indices
      - assignment_ip
      - assignment_oop
      - total_ip
      - total_oop
    """
    if not base_xi_indices:
        return []

    base_xi = sorted(set(base_xi_indices))

    available_for_xi = [
        i for i in available_indices if not players[i].get("injured")
    ]
    if not available_for_xi:
        return []

    # Base assignments & score (IP and OOP can each have multiple equal-best layouts)
    base_assignments_ip, base_ip_score = optimize_xi_positions_ip(
        players, base_xi, use_fullbacks=use_fullbacks, use_back_three=use_back_three
    )
    if not base_assignments_ip or base_ip_score <= 0:
        return []

    base_assignments_oop, base_oop_score = optimize_xi_positions_oop(
        players, base_xi, use_fullbacks=use_fullbacks, use_back_three=use_back_three
    )
    if not base_assignments_oop:
        # fall back to "same as IP" layouts
        base_assignments_oop = [ip.copy() for ip in base_assignments_ip]
        base_oop_score = lineup_oop_score(players, base_xi, base_assignments_oop[0])

    def counts_for_xi(xi_list: list[int]) -> tuple[int, int]:
        foreign = 0
        u23_dom = 0
        for idx in xi_list:
            p = players[idx]
            if not is_domestic(p.get("nationality", ""), club_country):
                foreign += 1
            if is_under23_domestic(p, club_country):
                u23_dom += 1
        return foreign, u23_dom

    base_foreign, base_u23_dom = counts_for_xi(base_xi)
    base_has_u23_dom = base_u23_dom > 0

    variants: list[dict] = []
    seen_sets: set[tuple[int, ...]] = set()

    def add_variant(
        xi_list: list[int],
        assign_ip: dict[int, str],
        assign_oop: dict[int, str],
        score_ip: float,
        score_oop: float,
    ):
        # Deduplicate on (XI set + IP/OOP positions), so
        # "Risto CB" and "Risto CDM" are different variants.
        xi_sorted = sorted(xi_list)
        oop_map = assign_oop or assign_ip
        signature = tuple(
            (i, assign_ip.get(i, ""), oop_map.get(i, ""))
            for i in xi_sorted
        )

        if signature in seen_sets:
            return
        seen_sets.add(signature)

        variants.append(
            {
                "xi_indices": xi_sorted,
                "assignment_ip": dict(assign_ip),
                "assignment_oop": dict(oop_map),
                "total_ip": float(score_ip),
                "total_oop": float(score_oop),
            }
        )

    # Always include baseline variants for all equal-best IP×OOP layout pairs
    for ip_assignment in base_assignments_ip:
        for oop_assignment in base_assignments_oop:
            add_variant(base_xi, ip_assignment, oop_assignment, base_ip_score, base_oop_score)
            if len(variants) >= max_variants:
                return variants

    # Helper: common checks & optimiser run for a candidate XI
    def try_candidate_xi(candidate_xi: list[int]):
        foreign, u23_dom = counts_for_xi(candidate_xi)
        if foreign > 7:
            return
        if base_has_u23_dom and u23_dom == 0:
            return

        assignments_ip, ip_score = optimize_xi_positions_ip(
            players,
            candidate_xi,
            use_fullbacks=use_fullbacks,
            use_back_three=use_back_three,
        )
        if not assignments_ip:
            return

        assignments_oop, oop_score = optimize_xi_positions_oop(
            players,
            candidate_xi,
            use_fullbacks=use_fullbacks,
            use_back_three=use_back_three,
        )
        if not assignments_oop:
            # fall back to using the IP layouts for OOP
            assignments_oop = [ip.copy() for ip in assignments_ip]
            oop_score = lineup_oop_score(players, candidate_xi, assignments_oop[0])

        # Add variants for each equal-best IP×OOP layout pair
        for ip_assignment in assignments_ip:
            for oop_assignment in assignments_oop:
                add_variant(candidate_xi, ip_assignment, oop_assignment, ip_score, oop_score)
                if len(variants) >= max_variants:
                    return

    # ========== 1-SWAP VARIANTS ==========
    for idx_out in base_xi:
        for idx_in in available_for_xi:
            if idx_in in base_xi:
                continue
            candidate_xi = [i for i in base_xi if i != idx_out] + [idx_in]
            try_candidate_xi(candidate_xi)
            if len(variants) >= max_variants:
                return variants

    # ========== 2-SWAP VARIANTS ==========
    pool = [i for i in available_for_xi if i not in base_xi]
    if len(variants) < max_variants and len(base_xi) >= 2 and len(pool) >= 2:
        for i_out_a in range(len(base_xi)):
            for i_out_b in range(i_out_a + 1, len(base_xi)):
                out1 = base_xi[i_out_a]
                out2 = base_xi[i_out_b]

                for i_in_a in range(len(pool)):
                    for i_in_b in range(i_in_a + 1, len(pool)):
                        in1 = pool[i_in_a]
                        in2 = pool[i_in_b]

                        for (first_in, second_in) in ((in1, in2), (in2, in1)):
                            candidate_xi = [
                                i for i in base_xi if i not in (out1, out2)
                            ] + [first_in, second_in]
                            try_candidate_xi(candidate_xi)
                            if len(variants) >= max_variants:
                                return variants

    return variants

def _finalize_xi_and_lists(**kwargs):
    """
    Finalize XI + bench/reserves + rule tracker.

    This is intentionally flexible (accepts **kwargs) because the caller signature
    changed during refactors.
    """
    players = kwargs.get("players") or st.session_state.get("players") or []
    club_country = kwargs.get("club_country") or ""
    formation_mode = kwargs.get("formation_mode") or st.session_state.get("formation_mode")

    xi_indices = list(kwargs.get("xi_indices") or [])
    assignment_ip = dict(kwargs.get("assignment_ip") or {})
    assignment_oop = dict(kwargs.get("assignment_oop") or {})

    available_indices = list(kwargs.get("available_indices") or [])
    if not available_indices:
        # fallback: anyone not out on loan
        available_indices = [
            i for i, p in enumerate(players)
            if p.get("availability", "Available") != "Out on loan"
        ]

    # Reset roles/assignments first
    for p in players:
        p["assigned_position_ip"] = None
        p["assigned_position_oop"] = None
        p["squad_role"] = "Unselected"
        p["bench_cover_pos"] = None
        p["reserve_cover_pos"] = None
        p["bench_better_notes"] = ""

    # Store XI variants in the format the app already uses elsewhere
    if xi_indices:
        st.session_state.xi_variants = [{
            "xi_indices": sorted(xi_indices),
            "assignment_ip": dict(assignment_ip),
            "assignment_oop": dict(assignment_oop),
            "total_ip": float(sum(single_pos_rating(players[i], assignment_ip.get(i, "") or "") for i in xi_indices)),
            "total_oop": float(sum(single_pos_rating_oop(players[i], assignment_oop.get(i, "") or "") for i in xi_indices)),
        }]
        st.session_state.xi_variant_count = len(st.session_state.xi_variants)
        if "xi_variant_choice" not in st.session_state:
            st.session_state.xi_variant_choice = 0
        else:
            st.session_state.xi_variant_choice = min(int(st.session_state.xi_variant_choice or 0), st.session_state.xi_variant_count - 1)
    else:
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.xi_variant_choice = 0

    # Apply XI assignment to player objects
    for idx in xi_indices:
        if idx < 0 or idx >= len(players):
            continue
        players[idx]["assigned_position_ip"] = assignment_ip.get(idx)
        players[idx]["assigned_position_oop"] = assignment_oop.get(idx) or assignment_ip.get(idx)
        players[idx]["squad_role"] = "XI"

    # Build bench/reserves from remaining available players (prefer not injured)
    remaining = [i for i in available_indices if i not in xi_indices]
    not_injured = [i for i in remaining if not players[i].get("injured")]
    injured = [i for i in remaining if players[i].get("injured")]
    remaining_sorted = not_injured + injured

    def bench_score(i: int) -> float:
        # Prefer players who cover the active formation well (combined IP+OOP)
        pos = best_cover_pos_for_formation(players[i], formation_mode)
        if not pos:
            return 0.0
        return combined_ip_oop_for_pos(players[i], pos)

    remaining_sorted.sort(key=lambda i: bench_score(i), reverse=True)

    bench_indices = remaining_sorted[:7]
    reserve_indices = remaining_sorted[7:]

    for idx in bench_indices:
        players[idx]["squad_role"] = "Bench"
        players[idx]["bench_cover_pos"] = best_cover_pos_for_formation(players[idx], formation_mode)

    for idx in reserve_indices:
        players[idx]["squad_role"] = "Reserves"
        players[idx]["reserve_cover_pos"] = best_cover_pos_for_formation(players[idx], formation_mode)

    # Rules tracker (keep consistent with your existing keys)
    foreign_xi = 0
    foreign_bench = 0
    u23_dom_xi = 0

    for idx in xi_indices:
        p = players[idx]
        if not is_domestic(p.get("nationality", ""), club_country):
            foreign_xi += 1
        if is_under23_domestic(p, club_country):
            u23_dom_xi += 1

    for idx in bench_indices:
        p = players[idx]
        if not is_domestic(p.get("nationality", ""), club_country):
            foreign_bench += 1

    st.session_state.rules_tracker = {
        "foreign_xi": foreign_xi,
        "foreign_xi_limit": 7,
        "foreign_xi_bench": foreign_bench,
        "foreign_xi_bench_limit": 9,
        "u23_domestic_xi": u23_dom_xi,
        "u23_domestic_xi_min": 1,
        "xi_size": len(xi_indices),
        "bench_size": len(bench_indices),
        "reserves_size": len(reserve_indices),
        "total_selected": len(xi_indices) + len(bench_indices) + len(reserve_indices),
    }

def recompute_squad_assignments(
    club_country: str,
    force_variant_idx: int | None = None,
):
    """
    Central entry point.

    - Uses 'formation_mode' in session_state as the *global* selector.
    - 'Auto' uses the old flexible 2+ logic via _recompute_squad_assignments_auto.
    - Locked 4-2-3-1 / 5-2-1-2 use _recompute_squad_assignments_locked.
    """
    formation_mode = st.session_state.get("formation_mode", "4-2-3-1")
    formations = st.session_state.get("formations", {}) or {}

    # If the chosen formation doesn't exist anymore, fall back to the first one available
    if formation_mode not in formations:
        if formations:
            formation_mode = list(formations.keys())[0]
        else:
            formation_mode = "4-2-3-1"

    return _recompute_squad_assignments_locked(
        club_country,
        formation_mode,
        force_variant_idx=force_variant_idx,
    )

def _recompute_squad_assignments_locked(
    club_country: str,
    formation_mode: str,
    force_variant_idx: int | None = None,
):
    """
    Locked formations (now dynamic):
    - Positions are fixed per slot (IP + OOP mapping) from st.session_state.formations[formation_mode]
    - Still obey: max 7 foreigners in XI, at least 1 U23 domestic in XI.
    - Bench / reserves + rule tracker are built via shared helper.
    """
    players = st.session_state.players or []
    if not players:
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.rules_tracker = {}
        return

    # Available = not out on loan (injury handled at selection time)
    available_indices: list[int] = [
        i
        for i, p in enumerate(players)
        if p.get("availability", "Available") != "Out on loan"
    ]
    if not available_indices:
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.rules_tracker = {}
        return

    formations = st.session_state.get("formations", {}) or {}
    formation_def = formations.get(formation_mode)

    # Backward compatibility: older saved formations were stored as a simple list of 11 IP positions
    if isinstance(formation_def, list):
        ip_11 = [p for p in formation_def]
        oop_11 = [p for p in formation_def]
        formations[formation_mode] = {"ip": ip_11, "oop": oop_11}
        st.session_state.formations = formations
    elif isinstance(formation_def, dict):
        ip_11 = list(formation_def.get("ip") or [])
        oop_11 = list(formation_def.get("oop") or [])
    else:
        ip_11 = []
        oop_11 = []

    ok, _ = validate_formation_positions(ip_11, oop_11)
    if not ok:
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.rules_tracker = {}
        return

    slot_defs = [{"ip": ip_11[i], "oop": oop_11[i]} for i in range(11)]
    num_slots = len(slot_defs)

    # Precompute candidates per slot: (player_idx, ip, oop, combined, is_foreign, is_u23_dom)
    slot_candidates: list[list[tuple[int, float, float, float, bool, bool]]] = []
    slot_max_scores: list[float] = []

    for slot in slot_defs:
        ip_pos = slot["ip"]
        oop_pos = slot["oop"]
        cand_list: list[tuple[int, float, float, float, bool, bool]] = []
        max_score = 0.0

        for idx in available_indices:
            p = players[idx]
            if p.get("injured"):
                continue

            ip_score = single_pos_rating(p, ip_pos)
            oop_score = single_pos_rating_oop(p, oop_pos)
            combined = ip_score + oop_score

            is_foreign = (p.get("nationality") or "").strip().lower() != (club_country or "").strip().lower()
            is_u23_dom = (not is_foreign) and int(p.get("age") or 99) <= 23

            cand_list.append((idx, ip_score, oop_score, combined, is_foreign, is_u23_dom))
            if combined > max_score:
                max_score = combined

        cand_list.sort(key=lambda t: t[3], reverse=True)
        slot_candidates.append(cand_list)
        slot_max_scores.append(max_score)

    # Search best assignment with constraints
    best_total = -1e18
    best_total_ip = -1e18
    best_total_oop = -1e18
    best_assign: list[tuple[int, float, float, float, bool, bool]] | None = None

    used: set[int] = set()
    current: list[tuple[int, float, float, float, bool, bool]] = [None] * num_slots  # type: ignore

    def backtrack(slot_i: int, total_ip: float, total_oop: float, foreign_count: int, u23_dom_count: int):
        nonlocal best_total, best_total_ip, best_total_oop, best_assign

        if slot_i >= num_slots:
            if foreign_count <= 7 and u23_dom_count >= 1:
                total = total_ip + total_oop
                if total > best_total:
                    best_total = total
                    best_total_ip = total_ip
                    best_total_oop = total_oop
                    best_assign = list(current)
            return

        # optimistic bound
        remaining_max = 0.0
        for j in range(slot_i, num_slots):
            remaining_max += slot_max_scores[j]
        if (total_ip + total_oop + remaining_max) <= best_total:
            return

        for cand in slot_candidates[slot_i]:
            idx, ip_s, oop_s, combined, is_foreign, is_u23_dom = cand
            if idx in used:
                continue

            new_foreign = foreign_count + (1 if is_foreign else 0)
            if new_foreign > 7:
                continue

            used.add(idx)
            current[slot_i] = cand

            backtrack(
                slot_i + 1,
                total_ip + ip_s,
                total_oop + oop_s,
                new_foreign,
                u23_dom_count + (1 if is_u23_dom else 0),
            )

            used.remove(idx)
            current[slot_i] = None  # type: ignore

    backtrack(0, 0.0, 0.0, 0, 0)

    if not best_assign:
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.rules_tracker = {}
        return

    # Build XI player dicts
    xi_players: list[dict] = []
    for slot_i, cand in enumerate(best_assign):
        idx, ip_s, oop_s, combined, is_foreign, is_u23_dom = cand
        p = dict(players[idx])
        p["assigned_position_ip"] = slot_defs[slot_i]["ip"]
        p["assigned_position_oop"] = slot_defs[slot_i]["oop"]
        p["_assigned_ip_score"] = float(ip_s)
        p["_assigned_oop_score"] = float(oop_s)
        p["_assigned_total_score"] = float(combined)
        xi_players.append(p)

    # Use shared builder for bench/reserves/rules tracking (your existing helper)
    _finalize_xi_and_lists(
        club_country=club_country,
        xi_players=xi_players,
        formation_mode=formation_mode,
        force_variant_idx=force_variant_idx,
    )

    def dfs(
        slot_idx: int,
        current_total: float,
        current_ip_total: float,
        current_oop_total: float,
        foreign_count: int,
        u23_dom_count: int,
    ):
        nonlocal best_total, best_total_ip, best_total_oop, best_assign

        # Upper bound pruning
        remaining_max = sum(slot_max_scores[slot_idx:])
        if current_total + remaining_max <= best_total + 1e-6:
            return

        if slot_idx >= num_slots:
            # Check constraints once XI is full
            if foreign_count > 7:
                return
            if u23_dom_count < 1:
                return
            if current_total > best_total + 1e-6:
                best_total = current_total
                best_total_ip = current_ip_total
                best_total_oop = current_oop_total
                best_assign = [dict(a) for a in current_assign]
            return

        # Try each candidate for this slot
        for (player_idx, ip_score, oop_score, combined, is_foreign, is_u23_dom) in slot_candidates[slot_idx]:
            if player_idx in used_players:
                continue

            new_foreign = foreign_count + (1 if is_foreign else 0)
            if new_foreign > 7:
                continue

            new_u23 = u23_dom_count + (1 if is_u23_dom else 0)

            used_players.add(player_idx)
            current_assign.append(
                {
                    "slot_idx": slot_idx,
                    "player_idx": player_idx,
                    "ip_score": ip_score,
                    "oop_score": oop_score,
                    "combined": combined,
                }
            )

            dfs(
                slot_idx + 1,
                current_total + combined,
                current_ip_total + ip_score,
                current_oop_total + oop_score,
                new_foreign,
                new_u23,
            )

            current_assign.pop()
            used_players.remove(player_idx)

    dfs(
        slot_idx=0,
        current_total=0.0,
        current_ip_total=0.0,
        current_oop_total=0.0,
        foreign_count=0,
        u23_dom_count=0,
    )

    # No valid XI satisfying rules → fall back
    if best_total < 0 or not best_assign:
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.rules_tracker = {}
        return

    # Build final XI based on best assignment
    final_xi_indices: list[int] = []
    assignment_ip: dict[int, str] = {}
    assignment_oop: dict[int, str] = {}

    for a in best_assign:
        slot_idx = a["slot_idx"]
        player_idx = a["player_idx"]
        ip_pos = slot_defs[slot_idx]["ip"]
        oop_pos = slot_defs[slot_idx]["oop"]

        final_xi_indices.append(player_idx)
        assignment_ip[player_idx] = ip_pos
        assignment_oop[player_idx] = oop_pos

    # Ensure exactly one player per slot, no duplicates
    final_xi_indices = list(dict.fromkeys(final_xi_indices))
    if len(final_xi_indices) != num_slots:
        # Safety net
        st.session_state.xi_variants = []
        st.session_state.xi_variant_count = 0
        st.session_state.rules_tracker = {}
        return

    # Clear all previous roles
    for p in players:
        p["assigned_position_ip"] = None
        p["assigned_position_oop"] = None
        p["squad_role"] = "Unselected"
        p.pop("bench_cover_pos", None)
        p.pop("reserve_cover_pos", None)
        p.pop("bench_better_notes", None)

    # Apply XI assignments
    for idx in final_xi_indices:
        p = players[idx]
        p["squad_role"] = "XI"
        p["assigned_position_ip"] = assignment_ip.get(idx)
        p["assigned_position_oop"] = assignment_oop.get(idx) or assignment_ip.get(idx)

    # Single XI variant for locked formations
    st.session_state.xi_variants = [
        {
            "xi_indices": sorted(final_xi_indices),
            "assignment_ip": assignment_ip,
            "assignment_oop": assignment_oop,
            "total_ip": float(best_total_ip),
            "total_oop": float(best_total_oop),
        }
    ]
    st.session_state.xi_variant_count = 1
    st.session_state.xi_variant_choice = 0
    n = len(final_xi_indices) or 1
    st.session_state["xi_best_avg"] = round((best_total_ip + best_total_oop) / n, 2)

    # Build bench & reserves + rules tracker with shared helper
    bench_indices, reserve_indices, rules_tracker = _build_bench_and_reserves(
        players=players,
        available_indices=available_indices,
        final_xi_indices=final_xi_indices,
        club_country=club_country,
        formation_mode=formation_mode,
    )
    st.session_state.rules_tracker = rules_tracker

def _recompute_squad_assignments_auto(
    club_country: str,
    force_variant_idx: int | None = None,
):
    """
    Auto-picks XI, Bench (10) og Reserves (op til 12).

    Regler (samme som før):
    - Præcis 1 GK i XI (hvis der findes en GK-rated spiller)
    - Max 2 ST i XI
    - Fullback / CB logik:
        * Hvis truppen har mindst én LB/LWB-rated OG mindst én RB/RWB-rated (ikke skadet):
            -> XI skal indeholde præcis én LB/LWB og præcis én RB/RWB
            -> Min. 2 CB
        * Ellers:
            -> XI har INGEN LB/LWB/RB/RWB og PRÆCIS 3 CB i alt
    - Max 1 LB/LWB i XI
    - Max 1 RB/RWB i XI
    - Max 1 LM/LW i XI
    - Max 1 RM/RW i XI
    - Min. 1 CDM eller CM i XI (hvis der findes en ikke-skadet spiller med rating > 0 der)
    - Max 7 udlændinge i XI
    - Max 9 udlændinge i XI + Bænk
    - Min. 1 U23-indoneser i XI hvis muligt
    - Skadede spillere må KUN være Reserve/Unselected (ikke XI, ikke bænk)
    - Efter baseline XI er valgt (spillere), bygger vi XI-varianter:
      * samme totale IP-rating
      * 1–2 swaps ind/ud
      * IP og OOP deler altid samme XI
    """

    players = st.session_state.players

    # Reset pr. spiller + recompute primary position
    for p in players:
        p["assigned_position_ip"] = None
        p["assigned_position_oop"] = None
        p["squad_role"] = "Unselected"
        p["primary_position"] = compute_primary_position(p)
        p["bench_cover_pos"] = None
        p["reserve_cover_pos"] = None
        p["bench_better_notes"] = ""

    # Reset rule tracker
    st.session_state.rules_tracker = {
        "foreign_xi": 0,
        "foreign_xi_limit": 7,
        "foreign_xi_bench": 0,
        "foreign_xi_bench_limit": 9,
        "u23_domestic_xi": 0,
        "u23_domestic_xi_min": 1,
        "xi_size": 0,
        "bench_size": 0,
        "reserves_size": 0,
        "total_selected": 0,
    }

    # Reset XI-variant state
    st.session_state.xi_variants = []
    st.session_state.xi_variant_count = 0

    if not club_country or not players:
        return

    # Kun spillere der ikke er udlejet
    available_indices = [
        i
        for i, p in enumerate(players)
        if p.get("availability", "Available") != "Out on loan"
    ]
    if not available_indices:
        return

    xi_indices: list[int] = []

    gk_count = 0
    cb_count = 0
    lb_like_count = 0
    rb_like_count = 0
    lm_like_count = 0
    rm_like_count = 0
    mid_like_count = 0
    st_count = 0

    foreign_xi = 0
    u23_domestic_xi = 0

    # STEP 1: find kandidater til fullbacks vs back-three mode
    remaining_for_scan = [i for i in available_indices if not players[i].get("injured")]

    has_lb_like = any(
        best_rating_for_allowed_positions(players[i], ["LB", "LWB"])[0] > 0
        for i in remaining_for_scan
    )
    has_rb_like = any(
        best_rating_for_allowed_positions(players[i], ["RB", "RWB"])[0] > 0
        for i in remaining_for_scan
    )

    use_fullbacks = has_lb_like and has_rb_like
    use_back_three = not use_fullbacks

    # STEP 2: vælg GK først
    gk_candidates = []
    for i in available_indices:
        p = players[i]
        if p.get("injured"):
            continue
        score, pos = best_rating_for_allowed_positions(p, ["GK"])
        if score > 0:
            gk_candidates.append((score, i, pos))

    if gk_candidates:
        score, idx, pos = max(gk_candidates, key=lambda t: t[0])
        xi_indices.append(idx)
        gk_count = 1
        if not is_domestic(players[idx].get("nationality", ""), club_country):
            foreign_xi += 1
        if is_under23_domestic(players[idx], club_country):
            u23_domestic_xi += 1

    # Helper til forsvarere (kun for at bestemme baseline XI-puljen)
    def pick_defender(allowed_positions: list[str]):
        nonlocal cb_count, lb_like_count, rb_like_count, lm_like_count, rm_like_count, mid_like_count
        nonlocal foreign_xi, u23_domestic_xi

        best_tuple = None  # (score, idx, chosen_pos)

        for i in available_indices:
            if i in xi_indices:
                continue
            p = players[i]
            if p.get("injured"):
                continue

            score, chosen_pos = best_rating_for_allowed_positions(
                p, allowed_positions
            )
            if score <= 0:
                continue

            if chosen_pos == "GK":
                continue

            if chosen_pos in ("LB", "LWB") and lb_like_count >= 1:
                continue
            if chosen_pos in ("RB", "RWB") and rb_like_count >= 1:
                continue

            foreign = not is_domestic(p.get("nationality", ""), club_country)
            if foreign and foreign_xi + 1 > 7:
                continue

            if best_tuple is None or score > best_tuple[0]:
                best_tuple = (score, i, chosen_pos)

        if best_tuple is None:
            return False

        score, idx, chosen_pos = best_tuple
        xi_indices.append(idx)

        if chosen_pos == "CB":
            cb_count += 1
        if chosen_pos in ("LB", "LWB"):
            lb_like_count += 1
        if chosen_pos in ("RB", "RWB"):
            rb_like_count += 1
        if chosen_pos in ("LM", "LW"):
            lm_like_count += 1
        if chosen_pos in ("RM", "RW"):
            rm_like_count += 1
        if chosen_pos in ("CDM", "CM"):
            mid_like_count += 1

        if not is_domestic(players[idx].get("nationality", ""), club_country):
            foreign_xi += 1
        if is_under23_domestic(players[idx], club_country):
            u23_domestic_xi += 1

        return True

    # STEP 3: baseline defensiv enhed
    if use_fullbacks:
        pick_defender(["LB", "LWB"])
        pick_defender(["RB", "RWB"])
        pick_defender(["CB"])
        pick_defender(["CB"])
    else:
        pick_defender(["CB"])
        pick_defender(["CB"])
        pick_defender(["CB"])

    # STEP 4: sørg for mindst én U23-domestic i XI hvis muligt
    if u23_domestic_xi == 0:
        u23_candidates = []
        for i in available_indices:
            if i in xi_indices:
                continue
            p = players[i]
            if p.get("injured"):
                continue
            if not is_under23_domestic(p, club_country):
                continue
            score, pos = best_rating_for_allowed_positions(
                p,
                [pos for pos in POSITION_CHOICES if pos != "GK"],
            )
            if score > 0:
                u23_candidates.append((score, i, pos))

        if u23_candidates and len(xi_indices) < 11:
            score, idx, pos = max(u23_candidates, key=lambda t: t[0])
            xi_indices.append(idx)
            if pos == "CB":
                cb_count += 1
            if pos in ("LB", "LWB"):
                lb_like_count += 1
            if pos in ("RB", "RWB"):
                rb_like_count += 1
            if pos in ("LM", "LW"):
                lm_like_count += 1
            if pos in ("RM", "RW"):
                rm_like_count += 1
            if pos in ("CDM", "CM"):
                mid_like_count += 1
            if pos == "ST":
                st_count += 1
            if not is_domestic(players[idx].get("nationality", ""), club_country):
                foreign_xi += 1
            u23_domestic_xi += 1

    # STEP 4.5: hvis ingen CDM/CM i XI, prøv at tilføje én
    if mid_like_count == 0 and len(xi_indices) < 11:
        best_mid = None  # (score, idx, chosen_pos)
        for i in available_indices:
            if i in xi_indices:
                continue
            p = players[i]
            if p.get("injured"):
                continue

            score_cdm, _ = best_rating_for_allowed_positions(p, ["CDM"])
            score_cm, _ = best_rating_for_allowed_positions(p, ["CM"])

            if score_cdm <= 0 and score_cm <= 0:
                continue

            if score_cdm >= score_cm:
                score = score_cdm
                pos = "CDM"
            else:
                score = score_cm
                pos = "CM"

            if score <= 0:
                continue

            foreign = not is_domestic(p.get("nationality", ""), club_country)
            if foreign and foreign_xi + 1 > 7:
                continue

            if best_mid is None or score > best_mid[0]:
                best_mid = (score, i, pos)

        if best_mid is not None:
            score, idx, pos = best_mid
            xi_indices.append(idx)
            mid_like_count += 1
            if not is_domestic(players[idx].get("nationality", ""), club_country):
                foreign_xi += 1
            if is_under23_domestic(players[idx], club_country):
                u23_domestic_xi += 1

    # STEP 5: fyld resten af XI (kun spiller-valg)
    if len(xi_indices) < 11:
        remaining_indices = [i for i in available_indices if i not in xi_indices]
        remaining_indices.sort(key=lambda i: -best_position_rating(players[i]))

        for i in remaining_indices:
            if len(xi_indices) >= 11:
                break
            p = players[i]
            if p.get("injured"):
                continue

            best_score = 0.0
            best_pos = None

            for pos in POSITION_CHOICES:
                up = pos.upper()

                if up == "GK" and gk_count >= 1:
                    continue
                if up == "ST" and st_count >= 2:
                    continue

                if use_back_three and up in ("LB", "LWB", "RB", "RWB"):
                    continue
                if use_back_three and up == "CB" and cb_count >= 3:
                    continue

                if up in ("LB", "LWB") and lb_like_count >= 1:
                    continue
                if up in ("RB", "RWB") and rb_like_count >= 1:
                    continue
                if up in ("LM", "LW") and lm_like_count >= 1:
                    continue
                if up in ("RM", "RW") and rm_like_count >= 1:
                    continue

                score = single_pos_rating(p, up)
                if score > best_score:
                    best_score = score
                    best_pos = up

            if best_score <= 0 or best_pos is None:
                continue

            foreign = not is_domestic(p.get("nationality", ""), club_country)
            if foreign and foreign_xi + 1 > 7:
                continue

            xi_indices.append(i)

            if best_pos == "GK":
                gk_count += 1
            if best_pos == "CB":
                cb_count += 1
            if best_pos in ("LB", "LWB"):
                lb_like_count += 1
            if best_pos in ("RB", "RWB"):
                rb_like_count += 1
            if best_pos in ("LM", "LW"):
                lm_like_count += 1
            if best_pos in ("RM", "RW"):
                rm_like_count += 1
            if best_pos in ("CDM", "CM"):
                mid_like_count += 1
            if best_pos == "ST":
                st_count += 1

            if foreign:
                foreign_xi += 1
            if is_under23_domestic(p, club_country):
                u23_domestic_xi += 1

    xi_indices = xi_indices[:11]
    if len(xi_indices) == 0:
        return

    # STEP 5.9: byg XI-varianter (forskellige spiller-sæt)
    variants = build_xi_variants(
        players=players,
        base_xi_indices=xi_indices,
        available_indices=available_indices,
        club_country=club_country,
        use_fullbacks=use_fullbacks,
        use_back_three=use_back_three,
        max_variants=200,
    )

    if not variants:
        # fallback: bare baseline assignments (IP and OOP both may have multiple layouts)
        base_assignments_ip, base_ip_score = optimize_xi_positions_ip(
            players, xi_indices, use_fullbacks=use_fullbacks, use_back_three=use_back_three
        )
        if not base_assignments_ip:
            return

        base_assignments_oop, base_oop_score = optimize_xi_positions_oop(
            players, xi_indices, use_fullbacks=use_fullbacks, use_back_three=use_back_three
        )
        if not base_assignments_oop:
            base_assignments_oop = [ip.copy() for ip in base_assignments_ip]
            base_oop_score = lineup_oop_score(players, xi_indices, base_assignments_oop[0])

        variants = []
        for ip_assignment in base_assignments_ip:
            for oop_assignment in base_assignments_oop:
                variants.append(
                    {
                        "xi_indices": sorted(xi_indices),
                        "assignment_ip": ip_assignment,
                        "assignment_oop": oop_assignment,
                        "total_ip": float(base_ip_score),
                        "total_oop": float(base_oop_score),
                    }
                )
                if len(variants) >= 20:
                    break
            if len(variants) >= 20:
                break

    # Filter variants: keep those whose average (IP+OOP) is within a tiny buffer
    # of the absolute best. This keeps structurally neutral swaps alive instead
    # of killing them on floating point / rounding noise.
    XI_AVG_TOLERANCE = 0.005  # allow up to 0.005⭐ below best

    def _avg_score(v: dict) -> float:
        xi_list = v.get("xi_indices") or []
        n = len(xi_list) or 1
        ip = float(v.get("total_ip", 0.0))
        oop = float(v.get("total_oop", 0.0))
        return (ip + oop) / n

    if variants:
        # Raw best average (no rounding)
        best_avg_raw = max(_avg_score(v) for v in variants)

        # What the UI shows
        best_score_rounded = round(best_avg_raw, 2)
        st.session_state["xi_best_avg"] = best_score_rounded

        # Keep all variants that are effectively equal-best within the tolerance
        best_variants: list[dict] = []
        for v in variants:
            if _avg_score(v) >= best_avg_raw - XI_AVG_TOLERANCE:
                best_variants.append(v)

        variants = best_variants or variants
    else:
        st.session_state["xi_best_avg"] = 0.0

    st.session_state.xi_variants = variants
    st.session_state.xi_variant_count = len(variants)

    # Decide which XI variant to use right now
    if force_variant_idx is not None:
        # coming directly from the radio choice
        idx = int(force_variant_idx)
    else:
        # normal path: reuse whatever is in session_state
        idx = st.session_state.get("xi_variant_choice", 0)

    # Clamp safely
    if not isinstance(idx, int) or idx < 0 or idx >= len(variants):
        idx = 0

    # Persist the final choice
    st.session_state.xi_variant_choice = idx

    # This is the variant whose IP/OOP assignments we actually apply
    chosen_variant = variants[idx]
    final_xi_indices = list(chosen_variant["xi_indices"])
    assignment_ip = chosen_variant.get("assignment_ip", {}) or {}
    assignment_oop = chosen_variant.get("assignment_oop", {}) or {}

    # Clear any previous roles/positions
    for p in players:
        p["assigned_position_ip"] = None
        p["assigned_position_oop"] = None
        p["squad_role"] = "Unselected"

    # Assign XI players + positions
    for idx in final_xi_indices:
        p = players[idx]
        p["squad_role"] = "XI"
        p["assigned_position_ip"] = assignment_ip.get(idx)
        p["assigned_position_oop"] = assignment_oop.get(idx) or assignment_ip.get(idx)

    # Collect XI IP positions (current formation) for formation-aware cover roles
    xi_ip_positions = sorted(
        {
            (players[idx].get("assigned_position_ip") or "").upper()
            for idx in final_xi_indices
            if players[idx].get("assigned_position_ip")
        },
        key=position_sort_key,
    )

    def best_cover_pos_for_xi(p: dict) -> str | None:
        """
        Pick the best cover position for this player, restricted to
        positions that actually exist in the current XI (IP).
        """
        if not xi_ip_positions:
            return None
        best_score = 0.0
        best_pos: str | None = None
        for pos in xi_ip_positions:
            score = combined_ip_oop_for_pos(p, pos)
            if score > best_score + 1e-6:
                best_score = score
                best_pos = pos
        return best_pos

    formation_mode = st.session_state.get("formation_mode", "4-2-3-1")
    # STEP 7–9: bench, reserves & rules (shared helper)
    bench_indices, reserve_indices, rules_tracker = _build_bench_and_reserves(
        players=players,
        available_indices=available_indices,
        final_xi_indices=final_xi_indices,
        club_country=club_country,
        formation_mode=formation_mode,
    )
    st.session_state.rules_tracker = rules_tracker

def best_cover_pos_for_xi(player: dict) -> str | None:
    """
    Helper used for bench / reserves: returns the player's 'natural' cover position
    based on current XI / bench / reserve assignments, falling back to best IP pos.
    """
    # Prefer explicit XI position if set
    pos = player.get("assigned_position_ip")
    if pos:
        return pos

    # Otherwise bench / reserve cover positions if they exist
    pos = player.get("bench_cover_pos") or player.get("reserve_cover_pos")
    if pos:
        return pos

    # Last resort: generic best IP position
    return best_ip_position(player)

def _build_bench_and_reserves(
    players: list[dict],
    available_indices: list[int],
    final_xi_indices: list[int],
    club_country: str,
    formation_mode: str,
) -> tuple[list[int], list[int], dict]:
    """
    Bench + Reserves builder.

    Bench:
      - Max 10 players
      - First: 1 cover for every position that appears in XI (IP) if possible
      - Then: extra bench players only where formation has 2+ slots (CB, ST, etc)
      - Foreigners in XI+Bench: max 9 (unique players)

    Reserves:
      - Max 12 players
      - Injured players allowed ONLY as Reserves / Unselected
      - Reserves respect global position caps, but injured are added first even if over cap

    Tiebreaks everywhere:
      - rating (combined IP+OOP for cover position) DESC
      - potential band (Leading > Good > Decent > Standard > rest)
      - potential league (Super League > Championship > Liga Nusantara)
      - age (younger first)
    """

    # --- XI shape (IP only) ---
    formation_pos_counts = Counter()
    xi_cover_counts = Counter()
    foreign_xi_final = 0
    u23_domestic_xi_final = 0

    for idx in final_xi_indices:
        p = players[idx]
        pos_ip = (p.get("assigned_position_ip") or "").upper()
        if pos_ip:
            formation_pos_counts[pos_ip] += 1
            xi_cover_counts[pos_ip] += 1

        if not is_domestic(p.get("nationality", ""), club_country):
            foreign_xi_final += 1
        if is_under23_domestic(p, club_country):
            u23_domestic_xi_final += 1

    # --- caps per position ---
    def _bench_cap_for_pos(pos: str) -> int:
        """Max bench players for this position."""
        pos = (pos or "").upper()
        if not pos:
            return 1
        count = formation_pos_counts.get(pos, 0)
        return 2 if count >= 2 else 1

    def _squad_cap_for_pos(pos: str) -> int:
        """Max XI+Bench+Reserves coverage for this position."""
        pos = (pos or "").upper()
        if not pos:
            return 3
        count = formation_pos_counts.get(pos, 0)
        if count >= 3:
            return 6   # 3 slots in XI → max 6 total
        if count == 2:
            return 5   # 2 slots in XI → max 5 total
        return 3       # 0–1 slots in XI → max 3 total

    FOREIGN_XI_BENCH_LIMIT = 9

    # --- helpers for cover scoring ---
    def _cover_score(player: dict, pos: str) -> float:
        pos = (pos or "").upper()
        if not pos:
            return 0.0
        return combined_ip_oop_for_pos(player, pos)

    def _cover_pos_for_formation(p: dict) -> str | None:
        """
        Formation-aware cover position:
        - For locked formations: best among positions that exist in that shape.
        """
        pos = best_cover_pos_for_formation(p, formation_mode)
        if not pos:
            pos = best_ip_position(p)
        return pos

    # =========================================================
    # BENCH
    # =========================================================
    bench_indices: list[int] = []
    bench_pos_counts = Counter()
    squad_pos_counts = Counter(xi_cover_counts)
    # remember which position each bench player is actually covering
    bench_cover_choice: dict[int, str] = {}

    # foreigners already in XI
    foreign_players_set = set(
        idx
        for idx in final_xi_indices
        if not is_domestic(players[idx].get("nationality", ""), club_country)
    )

    # Candidates pool: not XI, not injured, not out on loan
    bench_pool = [
        i
        for i in available_indices
        if i not in final_xi_indices
        and not players[i].get("injured")
        and players[i].get("availability", "Available") != "Out on loan"
    ]

    def _bench_score_for_pos(idx: int, pos: str) -> float:
        """Score this specific player *in this specific position*."""
        p = players[idx]
        return _cover_score(p, pos)

    def _pick_best_for_pos(pos: str) -> int | None:
        """
        Choose the best bench player to cover a *given* position, even if
        that is not his absolute best role, while respecting:
          - foreigner limit (XI+Bench <= 9)
          - squad position caps
        Returns the player index or None if nobody fits.
        """
        pos_u = (pos or "").upper()
        best_idx: int | None = None
        best_score = 0.0
        best_tiebreak: tuple[int, int, int] | None = None

        for idx in bench_pool:
            if idx in bench_indices:
                continue

            p = players[idx]
            score = _bench_score_for_pos(idx, pos_u)
            if score <= 0:
                continue

            is_foreign = not is_domestic(p.get("nationality", ""), club_country)

            # foreigner cap for XI+Bench
            if is_foreign and idx not in foreign_players_set:
                if len(foreign_players_set) + 1 > FOREIGN_XI_BENCH_LIMIT:
                    continue

            # global squad cap for that position
            if squad_pos_counts[pos_u] >= _squad_cap_for_pos(pos_u):
                continue

            tb = potential_tiebreak_tuple(p)

            if (
                best_idx is None
                or score > best_score + 1e-6
                or (abs(score - best_score) <= 1e-6 and tb < (best_tiebreak or (999, 999, 999)))
            ):
                best_idx = idx
                best_score = score
                best_tiebreak = tb

        return best_idx

    def _add_to_bench(idx: int, pos: str):
        """Register a player as bench cover for pos."""
        nonlocal bench_indices, bench_pos_counts, squad_pos_counts, foreign_players_set, bench_cover_choice
        pos_u = (pos or "").upper()
        bench_indices.append(idx)
        bench_pos_counts[pos_u] += 1
        squad_pos_counts[pos_u] += 1
        # remember the exact cover position used in the bench logic
        bench_cover_choice[idx] = pos_u

        p = players[idx]
        if not is_domestic(p.get("nationality", ""), club_country):
            foreign_players_set.add(idx)

    # All positions used in XI (IP)
    single_positions = sorted(
        [p for p in formation_pos_counts.keys() if p in POSITION_CHOICES],
        key=position_sort_key,
    )

    # 1) ensure a bench GK cover if possible (real GK rating, not "best overall")
    gk_idx = _pick_best_for_pos("GK")
    if gk_idx is not None and len(bench_indices) < 10:
        _add_to_bench(gk_idx, "GK")

    # 2) ensure *one* bench cover for each XI position (except GK, already handled)
    for pos in single_positions:
        if pos == "GK":
            continue
        if len(bench_indices) >= 10:
            break
        if bench_pos_counts[pos] >= 1:
            continue

        idx = _pick_best_for_pos(pos)
        if idx is not None:
            _add_to_bench(idx, pos)

    # 3) remaining bench spots: best overall cover (combined IP+OOP for their best position),
    #    allowing extra for positions with 2+ slots in XI (CB/ST etc.)
    bench_candidates: list[tuple[int, str, float, bool]] = []
    for idx in bench_pool:
        if idx in bench_indices:
            continue
        p = players[idx]
        cover_pos = _cover_pos_for_formation(p)
        if not cover_pos:
            continue
        cover_pos = cover_pos.upper()
        score = _cover_score(p, cover_pos)
        if score <= 0:
            continue
        is_foreign = not is_domestic(p.get("nationality", ""), club_country)
        bench_candidates.append((idx, cover_pos, score, is_foreign))

    bench_candidates.sort(
        key=lambda t: (
            -t[2],
            *potential_tiebreak_tuple(players[t[0]]),
        )
    )

    for idx, pos, score, is_foreign in bench_candidates:
        if len(bench_indices) >= 10:
            break
        pos_u = pos.upper()

        # foreigner cap XI+Bench
        if is_foreign and idx not in foreign_players_set:
            if len(foreign_players_set) + 1 > FOREIGN_XI_BENCH_LIMIT:
                continue

        # position caps (now allow second CB/ST etc. via _bench_cap_for_pos)
        if bench_pos_counts[pos_u] >= _bench_cap_for_pos(pos_u):
            continue
        if squad_pos_counts[pos_u] >= _squad_cap_for_pos(pos_u):
            continue

        _add_to_bench(idx, pos_u)

    # assign bench roles & cover positions
    for idx in bench_indices:
        p = players[idx]
        p["squad_role"] = "Bench"
        # Prefer the exact cover position we picked in the bench builder
        cover_pos = bench_cover_choice.get(idx) or _cover_pos_for_formation(p)
        p["bench_cover_pos"] = (cover_pos or "").upper()

    # =========================================================
    # RESERVES
    # =========================================================
    reserve_indices: list[int] = []
    reserve_pos_counts = Counter()

    reserve_pool_all = [
        i
        for i in available_indices
        if i not in final_xi_indices
        and i not in bench_indices
        and players[i].get("availability", "Available") != "Out on loan"
    ]

    injured_pool = [i for i in reserve_pool_all if players[i].get("injured")]
    healthy_pool = [i for i in reserve_pool_all if not players[i].get("injured")]

    # base global coverage for reserves: XI + Bench
    squad_pos_counts_res = Counter(xi_cover_counts)
    for idx in bench_indices:
        p = players[idx]
        pos = (p.get("bench_cover_pos") or "").upper()
        if pos:
            squad_pos_counts_res[pos] += 1

    # 1) add all injured as reserves first (can overflow caps)
    for idx in injured_pool:
        p = players[idx]
        cover_pos = _cover_pos_for_formation(p)
        pos = (cover_pos or "").upper()
        reserve_indices.append(idx)
        if pos:
            reserve_pos_counts[pos] += 1
            squad_pos_counts_res[pos] += 1

    # 2) healthy reserve candidates with caps
    reserve_candidates: list[tuple[int, str, float]] = []
    for idx in healthy_pool:
        p = players[idx]
        cover_pos = _cover_pos_for_formation(p)
        if not cover_pos:
            continue
        pos = cover_pos.upper()
        score = _cover_score(p, pos)
        if score <= 0:
            continue
        reserve_candidates.append((idx, pos, score))

    reserve_candidates.sort(
        key=lambda t: (
            -t[2],
            *potential_tiebreak_tuple(players[t[0]]),
        )
    )

    for idx, _, _ in reserve_candidates:
        if len(reserve_indices) >= 12:
            break

        p = players[idx]

        # Determine cover_pos
        cover_pos = _cover_pos_for_formation(p)

        # If still nothing AND player is GK, force GK
        if not cover_pos:
            if single_pos_rating(p, "GK") > 0 or single_pos_rating_oop(p, "GK") > 0:
                cover_pos = "GK"

        # Still nothing? Skip this player entirely
        if not cover_pos:
            continue

        pos = cover_pos.upper()
        score = _cover_score(p, pos)

        # Respect squad caps (GK included)
        if squad_pos_counts_res[pos] >= _squad_cap_for_pos(pos):
            continue

        reserve_indices.append(idx)
        reserve_pos_counts[pos] += 1
        squad_pos_counts_res[pos] += 1

        # Assign reserve cover pos
        p["reserve_cover_pos"] = pos

    # assign reserve roles & cover positions
    for idx in reserve_indices:
        p = players[idx]
        p["squad_role"] = "Reserve"
        cover_pos = _cover_pos_for_formation(p)
        p["reserve_cover_pos"] = (cover_pos or "").upper()

    # --- Ensure bench has 10 players: promote best non-injured reserve(s) ---
    if len(bench_indices) < 10:
        # Only non-injured reserves can be promoted
        promo_candidates = [idx for idx in reserve_indices if not players[idx].get("injured")]

        # Sort same style: best IP rating, then potential, then age
        promo_candidates.sort(
            key=lambda idx: (
                -best_ip_rating(players[idx]),
                *potential_tiebreak_tuple(players[idx]),
            )
        )

        # Promote until bench reaches 10 or we run out of candidates
        while len(bench_indices) < 10 and promo_candidates:
            to_promote = promo_candidates.pop(0)
            reserve_indices.remove(to_promote)

            p = players[to_promote]
            # Change role to Bench
            p["squad_role"] = "Bench"
            # Clear any previous reserve cover
            p["reserve_cover_pos"] = None
            # As requested: promoted player shows no cover position on bench
            p["bench_cover_pos"] = ""

            bench_indices.append(to_promote)

    # foreigners in XI+Bench (unique) AFTER promotion
    foreign_xi_bench = 0
    for idx in set(final_xi_indices + bench_indices):
        if not is_domestic(players[idx].get("nationality", ""), club_country):
            foreign_xi_bench += 1

    # =========================================================
    # RULE TRACKER
    # =========================================================
    rules_tracker = {
        "foreign_xi": foreign_xi_final,
        "foreign_xi_limit": 7,
        "foreign_xi_bench": foreign_xi_bench,
        "foreign_xi_bench_limit": FOREIGN_XI_BENCH_LIMIT,
        "u23_domestic_xi": u23_domestic_xi_final,
        "u23_domestic_xi_min": 1,
        "xi_size": len(final_xi_indices),
        "bench_size": len(bench_indices),
        "reserves_size": len(reserve_indices),
        "total_selected": len(final_xi_indices) + len(bench_indices) + len(reserve_indices),
    }

    return bench_indices, reserve_indices, rules_tracker

def _preview_locked_squad(
    club_country: str,
    formation_mode: str,
) -> tuple[set[int], set[int], set[int]]:
    """
    Compute which players would be in XI, Bench and Reserves for a given locked
    formation (4-2-3-1 or 5-2-1-2), WITHOUT mutating st.session_state.players.

    Returns (xi_set, bench_set, reserve_set) with indices into st.session_state.players.
    """
    players_master = st.session_state.players or []
    if not players_master:
        return set(), set(), set()

    # Only consider players not out on loan
    available_indices = [
        i
        for i, p in enumerate(players_master)
        if p.get("availability", "Available") != "Out on loan"
    ]
    if not available_indices:
        return set(), set(), set()

    # Local copy of players so we can freely mutate roles/positions
    players = [dict(p) for p in players_master]

    # Define slot templates per formation (must match locked XI logic)
    if formation_mode == "4-2-3-1":
        slot_defs = [
            {"ip": "GK",  "oop": "GK"},
            {"ip": "LB",  "oop": "LB"},
            {"ip": "CB",  "oop": "CB"},
            {"ip": "CB",  "oop": "CB"},
            {"ip": "RB",  "oop": "RB"},
            {"ip": "CDM", "oop": "CDM"},
            {"ip": "CM",  "oop": "CDM"},
            {"ip": "CAM", "oop": "CM"},
            {"ip": "LW",  "oop": "LM"},
            {"ip": "RW",  "oop": "RM"},
            {"ip": "ST",  "oop": "ST"},
        ]
    elif formation_mode == "5-2-1-2":
        slot_defs = [
            {"ip": "GK",  "oop": "GK"},
            {"ip": "LWB", "oop": "LWB"},
            {"ip": "CB",  "oop": "CB"},
            {"ip": "CB",  "oop": "CB"},
            {"ip": "RWB", "oop": "CB"},
            {"ip": "CDM", "oop": "RWB"},
            {"ip": "CM",  "oop": "CDM"},
            {"ip": "CM",  "oop": "CDM"},
            {"ip": "CAM", "oop": "CAM"},
            {"ip": "ST",  "oop": "ST"},
            {"ip": "ST",  "oop": "ST"},
        ]
    else:
        # Not a locked formation → nothing to preview
        return set(), set(), set()

    num_slots = len(slot_defs)

    # Precompute candidates per slot: (player_idx, ip, oop, combined, is_foreign, is_u23_dom)
    slot_candidates: list[list[tuple[int, float, float, float, bool, bool]]] = []
    slot_max_scores: list[float] = []

    for slot in slot_defs:
        ip_pos = slot["ip"]
        oop_pos = slot["oop"]
        cand_list: list[tuple[int, float, float, float, bool, bool]] = []
        max_score = 0.0

        for idx in available_indices:
            p = players[idx]
            if p.get("injured"):
                continue

            ip_score = single_pos_rating(p, ip_pos)
            oop_score = single_pos_rating_oop(p, oop_pos)

            # Locked formations: must have real IP *and* OOP rating in this slot
            if ip_score <= 0 or oop_score <= 0:
                continue

            combined = (ip_score + oop_score) / 2.0

            foreign = not is_domestic(p.get("nationality", ""), club_country)
            u23_dom = is_under23_domestic(p, club_country)

            cand_list.append((idx, ip_score, oop_score, combined, foreign, u23_dom))
            if combined > max_score:
                max_score = combined

        # Sort by combined rating desc, then potential (band/league) and age
        cand_list.sort(
            key=lambda t: (
                -t[3],  # combined score (IP+OOP)/2
                *potential_tiebreak_tuple(players[t[0]]),
            )
        )
        slot_candidates.append(cand_list)
        slot_max_scores.append(max_score)

    # DFS to pick the best XI respecting foreign/U23 constraints
    best_total = -1.0
    best_total_ip = 0.0
    best_total_oop = 0.0
    best_assign: list[dict] = []

    current_assign: list[dict] = []
    used_players: set[int] = set()

    def dfs(
        slot_idx: int,
        current_total: float,
        current_ip_total: float,
        current_oop_total: float,
        foreign_count: int,
        u23_dom_count: int,
    ):
        nonlocal best_total, best_total_ip, best_total_oop, best_assign

        # Upper bound pruning
        remaining_max = sum(slot_max_scores[slot_idx:])
        if current_total + remaining_max <= best_total + 1e-6:
            return

        if slot_idx >= num_slots:
            # Check constraints once XI is full
            if foreign_count > 7:
                return
            if u23_dom_count < 1:
                return
            if current_total > best_total + 1e-6:
                best_total = current_total
                best_total_ip = current_ip_total
                best_total_oop = current_oop_total
                best_assign = [dict(a) for a in current_assign]
            return

        # Try each candidate for this slot
        for (
            player_idx,
            ip_score,
            oop_score,
            combined,
            is_foreign,
            is_u23_dom,
        ) in slot_candidates[slot_idx]:
            if player_idx in used_players:
                continue

            new_foreign = foreign_count + (1 if is_foreign else 0)
            if new_foreign > 7:
                continue

            new_u23 = u23_dom_count + (1 if is_u23_dom else 0)

            used_players.add(player_idx)
            current_assign.append(
                {
                    "slot_idx": slot_idx,
                    "player_idx": player_idx,
                    "ip_score": ip_score,
                    "oop_score": oop_score,
                    "combined": combined,
                }
            )

            dfs(
                slot_idx + 1,
                current_total + combined,
                current_ip_total + ip_score,
                current_oop_total + oop_score,
                new_foreign,
                new_u23,
            )

            current_assign.pop()
            used_players.remove(player_idx)

    dfs(
        slot_idx=0,
        current_total=0.0,
        current_ip_total=0.0,
        current_oop_total=0.0,
        foreign_count=0,
        u23_dom_count=0,
    )

    # No valid XI for this formation → no one is "currently used" here
    if best_total < 0 or not best_assign:
        return set(), set(), set()

    # Build XI from best assignment (local only)
    final_xi_indices: list[int] = []
    assignment_ip: dict[int, str] = {}
    assignment_oop: dict[int, str] = {}

    for a in best_assign:
        slot_idx = a["slot_idx"]
        player_idx = a["player_idx"]
        ip_pos = slot_defs[slot_idx]["ip"]
        oop_pos = slot_defs[slot_idx]["oop"]

        final_xi_indices.append(player_idx)
        assignment_ip[player_idx] = ip_pos
        assignment_oop[player_idx] = oop_pos

    # Ensure exactly one player per slot, no duplicates
    final_xi_indices = list(dict.fromkeys(final_xi_indices))
    if len(final_xi_indices) != num_slots:
        # Safety: treat as no valid XI
        return set(), set(), set()

    # Clear roles on local copy
    for p in players:
        p["assigned_position_ip"] = None
        p["assigned_position_oop"] = None
        p["squad_role"] = "Unselected"
        p.pop("bench_cover_pos", None)
        p.pop("reserve_cover_pos", None)
        p.pop("bench_better_notes", None)

    # Apply XI to local players
    for idx in final_xi_indices:
        p = players[idx]
        p["squad_role"] = "XI"
        p["assigned_position_ip"] = assignment_ip.get(idx)
        p["assigned_position_oop"] = assignment_oop.get(idx) or assignment_ip.get(idx)

    # Build bench & reserves on the local copy using the shared helper.
    bench_indices, reserve_indices, _ = _build_bench_and_reserves(
        players=players,
        available_indices=available_indices,
        final_xi_indices=final_xi_indices,
        club_country=club_country,
        formation_mode=formation_mode,
    )

    return set(final_xi_indices), set(bench_indices), set(reserve_indices)

# =========================
# SIDEBAR: TEAM & LOGO UPLOAD
# =========================

with st.sidebar:
    st.title("FM26 Squad Helper")

    st.subheader("Team setup")

    country_list = ["Indonesia"]
    country = st.selectbox(
        "Country",
        options=[""] + country_list,
        format_func=lambda x: x if x else "Select country",
        key="country_select",
    )

    if country:
        leagues = list(FM_STRUCTURE[country].keys())
        league = st.selectbox(
            "League",
            options=[""] + leagues,
            format_func=lambda x: x if x else "Select league",
            key="league_select",
        )
    else:
        league = ""

    team_name = ""
    if country and league:
        teams_in_league = FM_STRUCTURE[country][league]
        team_options = [""] + [CUSTOM_TEAM_LABEL] + teams_in_league
        team_choice = st.selectbox(
            "Team",
            options=team_options,
            format_func=lambda x: "Select team" if x == "" else x,
            key="team_select",
        )
        if team_choice == CUSTOM_TEAM_LABEL:
            team_name = st.text_input("Custom club name", key="team_custom_name").strip()
        elif team_choice:
            team_name = team_choice
        else:
            team_name = ""
    else:
        st.text_input("Custom club name", key="team_custom_name", value="", disabled=True)

    st.subheader("Club logo")
    logo_file = st.file_uploader(
        "PNG file",
        type=["png"],
        key="club_logo_upload",
    )
    if logo_file is not None:
        st.session_state.club_logo_bytes = logo_file.read()

# Auto-recompute XI / bench / reserves when team & players exist
if st.session_state.players and country:
    recompute_squad_assignments(country)

# =========================
# LOGOS (TOP RIGHT, NORMAL FLOW)
# =========================

club_data_uri = bytes_to_data_uri(st.session_state.club_logo_bytes)
flag_url = get_flag_url(st.session_state.get("country_select", ""))
league_logo_url = get_league_logo_url(
    st.session_state.get("country_select", ""),
    st.session_state.get("league_select", ""),
)

logos_html_parts = []
if flag_url:
    logos_html_parts.append(f'<img src="{flag_url}" alt="Flag" />')
if league_logo_url:
    logos_html_parts.append(f'<img src="{league_logo_url}" alt="League" />')
if club_data_uri:
    logos_html_parts.append(f'<img src="{club_data_uri}" alt="Club" />')
logos_html = "".join(logos_html_parts)

# =========================
# MAIN HEADER
# =========================

st.markdown(
    f"### Team: {team_name or 'N/A'}  |  Country: {country or 'N/A'}  |  League: {league or 'N/A'}"
)

if logos_html:
    st.markdown(
        """
        <style>
        .fm26-top-right-logos-bar {
            display: flex;
            justify-content: flex-end;
            gap: 4px;
            margin-top: -28px;
            margin-bottom: 8px;
        }
        .fm26-top-right-logos-bar img {
            width: 32px;
            height: auto;
            border-radius: 4px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="fm26-top-right-logos-bar">{logos_html}</div>',
        unsafe_allow_html=True,
    )

st.markdown("---")

# =========================
# MAIN TABS
# =========================

tab_players, tab_xi, tab_overview = st.tabs(
    ["Players", "XI", "Position overview"]
)

# =========================
# TAB 2: PLAYERS
# =========================

with tab_players:
    st.header("Players")

    # Reset kun værdierne, ikke hele editor-UI'en
    if st.session_state.get("reset_player_form"):
        st.session_state.p_name_input = ""
        st.session_state.p_age_input = 20
        st.session_state.p_nat_existing = ""
        st.session_state.p_nat_new = ""
        st.session_state.p_positions = []
        st.session_state.p_current_stars = 2.5
        st.session_state.p_potential_stars = 3.0
        st.session_state.p_availability = "Available"
        st.session_state.p_list_status = "None"
        st.session_state.p_injured = False
        for pos in POSITION_CHOICES:
            st.session_state.pop(f"rating_ip_{pos}", None)
            st.session_state.pop(f"rating_oop_{pos}", None)
        st.session_state.reset_player_form = False

    # *** HERFRA er editor-UI altid synlig ***
    existing_names = [p["name"] for p in st.session_state.players]
    edit_col1, edit_col2 = st.columns([3, 1])
    with edit_col1:
        player_to_edit = st.selectbox(
            "Select player to edit (optional)",
            [""] + existing_names,
            format_func=lambda x: x if x else "Add new",
            key="edit_select",
        )
    with edit_col2:
        if st.button("Load player into editor"):
            if player_to_edit:
                for p in st.session_state.players:
                    if p["name"] == player_to_edit:
                        st.session_state.p_name_input = p.get("name", "")
                        st.session_state.p_age_input = p.get("age", 20)
                        nat = p.get("nationality", "")
                        if nat in st.session_state.known_nationalities:
                            st.session_state.p_nat_existing = nat
                            st.session_state.p_nat_new = ""
                        else:
                            st.session_state.p_nat_existing = ""
                            st.session_state.p_nat_new = nat
                        st.session_state.p_positions = p.get("positions", [])
                        st.session_state.p_current_stars = float(p.get("current_stars", 2.5) or 2.5)
                        st.session_state.p_potential_stars = float(p.get("potential_stars", 3.0) or 3.0)

                        st.session_state.p_availability = p.get(
                            "availability", "Available"
                        )
                        st.session_state.p_list_status = p.get(
                            "list_status", "None"
                        )
                        st.session_state.p_injured = p.get("injured", False)
                        for pos in POSITION_CHOICES:
                            key_ip = f"rating_ip_{pos}"
                            key_oop = f"rating_oop_{pos}"
                            if "position_ratings" in p and pos in p["position_ratings"]:
                                st.session_state[key_ip] = float(
                                    p["position_ratings"][pos]
                                )
                            if (
                                "position_ratings_oop" in p
                                and pos in p["position_ratings_oop"]
                            ):
                                st.session_state[key_oop] = float(
                                    p["position_ratings_oop"][pos]
                                )
                        break

    st.markdown("#### Add / update player")

    c1, c2 = st.columns(2)

    st.session_state.setdefault("p_name_input", "")
    st.session_state.setdefault("p_age_input", 20)
    st.session_state.setdefault("p_nat_existing", "")
    st.session_state.setdefault("p_nat_new", "")
    st.session_state.setdefault("p_current_stars", 2.5)
    st.session_state.setdefault("p_potential_stars", 3.0)
    st.session_state.setdefault("p_positions", [])
    st.session_state.setdefault("p_availability", "Available")
    st.session_state.setdefault("p_list_status", "None")
    st.session_state.setdefault("p_injured", False)

    with c1:
        p_name = st.text_input("Name", key="p_name_input")
        p_age = st.number_input(
            "Age", min_value=15, max_value=50, key="p_age_input"
        )

        nat_options = [""] + sorted(set(st.session_state.known_nationalities))
        existing_nat = st.selectbox(
            "Existing nationality",
            nat_options,
            format_func=lambda x: x if x else "None / type new",
            key="p_nat_existing",
        )
        new_nat = st.text_input(
            "New nationality (optional)",
            key="p_nat_new",
        )

    with c2:
        p_positions = st.multiselect(
            "Positions the player can play",
            POSITION_CHOICES,
            key="p_positions",
        )

        row1_col1, row1_col2 = st.columns(2)
        with row1_col1:
            current_stars = st.selectbox(
                "Current (stars)",
                CP_STAR_VALUES,
                format_func=stars_to_label,
                key="p_current_stars",
            )
        with row1_col2:
            potential_stars = st.selectbox(
                "Potential (stars)",
                CP_STAR_VALUES,
                format_func=stars_to_label,
                key="p_potential_stars",
            )

        row3_col1, row3_col2 = st.columns(2)
        with row3_col1:
            p_availability = st.selectbox(
                "Availability",
                ["Available", "Out on loan"],
                key="p_availability",
            )
        with row3_col2:
            p_list_status = st.selectbox(
                "List status",
                ["None", "Loan list", "Transfer list"],
                key="p_list_status",
            )
        p_injured = st.checkbox(
            "Injured",
            key="p_injured",
        )

    st.markdown("#### Position ratings")
    rating_cols = st.columns(3)
    position_ratings_ip: dict[str, float] = {}
    position_ratings_oop: dict[str, float] = {}

    # One star selector per *selected* position
    for idx, pos in enumerate(p_positions):
        col = rating_cols[idx % 3]
        key_ip = f"rating_ip_{pos}"
        key_oop = f"rating_oop_{pos}"

        if key_ip not in st.session_state:
            st.session_state[key_ip] = 0.0
        if key_oop not in st.session_state:
            st.session_state[key_oop] = 0.0

        with col:
            st.markdown(f"**{pos}**")
            val_ip = st.selectbox(
                "In possession",
                STAR_VALUES,
                format_func=stars_to_label,
                key=key_ip,
            )
            val_oop = st.selectbox(
                "Out of possession",
                STAR_VALUES,
                format_func=stars_to_label,
                key=key_oop,
            )

            position_ratings_ip[pos] = float(val_ip)
            position_ratings_oop[pos] = float(val_oop)

    save_col, delete_col = st.columns(2)

    with save_col:
        if st.button("Save player"):
            if not p_name.strip():
                st.warning("Player needs a name.")
            else:
                nat_final = new_nat.strip() if new_nat.strip() else existing_nat.strip()
                if nat_final and nat_final not in st.session_state.known_nationalities:
                    st.session_state.known_nationalities.append(nat_final)

                player = {
                    "name": p_name.strip(),
                    "age": int(p_age),
                    "nationality": nat_final,
                    "positions": p_positions or [],
                    "position_ratings": position_ratings_ip,        # IP
                    "position_ratings_oop": position_ratings_oop,  # OOP
                    "current_stars": float(st.session_state.get("p_current_stars", 2.5) or 2.5),
                    "potential_stars": float(st.session_state.get("p_potential_stars", 3.0) or 3.0),
                    "availability": p_availability,
                    "list_status": p_list_status,
                    "injured": bool(st.session_state.get("p_injured", False)),
                }

                add_or_update_player(player)
                if country:
                    recompute_squad_assignments(country)
                st.success(f"Saved player {p_name}")

                # mark for reset on next run
                st.session_state.reset_player_form = True
                st.rerun()

    with delete_col:
        if player_to_edit and st.button("Delete player"):
            st.session_state.players = [
                p for p in st.session_state.players if p["name"] != player_to_edit
            ]
            if country:
                recompute_squad_assignments(country)
            st.session_state.reset_player_form = True
            st.success(f"Deleted player {player_to_edit}")

    if not st.session_state.players:
        st.info("No players yet.")
    else:

        st.markdown("### Quick edit (fast rating updates)")

        # Build editor table (use dataframe index as player index, so no _idx column)
        quick_rows = []
        for i, p in enumerate(st.session_state.players):
            row = {
                "Name": p.get("name", ""),
                "Age": int(p.get("age", 20) or 20),
                "Nationality": p.get("nationality", ""),
                "Current⭐": float(p.get("current_stars", 2.5) or 2.5),
                "Potential⭐": float(p.get("potential_stars", 3.0) or 3.0),
                "Injured": bool(p.get("injured", False)),
                "Availability": p.get("availability", "Available"),
                "List": p.get("list_status", "None"),
            }

            # Add one column per position for IP and OOP rating (0.0 = cannot play)
            pr_ip = p.get("position_ratings") or {}
            pr_oop = p.get("position_ratings_oop") or {}

            for pos in POSITION_CHOICES:
                row[f"IP {pos}"] = float(pr_ip.get(pos, 0.0) or 0.0)
                row[f"OOP {pos}"] = float(pr_oop.get(pos, 0.0) or 0.0)

            quick_rows.append(row)

        df_quick = pd.DataFrame(quick_rows)
        df_quick.index = range(len(df_quick))  # stable mapping to st.session_state.players

        # Column configs
        col_cfg = {
            "Current⭐": st.column_config.SelectboxColumn(
                "Current⭐",
                options=CP_STAR_VALUES,
                format_func=stars_to_label,
            ),
            "Potential⭐": st.column_config.SelectboxColumn(
                "Potential⭐",
                options=CP_STAR_VALUES,
                format_func=stars_to_label,
            ),
            "Availability": st.column_config.SelectboxColumn(
                "Availability",
                options=["Available", "Out on loan"],
            ),
            "List": st.column_config.SelectboxColumn(
                "List",
                options=["None", "Loan list", "Transfer list"],
            ),
        }

        # Position star options (0.0–5.0, including 0.0 as "can't play")
        for pos in POSITION_CHOICES:
            col_cfg[f"IP {pos}"] = st.column_config.SelectboxColumn(
                f"IP {pos}",
                options=STAR_VALUES,
                format_func=stars_to_label,
            )
            col_cfg[f"OOP {pos}"] = st.column_config.SelectboxColumn(
                f"OOP {pos}",
                options=STAR_VALUES,
                format_func=stars_to_label,
            )

        edited = st.data_editor(
            df_quick,
            use_container_width=True,
            hide_index=True,  # no index column shown
            column_config=col_cfg,
            disabled=["Name", "Nationality"],
            key="players_quick_edit_table",
        )

        if st.button("Apply quick edits", key="apply_quick_edits"):
            # Apply back to players using dataframe index
            for idx, row in edited.iterrows():
                i = int(idx)
                if i < 0 or i >= len(st.session_state.players):
                    continue

                p = st.session_state.players[i]

                p["age"] = int(row["Age"])
                p["current_stars"] = float(row["Current⭐"])
                p["potential_stars"] = float(row["Potential⭐"])
                p["injured"] = bool(row["Injured"])
                p["availability"] = row["Availability"]
                p["list_status"] = row["List"]

                # Rebuild position ratings from table
                new_ip = {}
                new_oop = {}

                for pos in POSITION_CHOICES:
                    v_ip = float(row[f"IP {pos}"] or 0.0)
                    v_oop = float(row[f"OOP {pos}"] or 0.0)

                    if v_ip > 0:
                        new_ip[pos] = v_ip
                    if v_oop > 0:
                        new_oop[pos] = v_oop

                p["position_ratings"] = new_ip
                p["position_ratings_oop"] = new_oop

                # Update "positions" list to reflect anything playable in IP or OOP
                playable = [
                    pos for pos in POSITION_CHOICES
                    if new_ip.get(pos, 0) > 0 or new_oop.get(pos, 0) > 0
                ]
                p["positions"] = playable

            if country:
                recompute_squad_assignments(country)
            st.success("Quick edits applied.")
            st.rerun()

# =========================
# TAB 3: POSITION OVERVIEW
# =========================

def describe_xi_variant(idx: int) -> str:
    """
    Turn a variant index into a readable label, including IP+OOP averages and
    which players / formations change vs baseline (IP only, OOP only, or both).
    """
    variants = st.session_state.get("xi_variants") or []
    players = st.session_state.players

    if not variants or idx < 0 or idx >= len(variants):
        return f"XI {idx + 1}"

    base = variants[0]
    cur = variants[idx]

    base_xi = set(base.get("xi_indices") or [])
    cur_xi = set(cur.get("xi_indices") or [])

    # IP/OOP averages for this variant
    n = len(cur.get("xi_indices") or [])
    ip_total = float(cur.get("total_ip", 0.0))
    oop_total = float(cur.get("total_oop", 0.0))
    ip_avg = ip_total / n if n else 0.0
    oop_avg = oop_total / n if n else 0.0

    base_ip = base.get("assignment_ip", {}) or {}
    base_oop = base.get("assignment_oop", {}) or {}
    cur_ip = cur.get("assignment_ip", {}) or {}
    cur_oop = cur.get("assignment_oop", {}) or {}

    out_players = base_xi - cur_xi
    in_players = cur_xi - base_xi
    shared = base_xi & cur_xi

    changes: list[str] = []

    # OUT / IN (player swaps)
    for i in sorted(out_players):
        name = players[i].get("name", f"#{i}")
        changes.append(f"{name} OUT")

    for i in sorted(in_players):
        name = players[i].get("name", f"#{i}")
        changes.append(f"{name} IN")

    # Position changes for players that are in both XIs
    for i in sorted(shared):
        name = players[i].get("name", f"#{i}")

        ip_before = base_ip.get(i)
        ip_after = cur_ip.get(i)
        oop_before = base_oop.get(i)
        oop_after = cur_oop.get(i)

        ip_changed = bool(ip_before and ip_after and ip_before != ip_after)
        oop_changed = bool(oop_before and oop_after and oop_before != oop_after)

        if ip_changed and oop_changed:
            changes.append(
                f"{name}: IP {ip_before}→{ip_after}, OOP {oop_before}→{oop_after}"
            )
        elif ip_changed:
            changes.append(f"{name}: IP {ip_before}→{ip_after}")
        elif oop_changed:
            changes.append(f"{name}: OOP {oop_before}→{oop_after}")

    # Er det samme XI-spillere eller rigtige swaps?
    same_xi = (base_xi == cur_xi)

    if idx == 0:
        label_prefix = "XI 1 (baseline)"
    else:
        # Brug dansk label, som du bad om
        label_prefix = f"XI {idx + 1} ({'Per spiller' if same_xi else 'Swap'})"

    rating_part = f"[IP {ip_avg:.2f}⭐ | OOP {oop_avg:.2f}⭐]"

    if not changes:
        return f"{label_prefix} {rating_part}"

    summary = "; ".join(changes[:3])
    if len(changes) > 3:
        summary += "; ..."
    return f"{label_prefix} {rating_part} – {summary}"

with tab_xi:
    st.header("XI")

    if not st.session_state.players:
        st.warning("Add players first.")
    else:
        formations = st.session_state.get("formations", {}) or {}

        formation_options = list(formations.keys())
        if not formation_options:
            formation_options = ["4-2-3-1"]

        current_formation = st.session_state.get("formation_mode", formation_options[0])
        if current_formation not in formation_options:
            current_formation = formation_options[0]

        # Apply deferred formation change BEFORE the widget is instantiated
        pending = st.session_state.pop("_pending_formation_mode", None)
        if pending and pending in formation_options:
            current_formation = pending

        formation_choice = st.radio(
            "Formation",
            options=formation_options,
            index=formation_options.index(current_formation),
            horizontal=True,
            key="formation_mode",
        )

        st.markdown("---")
        st.subheader("Formation manager")

        formations = st.session_state.get("formations", {}) or {}

        with st.expander("Add / remove formations", expanded=False):
            if formations:
                st.markdown("**Existing formations**")
                for fname in list(formations.keys()):
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.markdown(f"- **{fname}**")
                    with cols[1]:
                        if st.button("Delete", key=f"del_form_{fname}"):
                            formations.pop(fname, None)
                            st.session_state.formations = formations
                            if st.session_state.get("formation_mode") == fname:
                                st.session_state["_pending_formation_mode"] = (list(formations.keys())[:1] or ["4-2-3-1"])[0]
                            if country:
                                recompute_squad_assignments(country)
                            st.rerun()
            else:
                st.caption("No formations yet.")

            st.markdown("#### Create new formation")
            new_name = st.text_input("Formation name", key="new_form_name").strip()

            st.caption("Pick exactly 11 IP positions and 11 OOP positions. Default max 1 each, but CB/CDM/CAM/ST can be up to 3.")

            new_ip: list[str] = []
            new_oop: list[str] = []

            for i in range(11):
                c_ip, c_oop = st.columns(2)
                with c_ip:
                    pos_ip = st.selectbox(
                        f"Slot {i+1} (IP)",
                        options=[""] + POSITION_CHOICES,
                        index=0,
                        key=f"new_form_ip_{i}",
                    )
                with c_oop:
                    pos_oop = st.selectbox(
                        f"Slot {i+1} (OOP)",
                        options=[""] + POSITION_CHOICES,
                        index=0,
                        key=f"new_form_oop_{i}",
                    )

                new_ip.append((pos_ip or "").upper())
                new_oop.append((pos_oop or "").upper())

            if st.button("Save formation", key="save_new_formation"):
                if not new_name:
                    st.warning("Formation needs a name.")
                elif new_name in formations:
                    st.warning("That formation name already exists.")
                else:
                    clean_ip = [p for p in new_ip if p]
                    clean_oop = [p for p in new_oop if p]
                    ok, msg = validate_formation_positions(clean_ip, clean_oop)
                    if not ok:
                        st.warning(msg)
                    else:
                        formations[new_name] = {"ip": clean_ip, "oop": clean_oop}
                        st.session_state.formations = formations
                        st.session_state["_pending_formation_mode"] = new_name
                        if country:
                            recompute_squad_assignments(country)
                        st.success(f"Saved formation: {new_name}")
                        st.rerun()

        # How many XI variants do we have?
        variant_count = st.session_state.get("xi_variant_count", 0)

        rt = st.session_state.rules_tracker or {}
        foreign_xi = rt.get("foreign_xi", 0)
        foreign_xi_limit = rt.get("foreign_xi_limit", 7)
        foreign_xi_bench = rt.get("foreign_xi_bench", 0)
        foreign_xi_bench_limit = rt.get("foreign_xi_bench_limit", 9)
        u23_domestic_xi = rt.get("u23_domestic_xi", 0)
        u23_domestic_xi_min = rt.get("u23_domestic_xi_min", 1)

        # ========== RULE TRACKER ==========
        st.subheader("Rule tracker")

        c1, c2, c3 = st.columns(3)

        with c1:
            ok = foreign_xi <= foreign_xi_limit
            color = "green" if ok else "red"
            st.markdown(
                f"<span style='color:{color}; font-weight:bold;'>Foreign in XI: "
                f"{foreign_xi}/{foreign_xi_limit}</span>",
                unsafe_allow_html=True,
            )
            st.slider(
                "Foreign in XI",
                min_value=0,
                max_value=foreign_xi_limit,
                value=min(foreign_xi, foreign_xi_limit),
                disabled=True,
                label_visibility="collapsed",
            )

        with c2:
            ok = foreign_xi_bench <= foreign_xi_bench_limit
            color = "green" if ok else "red"
            st.markdown(
                f"<span style='color:{color}; font-weight:bold;'>Foreign in XI+Bench: "
                f"{foreign_xi_bench}/{foreign_xi_bench_limit}</span>",
                unsafe_allow_html=True,
            )
            st.slider(
                "Foreign in XI + Bench",
                min_value=0,
                max_value=foreign_xi_bench_limit,
                value=min(foreign_xi_bench, foreign_xi_bench_limit),
                disabled=True,
                label_visibility="collapsed",
            )

        with c3:
            ok = u23_domestic_xi >= u23_domestic_xi_min
            color = "green" if ok else "red"
            st.markdown(
                f"<span style='color:{color}; font-weight:bold;'>Indonesian U23 in XI: "
                f"{u23_domestic_xi} (min {u23_domestic_xi_min})</span>",
                unsafe_allow_html=True,
            )
            # Show real count out of 11 instead of capping at the minimum
            st.slider(
                "Indonesian U23 in XI",
                min_value=0,
                max_value=11,
                value=min(u23_domestic_xi, 11),
                disabled=True,
                label_visibility="collapsed",
            )

        st.markdown("---")

        # ========== XI TIEBREAKER (POSITION & SWAP PREFERENCES, FULLY GENERIC) ==========
        variants = st.session_state.get("xi_variants") or []
        if variants:
            players = st.session_state.players
            variant_count = len(variants)

            # --- Collect IP and OOP positions per player across all equal-best variants ---
            ip_map: dict[int, set[str]] = {}
            oop_map: dict[int, set[str]] = {}

            for v in variants:
                xi = v.get("xi_indices") or []
                assign_ip = v.get("assignment_ip", {}) or {}
                assign_oop = v.get("assignment_oop", {}) or {}
                for idx in xi:
                    # IP
                    ip_pos = assign_ip.get(idx)
                    if ip_pos:
                        s = ip_map.setdefault(idx, set())
                        s.add(ip_pos)

                    # OOP uses explicit OOP if present, otherwise the IP position
                    oop_pos = assign_oop.get(idx) or assign_ip.get(idx)
                    if oop_pos:
                        s = oop_map.setdefault(idx, set())
                        s.add(oop_pos)

            def _player_name(i: int) -> str:
                return players[i].get("name", f"#{i}")

            # Candidates for position preferences:
            # any player that has >1 IP or >1 OOP position across variants.
            pos_candidates = []
            for idx in set(ip_map.keys()) | set(oop_map.keys()):
                ip_set = ip_map.get(idx, set())
                oop_set = oop_map.get(idx, set())
                multi_ip = len(ip_set) > 1
                multi_oop = len(oop_set) > 1
                if multi_ip or multi_oop:
                    pos_candidates.append(idx)

            pos_candidates.sort(key=_player_name)

            # Hard cap so UI doesn't explode
            MAX_POS_PLAYERS = 8
            pos_candidates = pos_candidates[:MAX_POS_PLAYERS]

            st.subheader("Starting XI tiebreakers")

            # --- Position preferences per player (IP and/or OOP) ---
            ip_preferences: dict[int, str | None] = {}
            oop_preferences: dict[int, str | None] = {}

            if pos_candidates:
                st.markdown("**Position preferences (IP / OOP / both)**")

            for idx in pos_candidates:
                name = _player_name(idx)
                ip_positions = sorted(ip_map.get(idx, set()), key=position_sort_key)
                oop_positions = sorted(oop_map.get(idx, set()), key=position_sort_key)
                multi_ip = len(ip_positions) > 1
                multi_oop = len(oop_positions) > 1

                # Show one line per player, then IP and/or OOP radios as needed
                st.markdown(f"**{name}**")

                # IP preference (if multiple IP positions available)
                if multi_ip:
                    ip_options = ip_positions
                    ip_key = f"xi_pos_pref_ip_{idx}"
                    ip_default = st.session_state.get(ip_key, ip_positions[0])
                    if ip_default not in ip_options:
                        ip_default = ip_positions[0]

                    ip_choice = st.radio(
                        "In possession (IP)",
                        options=ip_options,
                        index=ip_options.index(ip_default),
                        key=ip_key,
                        horizontal=True,
                    )
                    ip_preferences[idx] = ip_choice
                else:
                    ip_preferences[idx] = None

                # OOP preference (if multiple OOP positions available)
                if multi_oop:
                    oop_options = oop_positions
                    oop_key = f"xi_pos_pref_oop_{idx}"
                    oop_default = st.session_state.get(oop_key, oop_positions[0])
                    if oop_default not in oop_options:
                        oop_default = oop_positions[0]

                    oop_choice = st.radio(
                        "Out of possession (OOP)",
                        options=oop_options,
                        index=oop_options.index(oop_default),
                        key=oop_key,
                        horizontal=True,
                    )
                    oop_preferences[idx] = oop_choice
                else:
                    oop_preferences[idx] = None

                st.markdown("")  # tiny spacing between players

            # --- Player swap preferences (1-for-1 and 2-for-2 swaps between any equal-best variants) ---

            # key: (group_a_tuple, group_b_tuple) where each group is 1 or 2 player indices
            swap_group_pairs: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
            seen_pairs: set[tuple[tuple[int, ...], tuple[int, ...]]] = set()

            variant_xis = [set(v.get("xi_indices") or []) for v in variants]

            for i in range(len(variants)):
                xi_a = variant_xis[i]
                for j in range(i + 1, len(variants)):
                    xi_b = variant_xis[j]

                    out_players = xi_a - xi_b
                    in_players = xi_b - xi_a

                    if not out_players or not in_players:
                        continue

                    # Only care about clean 1-for-1 or 2-for-2 swaps
                    if len(out_players) == len(in_players) and len(out_players) in (1, 2):
                        g1 = tuple(sorted(out_players))
                        g2 = tuple(sorted(in_players))

                        # canonical order so (A,B) vs (C,D) matches (C,D) vs (A,B)
                        if g1 < g2:
                            key_pair = (g1, g2)
                        else:
                            key_pair = (g2, g1)

                        if key_pair in seen_pairs:
                            continue
                        seen_pairs.add(key_pair)
                        swap_group_pairs.append(key_pair)

            MAX_SWAP_PAIRS = 12
            swap_group_pairs = swap_group_pairs[:MAX_SWAP_PAIRS]

            swap_preferences: dict[tuple[tuple[int, ...], tuple[int, ...]], int | None] = {}
            if swap_group_pairs:
                st.markdown("**Player swap preferences (1-for-1 & 2-for-2)**")

            for g1, g2 in swap_group_pairs:
                names1 = ", ".join(_player_name(i) for i in g1)
                names2 = ", ".join(_player_name(i) for i in g2)

                opts = [
                    "No preference",
                    f"Prefer {names1} in XI",
                    f"Prefer {names2} in XI",
                ]
                key = f"xi_swap_pref_{'_'.join(map(str, g1))}__{'_'.join(map(str, g2))}"
                default = st.session_state.get(key, "No preference")
                if default not in opts:
                    default = "No preference"

                choice = st.radio(
                    f"{names1} ↔ {names2}",
                    options=opts,
                    index=opts.index(default),
                    key=key,
                    horizontal=False,
                )

                if choice == "No preference":
                    swap_preferences[(g1, g2)] = None
                elif choice.startswith("Prefer") and names1 in choice:
                    swap_preferences[(g1, g2)] = 0  # prefer group g1
                elif choice.startswith("Prefer") and names2 in choice:
                    swap_preferences[(g1, g2)] = 1  # prefer group g2
                else:
                    swap_preferences[(g1, g2)] = None

            # --- Filter variants using active preferences (IP, OOP, and swap groups) ---
            active_ip_prefs = {i: pos for i, pos in ip_preferences.items() if pos}
            active_oop_prefs = {i: pos for i, pos in oop_preferences.items() if pos}
            active_swap_prefs = {
                pair: pref for pair, pref in swap_preferences.items() if pref is not None
            }

            def variant_matches(v: dict) -> bool:
                xi = set(v.get("xi_indices") or [])
                assign_ip = v.get("assignment_ip", {}) or {}
                assign_oop = v.get("assignment_oop", {}) or {}

                # Position prefs: player must be in XI with chosen IP/OOP
                for idx, wanted_ip in active_ip_prefs.items():
                    if idx not in xi:
                        return False
                    if assign_ip.get(idx) != wanted_ip:
                        return False

                for idx, wanted_oop in active_oop_prefs.items():
                    if idx not in xi:
                        return False
                    effective_oop = assign_oop.get(idx) or assign_ip.get(idx)
                    if effective_oop != wanted_oop:
                        return False

                # Swap prefs (1-for-1 or 2-for-2):
                # If you prefer group g1, variant must have all g1 players in XI
                # and none of g2; and vice versa.
                for (g1, g2), pref_side in active_swap_prefs.items():
                    group1 = set(g1)
                    group2 = set(g2)
                    if pref_side == 0:
                        # prefer group1
                        if not group1.issubset(xi):
                            return False
                        if group2 & xi:
                            return False
                    elif pref_side == 1:
                        # prefer group2
                        if not group2.issubset(xi):
                            return False
                        if group1 & xi:
                            return False

                return True

            def _avg_score(v: dict) -> float:
                xi_list = v.get("xi_indices") or []
                n = len(xi_list) or 1
                ip = float(v.get("total_ip", 0.0))
                oop = float(v.get("total_oop", 0.0))
                return (ip + oop) / n

            # Variants that respect all active preferences
            candidate_indices = [
                i for i, v in enumerate(variants) if variant_matches(v)
            ]

            if candidate_indices:
                best_idx = max(candidate_indices, key=lambda i: _avg_score(variants[i]))
            else:
                # No variant can satisfy that combo → fallback to best scoring overall (automatic)
                best_idx = max(range(variant_count), key=lambda i: _avg_score(variants[i]))

            prev_idx = st.session_state.get("xi_variant_choice", 0)
            if (
                not isinstance(prev_idx, int)
                or prev_idx < 0
                or prev_idx >= variant_count
            ):
                prev_idx = 0

            if best_idx != prev_idx and country:
                st.session_state.xi_variant_choice = int(best_idx)
                recompute_squad_assignments(country, force_variant_idx=int(best_idx))

            # Just show what ended up active, NOT a manual picker
            st.caption(
                f"Active XI variant: {describe_xi_variant(st.session_state.xi_variant_choice)}"
            )

        st.markdown("---")

        # ========== STARTING XI FORMATIONS ==========

        xi_players = [
            p for p in st.session_state.players if p.get("squad_role") == "XI"
        ]

        if xi_players:
            # Show XI average stars IP & OOP for the *current* chosen variant
            ip_ratings = []
            oop_ratings = []
            for p in xi_players:
                pos_ip = p.get("assigned_position_ip")
                if pos_ip:
                    ip_ratings.append(single_pos_rating(p, pos_ip))

                pos_oop = (
                    p.get("assigned_position_oop")
                    or p.get("assigned_position_ip")
                    or best_oop_position(p)
                )
                if pos_oop:
                    oop_ratings.append(single_pos_rating_oop(p, pos_oop))

            if ip_ratings:
                ip_avg = sum(ip_ratings) / len(xi_players)
            else:
                ip_avg = 0.0

            if oop_ratings:
                oop_avg = sum(oop_ratings) / len(xi_players)
            else:
                oop_avg = 0.0

            st.markdown(
                f"**Current XI average rating:** "
                f"{ip_avg:.2f}⭐ in possession | {oop_avg:.2f}⭐ out of possession"
            )

            with st.expander("Starting XI – In possession", expanded=True):
                rows_ip = []
                for p in xi_players:
                    pos_ip = p.get("assigned_position_ip")
                    rating_ip = 0.0
                    if pos_ip:
                        rating_ip = single_pos_rating(p, pos_ip)
                    rows_ip.append(
                        {
                            "Name": p.get("name", ""),
                            "Position (IP)": pos_ip or "",
                            "Stars (IP)": stars_to_label(rating_ip),
                            "Potential league level": p.get("potential_level_league", ""),
                            "Potential level": p.get("potential_band", ""),
                            "Nationality": p.get("nationality", ""),
                            "Age": p.get("age", ""),
                        }
                    )

                df_ip = pd.DataFrame(rows_ip)
                if not df_ip.empty:
                    df_ip["__sort_key__"] = df_ip["Position (IP)"].apply(position_sort_key)
                    df_ip = df_ip.sort_values(
                        ["__sort_key__", "Position (IP)", "Name"],
                        kind="mergesort",
                    ).drop(columns=["__sort_key__"])
                st.dataframe(df_ip, use_container_width=True, hide_index=True)

            with st.expander("Starting XI – Out of possession", expanded=True):
                rows_oop = []
                for p in xi_players:
                    pos_oop = (
                        p.get("assigned_position_oop")
                        or p.get("assigned_position_ip")
                        or best_oop_position(p)
                    )
                    rating_oop = 0.0
                    if pos_oop:
                        rating_oop = single_pos_rating_oop(p, pos_oop)
                    rows_oop.append(
                        {
                            "Name": p.get("name", ""),
                            "Position (OOP)": pos_oop or "",
                            "Stars (OOP)": stars_to_label(rating_oop),
                            "Potential league level": p.get("potential_level_league", ""),
                            "Potential level": p.get("potential_band", ""),
                            "Nationality": p.get("nationality", ""),
                            "Age": p.get("age", ""),
                        }
                    )

                df_oop = pd.DataFrame(rows_oop)
                if not df_oop.empty:
                    df_oop["__sort_key__"] = df_oop["Position (OOP)"].apply(position_sort_key)
                    df_oop = df_oop.sort_values(
                        ["__sort_key__", "Position (OOP)", "Name"],
                        kind="mergesort",
                    ).drop(columns=["__sort_key__"])
                st.dataframe(df_oop, use_container_width=True, hide_index=True)

            st.markdown("---")

            # Bench table (same style idea as XI – IP)
            bench_players = [
                p for p in st.session_state.players if p.get("squad_role") == "Bench"
            ]

            with st.expander("Bench", expanded=True):
                if not bench_players:
                    st.info("No bench selected.")
                else:
                    rows_bench = []

                    formation_mode = st.session_state.get("formation_mode", "4-2-3-1")

                    for p in bench_players:
                        cover_pos = p.get("bench_cover_pos")
                        if not cover_pos:
                            cover_pos = best_cover_pos_for_formation(p, formation_mode)
                        if not cover_pos:
                            cover_pos = best_ip_position(p)

                        ip_rating = single_pos_rating(p, cover_pos) if cover_pos else 0.0
                        oop_rating = single_pos_rating_oop(p, cover_pos) if cover_pos else 0.0

                        rows_bench.append(
                            {
                                "Name": p.get("name", ""),
                                "Cover pos": cover_pos or "",
                                "IP": stars_to_label(ip_rating),
                                "OOP": stars_to_label(oop_rating),
                                "Potential league level": p.get("potential_level_league", ""),
                                "Potential level": p.get("potential_band", ""),
                                "Nationality": p.get("nationality", ""),
                                "Age": p.get("age", ""),
                                "Note": p.get("bench_better_notes", ""),
                                "__stars_numeric__": ip_rating,
                            }
                        )

                    df_bench = pd.DataFrame(rows_bench)
                    if not df_bench.empty:
                        df_bench["__pos_order__"] = df_bench["Cover pos"].apply(
                            position_sort_key
                        )
                        df_bench["__league_rank__"] = df_bench["Potential league level"].map(
                            POTENTIAL_LEAGUE_SORT
                        ).fillna(len(POTENTIAL_LEAGUE_SORT))
                        df_bench["__band_rank__"] = df_bench["Potential level"].map(
                            POTENTIAL_BAND_SORT
                        ).fillna(len(POTENTIAL_BAND_SORT))

                        df_bench = df_bench.sort_values(
                            [
                                "__pos_order__",
                                "Cover pos",
                                "__stars_numeric__",
                                "__league_rank__",
                                "__band_rank__",
                                "Age",
                                "Name",
                            ],
                            ascending=[True, True, False, True, True, True, True],
                            kind="mergesort",
                        ).drop(
                            columns=[
                                "__stars_numeric__",
                                "__league_rank__",
                                "__band_rank__",
                                "__pos_order__",
                            ]
                        )

                    st.dataframe(df_bench, use_container_width=True, hide_index=True)

            reserve_players = [
                p for p in st.session_state.players if p.get("squad_role") == "Reserve"
            ]

            reserve_players = [
                p for p in st.session_state.players if p.get("squad_role") == "Reserve"
            ]

            with st.expander("Reserves", expanded=False):
                if not reserve_players:
                    st.info("No reserves selected.")
                else:
                    rows_res = []

                    formation_mode = st.session_state.get("formation_mode", "4-2-3-1")

                    for p in reserve_players:
                        cover_pos = p.get("reserve_cover_pos")
                        if not cover_pos:
                            cover_pos = best_cover_pos_for_formation(p, formation_mode)
                        if not cover_pos:
                            cover_pos = best_ip_position(p)

                        ip_rating = single_pos_rating(p, cover_pos) if cover_pos else 0.0
                        oop_rating = single_pos_rating_oop(p, cover_pos) if cover_pos else 0.0

                        rows_res.append(
                            {
                                "Name": p.get("name", ""),
                                "Cover pos": cover_pos or "",
                                "IP": stars_to_label(ip_rating),
                                "OOP": stars_to_label(oop_rating),
                                "Potential league level": p.get("potential_level_league", ""),
                                "Potential level": p.get("potential_band", ""),
                                "Nationality": p.get("nationality", ""),
                                "Age": p.get("age", ""),
                                "__stars_numeric__": ip_rating,
                            }
                        )

                    df_res = pd.DataFrame(rows_res)
                    if not df_res.empty:
                        df_res["__pos_order__"] = df_res["Cover pos"].apply(
                            position_sort_key
                        )
                        df_res["__league_rank__"] = df_res["Potential league level"].map(
                            POTENTIAL_LEAGUE_SORT
                        ).fillna(len(POTENTIAL_LEAGUE_SORT))
                        df_res["__band_rank__"] = df_res["Potential level"].map(
                            POTENTIAL_BAND_SORT
                        ).fillna(len(POTENTIAL_BAND_SORT))

                        df_res = df_res.sort_values(
                            [
                                "__pos_order__",
                                "Cover pos",
                                "__stars_numeric__",
                                "__league_rank__",
                                "__band_rank__",
                                "Age",
                                "Name",
                            ],
                            ascending=[True, True, False, True, True, True, True],
                            kind="mergesort",
                        ).drop(
                            columns=[
                                "__stars_numeric__",
                                "__league_rank__",
                                "__band_rank__",
                                "__pos_order__",
                            ]
                        )

                    st.dataframe(df_res, use_container_width=True, hide_index=True)
    # ========== SURPLUS (UNSELECTED) PLAYERS ==========
    all_players = st.session_state.players

    # ========== INJURY LIST ==========
    all_players = st.session_state.players

    # Only players currently injured and not out on loan
    injured_players = [
        p for p in all_players
        if p.get("injured", False)
        and p.get("availability", "Available") != "Out on loan"
    ]

    st.subheader("Injury list")
    with st.expander("Injured players", expanded=False):

        # --- TABLE of injured players ---
        if not injured_players:
            st.info("No injured players.")
        else:
            rows_inj = []
            for p in injured_players:
                rows_inj.append({
                    "Name": p.get("name", ""),
                    "Positions": ", ".join(p.get("positions") or []),
                    "Age": p.get("age", ""),
                    "Nationality": p.get("nationality", ""),
                    "Availability": p.get("availability", "Available"),
                })
            df_inj = pd.DataFrame(rows_inj)
            st.dataframe(df_inj, use_container_width=True, hide_index=True)
  
            # ---- RECOVER PLAYER ----
            st.markdown("#### Mark player as recovered")
            recover_choice = st.radio(
                "Select injured player",
                options=[""] + [p.get("name", "") for p in injured_players],
                format_func=lambda x: "Select player" if x == "" else x,
                key="inj_recover_choice",
            )

            if recover_choice:
                if st.button("Set as recovered", key="inj_recover_button"):
                    for p in all_players:
                        if p.get("name", "") == recover_choice:
                            p["injured"] = False
                            break
                    if country:
                        recompute_squad_assignments(country)
                    st.rerun()

        # --- ADD NEW INJURED PLAYER ---
        st.markdown("#### Add injured player")

        healthy_candidates = [
            p for p in all_players
            if not p.get("injured", False)
            and p.get("availability", "Available") != "Out on loan"
        ]

        if not healthy_candidates:
            st.caption("No healthy players available.")
        else:
            add_choice = st.selectbox(
                "Select player to mark as injured",
                options=[""] + [p.get("name", "") for p in healthy_candidates],
                format_func=lambda x: "Select player" if x == "" else x,
                key="inj_add_choice",
            )

            if add_choice:
                if st.button("Mark as injured", key="inj_add_button"):
                    for p in all_players:
                        if p.get("name", "") == add_choice:
                            p["injured"] = True
                            break
                    if country:
                        recompute_squad_assignments(country)
                    st.rerun()

    # ========== FOREIGN PLAYERS (CAP 11) ==========
    foreign_indices: list[int] = []
    for idx, p in enumerate(all_players):
        # Only care about players still at the club
        if p.get("availability", "Available") == "Out on loan":
            continue
        nat = p.get("nationality", "")
        if not nat or is_domestic(nat, country):
            continue
        foreign_indices.append(idx)

    def _foreign_sort_key(idx: int):
        p = all_players[idx]
        # Sort by best IP stars (desc), then potential (band/league), then age (younger first)
        return (
            -best_ip_rating(p),
            *potential_tiebreak_tuple(p),
        )

    foreign_indices_sorted = sorted(foreign_indices, key=_foreign_sort_key)
    foreign_surplus_indices: set[int] = set()

    # Cap at 11 foreign players: anything above is "surplus" foreign
    if len(foreign_indices_sorted) > 11:
        foreign_surplus_indices = set(foreign_indices_sorted[11:])
    else:
        foreign_surplus_indices = set()

    if foreign_indices_sorted:
        st.subheader("Foreign players")
        with st.expander("Foreign players (max 11)", expanded=False):
            rows_foreign = []
            for rank, idx in enumerate(foreign_indices_sorted, start=1):
                p = all_players[idx]
                best_pos = best_ip_position(p)
                best_star = best_ip_rating(p)
                rows_foreign.append(
                    {
                        "Rank": rank,
                        "Name": p.get("name", ""),
                        "Best pos": best_pos or "",
                        "Stars": stars_to_label(best_star),
                        "Potential league level": p.get("potential_level_league", ""),
                        "Potential level": p.get("potential_band", ""),
                        "Age": p.get("age", ""),
                        "Nationality": p.get("nationality", ""),
                        "Status": "Over cap (surplus)" if idx in foreign_surplus_indices else "",
                    }
                )

            df_foreign = pd.DataFrame(rows_foreign)
            st.dataframe(df_foreign, use_container_width=True, hide_index=True)

    # Build the set of players that are used in at least one locked formation
    used_any_locked: set[int] = set()
    if country:
        xi_4231, bench_4231, res_4231 = _preview_locked_squad(country, "4-2-3-1")
        xi_5212, bench_5212, res_5212 = _preview_locked_squad(country, "5-2-1-2")
        used_any_locked = (
            xi_4231 | bench_4231 | res_4231 |
            xi_5212 | bench_5212 | res_5212
        )

    # Build surplus list:
    #  - Players not used in XI/Bench/Reserves in either locked formation
    #  - PLUS foreign players above the 11-player club cap
    surplus_players = []
    for idx, p in enumerate(all_players):
        # Skip players already out on loan
        if p.get("availability", "Available") == "Out on loan":
            continue

        # Foreigners above cap are ALWAYS surplus, even if used elsewhere
        if idx in foreign_surplus_indices:
            surplus_players.append(p)
            continue

        # Normal surplus logic: not used in any locked formation
        if idx in used_any_locked:
            continue

        surplus_players.append(p)

    if surplus_players:
        st.subheader("Surplus players")

        st.markdown(
            "Players that are **not** in XI, Bench or Reserves in either locked formation "
            "and/or foreign players above the 11-player club limit, and not already out on loan. "
            "Use the buttons to keep, loan out or sell."
        )

        # Build table-style rows (similar to bench)
        rows_surplus = []
        for p in surplus_players:
            cover_pos = best_ip_position(p)
            ip_rating = single_pos_rating(p, cover_pos) if cover_pos else 0.0
            oop_rating = single_pos_rating_oop(p, cover_pos) if cover_pos else 0.0
            rows_surplus.append(
                {
                    "Name": p.get("name", ""),
                    "Cover pos": cover_pos or "",
                    "IP": stars_to_label(ip_rating),
                    "OOP": stars_to_label(oop_rating),
                    "Potential league level": p.get("potential_level_league", ""),
                    "Potential level": p.get("potential_band", ""),
                    "Nationality": p.get("nationality", ""),
                    "Age": p.get("age", ""),
                    "__stars_numeric__": ip_rating,
                }
            )
 
        with st.expander("Surplus / unselected players", expanded=True):
            # Table view
            df_surplus = pd.DataFrame(rows_surplus)
            if not df_surplus.empty:
                df_surplus["__league_rank__"] = df_surplus["Potential league level"].map(
                    POTENTIAL_LEAGUE_SORT
                ).fillna(len(POTENTIAL_LEAGUE_SORT))
                df_surplus["__band_rank__"] = df_surplus["Potential level"].map(
                    POTENTIAL_BAND_SORT
                ).fillna(len(POTENTIAL_BAND_SORT))
                df_surplus = df_surplus.sort_values(
                    ["__stars_numeric__", "__league_rank__", "__band_rank__", "Age", "Name"],
                    ascending=[False, True, True, True, True],
                    kind="mergesort",
                ).drop(columns=["__stars_numeric__", "__league_rank__", "__band_rank__"])
            st.dataframe(df_surplus, use_container_width=True, hide_index=True)
  
            st.markdown("#### Actions")
  
            # Per-player buttons: Keep / Loan out / Sell
            for p in surplus_players:
                name = p.get("name", "")
                col_name, col_keep, col_loan, col_sell = st.columns([3, 1, 1, 1])
                with col_name:
                    st.markdown(f"**{name}**")

                with col_keep:
                    if st.button("Keep", key=f"surplus_keep_{name}"):
                        p["list_status"] = "None"
                        if country:
                            recompute_squad_assignments(country)
                        st.rerun()

                with col_loan:
                    if st.button("Loan out", key=f"surplus_loan_{name}"):
                        p["availability"] = "Out on loan"
                        p["list_status"] = "Loan list"
                        if country:
                            recompute_squad_assignments(country)
                        st.rerun()

                with col_sell:
                    if st.button("Sell", key=f"surplus_sell_{name}"):
                        st.session_state.players = [
                            q for q in st.session_state.players if q is not p
                        ]
                        if country:
                            recompute_squad_assignments(country)
                        st.rerun()

    # ========== PLAYERS OUT ON LOAN ==========
    loaned = [p for p in all_players if p.get("availability") == "Out on loan"]
    if loaned:
        st.subheader("Players out on loan")
        with st.expander("Players out on loan", expanded=False):
            rows_loan = []
            for p in loaned:
                positions_str = ", ".join(p.get("positions") or [])
                rows_loan.append(
                    {
                        "Name": p.get("name", ""),
                        "Positions": positions_str,
                        "Age": p.get("age", ""),
                        "Nationality": p.get("nationality", ""),
                        "List": p.get("list_status", "None"),
                    }
                )
            df_loan = pd.DataFrame(rows_loan)
            st.dataframe(df_loan, use_container_width=True, hide_index=True)

with tab_overview:
    st.header("Position overview")

    # Always have players available for this tab
    players = st.session_state.players

    # Formation selector here mirrors the XI tab and also controls targets
    formations = st.session_state.get("formations", {}) or {}
    formation_options = list(formations.keys())

    if not formation_options:
        st.warning("No formations exist yet. Add one in the XI tab.")
        formation_choice = ""
        formation_ip_positions = []
    else:
        current_formation = st.session_state.get("formation_mode", formation_options[0])
        if current_formation not in formation_options:
            current_formation = formation_options[0]

        pending = st.session_state.pop("_pending_formation_mode", None)
        if pending and pending in formation_options:
            current_formation = pending

        formation_choice = st.radio(
            "Formation",
            options=formation_options,
            index=formation_options.index(current_formation),
            horizontal=True,
            key="formation_mode",
        )

        # Keep the app-wide formation_mode in sync with overview selector

        fdef = formations.get(formation_choice, {}) or {}
        formation_ip_positions = fdef.get("ip") or []

    formation_pos_counts = Counter(formation_ip_positions)

    if not st.session_state.players:
        st.warning("Add players first.")
    else:
        players = st.session_state.players

        # Kun spillere der faktisk er i XI / Bench / Reserves og ikke er udlejet
        active_players = [
            p
            for p in players
            if p.get("availability", "Available") != "Out on loan"
            and p.get("squad_role") in ("XI", "Bench", "Reserve")
        ]

        if not active_players:
            st.info("No XI / Bench / Reserves selected yet.")
        else:
            def _cover_pos_ip(p: dict) -> str | None:
                role = p.get("squad_role")
                if role == "XI":
                    return p.get("assigned_position_ip")
                if role == "Bench":
                    return p.get("bench_cover_pos")
                if role == "Reserve":
                    return p.get("reserve_cover_pos")
                return None

            def _cover_pos_oop(p: dict) -> str | None:
                role = p.get("squad_role")
                if role == "XI":
                    return p.get("assigned_position_oop") or p.get("assigned_position_ip")
                if role == "Bench":
                    return p.get("bench_cover_pos")
                if role == "Reserve":
                    return p.get("reserve_cover_pos")
                return None

            def build_position_table(which: str) -> pd.DataFrame:
                """
                which = 'ip' eller 'oop'
                Bygger én tabel over positioner med:
                  - Coverage (players)
                  - Coverage vs target (x/3 eller x/5)
                  - Avg stars
                  - Alle spillere i den position (navn + stjerner)
                """
                coverage: dict[str, list[tuple[str, float]]] = {}

                for p in active_players:
                    if which == "ip":
                        pos = _cover_pos_ip(p)
                    else:
                        pos = _cover_pos_oop(p)

                    if not pos:
                        continue

                    pos = (pos or "").upper()

                    if which == "ip":
                        rating = single_pos_rating(p, pos)
                    else:
                        rating = single_pos_rating_oop(p, pos)

                    name = p.get("name", "")
                    coverage.setdefault(pos, []).append((name, rating))

                rows: list[dict] = []

                # Only positions that actually appear in the chosen formation.
                positions_for_view = sorted(
                    [p for p in formation_pos_counts.keys() if p in POSITION_CHOICES],
                    key=position_sort_key,
                )

                for pos in positions_for_view:
                    players_list = coverage.get(pos, [])
                    cov_count = len(players_list)

                    if cov_count > 0:
                        ratings = [r for _, r in players_list]
                        avg_rating = sum(ratings) / cov_count
                    else:
                        avg_rating = 0.0

                    # ALL players for display, not just top 3
                    players_sorted = sorted(
                        players_list, key=lambda t: t[1], reverse=True
                    )
                    if players_sorted:
                        players_display = ", ".join(
                            f"{name} ({stars_to_label(r)})" for name, r in players_sorted
                        )
                    else:
                        players_display = ""

                    # Target: 3 per position, or 5 if the formation uses that position 2+ times
                    count_in_formation = formation_pos_counts.get(pos, 0)
                    target = 5 if count_in_formation >= 2 else 3

                    rows.append(
                        {
                            "Position": pos,
                            "Coverage (players)": cov_count,
                            "Coverage vs target": f"{cov_count}/{target}",
                            "Avg stars": stars_to_label(avg_rating),
                            "Players": players_display,
                            "_avg_numeric": avg_rating,
                            "_cov": cov_count,
                            "_weak": 0 if cov_count < target else 1,
                            "_order": position_sort_key(pos),
                        }
                    )

                df = pd.DataFrame(rows)
                df = df.sort_values(
                    ["_weak", "_cov", "_avg_numeric", "_order"],
                    ascending=[True, True, True, True],
                    kind="mergesort",
                )
                return df.drop(columns=["_weak", "_cov", "_avg_numeric", "_order"])

            # IP-tabel
            with st.expander("In possession (IP)", expanded=True):
                df_ip = build_position_table("ip")
                st.dataframe(df_ip, use_container_width=True, hide_index=True)

            # OOP-tabel
            with st.expander("Out of possession (OOP)", expanded=True):
                df_oop = build_position_table("oop")
                st.dataframe(df_oop, use_container_width=True, hide_index=True)

# =========================
# FINAL: SAVE STATE
# =========================

save_state_to_disk()

