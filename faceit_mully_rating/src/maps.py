import requests
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from src.match import analyze_match
from src.score import compute_score, clutch_rate, multikill_score, score_tier


def get_map_stats(player_id, headers, limit=50):

    url = f"https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats"

    params = {
        "limit": limit,
        "offset": 0
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    matches = data.get("items", [])

    maps = defaultdict(list)

    # потоковая функция
    def fetch(match):

        stats = match["stats"]

        match_id = stats.get("Match Id")

        if not match_id:
            return None

        advanced = analyze_match(match_id, player_id, headers)

        if not advanced:
            return None

        map_name = (
            stats.get("Map")
            or stats.get("Map Name")
            or stats.get("Game Map")
            or "Unknown"
        )

        basic = {
            "ADR": float(stats.get("ADR", 0)),
            "KD": float(stats.get("K/D Ratio", 0)),
            "KR": float(stats.get("K/R Ratio", 0)),
            "MVP": float(stats.get("MVPs", 0))
        }

        stat = {}

        stat["ADR_avg"] = basic["ADR"]
        stat["KD_avg"] = basic["KD"]
        stat["KR_avg"] = basic["KR"]
        stat["MVP_avg"] = basic["MVP"]

        stat["entry"] = advanced["entry_success"]

        stat["1v1"] = clutch_rate(*advanced["1v1"])
        stat["1v2"] = clutch_rate(*advanced["1v2"])
        stat["1v3"] = clutch_rate(*advanced["1v3"])
        stat["1v4"] = clutch_rate(*advanced["1v4"])
        stat["1v5"] = clutch_rate(*advanced["1v5"])

        stat["multi"] = multikill_score(
            advanced["double"],
            advanced["triple"],
            advanced["quadra"],
            advanced["ace"],
            advanced["rounds"]
        )

        score = compute_score(stat)

        return map_name, score

    # параллельно
    with ThreadPoolExecutor(max_workers=15) as executor:
        results = list(executor.map(fetch, matches))

    for item in results:
        if not item:
            continue
        map_name, score = item
        maps[map_name].append(score)

    result = []

    for m, values in maps.items():
        avg_score = sum(values) / len(values)
        tier = score_tier(avg_score)
        result.append((m, round(avg_score, 1), tier, len(values)))

    result.sort(key=lambda x: x[1], reverse=True)

    return result