import pandas as pd
import os
import requests
import csv
from androguard.core.apk import APK
from loguru import logger

# disable androguard logging: this is super annoying
logger.disable("androguard")

APIKEY = "YOUR_API_KEY"
DOWNLOAD_DIR = "apks"
PICKLEFILE = "data/keys1.pkl"
APIURL = "https://androzoo.uni.lu/api/download"
DOWNLOAD_LIMIT = 100
SHUFFLEDATASET = True
# safety check
if APIKEY == "YOUR_API_KEY":
    logger.error("Please set your API key in main.py")
    exit(1)

if not os.path.exists(PICKLEFILE):
    logger.error(f"Please make sure create or download the pickle file first and put it in {PICKLEFILE}")
    exit(1)


data = pd.read_pickle(PICKLEFILE)
def create_apk_folder():
    if not os.path.exists(DOWNLOAD_DIR):
        os.mkdir(DOWNLOAD_DIR)

def download_file(sha256):
  if not os.path.exists(f"apks/{sha256}.apk"):
    print(f"Downloading {sha256}.apk")
    response = requests.get(f"{APIURL}?apikey={APIKEY}&sha256={sha256}")
    with open(f"{DOWNLOAD_DIR}/{sha256}.apk", "wb") as f:
      f.write(response.content)
  else:
    print(f"{sha256}.apk already exists")

def get_apk(sha256):
    return APK(f"{DOWNLOAD_DIR}/{sha256}.apk", testzip = False)

def sha_list():
    columns = data.get(data.columns[1])
    if SHUFFLEDATASET:
        return columns.sample(frac=1).reset_index(drop=True)
    return columns

def main():
    create_apk_folder()
    with open('result.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['sha256', 'app_name', 'android_version', 'activities', 'permissions'])
        for index, sha256 in enumerate(sha_list()):
            if index >= DOWNLOAD_LIMIT:
                break
            download_file(sha256)
            try:
                apk = get_apk(sha256)
                csv_writer.writerow([sha256, apk.get_app_name(), apk.get_androidversion_name(), apk.get_activities(), apk.get_permissions()])
            except Exception as e:
                logger.error(e)
                os.remove(f"{DOWNLOAD_DIR}/{sha256}.apk")
        
if __name__ == "__main__":
    main()