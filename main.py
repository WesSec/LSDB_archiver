from __future__ import unicode_literals

import os
import re
import sys

import requests
import youtube_dl
from bs4 import BeautifulSoup

import config

prog_path = os.path.dirname(os.path.abspath(__file__))


def DownloadSet(setID):
	result = requests.get("https://lsdb.nl/set/" + setID)
	if result.status_code == 200:
		# Check if youtube/mixcloud/soundcloud is available
		soup = BeautifulSoup(result.content, "html.parser")
		reg = re.compile(r'you|mixcloud|soundcloud')
		golink = [e for e in soup.find_all('a') if reg.match(e.text)]
		# If youtube/mixcloud/soundcloud is available, letsgodownload
		if golink:
			FollowDownloadLink("https://lsdb.nl" + golink[0]['href'], 'ytdl')
		else:
			reg = re.compile(r'archive.org')
			golink = [e for e in soup.find_all('a') if reg.match(e.text)]
			if golink:
				FollowDownloadLink("https://lsdb.nl" + golink[0]['href'], 'direct')
			else:
				reg = re.compile(r'you|mixcloud|soundcloud')
				golink = [e for e in soup.find_all('a') if reg.match(e.text)]
				if golink:
					print("Only a zippy link found, download manual here: " + "https://lsdb.nl" + golink[0]['href'])
				else:
					print("No link found, i'm sorry :(, set ID: " + setID)
					return

	else:
		print("Something went wrong while looking up download link. exiting..")
		sys.exit()


def FollowDownloadLink(go_url, provider):
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
	args = config.loadargs()
	config = config.Load_config()
	if args.output:
		output = args.output
	else:
		output = prog_path
	if args.ID:
		try:
			DownloadSet(str(args.ID))
		except:
			print("something went wrong, please double check your set ID")
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
