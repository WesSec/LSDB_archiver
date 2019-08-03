from __future__ import unicode_literals

import os
import re
import sys

import requests
import youtube_dl
from bs4 import BeautifulSoup

import config

prog_path = os.path.dirname(os.path.abspath(__file__))


def GetMetadata(soup):
	# Retrieve Artist name
	metadata = {}
	artists = soup.select("a[href*=artist]")
	# Retrieve Event name
	event = soup.select_one("a[href*=event]").text
	# Combine artist names if b2b set
	artist = ' & '.join(rat.text for rat in artists)
	metadata.update({'Artist': artist})
	# combine full filename
	return artist + " @ " + event

def DownloadSet(setID):
	result = requests.get("https://lsdb.nl/set/" + setID)
	if result.status_code == 200:
		soup = BeautifulSoup(result.content, "html.parser")
		# Check if youtube/mixcloud/soundcloud are available
		reg = re.compile(r'you|mixcloud|soundcloud')
		golink = [e for e in soup.find_all('a') if reg.match(e.text)]
		filename = GetMetadata(soup)
		# If youtube/mixcloud/soundcloud is available, letsgodownload
		if golink:
			FollowDownloadLink("https://lsdb.nl" + golink[0]['href'], 'ytdl', filename)
		# If not, try to download using archive.org
		else:
			reg = re.compile(r'archive.org')
			golink = [e for e in soup.find_all('a') if reg.match(e.text)]
			if golink:
				FollowDownloadLink("https://lsdb.nl" + golink[0]['href'], 'direct', filename)
			else:
				reg = re.compile(r'zippy')
				golink = [e for e in soup.find_all('a') if reg.match(e.text)]
				if golink:
					print("Only a zippy link found, download manual here: " + "https://lsdb.nl" + golink[0]['href'],
					      filename)
				else:
					print("No download found, i'm sorry :(, set ID: " + setID)
					return

	else:
		print("Something went wrong while looking up download link. exiting..")
		sys.exit()


def FollowDownloadLink(go_url, provider, filename):
	# Actual link is behind a referral url.
	result = requests.get(go_url)
	if result.status_code == 200:
		soup = BeautifulSoup(result.content, "html.parser")
		# Get actual download link
		downloadlink = soup.find_all("a")
		# Debug purposes
		print(downloadlink[1].string)
		# Actual download command (zippy not supported at this moment
		if provider == 'ytdl':
			ytdownload(downloadlink[1].string)
		elif provider == 'direct':
			directdownload(downloadlink[1].string)
	else:
		print("Something went wrong. exiting program")
		sys.exit()


# Used for archive.org
def directdownload(link):
	print("start download using direct download")
	if link.find('/'):
		filename = link.rsplit('/', 1)[1]
		r = requests.get(link)
		with open(output + '/' + filename, 'wb') as f:
			f.write(r.content)
			print("download finished: " + filename)


def ytdownload(link):
	# Check config file if mp3 is needed, otherwise download mp3/m4a. Note: mp3 conversion make the scrape slow as fuck.
	if config.getboolean('DEFAULT', 'force_mp3'):
		ydl_opts = {'outtmpl': output + '/%(title)s.%(ext)s', 'format': 'bestaudio/best', 'quiet': 'true',
		            'postprocessors': [{
			            'key': 'FFmpegExtractAudio',
			            'preferredcodec': 'mp3',
		            }], }
	else:
		ydl_opts = {'outtmpl': output + '/%(title)s.%(ext)s', 'quiet': 'true', 'format': 'bestaudio/best', }
	# Download the shit
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([link])
		# Get info from video, which is used for recalling the file
		info_dict = ydl.extract_info(link, download=False)
		filename = info_dict.get('title', None)
	print(filename)


if __name__ == '__main__':
	# Load arguments
	args = config.loadargs()
	config = config.Load_config()
	# If custom location is set, use it
	if args.output:
		output = args.output
	# If no custom location is set: use project directory
	else:
		output = prog_path
	# If ID is given, try to download the specific ID, error if something goes wrong
	if args.ID:
		DownloadSet(args.ID)
	# If list with ID's is provided, loop through file and try download for each setID
	if args.list:
		try:
			f = open(args.list, "r")
			for line in f:
				try:
					DownloadSet(line)
				except:
					print("something went wrong with setID: " + line)
		except:
			print("task failed successfully")
