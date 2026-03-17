import requests

match_cache = {}

def analyze_match(match_id, player_id, headers):

    if match_id in match_cache:
        return match_cache[match_id]

    url = f"https://open.faceit.com/data/v4/matches/{match_id}/stats"

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None

        data = response.json()

    except:
        return None

    if "rounds" not in data or not data["rounds"]:
        return None

    round_data = data["rounds"][0]

    rounds = int(round_data.get("round_stats", {}).get("Rounds", 0))

    for team in round_data.get("teams", []):
        for player in team.get("players", []):

            if player.get("player_id") == player_id:

                stats = player.get("player_stats", {})

                result = {
                    "rounds": rounds,
                    "entry_success": float(stats.get("Match Entry Success Rate", 0)),
                    "1v1": (int(stats.get("1v1Count", 0)), int(stats.get("1v1Wins", 0))),
                    "1v2": (int(stats.get("1v2Count", 0)), int(stats.get("1v2Wins", 0))),
                    "1v3": (int(stats.get("1v3Count", 0)), int(stats.get("1v3Wins", 0))),
                    "1v4": (int(stats.get("1v4Count", 0)), int(stats.get("1v4Wins", 0))),
                    "1v5": (int(stats.get("1v5Count", 0)), int(stats.get("1v5Wins", 0))),
                    "double": int(stats.get("Double Kills", 0)),
                    "triple": int(stats.get("Triple Kills", 0)),
                    "quadra": int(stats.get("Quadro Kills", 0)),
                    "ace": int(stats.get("Penta Kills", 0))
                }

                match_cache[match_id] = result  # 🔥 КЭШ

                return result

    return None