# Code adapted from fetch_media.py, crawl_feeds.py, & bhl_twarc.py

import argparse
import csv
import logging
import os
from os.path import join
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import urllib.request
import urllib.parse

dead_tweets = []
stale_tweets = []
live_tweets = []
new_tweets = []

dead_profiles = []
stale_profiles = []
live_profiles = []
new_profiles = []


def fetch_media_for_feed(feed_dict):

    # Loop through my list of folders
    for feeds in feed_dict:
        short_name = feeds
        feeds = join(feed_dir, feeds)
        media_dir = join(feeds, 'media')
        image_dir = join(media_dir, 'tweet_images')
        profile_images_dir = join(media_dir, 'profile_images')

    # Log creation
        logs_dir = join(media_dir, 'media_logs')
        log_file = join(logs_dir, 'twarc.log')

    # Loop through each folder and make directories
        for directory in [feed_dir, media_dir, logs_dir]:
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)
                print("Creating tweet image directory for {0}".format(image_dir))
            if not os.path.exists(profile_images_dir):
                os.makedirs(profile_images_dir)
                print("Creating profile image directory for {0}".format(profile_images_dir))
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
                print("Creating logs directory for {0}".format(logs_dir))

    # LOGGING formatting
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logger = logging.getLogger(short_name)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    # Setting up CSV dictionaries
        media_urls_csv = join(media_dir, 'tweet_images.csv')
        profile_image_csv = join(media_dir, 'profile_images.csv')

        media_urls = {}
        profile_image_urls = {}

        logger.info("Starting media downloads for %s", short_name)

    # Forcing the request to retry after a URLError
        retry_strategy = Retry(total=25,backoff_factor=60,status_forcelist=[429,500,502,503,504])
            # Retry the quest a maximum of 25 times with 60 seconds in between retries
        adapter = HTTPAdapter(max_retries=retry_strategy)
        # adapter = requests.adapters.HTTPAdapter(max_retries = 20)


    # Reading tweet_images.csv
        with open(media_urls_csv, 'r', newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url = row[0]
                filename = row[1]
                media_urls[url] = filename

    # Reading profile_images.csv
        with open(profile_image_csv, 'r', newline="") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url = row[0]
                profile_dir = row[1]
                filename = row[2]
                profile_image_urls[url] = {'profile_dir': profile_dir, 'filename': filename}

    # Download Tweet Media
        with requests.Session() as s:
            for url in media_urls:
            # Sort inactive URLs
                try:
                   status_code = urllib.request.urlopen(url)

                except urllib.error.HTTPError as e:
                    if e.getcode()==200:
                        live_tweets.append(url)
                    else:
                        if e.getcode() !=200:
                            print(e, url)
                            logger.info("{0} > {1}".format(e,url))
                            dead_tweets.append(url)

                except urllib.error.URLError as e:
                    logger.info("{0} stopped at > {1}".format(e,url))
                    print("{0} stopped at > {1}".format(e,url))
                    print("*** RETRY ADAPTER ACTIVATED ***")

                except requests.exceptions.Timeout as e:
                    logger.info("{0} stopped at > {1}".format(e,url))
                    print("{0} stopped at > {1}".format(e,url))

                except requests.exceptions.ConnectionError as e:
                    logger.info("{0} stopped at > {1}".format(e,url))
                    print("{0} stopped at > {1}".format(e,url))

            # Check if the image has already been downloaded
                if media_urls[url] in os.listdir(image_dir):
                    logger.info("OLD Tweet Media > {0}".format(url))
                    stale_tweets.append(url)
                    continue

            # If the image hasn't already been downloaded
                else:
                    new_tweets.append(url)
                    logger.info("FETCHING Tweet Media > {0}".format(url))
                    # sAdapt = s.mount('http://',adapter)
                    # media = sAdapt.get(url)
                    media = s.get(url)
                    media_file = join(image_dir, media_urls[url])
                    with open(media_file, 'wb') as media_out:
                        media_out.write(media.content)
                        print("Fetching Tweet Media > {0}".format(media_urls[url]))
                    time.sleep(1)


    # Downloading Profile Images
        with requests.Session() as s:
            for url in profile_image_urls:
                profile_dir_name = profile_image_urls[url]['profile_dir']
                filename = profile_image_urls[url]['filename']
                profile_dir = join(profile_images_dir, profile_dir_name)
                profile_folder = os.path.split(profile_dir)

                try:
                    response = urllib.request.urlopen(url)

                except urllib.error.HTTPError as e:
                    if e.getcode()==200:
                        live_profiles.append(url)
                    else:
                        if e.getcode() !=200:
                            print(e, url)
                            logger.info("{0} > {1}".format(e,url))
                            dead_profiles.append(url)

                except urllib.error.URLError as e:
                    logger.info("{0} stopped at > {1}".format(e,url))
                    print("{0} stopped at > {1}".format(e,url))
                    print("*** RETRY ADAPTER ACTIVATED ***")

                except requests.exceptions.Timeout as e:
                    logger.info("{0} stopped at > {1}".format(e,url))
                    print("{0} stopped at > {1}".format(e,url))

                except requests.exceptions.ConnectionError as e:
                    logger.info("{0} stopped at > {1}".format(e,url))
                    print("{0} stopped at > {1}".format(e,url))

            # Check if ID folder exists
                if not os.path.exists(profile_dir):
                    logger.info("CREATNG profile_dir > {0}: {1}".format(profile_folder[1],url))
                    os.makedirs(profile_dir)

                # Check if image exists in ID folder immediately after identifying the profile_dir
                    if filename not in os.listdir(profile_dir):
                        live_profiles.append(filename)
                        logger.info("FETCHING Profile Media > {0}: {1}".format(profile_folder[1],url))
                        # sAdapt = s.mount('http://',adapter)
                        # profile_image = sAdapt.get(url)
                        profile_image = s.get(url)
                        profile_image_file = join(profile_dir, filename)
                        with open(profile_image_file, 'wb') as profile_image_out:
                            profile_image_out.write(profile_image.content)
                        time.sleep(1)
                        print("FETCHING Profile Media > {0}: {1}".format(profile_folder[1],filename))
                    else:
                        stale_profiles.append(filename)

    return

fetch_media_for_feed(feed_dict)

print("\nDead Tweet Images:", len(dead_tweets))
print("Previously Downloadeded Tweet Images:", len(stale_tweets))
print("Newly Downloaded Tweet Images:", len(new_tweets))

print("\nDead Profile Images:", len(dead_profiles))
print("Previously Downloadeded Profile Images:", len(stale_profiles))
print("Newly Downloaded Profile Images:", len(new_profiles))
now = time.asctime(time.localtime(time.time()))
print("\nTwitter image downloads finished at: {0}".format(now))
