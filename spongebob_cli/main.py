#!/usr/bin/env python3
# This code is licensed under GNU General Public License v3.0. I encouruage you to do the same to the software you write!

# TODO: queee {1-10} this will play first to tenth episode |  queee {1 2 3} This will play first, second and third episode

try:
    import requests, subprocess, sys, random, time, os, webbrowser
    from bs4 import BeautifulSoup
    from termcolor import colored
    from prettytable import PrettyTable
    from urllib.error import HTTPError
    from halo import Halo
   
    # local file, func.py
    from func import httperror_assess
    
except ImportError or ModuleNotFoundError:
    # Using python color codes instead of termcolor if it isn't found
    raise SystemExit("\033[0;31;40mOne or more library is missing! Check the list of libraries!\033[0;37;40m")
    
            
def ListEpisodes(limit_real, soup):
    counter = 0
    table = PrettyTable()
    
    episode_number = []
    episode_title = []

    # Get first episode (class is "btn btn-sm btn-default series-current" instead of "btn btn-sm btn-default")
    data = soup.find("a", class_ = "btn btn-sm btn-default series-current")
    counter += 1
    episode_title.append(data.get("title"))
    episode_number.append(colored(counter, "cyan" ))

    for data in soup.find_all("a", class_ = "btn btn-sm btn-default", limit = limit_real):        
        counter += 1
        episode_title.append(data.get("title"))
        episode_number.append(colored(counter, "cyan" ))
    
    table.add_column("Title", episode_title)
    table.add_column("Episode", episode_number)
    
    table.align["Title"] = "l"
    print(table)


# This function get the direct mp4 link
@Halo(text="Getting video source", spinner="shark", color="green")
def VideoSource(source):

    raw = requests.get(source).text
    soup = BeautifulSoup(raw, "html.parser")

    # This took me way to long to figure out, DONT TOUCH
    link = soup.find("input", {"name":"main_video_url"})["value"]
    return link

# It used to just void the output of MPV but since that was introduces half of the episdoes failed to play. Thats why its no longer voiding the MPV output
# This function for some reason randomly fails and need to be fixed ASAP
def Play(DirectLink):
    
    check = input(colored("Do you want to play this video in browser(1), mpv(2), or fullscreen-mpv(3) {default fullscreen-mpv}: ", "cyan"))

    if check in ("1", "browser"):
        print(DirectLink)
        webbrowser.open_new_tab(DirectLink)

    elif check in ("2", "mpv"):
        try:
            subprocess.run(["mpv", DirectLink])
                
        except subprocess.CalledProcessError:
            print(colored("\nAn error occured while tying to play the video! Make sure you have mpv or youtube-dl installed.", "red"))

    else:

        try:
            subprocess.run(["mpv", "--fs", DirectLink])
                
        except subprocess.CalledProcessError:
            print(colored("\nAn error occured while tying to play the video! Make sure you have mpv or youtube-dl installed.", "red"))
    
    
@Halo(text="Downloading episode.", spinner="shark", color="green")
def Download(source):
    try:
        subprocess.run(["youtube-dl", source],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT)
         
        print(colored("\nDownload complete!", "green"))
    
    except ImportError or subprocess.CalledProcessError:
        print(colored("Downloading the video failed. Be sure to have youtube-dl installed.", "red"))


