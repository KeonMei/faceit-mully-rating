import requests


def get_player_info(nickname, headers):

    url = "https://open.faceit.com/data/v4/players"

    params = {
        "nickname": nickname
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    if "errors" in data:
        return None

    player_id = data["player_id"]

    avatar = data.get("avatar")

    if avatar:
        avatar = avatar.strip()

    if not avatar or not avatar.startswith("http"):
        avatar = None

    country = data.get("country", "unknown")

    cs2 = data.get("games", {}).get("cs2", {})

    elo = cs2.get("faceit_elo", "N/A")
    level = cs2.get("skill_level", "N/A")

    return player_id, avatar, elo, level, country


def get_matches(player_id, headers, limit=30):

    url = f"https://open.faceit.com/data/v4/players/{player_id}/games/cs2/stats"

    params = {
        "limit": limit,
        "offset": 0
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Match API error: {response.status_code}")

    data = response.json()

    if "items" not in data:
        raise Exception("No matches found")

    matches = []

    for match in data["items"]:

        stats = match["stats"]

        matches.append({
            "match_id": stats.get("Match Id"),
            "ADR": float(stats.get("ADR", 0)),
            "KD": float(stats.get("K/D Ratio", 0)),
            "Kills": float(stats.get("Kills", 0)),
            "Deaths": float(stats.get("Deaths", 0)),
            "KR": float(stats.get("K/R Ratio", 0)),
            "MVPs": float(stats.get("MVPs", 0))
        })

    return matches