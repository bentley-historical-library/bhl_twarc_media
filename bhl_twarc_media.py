# Code adapted from fetch_media.py, crawl_feeds.py, & bhl_twarc.py

import argparse
import csv
import logging
import os
from os.path import join
import requests
import time
import urllib.request
import urllib.parse


dead_tweets = []
stale_tweets = []
del_tweets = []
new_tweets = []

dead_profiles = []
stale_profiles = []
del_profs = []
new_profiles = []

profile_image_urls = {}
media_urls = {}

def fetch_media_for_feed(feed_dict):
## Loop through list of folders
    for feeds in feed_dict:
        global short_name
        global feed
        global media_dir
        global image_dir
        global profile_images_dir
        global logger

        short_name = feeds
        feed = join(feed_dir, feeds)
        media_dir = join(feed, 'media')
        image_dir = join(media_dir, 'tweet_images')
        profile_images_dir = join(media_dir, 'profile_images')

    ## Log creation
        logs_dir = join(media_dir, 'media_logs')
        log_file = join(logs_dir, 'media.log')


    ## Loop through each individual folder and make directories
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

    ## LOGGING formatting
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        logger = logging.getLogger(short_name)
        handler = logging.FileHandler(log_file)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    ## Setting up CSV dictionaries
        media_urls_csv = join(media_dir, 'tweet_images.csv')
        profile_image_csv = join(media_dir, 'profile_images.csv')

    ## Turn on the logger
        logger.info("Starting media downloads for %s", short_name)

## ============================================
## ===== Sorting ===== Tweet ===== Images =====
## ============================================
## Reading tweet_images.csv
    with open(media_urls_csv, 'r', newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            url = row[0]
            filename = row[1]
            media_urls[url] = filename

    ## If TWEET image already exists
        print("Sorting TWEETS...")
        for url in media_urls:
            if media_urls[url] not in os.listdir(image_dir):
                try:
                    status_code = urllib.request.urlopen(url)
                except urllib.error.HTTPError as e:
                    logger.info("{0} > {1}".format(e, url))
                if status_code.getcode() == 200:
                    continue
                else:
                    dead_tweets.append(url)
                    del_tweets.append(url)
                    continue
    ## If TWEET image doesn't exist
            else:
                logger.info("OLD Tweet Media > {0}".format(url))
                stale_tweets.append(url)
                del_tweets.append(url)

        for x in del_tweets:
            if x in media_urls.keys():
                del media_urls[x]
            else:
                continue
        get_tweets(media_urls)

## ==============================================
## ===== Sorting ===== Profile ===== Images =====
## ==============================================
## Reading profile_images.csv
    with open(profile_image_csv, 'r', newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            url = row[0]
            profile_dir = row[1]
            filename = row[2]
            profile_image_urls[url] = {'profile_dir': profile_dir, 'filename': filename}

    ## Sorting
        print("Sorting PROFILES...")
        for url in profile_image_urls:
            profile_dir_name = profile_image_urls[url]['profile_dir']
            filename = profile_image_urls[url]['filename']
            profile_dir = join(profile_images_dir, profile_dir_name)
            profile_folder = os.path.split(profile_dir)

    ## Check for new profile directories 1st
            if os.path.isdir(profile_dir) == False:
                try:
                    res = urllib.request.urlopen(url)
                except urllib.error.HTTPError as e:
                    logger.info("{0} > {1}".format(res, url))
                if res.getcode() != 200:
                    logger.info("{0} > {1}".format(res, url))
                    dead_profiles.append(url)
                    del_profs.append(url)
                else:
                    os.makedirs(profile_dir)
                    logger.info("CREATNG profile_dir > {0}: {1}".format(profile_folder[1], filename))
                    print(("CREATNG profile_dir > {0}: {1}".format(profile_folder[1], filename)))

       ## If profile_dir already exists
            if os.path.exists(profile_dir):
            ## If image already exists
                if filename in os.listdir(profile_dir):
                    ## URL won't delete Directory later
                    stale_profiles.append(url)
                    del_profs.append(url)
                    logger.info("OLD Profile Media > {0}: {1}".format(profile_folder[1], filename))
            ## If profile_dir exists but not image
                else:
                    if filename not in os.listdir(profile_dir):
                        try:
                            res = urllib.request.urlopen(url)
                        except urllib.error.HTTPError as e:
                            logger.info("{0} > {1}".format(res, url))
                        if res.getcode() != 200:
                            logger.info("{0} > {1}".format(res, url))
                            dead_profiles.append(url)
                            del_profs.append(url)
                        else:
                            continue

        for x in del_profs:
            if x in profile_image_urls.keys():
                del profile_image_urls[x]
            else:
                continue

        get_profs(profile_image_urls)
    return

def get_tweets(media_urls):
    if len(media_urls) != 0:
        print("Fetching Tweets...")
        for url in media_urls:
            global logger
            logger = logging.getLogger(short_name)
            with requests.Session() as s:
                # print("2nd loop > {}".format(url))
                logger.info("FETCHING Tweet Media > {0}".format(url))
                print("Fetching Tweet Media > {0}".format(media_urls[url]))
                media = s.get(url)
                media_file = join(image_dir, media_urls[url])
                with open(media_file, 'wb') as media_out:
                    media_out.write(media.content)
                new_tweets.append(url)
                time.sleep(1)
    else:
        print("No TWEETS to Download...")
    return

def get_profs(profile_image_urls):
    if len(profile_image_urls) != 0:
        print("Fetching PROFILES...")
        for url in profile_image_urls:
        ## Need to pull old variables
            global profile_dir_name
            global filename
            global profile_dir
            global profile_folder
            global logger
            logger = logging.getLogger(short_name)

         ## Then call them
            profile_dir_name = profile_image_urls[url]['profile_dir']
            filename = profile_image_urls[url]['filename']
            profile_dir = join(profile_images_dir, profile_dir_name)
            profile_folder = os.path.split(profile_dir)

        ## Finally make the request
            with requests.Session() as s:
                logger.info("FETCHING Profile Media > {0}: {1}".format(profile_folder[1], url))
                print("FETCHING Profile Media > {0}: {1}".format(profile_folder[1], filename))
                profile_image = s.get(url)
                profile_image_file = join(profile_dir, filename)
                with open(profile_image_file, 'wb') as profile_image_out:
                    profile_image_out.write(profile_image.content)
                new_profiles.append(url)
                time.sleep(1)
    else:
        print("No PROFILES to Download...")
    return

fetch_media_for_feed(feed_dict)

now = time.asctime(time.localtime(time.time()))
print("\n--------------------------------------------------------------")
print("Finished Downloading Twitter Images @ {0}".format(now))
print("--------------------------------------------------------------")
print("Tweet Image Stats | New: {0} | Old: {1} | Dead: {2}".format(len(new_tweets),len(stale_tweets),len(dead_tweets)))
print("--------------------------------------------------------------")
print("Profile Image Stats | New: {0} | Old: {1} | Dead: {2}".format(len(new_profiles),len(stale_profiles),len(dead_profiles)))
print("--------------------------------------------------------------\n")
