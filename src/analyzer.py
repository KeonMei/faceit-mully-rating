from src.player import get_player_info, get_matches
from src.match import analyze_match
from src.score import clutch_rate, multikill_score, compute_score
from src.score import score_tier, pretty_rank, progress_bar
from concurrent.futures import ThreadPoolExecutor

def analyze_player(nickname, headers, match_limit=30):

    player_info = get_player_info(nickname, headers)

    if not player_info:
        return None

    player_id, avatar, elo, level, country = player_info

    matches = get_matches(player_id, headers, limit=match_limit)

    if not matches:
        return None

    totals = {
        "ADR": 0,
        "KD": 0,
        "KR": 0,
        "MVP": 0,
        "entry": 0,
        "double": 0,
        "triple": 0,
        "quadra": 0,
        "ace": 0,
        "rounds": 0,
        "1v1_w": 0, "1v1_c": 0,
        "1v2_w": 0, "1v2_c": 0,
        "1v3_w": 0, "1v3_c": 0,
        "1v4_w": 0, "1v4_c": 0,
        "1v5_w": 0, "1v5_c": 0
    }

    match_scores = []
    match_maps = []

    matches_count = 0

    # -----------------PARALEL FUNCTION------------------
    def fetch_advanced(match):
        match_id = match.get("match_id")
        if not match_id:
            return None
        return analyze_match(match_id, player_id, headers)

    # --------------PARALEL EJ---------------------------------------------
    with ThreadPoolExecutor(max_workers=15) as executor:
        advanced_results = list(executor.map(fetch_advanced, matches))

    # -------------RESULT FEDBACK----------------
    for match, advanced in zip(matches, advanced_results):

        if not advanced:
            continue

        matches_count += 1

        totals["ADR"] += match["ADR"]
        totals["KD"] += match["KD"]
        totals["KR"] += match["KR"]
        totals["MVP"] += match["MVPs"]

        totals["entry"] += advanced["entry_success"]

        totals["double"] += advanced["double"]
        totals["triple"] += advanced["triple"]
        totals["quadra"] += advanced["quadra"]
        totals["ace"] += advanced["ace"]

        totals["rounds"] += advanced["rounds"]

        totals["1v1_c"] += advanced["1v1"][0]
        totals["1v1_w"] += advanced["1v1"][1]

        totals["1v2_c"] += advanced["1v2"][0]
        totals["1v2_w"] += advanced["1v2"][1]

        totals["1v3_c"] += advanced["1v3"][0]
        totals["1v3_w"] += advanced["1v3"][1]

        totals["1v4_c"] += advanced["1v4"][0]
        totals["1v4_w"] += advanced["1v4"][1]

        totals["1v5_c"] += advanced["1v5"][0]
        totals["1v5_w"] += advanced["1v5"][1]

        stat = {
            "ADR_avg": match["ADR"],
            "KD_avg": match["KD"],
            "KR_avg": match["KR"],
            "MVP_avg": match["MVPs"],
            "entry": advanced["entry_success"],
            "1v1": clutch_rate(*advanced["1v1"]),
            "1v2": clutch_rate(*advanced["1v2"]),
            "1v3": clutch_rate(*advanced["1v3"]),
            "1v4": clutch_rate(*advanced["1v4"]),
            "1v5": clutch_rate(*advanced["1v5"]),
            "multi": multikill_score(
                advanced["double"],
                advanced["triple"],
                advanced["quadra"],
                advanced["ace"],
                advanced["rounds"]
            )
        }

        match_scores.append(compute_score(stat))
        match_maps.append(match.get("map", "Unknown"))

    if matches_count == 0:
        return None

    stats = {}

    stats["ADR_avg"] = totals["ADR"] / matches_count
    stats["KD_avg"] = totals["KD"] / matches_count
    stats["KR_avg"] = totals["KR"] / matches_count
    stats["MVP_avg"] = totals["MVP"] / matches_count

    stats["entry"] = totals["entry"] / matches_count

    stats["1v1"] = clutch_rate(totals["1v1_w"], totals["1v1_c"])
    stats["1v2"] = clutch_rate(totals["1v2_w"], totals["1v2_c"])
    stats["1v3"] = clutch_rate(totals["1v3_w"], totals["1v3_c"])
    stats["1v4"] = clutch_rate(totals["1v4_w"], totals["1v4_c"])
    stats["1v5"] = clutch_rate(totals["1v5_w"], totals["1v5_c"])

    stats["multi"] = multikill_score(
        totals["double"],
        totals["triple"],
        totals["quadra"],
        totals["ace"],
        totals["rounds"]
    )

    score = compute_score(stats)

    bar = progress_bar(score)

    tier = score_tier(score)

    rank = pretty_rank(tier)

    def country_flag(code):
        if not code or len(code) != 2:
            return ""
        return chr(127397 + ord(code[0].upper())) + chr(127397 + ord(code[1].upper()))

    flag = country_flag(country)

    return score, rank, bar, matches_count, avatar, elo, level, flag, match_scores, match_maps