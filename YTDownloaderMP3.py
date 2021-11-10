import sys, os
import csv, re, json
from youtube_search import YoutubeSearch
from pytube import YouTube
from moviepy.editor import *

# Check given values by user
argv = sys.argv
if len(argv) != 3:
    print("Usage: python.exe .\\SpotifyDL.py <excel_file_path> <dl_path>")
    exit(1)


# Use function to stop output (MoviePy)
# Disable
def block_print():
    sys.stdout = open(os.devnull, 'w')
# Restore
def enable_print():
    sys.stdout = sys.__stdout__
def get_sec(time_str):
    """
    Get Seconds from time.
    
    """
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)


def extract_row_csv(csv_path):
    """
    Extract data from csv

    :param csv_path: path for the csv file to use
    :return: array of song_info
    """
    rows = []
    with open(csv_path, mode="r", encoding="Latin1") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for row in spamreader:
            if len(row) != 4:
                print("Bad Input for: ", row, "\r\nColumns are: Artist(s) Name, Track Name, Album Name, Length")
                continue
            row = [elt.strip() for elt in row] # remove any trailing whitespace
            row[0] = ';'.join([elt.strip() for elt in row[0].split(";")])
            rows.append(row)
    print("=====ROWS EXTRACTED=====\r\n")
    return rows

def youtube_dl_song(folder, song_info, row): # song_info is always an array of 4: Artist(s) Name, Track Name, Album Name, Length
    """
    Download one song from youtube

    :param folder: folder where download will save file
    :param song_info: array with song info
    :param row: number of current row
    :return: 
    """
    artists, track, album, length = song_info[0], song_info[1], song_info[2], song_info[3]
    first_artist = artists.split(' ')[0] # FIXME split could be ; also
    results = YoutubeSearch(track + " " + first_artist, max_results=10).to_json()
    print(row, "- Reseach: ", track, artists)
    if get_sec(length) > get_sec('00:08:00'):
        print("Song too long: skipped!")
        return
    first_track = None
    try:
        first_track = json.loads(results)["videos"][0]
    except:
        print("Fail to retrieve first track!")
        return

    title_real = first_track["title"]
    title = first_track["title"].encode().decode('ascii', 'replace').replace(u'\ufffd', '_')
    print("Track Found:", title, "\r\n")
    
    url = "https://youtube.com" + first_track["url_suffix"]
    filename_no_ext = folder + "/" + title
    if os.path.exists(filename_no_ext + ".mp3"): # if mp3 is already downloaded pass
        print("File Exists:", filename_no_ext + ".mp3")
        return
    YouTube(url).streams.filter(only_audio=True).first().download(filename=title+".mp4", output_path=folder)

    block_print()
    try:
        AudioFileClip(filename_no_ext + ".mp4").write_audiofile(filename_no_ext + ".mp3")
    except:
        # Remove old weird name
        os.remove(filename_no_ext + ".mp4")
        filename_no_ext = folder + "/" + str(row)
        YouTube(url).streams.filter(only_audio=True).first().download(filename=str(row)+".mp4", output_path=folder)
        AudioFileClip(filename_no_ext + ".mp4").write_audiofile(filename_no_ext + ".mp3")
    enable_print()
    try:
        os.remove(filename_no_ext + ".mp4")
    except:
        print("Could not remove mp4!")

    try:
        os.rename(filename_no_ext + ".mp3", folder + "/" + title_real + ".mp3")
    except:
        print("No rename - Fail")


def create_folders(folder, folder_dl):
    """
    Create folder

    :param folder: base folder for music DL
    :param folder_dl: folder chosen by user under base folder
    :return: 
    """
    try:
        os.mkdir(folder)
    except:
        print("Folder music present:", folder)

    try:
        os.mkdir(folder_dl)
    except:
        print("Folder music present:", folder_dl)

def main(argv):
    """
    Download one song from youtube

    :param argv: sys.argv 
    :return: 
    """
    if len(argv) != 3:
        print("Usage: python.exe .\\SpotifyDL.py <excel_file_path> <dl_path>")
        exit(1)

    folder = "musics"
    folder_dl = folder + "/" + argv[2]
    create_folders(folder, folder_dl)

    csv_path = argv[1]
    rows = extract_row_csv(csv_path)
    if rows == []:
        return
    i = 0
    if "Artist(s)" in rows[0] or "Track Name" in rows[0]:
        rows.pop(0)
    for row in rows:
        try:
            youtube_dl_song(folder_dl, row, i)
            i += 1
        except:
            print("Something Failed with row:", row)


main(argv)