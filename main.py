from __future__ import unicode_literals

import os
import re
import sys

import requests
import youtube_dl
from bs4 import BeautifulSoup

import config

prog_path = os.path.dirname(os.path.abspath(__file__))


def get_metadata(soup):
    # Retrieve Artist name
    metadata = {}
    artists = soup.select("a[href*=artist]")
    # Retrieve Event name
    event = soup.select_one("a[href*=event]").text
    # Combine artist names if b2b set
    artist = ' & '.join(rat.text for rat in artists)
    # Write data into dict
    metadata.update({'Artist': artist})
    metadata.update({'Event': event})
    # combine full filename
    return metadata


# Get setdata from LSDB and check for availability
def download_set(set_id):
    result = requests.get("https://lsdb.nl/set/" + set_id)
    if result.status_code == 200:
        soup = BeautifulSoup(result.content, "html.parser")
        # Check if youtube/mixcloud/soundcloud are available
        reg = re.compile(r'you|mixcloud|soundcloud')
        golink = [e for e in soup.find_all('a') if reg.match(e.text)]
        metadata = get_metadata(soup)
        # If youtube/mixcloud/soundcloud is available, letsgodownload
        if golink:
            follow_download_link("https://lsdb.nl" + golink[0]['href'], 'ytdl', metadata)
        # If not, try to download using archive.org
        else:
            reg = re.compile(r'archive.org')
            golink = [e for e in soup.find_all('a') if reg.match(e.text)]
            if golink:
                follow_download_link("https://lsdb.nl" + golink[0]['href'], 'direct', metadata)
            else:
                reg = re.compile(r'zippy')
                golink = [e for e in soup.find_all('a') if reg.match(e.text)]
                if golink:
                    print("Only a zippy link found, download manual here: " + "https://lsdb.nl" + golink[0]['href'],
                          metadata)
                else:
                    print("No download found, i'm sorry :(, set ID: " + set_id)
                    return

    else:
        print("Something went wrong while looking up download link. exiting..")
        sys.exit()


# Check go URL and get actual link
def follow_download_link(go_url, provider, metadata):
    # Actual link is behind a referral url.
    result = requests.get(go_url)
    if result.status_code == 200:
        soup = BeautifulSoup(result.content, "html.parser")
        # Get actual download link
        downloadlink = soup.find_all("a")
        # Debug purposes
        print(downloadlink[1].string)
        # Create event directory if not existing
        make_dir(metadata['Event'])
        # Actual download command (zippy not supported at this moment
        if provider == 'ytdl':
            yt_download(downloadlink[1].string, metadata)
        elif provider == 'direct':
            direct_download(downloadlink[1].string, metadata)
    else:
        print("Something went wrong. exiting program")
        sys.exit()


# checks if event directory exists, othewise creates it
def make_dir(event):
    if not os.path.exists(output + "/" + event):
        os.makedirs(output + "/" + event)


# Used for archive.org
def direct_download(link, metadata):
    print("start download using direct download")
    if link.find('/'):
        ext = link.rsplit('.', 1)[1]
        r = requests.get(link)
        with open(output + '/' + metadata['Event'] + '/' + metadata['Artist'] + " @ " + metadata['Event'] + "." + ext,
                  'wb') as f:
            f.write(r.content)
            print("download finished: " + metadata['Artist'] + " @ " + metadata['Event'])


def yt_download(link, metadata):
    download_location = output + '/' + metadata['Event'] + '/' + metadata['Artist'] + " @ " + metadata[
        'Event'] + '.%(ext)s'
    # Check config file if mp3 is needed, otherwise download mp3/m4a. Note: mp3 conversion make the scrape slow as fuck.
    if config.getboolean('DEFAULT', 'force_mp3'):
        ydl_opts = {'outtmpl': download_location, 'format': 'bestaudio/best', 'quiet': 'true',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                    }], }
    else:
        ydl_opts = {'outtmpl': download_location, 'quiet': 'true', 'format': 'bestaudio/best', }
    # Download the shit
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
        print(download_location)


if __name__ == '__main__':
    # Load arguments
    args = config.load_args()
    config = config.load_config()
    # If custom location is set, use it
    if args.output:
        output = args.output
    # If no custom location is set: use project directory
    else:
        output = prog_path
    # If ID is given, try to download the specific ID, error if something goes wrong
    if args.ID:
        download_set(args.ID)
    # If list with ID's is provided, loop through file and try download for each setID
    if args.list:
        try:
            f = open(args.list, "r")
            for line in f:
                try:
                    download_set(line)
                except:
                    print("something went wrong with setID: " + line)
        except:
            print("task failed successfully")
