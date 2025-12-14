 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/fm26_helper_app.py b/fm26_helper_app.py
index 5148148bac255d6b8df1ae90af746ef982fcdf6a..5ad834308291a8e6a22785254f29925e658482b5 100644
--- a/fm26_helper_app.py
+++ b/fm26_helper_app.py
@@ -1,404 +1,400 @@
-#!/usr/bin/env python3
-import streamlit as st
-import pandas as pd
-import base64
-import json
+#!/usr/bin/env python3
+import streamlit as st
+import pandas as pd
+import base64
+import json
 import os
-from collections import Counter
-
-st.set_page_config(page_title="FM26 Squad Helper", layout="wide")
-
-STATE_FILE = "fm26_state.json"
-
-# =========================
-# FIXED INDONESIA STRUCTURE
-# =========================
-
-SUPER_LEAGUE_TEAMS = [for key in ["positions", "players", "known_nationalities", "formations", "formation_selected"]:
-    if key in data:
-        st.session_state[key] = data[key]
-
-
-    "Arema",
-    "Bali United",
-    "Barito Putera",
-    "Borneo Samarinda",
-    "Dewa United",
-    "Madura United",
-    "Malut United",
-    "Persebaya",
-    "Persib",
-    "Persija",
-    "Persik",
-    "Persis",
-    "PSBS",
-    "PSM",
-    "PSIS",
-    "PSS",
-    "Semen Padang",
-    "Persita",
-]
-
-CHAMPIONSHIP_TEAMS = [
-    "Adhyaksa",
-    "Bekasi City",
-    "Bhayangkara Presisi",
-    "Dejan",
-    "Deltras",
-    "Gresik United",
-    "Nusantara United",
-    "Persekat",
-    "Persela",
-    "Persewar",
-    "Persibo",
-    "Persijap",
-    "Persikabo 1973",
-    "Persikas",
-    "Persikota",
-    "Persiku",
-    "Persipa",
-    "Persipal",
-    "Persipura",
-    "Persiraja",
-    "PSIM",
-    "PSKC",
-    "PSMS",
-    "PSPS",
-    "Sriwijaya",
-    "RANS Nusantara",
-]
-
-LIGA_NUSANTARA_TEAMS = [
-    "Persipa",
-    "Nusantara United",
-    "Persikabo 1973",
-    "Batavia FC",
-    "Dejan FC",
-    "PSDS Deli Serdang",
-    "Pekanbaru FC",
-    "PSGC Ciamis",
-    "Persikota Tangerang",
-    "Perserang Serang",
-    "Tri Brata Rafflesia FC",
-    "Persitara Jakarta Utara",
-    "Persibo Bojonegoro",
-    "Persika Karanganyar",
-    "Persewar Waropen",
-    "Persikutim United",
-    "Rans Nusantara FC",
-    "Sang Maestro FC",
-    "Persiba Bantul",
-    "Perseden Denpasar",
-    "Gresik United",
-    "Persebata Lembata",
-    "Waanal Brothers",
-    "Persekabpas Pasuruan",
-]
-
-FM_STRUCTURE = {
-    "Indonesia": {
-        "Super League": SUPER_LEAGUE_TEAMS,
-        "Championship": CHAMPIONSHIP_TEAMS,
-        "Liga Nusantara": LIGA_NUSANTARA_TEAMS,
-    }
-}
-
-CUSTOM_TEAM_LABEL = "Custom club name"
-
-# =========================
-# ONLINE IMAGES FOR FLAG & LEAGUES
-# =========================
-
-FLAG_URLS = {
-    "Indonesia": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/800px-Flag_of_Indonesia.svg.png",
-}
-
-LEAGUE_LOGO_URLS = {
-    ("Indonesia", "Super League"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/BRI_Super_League_Indonesia.png/960px-BRI_Super_League_Indonesia.png",
-    ("Indonesia", "Championship"): "https://upload.wikimedia.org/wikipedia/id/thumb/9/99/Logo_Terbaru_Liga_2_Indonesia.png/600px-Logo_Terbaru_Liga_2_Indonesia.png",
-    ("Indonesia", "Liga Nusantara"): "https://upload.wikimedia.org/wikipedia/id/thumb/9/9a/PNM_Liga_Nusantara_Logo.png/500px-PNM_Liga_Nusantara_Logo.png",
-}
-
-
-def get_flag_url(country: str) -> str:
-    return FLAG_URLS.get(country or "", "")
-
-
-def get_league_logo_url(country: str, league: str) -> str:
-    return LEAGUE_LOGO_URLS.get((country or "", league or ""), "")
-
-
-def bytes_to_data_uri(png_bytes: bytes | None) -> str:
-    if not png_bytes:
-        return ""
-    b64 = base64.b64encode(png_bytes).decode("utf-8")
-    return f"data:image/png;base64,{b64}"
-
-
-# =========================
-# POSITIONS, FAMILIES & ROLES
-# =========================
-
-POSITION_CHOICES = [
-    "GK",
-    "LB", "LWB", "CB", "RB", "RWB",
-    "CDM", "CM",
-    "LM", "LW", "RM", "RW",
-    "CAM", "ST",
-]
+from collections import Counter
+
+st.set_page_config(page_title="FM26 Squad Helper", layout="wide")
+
+STATE_FILE = "fm26_state.json"
+
+# =========================
+# FIXED INDONESIA STRUCTURE
+# =========================
+
+SUPER_LEAGUE_TEAMS = [
+    "Arema",
+    "Bali United",
+    "Barito Putera",
+    "Borneo Samarinda",
+    "Dewa United",
+    "Madura United",
+    "Malut United",
+    "Persebaya",
+    "Persib",
+    "Persija",
+    "Persik",
+    "Persis",
+    "PSBS",
+    "PSM",
+    "PSIS",
+    "PSS",
+    "Semen Padang",
+    "Persita",
+]
+
+CHAMPIONSHIP_TEAMS = [
+    "Adhyaksa",
+    "Bekasi City",
+    "Bhayangkara Presisi",
+    "Dejan",
+    "Deltras",
+    "Gresik United",
+    "Nusantara United",
+    "Persekat",
+    "Persela",
+    "Persewar",
+    "Persibo",
+    "Persijap",
+    "Persikabo 1973",
+    "Persikas",
+    "Persikota",
+    "Persiku",
+    "Persipa",
+    "Persipal",
+    "Persipura",
+    "Persiraja",
+    "PSIM",
+    "PSKC",
+    "PSMS",
+    "PSPS",
+    "Sriwijaya",
+    "RANS Nusantara",
+]
+
+LIGA_NUSANTARA_TEAMS = [
+    "Persipa",
+    "Nusantara United",
+    "Persikabo 1973",
+    "Batavia FC",
+    "Dejan FC",
+    "PSDS Deli Serdang",
+    "Pekanbaru FC",
+    "PSGC Ciamis",
+    "Persikota Tangerang",
+    "Perserang Serang",
+    "Tri Brata Rafflesia FC",
+    "Persitara Jakarta Utara",
+    "Persibo Bojonegoro",
+    "Persika Karanganyar",
+    "Persewar Waropen",
+    "Persikutim United",
+    "Rans Nusantara FC",
+    "Sang Maestro FC",
+    "Persiba Bantul",
+    "Perseden Denpasar",
+    "Gresik United",
+    "Persebata Lembata",
+    "Waanal Brothers",
+    "Persekabpas Pasuruan",
+]
+
+FM_STRUCTURE = {
+    "Indonesia": {
+        "Super League": SUPER_LEAGUE_TEAMS,
+        "Championship": CHAMPIONSHIP_TEAMS,
+        "Liga Nusantara": LIGA_NUSANTARA_TEAMS,
+    }
+}
+
+CUSTOM_TEAM_LABEL = "Custom club name"
+
+# =========================
+# ONLINE IMAGES FOR FLAG & LEAGUES
+# =========================
+
+FLAG_URLS = {
+    "Indonesia": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9f/Flag_of_Indonesia.svg/800px-Flag_of_Indonesia.svg.png",
+}
+
+LEAGUE_LOGO_URLS = {
+    ("Indonesia", "Super League"): "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c2/BRI_Super_League_Indonesia.png/960px-BRI_Super_League_Indonesia.png",
+    ("Indonesia", "Championship"): "https://upload.wikimedia.org/wikipedia/id/thumb/9/99/Logo_Terbaru_Liga_2_Indonesia.png/600px-Logo_Terbaru_Liga_2_Indonesia.png",
+    ("Indonesia", "Liga Nusantara"): "https://upload.wikimedia.org/wikipedia/id/thumb/9/9a/PNM_Liga_Nusantara_Logo.png/500px-PNM_Liga_Nusantara_Logo.png",
+}
+
+
+def get_flag_url(country: str) -> str:
+    return FLAG_URLS.get(country or "", "")
+
+
+def get_league_logo_url(country: str, league: str) -> str:
+    return LEAGUE_LOGO_URLS.get((country or "", league or ""), "")
+
+
+def bytes_to_data_uri(png_bytes: bytes | None) -> str:
+    if not png_bytes:
+        return ""
+    b64 = base64.b64encode(png_bytes).decode("utf-8")
+    return f"data:image/png;base64,{b64}"
+
+
+# =========================
+# POSITIONS, FAMILIES & ROLES
+# =========================
+
+POSITION_CHOICES = [
+    "GK",
+    "LB", "LWB", "CB", "RB", "RWB",
+    "CDM", "CM",
+    "LM", "LW", "RM", "RW",
+    "CAM", "ST",
+]
 
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
-
-POSITION_FAMILIES = {
-    "GK": ["GK"],
-    "CB": ["CB"],
-    "FULLBACK": ["LB", "RB"],
-    "WINGBACK": ["LWB", "RWB"],
-    "DM": ["CDM"],
-    "CM": ["CM"],
-    "WIDE_MID": ["LM", "RM"],
-    "WIDE_AM": ["LW", "RW"],
-    "AMC": ["CAM"],
-    "ST": ["ST"],
-}
-
-
-def family_for_position(pos: str) -> str:
-    pos = (pos or "").upper()
-    for fam, members in POSITION_FAMILIES.items():
-        if pos in members:
-            return fam
-    return ""
-
-
-IN_POSSESSION_ROLES = {
-    "GK": [
-        "Goalkeeper",
-        "Ball-Playing Goalkeeper",
-        "No-Nonsense Goalkeeper",
-    ],
-    "CB": [
-        "Centre-Back",
-        "Ball-Playing Centre-Back",
-        "No-Nonsense Centre-Back",
-        "Wide Centre-Back",
-        "Advanced Centre-Back",
-    ],
-    "FULLBACK": [
-        "Full-Back",
-        "Inverted Full-Back",
-        "Wing-Back",
-        "Inverted Wing-Back",
-        "Playmaking Wing-Back",
-    ],
-    "WINGBACK": [
-        "Wing-Back",
-        "Playmaking Wing-Back",
-        "Advanced Wing-Back",
-        "Inside Wing-Back",
-        "Holding Wing-Back",
-    ],
-    "DM": [
-        "Defensive Midfielder",
-        "Deep-Lying Playmaker",
-        "Half Back",
-        "Box-to-Box Midfielder",
-        "Midfield Playmaker",
-    ],
-    "CM": [
-        "Central Midfielder",
-        "Attacking Midfielder",
-        "Advanced Playmaker",
-        "Channel Midfielder",
-        "Box-to-Box Midfielder",
-    ],
-    "WIDE_MID": [
-        "Wide Midfielder",
-        "Winger",
-        "Playmaking Winger",
-        "Inside Winger",
-        "Wide Playmaker",
-    ],
-    "WIDE_AM": [
-        "Winger",
-        "Inside Forward",
-        "Wide Forward",
-        "Playmaking Winger",
-        "Wide Playmaker",
-    ],
-    "AMC": [
-        "Attacking Midfielder",
-        "Advanced Playmaker",
-        "Free Role",
-        "Second Striker",
-        "Channel Midfielder",
-    ],
-    "ST": [
-        "Centre Forward",
-        "Deep-Lying Forward",
-        "Target Forward",
-        "Poacher",
-        "False Nine",
-    ],
-}
-
-OUT_OF_POSSESSION_ROLES = {
-    "GK": [
-        "Goalkeeper",
-        "Sweeper Keeper",
-        "Line-Holding Keeper",
-    ],
-    "CB": [
-        "Centre-Back",
-        "Stopping Centre-Back",
-        "Covering Centre-Back",
-        "Stopping Wide Centre-Back",
-        "Covering Wide Centre-Back",
-    ],
-    "FULLBACK": [
-        "Full-Back",
-        "Holding Full-Back",
-        "Pressing Full-Back",
-        "Holding Wing-Back",
-        "Pressing Wing-Back",
-    ],
-    "WINGBACK": [
-        "Wing-Back",
-        "Holding Wing-Back",
-        "Pressing Wing-Back",
-    ],
-    "DM": [
-        "Defensive Midfielder",
-        "Dropping Defensive Midfielder",
-        "Screening Defensive Midfielder",
-        "Pressing Defensive Midfielder",
-        "Wide Covering Defensive Midfielder",
-    ],
-    "CM": [
-        "Central Midfielder",
-        "Pressing Central Midfielder",
-        "Screening Central Midfielder",
-        "Wide Covering Central Midfielder",
-    ],
-    "WIDE_MID": [
-        "Wide Midfielder",
-        "Tracking Wide Midfielder",
-        "Wide Outlet Wide Midfielder",
-    ],
-    "WIDE_AM": [
-        "Winger",
-        "Tracking Winger",
-        "Inside Outlet Winger",
-        "Wide Outlet Winger",
-    ],
-    "AMC": [
-        "Attacking Midfielder",
-        "Tracking Attacking Midfielder",
-        "Central Outlet Attacking Midfielder",
-    ],
-    "ST": [
-        "Centre Forward",
-        "Tracking Centre Forward",
-        "Central Outlet Centre Forward",
-        "Splitting Outlet Centre Forward",
-    ],
-}
-
-# =========================
-# STAR & RATING HELPERS
-# =========================
-
-STAR_VALUES = [i / 2 for i in range(0, 11)]
-RATING_BANDS = ["Leading", "Good", "Decent", "Standard"]
-POTENTIAL_EXTRA = ["Unlikely to improve", "Could improve a lot", "Could improve slightly", "Could improve significantly"]
+
+POSITION_FAMILIES = {
+    "GK": ["GK"],
+    "CB": ["CB"],
+    "FULLBACK": ["LB", "RB"],
+    "WINGBACK": ["LWB", "RWB"],
+    "DM": ["CDM"],
+    "CM": ["CM"],
+    "WIDE_MID": ["LM", "RM"],
+    "WIDE_AM": ["LW", "RW"],
+    "AMC": ["CAM"],
+    "ST": ["ST"],
+}
+
+
+def family_for_position(pos: str) -> str:
+    pos = (pos or "").upper()
+    for fam, members in POSITION_FAMILIES.items():
+        if pos in members:
+            return fam
+    return ""
+
+
+IN_POSSESSION_ROLES = {
+    "GK": [
+        "Goalkeeper",
+        "Ball-Playing Goalkeeper",
+        "No-Nonsense Goalkeeper",
+    ],
+    "CB": [
+        "Centre-Back",
+        "Ball-Playing Centre-Back",
+        "No-Nonsense Centre-Back",
+        "Wide Centre-Back",
+        "Advanced Centre-Back",
+    ],
+    "FULLBACK": [
+        "Full-Back",
+        "Inverted Full-Back",
+        "Wing-Back",
+        "Inverted Wing-Back",
+        "Playmaking Wing-Back",
+    ],
+    "WINGBACK": [
+        "Wing-Back",
+        "Playmaking Wing-Back",
+        "Advanced Wing-Back",
+        "Inside Wing-Back",
+        "Holding Wing-Back",
+    ],
+    "DM": [
+        "Defensive Midfielder",
+        "Deep-Lying Playmaker",
+        "Half Back",
+        "Box-to-Box Midfielder",
+        "Midfield Playmaker",
+    ],
+    "CM": [
+        "Central Midfielder",
+        "Attacking Midfielder",
+        "Advanced Playmaker",
+        "Channel Midfielder",
+        "Box-to-Box Midfielder",
+    ],
+    "WIDE_MID": [
+        "Wide Midfielder",
+        "Winger",
+        "Playmaking Winger",
+        "Inside Winger",
+        "Wide Playmaker",
+    ],
+    "WIDE_AM": [
+        "Winger",
+        "Inside Forward",
+        "Wide Forward",
+        "Playmaking Winger",
+        "Wide Playmaker",
+    ],
+    "AMC": [
+        "Attacking Midfielder",
+        "Advanced Playmaker",
+        "Free Role",
+        "Second Striker",
+        "Channel Midfielder",
+    ],
+    "ST": [
+        "Centre Forward",
+        "Deep-Lying Forward",
+        "Target Forward",
+        "Poacher",
+        "False Nine",
+    ],
+}
+
+OUT_OF_POSSESSION_ROLES = {
+    "GK": [
+        "Goalkeeper",
+        "Sweeper Keeper",
+        "Line-Holding Keeper",
+    ],
+    "CB": [
+        "Centre-Back",
+        "Stopping Centre-Back",
+        "Covering Centre-Back",
+        "Stopping Wide Centre-Back",
+        "Covering Wide Centre-Back",
+    ],
+    "FULLBACK": [
+        "Full-Back",
+        "Holding Full-Back",
+        "Pressing Full-Back",
+        "Holding Wing-Back",
+        "Pressing Wing-Back",
+    ],
+    "WINGBACK": [
+        "Wing-Back",
+        "Holding Wing-Back",
+        "Pressing Wing-Back",
+    ],
+    "DM": [
+        "Defensive Midfielder",
+        "Dropping Defensive Midfielder",
+        "Screening Defensive Midfielder",
+        "Pressing Defensive Midfielder",
+        "Wide Covering Defensive Midfielder",
+    ],
+    "CM": [
+        "Central Midfielder",
+        "Pressing Central Midfielder",
+        "Screening Central Midfielder",
+        "Wide Covering Central Midfielder",
+    ],
+    "WIDE_MID": [
+        "Wide Midfielder",
+        "Tracking Wide Midfielder",
+        "Wide Outlet Wide Midfielder",
+    ],
+    "WIDE_AM": [
+        "Winger",
+        "Tracking Winger",
+        "Inside Outlet Winger",
+        "Wide Outlet Winger",
+    ],
+    "AMC": [
+        "Attacking Midfielder",
+        "Tracking Attacking Midfielder",
+        "Central Outlet Attacking Midfielder",
+    ],
+    "ST": [
+        "Centre Forward",
+        "Tracking Centre Forward",
+        "Central Outlet Centre Forward",
+        "Splitting Outlet Centre Forward",
+    ],
+}
+
+# =========================
+# STAR & RATING HELPERS
+# =========================
+
+STAR_VALUES = [i / 2 for i in range(0, 11)]
+RATING_BANDS = ["Leading", "Good", "Decent", "Standard"]
+POTENTIAL_EXTRA = ["Unlikely to improve", "Could improve a lot", "Could improve slightly", "Could improve significantly"]
 RATING_LEAGUES = ["Super League", "Championship", "Liga Nusantara"]
 
 # Sorting helpers for potential
 POTENTIAL_BAND_SORT = {band: idx for idx, band in enumerate(RATING_BANDS)}
 POTENTIAL_LEAGUE_SORT = {lg: idx for idx, lg in enumerate(RATING_LEAGUES)}
 
 def potential_tiebreak_tuple(player: dict) -> tuple[int, int, int]:
     """
     Common tiebreaker for players:
       1) potential_band (better band first)
       2) potential_level_league (higher league first)
       3) age (younger first)
     Used when ratings are equal.
     """
     band = (player.get("potential_band", "") or "").strip()
     league = (player.get("potential_level_league", "") or "").strip()
 
     try:
         age = int(player.get("age", 0) or 0)
     except Exception:
         age = 0
 
     band_rank = POTENTIAL_BAND_SORT.get(band, len(POTENTIAL_BAND_SORT))
     league_rank = POTENTIAL_LEAGUE_SORT.get(league, len(POTENTIAL_LEAGUE_SORT))
 
     # Lower band_rank = better (Leading < Good < Decent < Standard)
     # Lower league_rank = better (Super League < Championship < Liga Nusantara)
     # Lower age = better (younger first)
-    return (band_rank, league_rank, age)
-
-
-def stars_to_label(value: float) -> str:
-    full = int(value)
-    half = 1 if value - full >= 0.5 else 0
-    full_part = "⭐" * full
-    half_part = "½" if half else ""
-    return full_part + half_part
-
-
-def rating_text(band: str, league_level: str | None) -> str:
-    if not band:
-        return ""
-    if band in POTENTIAL_EXTRA:
-        if league_level:
-            return f"{band} ({league_level})"
-        return band
-    lg = league_level if league_level else "this level"
-    return f"{band} {lg}"
-
-
+    return (band_rank, league_rank, age)
+
+
+def stars_to_label(value: float) -> str:
+    full = int(value)
+    half = 1 if value - full >= 0.5 else 0
+    full_part = "⭐" * full
+    half_part = "½" if half else ""
+    return full_part + half_part
+
+
+def rating_text(band: str, league_level: str | None) -> str:
+    if not band:
+        return ""
+    if band in POTENTIAL_EXTRA:
+        if league_level:
+            return f"{band} ({league_level})"
+        return band
+    lg = league_level if league_level else "this level"
+    return f"{band} {lg}"
+
+
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
@@ -466,245 +462,270 @@ def best_oop_rating(player: dict) -> float:
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
 
-    - For locked formations (4-2-3-1 / 5-2-1-2), only positions that exist in that shape.
-    - For Auto, prefer positions where the player actually has IP or OOP rating.
+    - Only positions that exist in the selected formation are considered.
     - Uses combined IP + OOP for scoring, so both sides are taken into account.
     """
     if formation_mode is None:
-        formation_mode = st.session_state.get("formation_mode", "Auto")
+        formation_mode = st.session_state.get("formation_mode", "")
 
-    formation_mode = formation_mode or "Auto"
+    allowed: list[str] = []
+    formation = get_formation_by_name(formation_mode) if formation_mode else get_active_formation()
+    if formation:
+        allowed = list({(pos or "").upper() for pos in formation.get("positions", []) if pos})
 
-    if formation_mode == "4-2-3-1":
-        allowed = ["GK", "LB", "CB", "RB", "CDM", "CM", "CAM", "LW", "RW", "ST"]
-    elif formation_mode == "5-2-1-2":
-        allowed = ["GK", "LWB", "CB", "RWB", "CDM", "CM", "CAM", "ST"]
-    else:
-        # Auto: prefer positions they actually have a rating in
+    if not allowed:
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
-
-
+
+
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
-
-def current_rating_display_overall(player: dict) -> str:
-    stars = best_position_rating(player)
-    star_str = stars_to_label(stars)
-    band = player.get("current_band", "")
-    lvl = player.get("current_level_league", "")
-    text = rating_text(band, lvl)
-    return f"{star_str} | {text}" if text else star_str
-
-
-def current_rating_for_position_display(player: dict, pos: str) -> str:
-    stars = combined_rating_for_position(player, pos)
-    star_str = stars_to_label(stars)
-    band = player.get("current_band", "")
-    lvl = player.get("current_level_league", "")
-    text = rating_text(band, lvl)
-    return f"{star_str} | {text}" if text else star_str
-
-
-def potential_rating_display(player: dict) -> str:
-    band = player.get("potential_band", "")
-    lvl = player.get("potential_level_league", "")
-    return rating_text(band, lvl)
-
-
-# =========================
-# STATE LOAD / SAVE
-# =========================
-
-def load_state_from_disk():
-    if not os.path.exists(STATE_FILE):
-        return
-    try:
-        with open(STATE_FILE, "r", encoding="utf-8") as f:
-            data = json.load(f)
-    except Exception:
-        return
-
-    for key in ["positions", "players", "known_nationalities"]:
-        if key in data:
-            st.session_state[key] = data[key]
-
-    for key in ["country_select", "league_select", "team_select", "team_custom_name"]:
-        if key in data:
-            st.session_state[key] = data[key]
-
-    logo_b64 = data.get("club_logo_b64", "")
-    if logo_b64:
-        try:
-            st.session_state.club_logo_bytes = base64.b64decode(logo_b64)
-        except Exception:
-            st.session_state.club_logo_bytes = None
-
-
-def save_state_to_disk():
-    try:
-        logo_b64 = ""
-        if st.session_state.get("club_logo_bytes"):
-            logo_b64 = base64.b64encode(st.session_state["club_logo_bytes"]).decode(
-                "utf-8"
-            )
-
+
+def current_rating_display_overall(player: dict) -> str:
+    stars = best_position_rating(player)
+    star_str = stars_to_label(stars)
+    band = player.get("current_band", "")
+    lvl = player.get("current_level_league", "")
+    text = rating_text(band, lvl)
+    return f"{star_str} | {text}" if text else star_str
+
+
+def current_rating_for_position_display(player: dict, pos: str) -> str:
+    stars = combined_rating_for_position(player, pos)
+    star_str = stars_to_label(stars)
+    band = player.get("current_band", "")
+    lvl = player.get("current_level_league", "")
+    text = rating_text(band, lvl)
+    return f"{star_str} | {text}" if text else star_str
+
+
+def potential_rating_display(player: dict) -> str:
+    band = player.get("potential_band", "")
+    lvl = player.get("potential_level_league", "")
+    return rating_text(band, lvl)
+
+
+# =========================
+# STATE LOAD / SAVE
+# =========================
+
+def load_state_from_disk():
+    if not os.path.exists(STATE_FILE):
+        return
+    try:
+        with open(STATE_FILE, "r", encoding="utf-8") as f:
+            data = json.load(f)
+    except Exception:
+        return
+
+    for key in ["positions", "players", "known_nationalities", "formations", "formation_selected"]:
+        if key in data:
+            st.session_state[key] = data[key]
+
+    for key in ["country_select", "league_select", "team_select", "team_custom_name"]:
+        if key in data:
+            st.session_state[key] = data[key]
+
+    logo_b64 = data.get("club_logo_b64", "")
+    if logo_b64:
+        try:
+            st.session_state.club_logo_bytes = base64.b64decode(logo_b64)
+        except Exception:
+            st.session_state.club_logo_bytes = None
+
+
+def save_state_to_disk():
+    try:
+        logo_b64 = ""
+        if st.session_state.get("club_logo_bytes"):
+            logo_b64 = base64.b64encode(st.session_state["club_logo_bytes"]).decode(
+                "utf-8"
+            )
+
         data = {
-    "positions": st.session_state.get("positions", []),
-    "players": st.session_state.get("players", []),
-    "known_nationalities": st.session_state.get("known_nationalities", []),
-    "country_select": st.session_state.get("country_select", ""),
-    "league_select": st.session_state.get("league_select", ""),
-    "team_select": st.session_state.get("team_select", ""),
-    "team_custom_name": st.session_state.get("team_custom_name", ""),
-    "club_logo_b64": logo_b64,
-    "formations": st.session_state.get("formations", []),
-    "formation_selected": st.session_state.get("formation_selected", ""),
-}
-
-        with open(STATE_FILE, "w", encoding="utf-8") as f:
-            json.dump(data, f, ensure_ascii=False, indent=2)
-    except Exception:
-        pass
-
-
-# =========================
-# SESSION STATE DEFAULTS
-# =========================
-
-if "positions" not in st.session_state:
-    st.session_state.positions = []
-
-if "players" not in st.session_state:
-    st.session_state.players = []
-
-if "known_nationalities" not in st.session_state:
-    st.session_state.known_nationalities = ["Indonesia"]
-
-if "club_logo_bytes" not in st.session_state:
-    st.session_state.club_logo_bytes = None
-
-if "rules_tracker" not in st.session_state:
-    st.session_state.rules_tracker = {}
-
-if "reset_player_form" not in st.session_state:
-    st.session_state.reset_player_form = False
-
+            "positions": st.session_state.get("positions", []),
+            "players": st.session_state.get("players", []),
+            "known_nationalities": st.session_state.get("known_nationalities", []),
+            "country_select": st.session_state.get("country_select", ""),
+            "league_select": st.session_state.get("league_select", ""),
+            "team_select": st.session_state.get("team_select", ""),
+            "team_custom_name": st.session_state.get("team_custom_name", ""),
+            "club_logo_b64": logo_b64,
+            "formations": st.session_state.get("formations", []),
+            "formation_selected": st.session_state.get("formation_selected", ""),
+        }
+
+        with open(STATE_FILE, "w", encoding="utf-8") as f:
+            json.dump(data, f, ensure_ascii=False, indent=2)
+    except Exception:
+        pass
+
+
+# =========================
+# SESSION STATE DEFAULTS
+# =========================
+
+if "positions" not in st.session_state:
+    st.session_state.positions = []
+
+if "players" not in st.session_state:
+    st.session_state.players = []
+
+if "known_nationalities" not in st.session_state:
+    st.session_state.known_nationalities = ["Indonesia"]
+
+if "club_logo_bytes" not in st.session_state:
+    st.session_state.club_logo_bytes = None
+
+if "rules_tracker" not in st.session_state:
+    st.session_state.rules_tracker = {}
+
+if "reset_player_form" not in st.session_state:
+    st.session_state.reset_player_form = False
+
 if "reset_position_form" not in st.session_state:
     st.session_state.reset_position_form = False
 
 if "xi_variants" not in st.session_state:
     st.session_state.xi_variants = []
 if "xi_variant_count" not in st.session_state:
     st.session_state.xi_variant_count = 0
 if "xi_variant_choice" not in st.session_state:
     st.session_state.xi_variant_choice = 0
 
+if "formations" not in st.session_state:
+    st.session_state.formations = []
+if "formation_selected" not in st.session_state:
+    st.session_state.formation_selected = ""
 if "formation_mode" not in st.session_state:
-    st.session_state.formation_mode = "Auto"
-
-if "state_loaded" not in st.session_state:
-    load_state_from_disk()
-    st.session_state.state_loaded = True
-
-
-# =========================
-# HELPER FUNCTIONS
-# =========================
-
-def is_domestic(nationality: str, club_country: str) -> bool:
-    if not nationality or not club_country:
-        return False
-    return nationality.strip().casefold() == club_country.strip().casefold()
-
-
-def is_under23_domestic(player: dict, club_country: str) -> bool:
-    try:
-        age = int(player.get("age", 0))
-    except Exception:
-        age = 0
-    return age < 23 and is_domestic(player.get("nationality", ""), club_country)
-
-
-def add_or_update_player(player: dict):
-    name = player["name"].strip()
-    for p in st.session_state.players:
-        if p["name"].strip().lower() == name.lower():
-            p.update(player)
-            return
+    st.session_state.formation_mode = ""
+
+if "state_loaded" not in st.session_state:
+    load_state_from_disk()
+    st.session_state.state_loaded = True
+
+
+# =========================
+# HELPER FUNCTIONS
+# =========================
+
+def is_domestic(nationality: str, club_country: str) -> bool:
+    if not nationality or not club_country:
+        return False
+    return nationality.strip().casefold() == club_country.strip().casefold()
+
+
+def is_under23_domestic(player: dict, club_country: str) -> bool:
+    try:
+        age = int(player.get("age", 0))
+    except Exception:
+        age = 0
+    return age < 23 and is_domestic(player.get("nationality", ""), club_country)
+
+
+def add_or_update_player(player: dict):
+    name = player["name"].strip()
+    for p in st.session_state.players:
+        if p["name"].strip().lower() == name.lower():
+            p.update(player)
+            return
     st.session_state.players.append(player)
 
+
+def get_formation_by_name(name: str) -> dict | None:
+    for f in st.session_state.get("formations", []):
+        if f.get("name", "").strip().lower() == (name or "").strip().lower():
+            return f
+    return None
+
+
+def get_active_formation() -> dict | None:
+    selected = st.session_state.get("formation_selected") or st.session_state.get(
+        "formation_mode", ""
+    )
+    if selected:
+        form = get_formation_by_name(selected)
+        if form:
+            return form
+
+    formations = st.session_state.get("formations") or []
+    if formations:
+        st.session_state.formation_selected = formations[0].get("name", "")
+        st.session_state.formation_mode = formations[0].get("name", "")
+        return formations[0]
+    return None
+
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
@@ -895,51 +916,51 @@ def optimize_xi_positions_ip(
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
 
-    return best_assignments, best_score
+    return best_assignments, best_score
 
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
 
@@ -1227,858 +1248,312 @@ def build_xi_variants(
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
 
-    return variants
-
+    return variants
+
 def recompute_squad_assignments(
     club_country: str,
     force_variant_idx: int | None = None,
 ):
     """
     Central entry point.
 
-    - Uses 'formation_mode' in session_state as the *global* selector.
-    - 'Auto' uses the old flexible 2+ logic via _recompute_squad_assignments_auto.
-    - Locked 4-2-3-1 / 5-2-1-2 use _recompute_squad_assignments_locked.
+    Uses the selected custom formation (11 positions) to build the XI.
     """
-    formation_mode = st.session_state.get("formation_mode", "Auto")
+    formation = get_active_formation()
+    if not formation:
+        st.session_state.xi_variants = []
+        st.session_state.xi_variant_count = 0
+        st.session_state.rules_tracker = {}
+        return
 
-    if formation_mode == "4-2-3-1":
-        return _recompute_squad_assignments_locked(
-            club_country,
-            "4-2-3-1",
-            force_variant_idx=force_variant_idx,
-        )
-    elif formation_mode == "5-2-1-2":
-        return _recompute_squad_assignments_locked(
-            club_country,
-            "5-2-1-2",
-            force_variant_idx=force_variant_idx,
-        )
-    else:
-        # Auto uses the original dynamic 2+ logic across XI variants
-        return _recompute_squad_assignments_auto(
-            club_country,
-            force_variant_idx=force_variant_idx,
-        )
+    slot_defs = [{"ip": pos.upper(), "oop": pos.upper()} for pos in formation.get("positions", [])]
+    return _recompute_squad_assignments_custom(
+        club_country,
+        slot_defs,
+        formation.get("name", ""),
+        force_variant_idx=force_variant_idx,
+    )
 
-def _recompute_squad_assignments_locked(
+def _recompute_squad_assignments_custom(
     club_country: str,
+    slot_defs: list[dict],
     formation_mode: str,
     force_variant_idx: int | None = None,
 ):
     """
-    Locked formations: 4-2-3-1 & 5-2-1-2.
+    Custom formations with fixed positions per slot (IP + OOP mapping).
 
-    - Positions are fixed per slot (IP + OOP mapping).
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
 
-    # Define slot templates per formation (IP position, OOP position)
-    if formation_mode == "4-2-3-1":
-        slot_defs = [
-            {"ip": "GK",  "oop": "GK"},
-            {"ip": "LB",  "oop": "LB"},
-            {"ip": "CB",  "oop": "CB"},
-            {"ip": "CB",  "oop": "CB"},
-            {"ip": "RB",  "oop": "RB"},
-            {"ip": "CDM", "oop": "CDM"},
-            {"ip": "CM",  "oop": "CDM"},
-            {"ip": "CAM", "oop": "CM"},
-            {"ip": "LW",  "oop": "LM"},
-            {"ip": "RW",  "oop": "RM"},
-            {"ip": "ST",  "oop": "ST"},
-        ]
-    elif formation_mode == "5-2-1-2":
-        slot_defs = [
-            {"ip": "GK",  "oop": "GK"},
-            {"ip": "LWB", "oop": "LWB"},
-            {"ip": "CB",  "oop": "CB"},
-            {"ip": "CB",  "oop": "CB"},
-            {"ip": "RWB", "oop": "CB"},
-            {"ip": "CDM", "oop": "RWB"},
-            {"ip": "CM",  "oop": "CDM"},
-            {"ip": "CM",  "oop": "CDM"},
-            {"ip": "CAM", "oop": "CAM"},
-            {"ip": "ST",  "oop": "ST"},
-            {"ip": "ST",  "oop": "ST"},
-        ]
-    else:
-        # Safety: if someone sets formation to nonsense, fall back
-        return _recompute_squad_assignments_auto(club_country, force_variant_idx=None)
-
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
 
             # Locked formations: player must have non-zero rating
             # in BOTH IP and OOP for this slot.
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
 
-    # If some slot has no viable players at all, fall back to auto logic
+    # If some slot has no viable players at all, abort
     if any(len(cands) == 0 for cands in slot_candidates):
-        return _recompute_squad_assignments_auto(club_country, force_variant_idx=None)
+        st.session_state.xi_variants = []
+        st.session_state.xi_variant_count = 0
+        st.session_state.rules_tracker = {}
+        return
 
     # DFS to pick the best XI respecting foreign/U23 constraints
     best_total = -1.0
     best_total_ip = 0.0
     best_total_oop = 0.0
     best_assign: list[dict] = []
 
     current_assign: list[dict] = []
-    used_players: set[int] = set()
 
     def dfs(
         slot_idx: int,
         current_total: float,
         current_ip_total: float,
         current_oop_total: float,
         foreign_count: int,
         u23_dom_count: int,
+        used_players: set[int],
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
+                used_players,
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
+        used_players=set(),
     )
 
-    # No valid XI satisfying rules → fall back
+    # No valid XI satisfying rules → clear assignments
     if best_total < 0 or not best_assign:
-        return _recompute_squad_assignments_auto(club_country, force_variant_idx=None)
+        st.session_state.xi_variants = []
+        st.session_state.xi_variant_count = 0
+        st.session_state.rules_tracker = {}
+        return
 
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
-        return _recompute_squad_assignments_auto(club_country, force_variant_idx=None)
+        st.session_state.xi_variants = []
+        st.session_state.xi_variant_count = 0
+        st.session_state.rules_tracker = {}
+        return
 
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
 
-def _recompute_squad_assignments_auto(
-    club_country: str,
-    force_variant_idx: int | None = None,
-):
-    """
-    Auto-picks XI, Bench (10) og Reserves (op til 12).
-
-    Regler (samme som før):
-    - Præcis 1 GK i XI (hvis der findes en GK-rated spiller)
-    - Max 2 ST i XI
-    - Fullback / CB logik:
-        * Hvis truppen har mindst én LB/LWB-rated OG mindst én RB/RWB-rated (ikke skadet):
-            -> XI skal indeholde præcis én LB/LWB og præcis én RB/RWB
-            -> Min. 2 CB
-        * Ellers:
-            -> XI har INGEN LB/LWB/RB/RWB og PRÆCIS 3 CB i alt
-    - Max 1 LB/LWB i XI
-    - Max 1 RB/RWB i XI
-    - Max 1 LM/LW i XI
-    - Max 1 RM/RW i XI
-    - Min. 1 CDM eller CM i XI (hvis der findes en ikke-skadet spiller med rating > 0 der)
-    - Max 7 udlændinge i XI
-    - Max 9 udlændinge i XI + Bænk
-    - Min. 1 U23-indoneser i XI hvis muligt
-    - Skadede spillere må KUN være Reserve/Unselected (ikke XI, ikke bænk)
-    - Efter baseline XI er valgt (spillere), bygger vi XI-varianter:
-      * samme totale IP-rating
-      * 1–2 swaps ind/ud
-      * IP og OOP deler altid samme XI
-    """
-
-    players = st.session_state.players
-
-    # Reset pr. spiller + recompute primary position
-    for p in players:
-        p["assigned_position_ip"] = None
-        p["assigned_position_oop"] = None
-        p["squad_role"] = "Unselected"
-        p["primary_position"] = compute_primary_position(p)
-        p["bench_cover_pos"] = None
-        p["reserve_cover_pos"] = None
-        p["bench_better_notes"] = ""
-
-    # Reset rule tracker
-    st.session_state.rules_tracker = {
-        "foreign_xi": 0,
-        "foreign_xi_limit": 7,
-        "foreign_xi_bench": 0,
-        "foreign_xi_bench_limit": 9,
-        "u23_domestic_xi": 0,
-        "u23_domestic_xi_min": 1,
-        "xi_size": 0,
-        "bench_size": 0,
-        "reserves_size": 0,
-        "total_selected": 0,
-    }
-
-    # Reset XI-variant state
-    st.session_state.xi_variants = []
-    st.session_state.xi_variant_count = 0
-
-    if not club_country or not players:
-        return
-
-    # Kun spillere der ikke er udlejet
-    available_indices = [
-        i
-        for i, p in enumerate(players)
-        if p.get("availability", "Available") != "Out on loan"
-    ]
-    if not available_indices:
-        return
-
-    xi_indices: list[int] = []
-
-    gk_count = 0
-    cb_count = 0
-    lb_like_count = 0
-    rb_like_count = 0
-    lm_like_count = 0
-    rm_like_count = 0
-    mid_like_count = 0
-    st_count = 0
-
-    foreign_xi = 0
-    u23_domestic_xi = 0
-
-    # STEP 1: find kandidater til fullbacks vs back-three mode
-    remaining_for_scan = [i for i in available_indices if not players[i].get("injured")]
-
-    has_lb_like = any(
-        best_rating_for_allowed_positions(players[i], ["LB", "LWB"])[0] > 0
-        for i in remaining_for_scan
-    )
-    has_rb_like = any(
-        best_rating_for_allowed_positions(players[i], ["RB", "RWB"])[0] > 0
-        for i in remaining_for_scan
-    )
-
-    use_fullbacks = has_lb_like and has_rb_like
-    use_back_three = not use_fullbacks
-
-    # STEP 2: vælg GK først
-    gk_candidates = []
-    for i in available_indices:
-        p = players[i]
-        if p.get("injured"):
-            continue
-        score, pos = best_rating_for_allowed_positions(p, ["GK"])
-        if score > 0:
-            gk_candidates.append((score, i, pos))
-
-    if gk_candidates:
-        score, idx, pos = max(gk_candidates, key=lambda t: t[0])
-        xi_indices.append(idx)
-        gk_count = 1
-        if not is_domestic(players[idx].get("nationality", ""), club_country):
-            foreign_xi += 1
-        if is_under23_domestic(players[idx], club_country):
-            u23_domestic_xi += 1
-
-    # Helper til forsvarere (kun for at bestemme baseline XI-puljen)
-    def pick_defender(allowed_positions: list[str]):
-        nonlocal cb_count, lb_like_count, rb_like_count, lm_like_count, rm_like_count, mid_like_count
-        nonlocal foreign_xi, u23_domestic_xi
-
-        best_tuple = None  # (score, idx, chosen_pos)
-
-        for i in available_indices:
-            if i in xi_indices:
-                continue
-            p = players[i]
-            if p.get("injured"):
-                continue
-
-            score, chosen_pos = best_rating_for_allowed_positions(
-                p, allowed_positions
-            )
-            if score <= 0:
-                continue
-
-            if chosen_pos == "GK":
-                continue
-
-            if chosen_pos in ("LB", "LWB") and lb_like_count >= 1:
-                continue
-            if chosen_pos in ("RB", "RWB") and rb_like_count >= 1:
-                continue
-
-            foreign = not is_domestic(p.get("nationality", ""), club_country)
-            if foreign and foreign_xi + 1 > 7:
-                continue
-
-            if best_tuple is None or score > best_tuple[0]:
-                best_tuple = (score, i, chosen_pos)
-
-        if best_tuple is None:
-            return False
-
-        score, idx, chosen_pos = best_tuple
-        xi_indices.append(idx)
-
-        if chosen_pos == "CB":
-            cb_count += 1
-        if chosen_pos in ("LB", "LWB"):
-            lb_like_count += 1
-        if chosen_pos in ("RB", "RWB"):
-            rb_like_count += 1
-        if chosen_pos in ("LM", "LW"):
-            lm_like_count += 1
-        if chosen_pos in ("RM", "RW"):
-            rm_like_count += 1
-        if chosen_pos in ("CDM", "CM"):
-            mid_like_count += 1
-
-        if not is_domestic(players[idx].get("nationality", ""), club_country):
-            foreign_xi += 1
-        if is_under23_domestic(players[idx], club_country):
-            u23_domestic_xi += 1
-
-        return True
-
-    # STEP 3: baseline defensiv enhed
-    if use_fullbacks:
-        pick_defender(["LB", "LWB"])
-        pick_defender(["RB", "RWB"])
-        pick_defender(["CB"])
-        pick_defender(["CB"])
-    else:
-        pick_defender(["CB"])
-        pick_defender(["CB"])
-        pick_defender(["CB"])
-
-    # STEP 4: sørg for mindst én U23-domestic i XI hvis muligt
-    if u23_domestic_xi == 0:
-        u23_candidates = []
-        for i in available_indices:
-            if i in xi_indices:
-                continue
-            p = players[i]
-            if p.get("injured"):
-                continue
-            if not is_under23_domestic(p, club_country):
-                continue
-            score, pos = best_rating_for_allowed_positions(
-                p,
-                [pos for pos in POSITION_CHOICES if pos != "GK"],
-            )
-            if score > 0:
-                u23_candidates.append((score, i, pos))
-
-        if u23_candidates and len(xi_indices) < 11:
-            score, idx, pos = max(u23_candidates, key=lambda t: t[0])
-            xi_indices.append(idx)
-            if pos == "CB":
-                cb_count += 1
-            if pos in ("LB", "LWB"):
-                lb_like_count += 1
-            if pos in ("RB", "RWB"):
-                rb_like_count += 1
-            if pos in ("LM", "LW"):
-                lm_like_count += 1
-            if pos in ("RM", "RW"):
-                rm_like_count += 1
-            if pos in ("CDM", "CM"):
-                mid_like_count += 1
-            if pos == "ST":
-                st_count += 1
-            if not is_domestic(players[idx].get("nationality", ""), club_country):
-                foreign_xi += 1
-            u23_domestic_xi += 1
-
-    # STEP 4.5: hvis ingen CDM/CM i XI, prøv at tilføje én
-    if mid_like_count == 0 and len(xi_indices) < 11:
-        best_mid = None  # (score, idx, chosen_pos)
-        for i in available_indices:
-            if i in xi_indices:
-                continue
-            p = players[i]
-            if p.get("injured"):
-                continue
-
-            score_cdm, _ = best_rating_for_allowed_positions(p, ["CDM"])
-            score_cm, _ = best_rating_for_allowed_positions(p, ["CM"])
-
-            if score_cdm <= 0 and score_cm <= 0:
-                continue
-
-            if score_cdm >= score_cm:
-                score = score_cdm
-                pos = "CDM"
-            else:
-                score = score_cm
-                pos = "CM"
-
-            if score <= 0:
-                continue
-
-            foreign = not is_domestic(p.get("nationality", ""), club_country)
-            if foreign and foreign_xi + 1 > 7:
-                continue
-
-            if best_mid is None or score > best_mid[0]:
-                best_mid = (score, i, pos)
-
-        if best_mid is not None:
-            score, idx, pos = best_mid
-            xi_indices.append(idx)
-            mid_like_count += 1
-            if not is_domestic(players[idx].get("nationality", ""), club_country):
-                foreign_xi += 1
-            if is_under23_domestic(players[idx], club_country):
-                u23_domestic_xi += 1
-
-    # STEP 5: fyld resten af XI (kun spiller-valg)
-    if len(xi_indices) < 11:
-        remaining_indices = [i for i in available_indices if i not in xi_indices]
-        remaining_indices.sort(key=lambda i: -best_position_rating(players[i]))
-
-        for i in remaining_indices:
-            if len(xi_indices) >= 11:
-                break
-            p = players[i]
-            if p.get("injured"):
-                continue
-
-            best_score = 0.0
-            best_pos = None
-
-            for pos in POSITION_CHOICES:
-                up = pos.upper()
-
-                if up == "GK" and gk_count >= 1:
-                    continue
-                if up == "ST" and st_count >= 2:
-                    continue
-
-                if use_back_three and up in ("LB", "LWB", "RB", "RWB"):
-                    continue
-                if use_back_three and up == "CB" and cb_count >= 3:
-                    continue
-
-                if up in ("LB", "LWB") and lb_like_count >= 1:
-                    continue
-                if up in ("RB", "RWB") and rb_like_count >= 1:
-                    continue
-                if up in ("LM", "LW") and lm_like_count >= 1:
-                    continue
-                if up in ("RM", "RW") and rm_like_count >= 1:
-                    continue
-
-                score = single_pos_rating(p, up)
-                if score > best_score:
-                    best_score = score
-                    best_pos = up
-
-            if best_score <= 0 or best_pos is None:
-                continue
-
-            foreign = not is_domestic(p.get("nationality", ""), club_country)
-            if foreign and foreign_xi + 1 > 7:
-                continue
-
-            xi_indices.append(i)
-
-            if best_pos == "GK":
-                gk_count += 1
-            if best_pos == "CB":
-                cb_count += 1
-            if best_pos in ("LB", "LWB"):
-                lb_like_count += 1
-            if best_pos in ("RB", "RWB"):
-                rb_like_count += 1
-            if best_pos in ("LM", "LW"):
-                lm_like_count += 1
-            if best_pos in ("RM", "RW"):
-                rm_like_count += 1
-            if best_pos in ("CDM", "CM"):
-                mid_like_count += 1
-            if best_pos == "ST":
-                st_count += 1
-
-            if foreign:
-                foreign_xi += 1
-            if is_under23_domestic(p, club_country):
-                u23_domestic_xi += 1
-
-    xi_indices = xi_indices[:11]
-    if len(xi_indices) == 0:
-        return
-
-    # STEP 5.9: byg XI-varianter (forskellige spiller-sæt)
-    variants = build_xi_variants(
-        players=players,
-        base_xi_indices=xi_indices,
-        available_indices=available_indices,
-        club_country=club_country,
-        use_fullbacks=use_fullbacks,
-        use_back_three=use_back_three,
-        max_variants=200,
-    )
-
-    if not variants:
-        # fallback: bare baseline assignments (IP and OOP both may have multiple layouts)
-        base_assignments_ip, base_ip_score = optimize_xi_positions_ip(
-            players, xi_indices, use_fullbacks=use_fullbacks, use_back_three=use_back_three
-        )
-        if not base_assignments_ip:
-            return
-
-        base_assignments_oop, base_oop_score = optimize_xi_positions_oop(
-            players, xi_indices, use_fullbacks=use_fullbacks, use_back_three=use_back_three
-        )
-        if not base_assignments_oop:
-            base_assignments_oop = [ip.copy() for ip in base_assignments_ip]
-            base_oop_score = lineup_oop_score(players, xi_indices, base_assignments_oop[0])
-
-        variants = []
-        for ip_assignment in base_assignments_ip:
-            for oop_assignment in base_assignments_oop:
-                variants.append(
-                    {
-                        "xi_indices": sorted(xi_indices),
-                        "assignment_ip": ip_assignment,
-                        "assignment_oop": oop_assignment,
-                        "total_ip": float(base_ip_score),
-                        "total_oop": float(base_oop_score),
-                    }
-                )
-                if len(variants) >= 20:
-                    break
-            if len(variants) >= 20:
-                break
-
-    # Filter variants: keep those whose average (IP+OOP) is within a tiny buffer
-    # of the absolute best. This keeps structurally neutral swaps alive instead
-    # of killing them on floating point / rounding noise.
-    XI_AVG_TOLERANCE = 0.005  # allow up to 0.005⭐ below best
-
-    def _avg_score(v: dict) -> float:
-        xi_list = v.get("xi_indices") or []
-        n = len(xi_list) or 1
-        ip = float(v.get("total_ip", 0.0))
-        oop = float(v.get("total_oop", 0.0))
-        return (ip + oop) / n
-
-    if variants:
-        # Raw best average (no rounding)
-        best_avg_raw = max(_avg_score(v) for v in variants)
-
-        # What the UI shows
-        best_score_rounded = round(best_avg_raw, 2)
-        st.session_state["xi_best_avg"] = best_score_rounded
-
-        # Keep all variants that are effectively equal-best within the tolerance
-        best_variants: list[dict] = []
-        for v in variants:
-            if _avg_score(v) >= best_avg_raw - XI_AVG_TOLERANCE:
-                best_variants.append(v)
-
-        variants = best_variants or variants
-    else:
-        st.session_state["xi_best_avg"] = 0.0
-
-    st.session_state.xi_variants = variants
-    st.session_state.xi_variant_count = len(variants)
-
-    # Decide which XI variant to use right now
-    if force_variant_idx is not None:
-        # coming directly from the radio choice
-        idx = int(force_variant_idx)
-    else:
-        # normal path: reuse whatever is in session_state
-        idx = st.session_state.get("xi_variant_choice", 0)
-
-    # Clamp safely
-    if not isinstance(idx, int) or idx < 0 or idx >= len(variants):
-        idx = 0
-
-    # Persist the final choice
-    st.session_state.xi_variant_choice = idx
-
-    # This is the variant whose IP/OOP assignments we actually apply
-    chosen_variant = variants[idx]
-    final_xi_indices = list(chosen_variant["xi_indices"])
-    assignment_ip = chosen_variant.get("assignment_ip", {}) or {}
-    assignment_oop = chosen_variant.get("assignment_oop", {}) or {}
-
-    # Clear any previous roles/positions
-    for p in players:
-        p["assigned_position_ip"] = None
-        p["assigned_position_oop"] = None
-        p["squad_role"] = "Unselected"
-
-    # Assign XI players + positions
-    for idx in final_xi_indices:
-        p = players[idx]
-        p["squad_role"] = "XI"
-        p["assigned_position_ip"] = assignment_ip.get(idx)
-        p["assigned_position_oop"] = assignment_oop.get(idx) or assignment_ip.get(idx)
-
-    # Collect XI IP positions (current formation) for formation-aware cover roles
-    xi_ip_positions = sorted(
-        {
-            (players[idx].get("assigned_position_ip") or "").upper()
-            for idx in final_xi_indices
-            if players[idx].get("assigned_position_ip")
-        },
-        key=position_sort_key,
-    )
-
-    def best_cover_pos_for_xi(p: dict) -> str | None:
-        """
-        Pick the best cover position for this player, restricted to
-        positions that actually exist in the current XI (IP).
-        """
-        if not xi_ip_positions:
-            return None
-        best_score = 0.0
-        best_pos: str | None = None
-        for pos in xi_ip_positions:
-            score = combined_ip_oop_for_pos(p, pos)
-            if score > best_score + 1e-6:
-                best_score = score
-                best_pos = pos
-        return best_pos
-
-    formation_mode = st.session_state.get("formation_mode", "Auto")
-    # STEP 7–9: bench, reserves & rules (shared helper)
-    bench_indices, reserve_indices, rules_tracker = _build_bench_and_reserves(
-        players=players,
-        available_indices=available_indices,
-        final_xi_indices=final_xi_indices,
-        club_country=club_country,
-        formation_mode=formation_mode,
-    )
-    st.session_state.rules_tracker = rules_tracker
-
-def best_cover_pos_for_xi(player: dict) -> str | None:
-    """
-    Helper used for bench / reserves: returns the player's 'natural' cover position
-    based on current XI / bench / reserve assignments, falling back to best IP pos.
-    """
-    # Prefer explicit XI position if set
-    pos = player.get("assigned_position_ip")
-    if pos:
-        return pos
-
-    # Otherwise bench / reserve cover positions if they exist
-    pos = player.get("bench_cover_pos") or player.get("reserve_cover_pos")
-    if pos:
-        return pos
-
-    # Last resort: generic best IP position
-    return best_ip_position(player)
-
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
@@ -2114,57 +1589,53 @@ def _build_bench_and_reserves(
 
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
-
-        - For locked formations (4-2-3-1 / 5-2-1-2): only positions that exist in that shape.
-        - For Auto: best among positions actually used in XI; falls back to best IP.
+        - Only positions that exist in the selected formation are considered.
         """
         pos = best_cover_pos_for_formation(p, formation_mode)
-        if not pos and formation_mode == "Auto":
-            pos = best_ip_position(p)
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
@@ -2546,59 +2017,59 @@ def _preview_locked_squad(
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
 
     # If some slot has no viable players at all, treat as "no valid XI" → empty sets
     if any(len(cands) == 0 for cands in slot_candidates):
         return set(), set(), set()
 
     # DFS to pick the best XI respecting foreign/U23 constraints
     best_total = -1.0
     best_total_ip = 0.0
     best_total_oop = 0.0
     best_assign: list[dict] = []
 
     current_assign: list[dict] = []
-    used_players: set[int] = set()
 
     def dfs(
         slot_idx: int,
         current_total: float,
         current_ip_total: float,
         current_oop_total: float,
         foreign_count: int,
         u23_dom_count: int,
+        used_players: set[int],
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
@@ -2612,62 +2083,64 @@ def _preview_locked_squad(
 
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
+                used_players,
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
+        used_players=set(),
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
@@ -2677,178 +2150,178 @@ def _preview_locked_squad(
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
-
-# =========================
-# SIDEBAR: TEAM & LOGO UPLOAD
-# =========================
-
-with st.sidebar:
-    st.title("FM26 Squad Helper")
-
-    st.subheader("Team setup")
-
-    country_list = ["Indonesia"]
-    country = st.selectbox(
-        "Country",
-        options=[""] + country_list,
-        format_func=lambda x: x if x else "Select country",
-        key="country_select",
-    )
-
-    if country:
-        leagues = list(FM_STRUCTURE[country].keys())
-        league = st.selectbox(
-            "League",
-            options=[""] + leagues,
-            format_func=lambda x: x if x else "Select league",
-            key="league_select",
-        )
-    else:
-        league = ""
-
-    team_name = ""
-    if country and league:
-        teams_in_league = FM_STRUCTURE[country][league]
-        team_options = [""] + [CUSTOM_TEAM_LABEL] + teams_in_league
-        team_choice = st.selectbox(
-            "Team",
-            options=team_options,
-            format_func=lambda x: "Select team" if x == "" else x,
-            key="team_select",
-        )
-        if team_choice == CUSTOM_TEAM_LABEL:
-            team_name = st.text_input("Custom club name", key="team_custom_name").strip()
-        elif team_choice:
-            team_name = team_choice
-        else:
-            team_name = ""
-    else:
-        st.text_input("Custom club name", key="team_custom_name", value="", disabled=True)
-
-    st.subheader("Club logo")
-    logo_file = st.file_uploader(
-        "PNG file",
-        type=["png"],
-        key="club_logo_upload",
-    )
+
+# =========================
+# SIDEBAR: TEAM & LOGO UPLOAD
+# =========================
+
+with st.sidebar:
+    st.title("FM26 Squad Helper")
+
+    st.subheader("Team setup")
+
+    country_list = ["Indonesia"]
+    country = st.selectbox(
+        "Country",
+        options=[""] + country_list,
+        format_func=lambda x: x if x else "Select country",
+        key="country_select",
+    )
+
+    if country:
+        leagues = list(FM_STRUCTURE[country].keys())
+        league = st.selectbox(
+            "League",
+            options=[""] + leagues,
+            format_func=lambda x: x if x else "Select league",
+            key="league_select",
+        )
+    else:
+        league = ""
+
+    team_name = ""
+    if country and league:
+        teams_in_league = FM_STRUCTURE[country][league]
+        team_options = [""] + [CUSTOM_TEAM_LABEL] + teams_in_league
+        team_choice = st.selectbox(
+            "Team",
+            options=team_options,
+            format_func=lambda x: "Select team" if x == "" else x,
+            key="team_select",
+        )
+        if team_choice == CUSTOM_TEAM_LABEL:
+            team_name = st.text_input("Custom club name", key="team_custom_name").strip()
+        elif team_choice:
+            team_name = team_choice
+        else:
+            team_name = ""
+    else:
+        st.text_input("Custom club name", key="team_custom_name", value="", disabled=True)
+
+    st.subheader("Club logo")
+    logo_file = st.file_uploader(
+        "PNG file",
+        type=["png"],
+        key="club_logo_upload",
+    )
     if logo_file is not None:
         st.session_state.club_logo_bytes = logo_file.read()
 
 # Auto-recompute XI / bench / reserves when team & players exist
 if st.session_state.players and country:
-    recompute_squad_assignments(country)
-
-# =========================
-# LOGOS (TOP RIGHT, NORMAL FLOW)
-# =========================
-
-club_data_uri = bytes_to_data_uri(st.session_state.club_logo_bytes)
-flag_url = get_flag_url(st.session_state.get("country_select", ""))
-league_logo_url = get_league_logo_url(
-    st.session_state.get("country_select", ""),
-    st.session_state.get("league_select", ""),
-)
-
-logos_html_parts = []
-if flag_url:
-    logos_html_parts.append(f'<img src="{flag_url}" alt="Flag" />')
-if league_logo_url:
-    logos_html_parts.append(f'<img src="{league_logo_url}" alt="League" />')
-if club_data_uri:
-    logos_html_parts.append(f'<img src="{club_data_uri}" alt="Club" />')
-logos_html = "".join(logos_html_parts)
-
-# =========================
-# MAIN HEADER
-# =========================
-
-st.markdown(
-    f"### Team: {team_name or 'N/A'}  |  Country: {country or 'N/A'}  |  League: {league or 'N/A'}"
-)
-
-if logos_html:
-    st.markdown(
-        """
-        <style>
-        .fm26-top-right-logos-bar {
-            display: flex;
-            justify-content: flex-end;
-            gap: 4px;
-            margin-top: -28px;
-            margin-bottom: 8px;
-        }
-        .fm26-top-right-logos-bar img {
-            width: 32px;
-            height: auto;
-            border-radius: 4px;
-        }
-        </style>
-        """,
-        unsafe_allow_html=True,
-    )
-    st.markdown(
-        f'<div class="fm26-top-right-logos-bar">{logos_html}</div>',
-        unsafe_allow_html=True,
-    )
-
-st.markdown("---")
-
-# =========================
-# MAIN TABS
-# =========================
-
+    recompute_squad_assignments(country)
+
+# =========================
+# LOGOS (TOP RIGHT, NORMAL FLOW)
+# =========================
+
+club_data_uri = bytes_to_data_uri(st.session_state.club_logo_bytes)
+flag_url = get_flag_url(st.session_state.get("country_select", ""))
+league_logo_url = get_league_logo_url(
+    st.session_state.get("country_select", ""),
+    st.session_state.get("league_select", ""),
+)
+
+logos_html_parts = []
+if flag_url:
+    logos_html_parts.append(f'<img src="{flag_url}" alt="Flag" />')
+if league_logo_url:
+    logos_html_parts.append(f'<img src="{league_logo_url}" alt="League" />')
+if club_data_uri:
+    logos_html_parts.append(f'<img src="{club_data_uri}" alt="Club" />')
+logos_html = "".join(logos_html_parts)
+
+# =========================
+# MAIN HEADER
+# =========================
+
+st.markdown(
+    f"### Team: {team_name or 'N/A'}  |  Country: {country or 'N/A'}  |  League: {league or 'N/A'}"
+)
+
+if logos_html:
+    st.markdown(
+        """
+        <style>
+        .fm26-top-right-logos-bar {
+            display: flex;
+            justify-content: flex-end;
+            gap: 4px;
+            margin-top: -28px;
+            margin-bottom: 8px;
+        }
+        .fm26-top-right-logos-bar img {
+            width: 32px;
+            height: auto;
+            border-radius: 4px;
+        }
+        </style>
+        """,
+        unsafe_allow_html=True,
+    )
+    st.markdown(
+        f'<div class="fm26-top-right-logos-bar">{logos_html}</div>',
+        unsafe_allow_html=True,
+    )
+
+st.markdown("---")
+
+# =========================
+# MAIN TABS
+# =========================
+
 tab_players, tab_xi, tab_overview = st.tabs(
     ["Players", "XI", "Position overview"]
-)
-
-# =========================
-# TAB 2: PLAYERS
-# =========================
-
+)
+
+# =========================
+# TAB 2: PLAYERS
+# =========================
+
 with tab_players:
     st.header("Players")
 
     # Reset kun værdierne, ikke hele editor-UI'en
     if st.session_state.get("reset_player_form"):
         st.session_state.p_name_input = ""
         st.session_state.p_age_input = 20
         st.session_state.p_nat_existing = ""
         st.session_state.p_nat_new = ""
         st.session_state.p_positions = []
         st.session_state.p_current_band = ""
         st.session_state.p_current_league = ""
         st.session_state.p_potential_band = ""
         st.session_state.p_potential_league = ""
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
@@ -3055,81 +2528,81 @@ with tab_players:
                     "current_level_league": current_level_league,
                     "potential_band": potential_band,
                     "potential_level_league": potential_level_league,
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
-            st.success(f"Deleted player {player_to_edit}")
-
-    if not st.session_state.players:
-        st.info("No players yet.")
-    else:
-        rows = []
-        for p in st.session_state.players:
-            positions_str = ", ".join(p.get("positions") or [])
-            current_str = current_rating_display_overall(p)
-            potential_str = potential_rating_display(p)
-            rows.append(
-                {
-                    "Name": p.get("name", ""),
-                    "Positions": positions_str,
-                    "Current": current_str,
-                    "Potential": potential_str,
-                    "Age": p.get("age", ""),
-                    "Nationality": p.get("nationality", ""),
-                    "Injured": "Yes" if p.get("injured") else "",
-                    "Availability": p.get("availability", "Available"),
-                    "List": p.get("list_status", "None"),
-                }
-            )
-
-        df_players = pd.DataFrame(rows)
-        st.dataframe(df_players, use_container_width=True, hide_index=True)
-
-# =========================
-# TAB 3: POSITION OVERVIEW
-# =========================
-
+            st.success(f"Deleted player {player_to_edit}")
+
+    if not st.session_state.players:
+        st.info("No players yet.")
+    else:
+        rows = []
+        for p in st.session_state.players:
+            positions_str = ", ".join(p.get("positions") or [])
+            current_str = current_rating_display_overall(p)
+            potential_str = potential_rating_display(p)
+            rows.append(
+                {
+                    "Name": p.get("name", ""),
+                    "Positions": positions_str,
+                    "Current": current_str,
+                    "Potential": potential_str,
+                    "Age": p.get("age", ""),
+                    "Nationality": p.get("nationality", ""),
+                    "Injured": "Yes" if p.get("injured") else "",
+                    "Availability": p.get("availability", "Available"),
+                    "List": p.get("list_status", "None"),
+                }
+            )
+
+        df_players = pd.DataFrame(rows)
+        st.dataframe(df_players, use_container_width=True, hide_index=True)
+
+# =========================
+# TAB 3: POSITION OVERVIEW
+# =========================
+
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
@@ -3176,132 +2649,198 @@ def describe_xi_variant(idx: int) -> str:
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
-        # Formation selector (stored, not yet fully wired into the optimiser)
-        formation_options = ["Auto", "4-2-3-1", "5-2-1-2"]
-        current_formation = st.session_state.get("formation_mode", "Auto")
-        if current_formation not in formation_options:
-            current_formation = "Auto"
-
-        formation_choice = st.radio(
-            "Formation",
-            options=formation_options,
-            index=formation_options.index(current_formation),
-            horizontal=True,
-            key="formation_mode",
-        )
+        formations = st.session_state.get("formations") or []
+        formation_names = [f.get("name", "") for f in formations if f.get("name")]
+
+        with st.expander("Manage formations", expanded=not formations):
+            st.markdown("Add or remove custom formations. Each formation must have exactly 11 positions.")
+
+            with st.form("formation_creator"):
+                new_name = st.text_input("Formation name", key="formation_new_name")
+                pos_max = {pos: (3 if pos in {"CB", "CDM", "CAM", "ST"} else 1) for pos in POSITION_CHOICES}
+                pos_counts: dict[str, int] = {}
+
+                cols = st.columns(3)
+                for idx, pos in enumerate(POSITION_CHOICES):
+                    with cols[idx % 3]:
+                        pos_counts[pos] = st.number_input(
+                            f"{pos}",
+                            min_value=0,
+                            max_value=pos_max[pos],
+                            step=1,
+                            value=0,
+                            key=f"formation_count_{pos}",
+                        )
+
+                total_positions = sum(pos_counts.values())
+                st.markdown(f"**Total positions: {total_positions}/11**")
+
+                submitted = st.form_submit_button("Add formation")
+                if submitted:
+                    if not new_name.strip():
+                        st.error("Name is required.")
+                    elif new_name.strip().lower() in [n.strip().lower() for n in formation_names]:
+                        st.error("Formation name must be unique.")
+                    elif total_positions != 11:
+                        st.error("You must assign exactly 11 positions.")
+                    else:
+                        positions: list[str] = []
+                        for pos, count in pos_counts.items():
+                            positions.extend([pos] * int(count))
+                        st.session_state.formations.append({
+                            "name": new_name.strip(),
+                            "positions": positions,
+                        })
+                        st.session_state.formation_selected = new_name.strip()
+                        st.session_state.formation_mode = new_name.strip()
+                        st.success(f"Added formation '{new_name.strip()}'.")
+                        formation_names.append(new_name.strip())
+
+            if formation_names:
+                remove_choice = st.selectbox(
+                    "Remove formation",
+                    [""] + formation_names,
+                    format_func=lambda x: x or "Choose formation",
+                    key="formation_remove_choice",
+                )
+                if remove_choice:
+                    if st.button("Delete selected formation"):
+                        st.session_state.formations = [
+                            f for f in st.session_state.formations if f.get("name") != remove_choice
+                        ]
+                        if st.session_state.get("formation_selected") == remove_choice:
+                            st.session_state.formation_selected = ""
+                            st.session_state.formation_mode = ""
+                        st.success(f"Removed formation '{remove_choice}'.")
+                        formation_names = [f.get("name", "") for f in st.session_state.get("formations", []) if f.get("name")]
+
+        if formation_names:
+            current_formation = st.session_state.get("formation_selected") or st.session_state.get("formation_mode", "")
+            if current_formation not in formation_names:
+                current_formation = formation_names[0]
+
+            formation_choice = st.selectbox(
+                "Formation",
+                options=formation_names,
+                index=formation_names.index(current_formation),
+                key="formation_mode",
+            )
+            st.session_state.formation_selected = formation_choice
+        else:
+            st.info("Create a formation to start building your XI.")
 
         # How many XI variants do we have?
         variant_count = st.session_state.get("xi_variant_count", 0)
 
         rt = st.session_state.rules_tracker or {}
-        foreign_xi = rt.get("foreign_xi", 0)
-        foreign_xi_limit = rt.get("foreign_xi_limit", 7)
-        foreign_xi_bench = rt.get("foreign_xi_bench", 0)
-        foreign_xi_bench_limit = rt.get("foreign_xi_bench_limit", 9)
-        u23_domestic_xi = rt.get("u23_domestic_xi", 0)
-        u23_domestic_xi_min = rt.get("u23_domestic_xi_min", 1)
-
-        # ========== RULE TRACKER ==========
-        st.subheader("Rule tracker")
-
-        c1, c2, c3 = st.columns(3)
-
-        with c1:
-            ok = foreign_xi <= foreign_xi_limit
-            color = "green" if ok else "red"
-            st.markdown(
-                f"<span style='color:{color}; font-weight:bold;'>Foreign in XI: "
-                f"{foreign_xi}/{foreign_xi_limit}</span>",
-                unsafe_allow_html=True,
-            )
-            st.slider(
-                "Foreign in XI",
-                min_value=0,
-                max_value=foreign_xi_limit,
-                value=min(foreign_xi, foreign_xi_limit),
-                disabled=True,
-                label_visibility="collapsed",
-            )
-
-        with c2:
-            ok = foreign_xi_bench <= foreign_xi_bench_limit
-            color = "green" if ok else "red"
-            st.markdown(
-                f"<span style='color:{color}; font-weight:bold;'>Foreign in XI+Bench: "
-                f"{foreign_xi_bench}/{foreign_xi_bench_limit}</span>",
-                unsafe_allow_html=True,
-            )
-            st.slider(
-                "Foreign in XI + Bench",
-                min_value=0,
-                max_value=foreign_xi_bench_limit,
-                value=min(foreign_xi_bench, foreign_xi_bench_limit),
-                disabled=True,
-                label_visibility="collapsed",
-            )
-
+        foreign_xi = rt.get("foreign_xi", 0)
+        foreign_xi_limit = rt.get("foreign_xi_limit", 7)
+        foreign_xi_bench = rt.get("foreign_xi_bench", 0)
+        foreign_xi_bench_limit = rt.get("foreign_xi_bench_limit", 9)
+        u23_domestic_xi = rt.get("u23_domestic_xi", 0)
+        u23_domestic_xi_min = rt.get("u23_domestic_xi_min", 1)
+
+        # ========== RULE TRACKER ==========
+        st.subheader("Rule tracker")
+
+        c1, c2, c3 = st.columns(3)
+
+        with c1:
+            ok = foreign_xi <= foreign_xi_limit
+            color = "green" if ok else "red"
+            st.markdown(
+                f"<span style='color:{color}; font-weight:bold;'>Foreign in XI: "
+                f"{foreign_xi}/{foreign_xi_limit}</span>",
+                unsafe_allow_html=True,
+            )
+            st.slider(
+                "Foreign in XI",
+                min_value=0,
+                max_value=foreign_xi_limit,
+                value=min(foreign_xi, foreign_xi_limit),
+                disabled=True,
+                label_visibility="collapsed",
+            )
+
+        with c2:
+            ok = foreign_xi_bench <= foreign_xi_bench_limit
+            color = "green" if ok else "red"
+            st.markdown(
+                f"<span style='color:{color}; font-weight:bold;'>Foreign in XI+Bench: "
+                f"{foreign_xi_bench}/{foreign_xi_bench_limit}</span>",
+                unsafe_allow_html=True,
+            )
+            st.slider(
+                "Foreign in XI + Bench",
+                min_value=0,
+                max_value=foreign_xi_bench_limit,
+                value=min(foreign_xi_bench, foreign_xi_bench_limit),
+                disabled=True,
+                label_visibility="collapsed",
+            )
+
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
-            )
-
+            )
+
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
@@ -3634,51 +3173,51 @@ with tab_xi:
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
 
-                    formation_mode = st.session_state.get("formation_mode", "Auto")
+                    formation_mode = st.session_state.get("formation_mode", "")
 
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
@@ -3710,51 +3249,51 @@ with tab_xi:
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
 
-                    formation_mode = st.session_state.get("formation_mode", "Auto")
+                    formation_mode = st.session_state.get("formation_mode", "")
 
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
 
@@ -3769,51 +3308,51 @@ with tab_xi:
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
 
-                    st.dataframe(df_res, use_container_width=True, hide_index=True)
+                    st.dataframe(df_res, use_container_width=True, hide_index=True)
 
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
@@ -4031,104 +3570,82 @@ if surplus_players:
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
-        st.dataframe(df_loan, use_container_width=True, hide_index=True)
+        st.dataframe(df_loan, use_container_width=True, hide_index=True)
 
 with tab_overview:
     st.header("Position overview")
 
     # Always have players available for this tab
     players = st.session_state.players
 
     # Formation selector here mirrors the XI tab and also controls targets
-    formation_options = ["Auto", "4-2-3-1", "5-2-1-2"]
-    current_formation = st.session_state.get("formation_mode", "Auto")
-    if current_formation not in formation_options:
-        current_formation = "Auto"
-
-    formation_choice = st.radio(
-        "Formation (affects position coverage targets)",
-        options=formation_options,
-        index=formation_options.index(current_formation),
-        horizontal=True,
-        key="formation_mode_overview",
-    )
+    formations = st.session_state.get("formations") or []
+    formation_options = [f.get("name", "") for f in formations if f.get("name")]
+    current_formation = st.session_state.get("formation_selected") or st.session_state.get("formation_mode", "")
+    if formation_options and current_formation not in formation_options:
+        current_formation = formation_options[0]
+
+    if formation_options:
+        formation_choice = st.selectbox(
+            "Formation (affects position coverage targets)",
+            options=formation_options,
+            index=formation_options.index(current_formation) if current_formation in formation_options else 0,
+            key="formation_mode_overview",
+        )
+    else:
+        formation_choice = ""
+        st.info("Create a formation to view the position coverage targets.")
 
     # Build position counts depending on formation
-    if formation_choice == "4-2-3-1":
-        # Fixed template
-        formation_ip_positions = [
-            "GK",
-            "LB", "CB", "CB", "RB",
-            "CDM", "CM",
-            "CAM",
-            "LW", "RW",
-            "ST",
-        ]
-    elif formation_choice == "5-2-1-2":
-        formation_ip_positions = [
-            "GK",
-            "LWB", "CB", "CB", "RWB",
-            "CDM", "CM", "CM",
-            "CAM",
-            "ST", "ST",
-        ]
+    if formation_choice:
+        formation = get_formation_by_name(formation_choice)
+        formation_ip_positions = formation.get("positions", []) if formation else []
     else:
-        # AUTO: derive from the XI currently in use
-        xi_players_auto = [
-            p for p in players
-            if p.get("squad_role") == "XI"
-        ]
         formation_ip_positions = []
-        for p in xi_players_auto:
-            pos_ip = (p.get("assigned_position_ip") or "").upper()
-            if pos_ip:
-                formation_ip_positions.append(pos_ip)
-
-    formation_pos_counts = Counter(formation_ip_positions)
 
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
@@ -4216,31 +3733,31 @@ with tab_overview:
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
-
-# =========================
-# FINAL: SAVE STATE
-# =========================
-
-save_state_to_disk()
+
+# =========================
+# FINAL: SAVE STATE
+# =========================
+
+save_state_to_disk()
\ No newline at end of file
 
EOF
)
