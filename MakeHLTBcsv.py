import csv
import sys
from GetHLTBStats import get_names_times

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("You need to provide a steamid as an argument")
        quit()
    try:
        game_times_list = get_names_times(sys.argv[1])
        game_times_list.sort(key=lambda a: a[1])
        with open('Games.csv', 'w', encoding="utf-8", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Game", "Time to beat"])
            for (name, hours) in game_times_list:
                writer.writerow([name,str(hours).replace(".",",")])
    except Exception as e:
        print(f"Error: {e}")


    