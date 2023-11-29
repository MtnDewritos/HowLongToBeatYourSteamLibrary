import requests
import numpy as np


def get_game_names(steamid):
    r = requests.get(f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key=C230F278EB63BA4ABFC5E00F28524392&steamid={steamid}&format=json&include_appinfo=true")

    if r.status_code != 200:
        raise Exception(f"Failed to connect to steam API: \nError code: {r.status_code} \nJson: {r.json()}")

    response_dict = r.json()

    games = response_dict.get("response").get("games")

    name_list = []
    for game in games:
        name_list.append(game.get("name"))

    splits = []
    i = 100
    while i < len(name_list):
        splits.append(i)
        i += 100

    split_list = np.split(name_list, splits)
    return split_list