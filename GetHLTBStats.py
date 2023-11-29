import asyncio
import platform
import re
from howlongtobeatpy import HowLongToBeat
from GetSteamGames import get_game_names


def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

def strip_crap(string):
    words = string.split(" ")
    if words[-1].lower() == "edition":
        string = " ".join(words[:-2])
    if words[-1].lower() == "player":
        string = " ".join(words[:-2])
    if words[-1].lower() == "singleplayer":
        string = " ".join(words[:-1])
    return string    

async def gather_with_concurrency(n, *coros):
    semaphore = asyncio.Semaphore(n)

    async def sem_coro(coro):
        async with semaphore:
            return await coro
    return await asyncio.gather(*(sem_coro(c) for c in coros))

async def get_game_times_to_beat(name_list):
    coroutines = [get_time_to_beat(name) for name in name_list]
    results = await gather_with_concurrency(128, *coroutines)
    return results
        
async def get_time_to_beat(game_name):
    async with asyncio.Semaphore(128):
        game_name = strip_crap(game_name)
        results_list = await HowLongToBeat().async_search(game_name.lower())
        if results_list is not None and len(results_list) > 0:
            best_element = max(results_list, key=lambda element: element.similarity)
            print(f"found name: {best_element.game_name}, searched name: {game_name}")
            value = (best_element.game_name, best_element.main_story)
        else:
            #print(f"{game_name} not found")
            game_name = strip_non_ascii(game_name)
            game_name = re.sub("\(.*\)|\s-\s.*", "", game_name)
            game_name = game_name.replace(":", "")
            game_name = game_name.replace("&", "and")
            results_list = await HowLongToBeat().async_search(game_name.lower())
            if results_list is not None and len(results_list) > 0:
                best_element = max(results_list, key=lambda element: element.similarity)
                print(f"found name: {best_element.game_name}, searched name: {game_name}")
                value = (best_element.game_name, best_element.main_story)
            else:
                value = (game_name, -1.0)
        return value
    
        
def get_names_times(steamid):
    if platform.system()=='Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    results_list = []
    try:
        print("Getting games list from steam")
        game_names = get_game_names(steamid)
    except Exception as e:
        raise e
    for name_list in game_names:
        print("getting how long to beat, please wait")
        results = asyncio.run(get_game_times_to_beat(name_list))
        results_list.extend(results)
    results_dict = dict(results_list)
    keys_to_remove = []
    not_found_keys = []
    for key in results_dict:
        if results_dict[key] == -1.0:
            not_found_keys.append(key)
            keys_to_remove.append(key)
        if results_dict[key] == 0.0:
            print(f"{key} has a playtime of 0, skipping")
            keys_to_remove.append(key)
    for key in not_found_keys:
        print(f"{key} not found")
    for key in keys_to_remove:
        results_dict.pop(key)
    res_list = []
    for key in results_dict:
        res_list.append((key, results_dict[key]))

    return res_list
