import requests
import matplotlib.pyplot as plt
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

from src.match import analyze_match
from src.score import compute_score, clutch_rate, multikill_score


def get_match_scores(player_id, headers, limit):

    url = f"https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats"

    params = {
        "limit": limit,
        "offset": 0
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    matches = data.get("items", [])

    # функция для потоков
    def fetch(match):
        stats = match["stats"]
        match_id = stats.get("Match Id")

        if not match_id:
            return None

        advanced = analyze_match(match_id, player_id, headers)

        if not advanced:
            return None

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

        return compute_score(stat)

    # параллельно
    with ThreadPoolExecutor(max_workers=15) as executor:
        scores = list(executor.map(fetch, matches))

    # убрать None
    scores = [s for s in scores if s is not None]

    scores.reverse()

    return scores


def build_trend_chart(scores):

    plt.style.use("dark_background")

    fig, ax = plt.subplots(figsize=(7, 4))

    x = list(range(1, len(scores) + 1))

    ax.plot(
        x,
        scores,
        color="#4da3ff",
        linewidth=3,
        marker="o",
        markersize=6
    )

    ax.fill_between(
        x,
        scores,
        color="#4da3ff",
        alpha=0.25
    )

    ax.set_ylim(0, 100)

    ax.set_title("Mully Rating Trend")

    ax.set_xlabel("Matches")
    ax.set_ylabel("Mully Rating")

    ax.grid(True, linestyle="--", alpha=0.3)

    buf = BytesIO()

    plt.savefig(buf, format="png", bbox_inches="tight", dpi=180)

    buf.seek(0)

    plt.close()

    return buf