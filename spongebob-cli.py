#!/usr/bin/env python3
# This code is licensed under GNU General Public License v3.0. I encouruage you to do the same to the software you write!
# TODO: --binge, --download-all, --list {n:}

try:
    from bs4 import BeautifulSoup
    import requests, subprocess, sys
    from termcolor import colored

except:
    print("One or more library is missing! Check the list of libraries!")

episodes = []
counter = 0

print(colored("Fetching episodes. This might take a while.", "green"))

# It fetches the episodes from this link, So that episode is not avaliable.
raw = requests.get("https://www.megacartoons.net/help-wanted/").text
soup = BeautifulSoup(raw, "html.parser")

for data in soup.find_all("a", class_ = "btn btn-sm btn-default"):
    counter = counter + 1
    episodes.append(data.get("href"))

def ListEpisodes():
    counter = 0
    for data in soup.find_all("a", class_ = "btn btn-sm btn-default"):
        counter = counter + 1
        print("Episode", colored(":", "cyan"), data.get("title"), "[", colored(counter, "cyan" ), "]")
            

# This function get the direct mp4 link
def VideoSource(source):

    raw = requests.get(source).text
    soup = BeautifulSoup(raw, "html.parser")

    # This took me way to long to figure out, DONT TOUCH
    link = soup.find("input", {"name":"main_video_url"})["value"]
    return link

def Play(DirectLink):
    try:
        subprocess.run(["mpv", DirectLink])
    
    except:
        print("An error occured while tying to play the video! Make sure you have youtube-dl and mpv installed.")

def Download(source):
    try:
        subprocess.run(["youtube-dl", source])
    
    except:
        print("Downloading the video failed. Be sure to have youtube-dl installed.")

try:
    args = sys.argv[1]

except IndexError:
    args = "  " 

try:
    args2 = sys.argv[2]
except:
    pass

# Download Function
if args == "--download" or args == "-d":
    try:
        args2 = int(args2)
        real = VideoSource(episodes[args2 - 1])
        Download(real)

    except:
        print(colored("No arguments passed with download function or the index is out of range, aborting...!", "red"))

# List function
if args == "--list" or args == "-l":
    ListEpisodes()

# Play function
if args == "-p" or args == "--play":
    try:
        args2 = int(args2)
        real = VideoSource(episodes[args2 - 1])
        Play(real)
    
    except:
        print(colored("No arguments were passed with the play function or the index is out of range, aborting...", "red"))

if args == "-h" or args == "--help":
    print("""
    --download | -d, usage --download {a number of a episode}, This will download that video under a directory the command was run
    --list | -l,     usage --list, this will list all the episodes and then exit the programm
    --play | -p      usage --play {a number of a episode}, This will play the episode without listing the episodes
    --help | -h      usage --help this will print what each argument does
    """)

real = ""

# This is if no arguments were passed.
if args == "  ":
    ListEpisodes()
    print(colored("No arguments were passed. Default settings applied.", "green"), "\n")

    while(True):
        try:
            video_input = int(input("What episode do you want to watch? {type a number by the right side}: "))

        except:
            print(colored("You need to type a number!", "red"))
            
            # This is the only way to force the real variable to be empty.
            video_input = 99999
        
        try:
            real = VideoSource(episodes[video_input - 1])
            print(colored("Now playing:", "green"), real, "\n")
            Play(real)

        except:
            print("The video you chose is out of range or doesnt exist")
            real = ""

