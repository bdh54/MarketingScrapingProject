import json
import logging
import os
import pexpect
import re

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def initialize_geolocation_shell():
    child = pexpect.spawn('python2 /Users/alexkim/MarketingScrapingProject/pigeo/pigeo.py --mode shell', timeout=150)
    try:
        child.expect('text to geolocate: ')
        logging.info("Geolocation model loaded successfully.")
    except pexpect.exceptions.TIMEOUT:
        logging.error("Timeout exceeded while loading the geolocation model.")
        raise
    return child

def geolocate_text(child, text):
    child.sendline(text)
    child.expect('text to geolocate: ')
    return child.before.strip()

def extract_location(output):
    try:
        location_match = re.search(r"\{.*\}", output.decode('utf-8'))
        if location_match:
            location_str = location_match.group(0)
            location_data = eval(location_str)
            return {
                'city': location_data.get('city', ''),
                'state': location_data.get('state', ''),
                'country': location_data.get('country', ''),
                'lat': location_data.get('lat', None),
                'lon': location_data.get('lon', None)
            }
        else:
            logging.error("No valid location data found.")
            return None
    except Exception as e:
        logging.error(f"Error extracting location: {e}")
        return None

def initialize_output_file(output_file_path):
    if not os.path.exists(output_file_path) or os.stat(output_file_path).st_size == 0:
        with open(output_file_path, 'w') as file:
            file.write("[\n")

def save_tweet_incrementally(tweet, output_file_path):
    try:
        with open(output_file_path, 'r+', encoding='utf-8') as file:
            file.seek(0, os.SEEK_END)
            position = file.tell()
            if position == 0:  # Empty file
                file.write("[\n")
            else:
                file.seek(position - 1)
                last_char = file.read(1)
                if last_char == ']':
                    file.seek(position - 1)
                    file.truncate()
                    file.write(",\n")
                elif last_char == '\n':
                    file.seek(position - 2)
                    last_char = file.read(1)
                    if last_char == ',':
                        file.seek(position - 2)
                        file.truncate()
                        file.write("\n")
            json.dump(tweet, file, ensure_ascii=False)
            file.write("\n]")
    except Exception as e:
        logging.error(f"Error saving tweet: {e}")

def finalize_output_file(output_file_path):
    with open(output_file_path, 'rb+') as file:
        file.seek(-2, os.SEEK_END)
        last_char = file.read(1)
        if last_char == b',':
            file.seek(-2, os.SEEK_END)
            file.truncate()  # Remove the last comma
        file.write(b"\n]")

def save_progress(index, progress_file):
    try:
        with open(progress_file, 'w') as file:
            file.write(str(index))
        logging.info(f"Progress saved at tweet index {index}.")
    except Exception as e:
        logging.error(f"Error saving progress: {e}")

def load_progress(progress_file):
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as file:
                return int(file.read().strip())
        except Exception as e:
            logging.error(f"Error loading progress: {e}")
    return 0

def process_tweets(tweets, child, output_file_path, progress_file):
    start_index = load_progress(progress_file)

    for index, tweet in enumerate(tweets[start_index:], start=start_index):
        if tweet.get('location') == 'N/A':
            retries = 3
            success = False
            text_to_geolocate = "{} {}".format(tweet['username'], tweet['text'])
            logging.info(f"Processing tweet {index + 1}/{len(tweets)}: {tweet.get('id', 'Unknown ID')}")
            while retries > 0 and not success:
                try:
                    output = geolocate_text(child, text_to_geolocate)
                    if output:
                        location = extract_location(output)
                        if location:
                            tweet['estimated_location'] = location
                            logging.info(f"Updated estimated location for Tweet ID {tweet.get('id', 'Unknown ID')}: {location}")
                            success = True
                    if not success:
                        retries -= 1
                        logging.warning(f"Retrying... ({3 - retries}/3)")
                except Exception as e:
                    logging.error(f"Error processing tweet: {e}")
                    retries -= 1

            if not success:
                logging.error(f"Skipping problematic tweet {tweet.get('id', 'Unknown ID')} after 3 retries.")
                continue

            save_tweet_incrementally(tweet, output_file_path)
            save_progress(index, progress_file)

    finalize_output_file(output_file_path)

def main():
    input_file_path = "/Users/alexkim/MarketingScrapingProject/senators_production_geo_map_stage2_senators/tweet_batch_1716173464.json"
    output_file_path = "/Users/alexkim/MarketingScrapingProject/tweet_batch_1716173464_geolocated.json"
    progress_file = "/Users/alexkim/MarketingScrapingProject/tweet_batch_1716173464_progress.txt"

    initialize_output_file(output_file_path)

    with open(input_file_path, 'r') as file:
        tweets = json.load(file)

    child = initialize_geolocation_shell()

    process_tweets(tweets, child, output_file_path, progress_file)

if __name__ == "__main__":
    main()
