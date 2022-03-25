import os
import random
import re
import requests
import urllib.parse


def games_list(games):
    """Return list of unplayed games and list of games to replay."""

    # Initialize lists
    games_list, unplayed_list, replay_list = ([] for i in range(3))

    # Populate games_list with games that have not been played within the past two weeks
    for game in games:
        if "playtime_2weeks" not in game:
            games_list.append(game)

    # Populate unplayed and replay lists
    for game in games_list:
        if game["playtime_forever"] == 0:
            unplayed_list.append(game)
        else:
            replay_list.append(game)

    return unplayed_list, replay_list


def pick_game(games):
    """Return information for a random Steam game from a list of games."""

    # Loop until a full game (not DLC, episodes, etc.) is selected
    while True:

        # Initialize
        appid = random.choice(games)["appid"]
        gameinfo = []

        # Contact API
        try:
            url = f"https://store.steampowered.com/api/appdetails?appids={appid}&l=english"
            response = requests.get(url)
        except requests.RequestException:
            return None

        # Validate response
        try:
            if "data" in response.json()[f"{appid}"]:
                gameinfo = response.json()[f"{appid}"]["data"]
            if gameinfo["type"] == "game":
                return {
                    "name": gameinfo["name"],
                    "header_image": gameinfo["header_image"],
                    "short_description": gameinfo["short_description"],
                    "release": gameinfo["release_date"]["date"],
                    "genre": gameinfo["genres"],
                    "play": f"steam://run/{appid}",
                    "store": f"https://store.steampowered.com/app/{appid}"
                }
        except (KeyError, TypeError, ValueError):
            return None


def resolve_vanity(fullurl):
    """Resolve Steam CommunityID vanity URL."""

    # Take vanity URL from full URL
    vanity = fullurl.partition("/id/")[2].replace("/", "")

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={api_key}&vanityurl={urllib.parse.quote_plus(vanity)}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        resolve = response.json()["response"]["steamid"]
        return resolve
    except (KeyError, TypeError, ValueError):
        return None


def validate_url(url):
    """Validate Steam URL."""

    if re.search("steamcommunity.com/profiles/", url):
        return 0
    elif re.search("steamcommunity.com/id/", url):
        return 1
    else:
        return -1


def validate_id(steamid):
    """Validate SteamID, returning array of all owned games in library."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={urllib.parse.quote(steamid)}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        library = response.json()
        return library["response"]["games"]
    except (KeyError, TypeError, ValueError):
        return None