def main():
    episodes = []
    counter = 0

    # It fetches the episodes from this link, So that episode is not avaliable.
    # Historically this used to be help wanted episode, but since it was the first episode it was changed to the last
    try:
        link = "https://www.megacartoons.net/truth-or-square/"
        raw = requests.get(link).text
        soup = BeautifulSoup(raw, "html.parser")

    except HTTPError as e:
        httperror_assess(e.code)    

    # This is to fetch all the episodes links
    # Get first episode (class is "btn btn-sm btn-default series-current" instead of "btn btn-sm btn-default")
    data = soup.find("a", class_ = "btn btn-sm btn-default series-current")
    episodes.append(data.get("href"))
    counter += 1
    for data in soup.find_all("a", class_ = "btn btn-sm btn-default"):
        counter += 1
        episodes.append(data.get("href"))


    try:
        args = sys.argv[1]
    except IndexError:
        args = ''

    try:
        args2 = sys.argv[2]
    except:
        pass


    # Download Function
    try:
        if args.replace(' ', '') in ["--download", "-d"]:
            try:
                args2 = int(args2)
                print(f"Downloading episode {colored(args2, 'cyan')}")
                Download(VideoSource(episodes[args2 - 1]))

            except IndexError or ValueError:
                print(colored("No arguments passed with download function or the index is out of range, aborting...!", "red"))

        # Dowload all
        elif args.replace(' ', '') in ["--download-all", "-da"]:
            dled = 0
            try:
                print(colored(f"Downloading all fetched episodes : {len(episodes)}", "green"))

                for x in range(len(episodes)):
                    print(f"Downloading episode {colored(x+1, 'cyan')}")
                    Download(VideoSource(episodes[x+1]))
                    print(f"Episode {x+1} downloaded!", end="") ; time.sleep(2) ; print("\r", end="")
                    dled += 1
                    continue
                
                print(colored(f"All {len(episodes)} are downloaded!", "green"))

            except HTTPError as e:
                httperror_assess(e.code)
                
            finally:
                print(colored(f"{dled} episodes were downloaded."))
            
        elif args.replace(' ', '') in ["--binge", "-b"]:
            try:
                print("Playing every episode from beggining")

                for x in range(len(episodes)):
                    print(f"Playing episode {x + 1}", end = "")
                    Play(VideoSource(episodes[x + 1]))                
                    time.sleep(2) ; print("\r", end="")
                    continue

            except HTTPError as e:
                httperror_assess(e.code)

        # List function
        elif args.replace(' ', '') in ["--list", "-l"]:
            try:
                ListEpisodes(int(args2), soup)

            except:
                # 3xx is replaced with len(episodes) to avoid error, if ever the fetched episodes if
                # less than 3xx (it is 399 or 339 I think, if I remember correctly)
                ListEpisodes(len(episodes), soup)

        # Play function
        elif args.replace(' ', '') in ["--play", "-p"]:
            try:
                args2 = int(args2)
                Play(VideoSource(episodes[args2 - 1]))
            
            except ValueError or IndexError:
                print(colored("No arguments were passed with the play function or the index is out of range, aborting...", "red"))

        elif args.replace('  ', '') in ['--update', "-u"]:
            print(colored("This is higly experimental and only works if you have installed spongebob-cli with git clone command!", "red"))
            sys.subprocess(["git", "fetch"])

        elif args.replace('  ', '') in ["--random", "-r"]:
            real = VideoSource(episodes[random.randint(1, len(episodes))])
            print(colored("You are now watching: ", "green"), real)
            Play(real)

        elif args.replace(' ', '') in ["--help", "-h"]:
            print("""
            --download | -d, usage --download {a number of a episode}, This will download that video under a directory the command was run
            --download-all | -da, usage --download-all, This will download every video spongebob video it scrapes
            --binge | -b , usage spongebob-cli --binge, This is used to start the first episode to the last
            --list | -l, usage --list, this will list all the episodes and then exit the programm
            --list | -l, usage --list {number} this will show the number of episodes with the limit you provided.
            --play | -p, usage --play {a number of a episode}, This will play the episode without listing the episodes
            --random | -r, usage spongebob-cli --random, This will play a random episode
            --help | -h, usage --help this will print what each argument does
            """)

        # This is if no arguments were passed.
        else:
            while True:
                if sys.platform != "win32":
                    os.system("clear")
                else:
                    os.system("cls")
                ListEpisodes(len(episodes), soup)
                print(colored("No arguments were passed. Default settings applied.\n", "green"))

                try:
                    video_input = input("What episode do you want to watch? (type a number by the right side or `q` to quit): ").replace(' ', '')
                    video_input = int(video_input)
                    
                except ValueError or AttributeError:
                    if video_input in ["exit", "quit", "close", 'q']:
                        raise SystemExit("Quitting the program!")
                    
                    print(colored("You need to type a number!", "red"))
                    continue

                except IndexError:
                    print("The video you chose is out of range or doesnt exist")
                    continue
                
                else:
                    real = VideoSource(episodes[video_input - 1])
                    print(colored(f"Now playing: {real}\n", "green"))
                    Play(real)         
    

    except KeyboardInterrupt:
        raise SystemExit(colored("\nUser interruped with the operation, aborting.", "red"))

if __name__ == "__main__":
    main()