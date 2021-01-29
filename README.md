# BHL TWARC MEDIA
A complementary script to the [Bentley Historical Library's implementation](https://github.com/bentley-historical-library/bhl_twarc) of [twarc](https://github.com/edsu/twarc), used to download tweet media from URLs captured in twarc crawls.

## Requirements
* [Python 3](https://www.python.org/)
* [requests](https://pypi.org/project/requests/)

## BHL TWARC MEDIA Set Up
* Clone `bhl_twarc_media.py`
* Place `bhl_twarc_media.py` in the same directory as `bhl_twarc.py`

## Twitter API Set Up
* Note the consumer key, consumer secret, access token, and access token secret are not required for execution.

## Use
* The script will only interact with the content inside the `media` directory
  * It parses rows from `profile_images.csv` and `tweet_images.csv` in each feed's media folder present
  * `bhl_twarc` will create the following directory structure, and this script will add to the `media` directory :
```
feeds
  examplehashtag
    html
    json
    logs
    media
      profile_images
      tweet_images
      media_logs
```

* Logs for the downloads will be stored to a `twarc.log` file in the new folder titled `media_logs` 
* Uses the same variable (**feed_dict**) to execute as:
  * [build_html.py](https://github.com/bentley-historical-library/bhl_twarc/blob/master/scripts/build_html.py)
  * [build_index.py](https://github.com/bentley-historical-library/bhl_twarc/blob/master/scripts/build_index.py)
  * [crawl_feeds.py](https://github.com/bentley-historical-library/bhl_twarc/blob/master/scripts/crawl_feeds.py)
  * [extract_urls.py](https://github.com/bentley-historical-library/bhl_twarc/blob/master/scripts/extract_urls.py)
  * [fetch_media.py](https://github.com/bentley-historical-library/bhl_twarc/blob/master/scripts/fetch_media.py)
  
### Potential media Directory Alternations
If the `profile_images` directory and/or `tweet_images` directory are not present, it/they will be created.
