import os
from datetime import datetime, timedelta

# Time information
now = datetime.now()
date = now.strftime("%Y-%m-%d")
yesterday = now - timedelta(days=1)
yesterday_date = yesterday.strftime("%Y-%m-%d")
sevenday = now - timedelta(days=7)
SEVEN_DAYS_AGO = sevenday.strftime("%Y_%m_%d")
UPDATEDAY = str(now.strftime("%Y_%m_%d"))
year = now.year
month = now.month
day = now.day

# File path
BASIC_PATH = os.path.dirname(os.path.abspath(__file__))

LOG_FILE_NAME = f"{BASIC_PATH}/log/{UPDATEDAY}_log_file.log"
OLD_LOG_FILE = f"{BASIC_PATH}/log/{SEVEN_DAYS_AGO}_log_file.log"
QUERY_FILE_NAME = f"{BASIC_PATH}/cip_c2_detect_query.json"

# Management files
CSV_FORMAT = ["Today", "IP Address"]
CHECK_CSV_FORMAT = ["Date", "IP Address"]
MAKE_TEMP_CSV_FORMAT = ["Update Date", "IP Address", "Group Name"]

CSV_FILE_PATH = f"{BASIC_PATH}/core/api/input/detect_IP_{date}.csv"  # File to fetch IP data from CIP
NEXTDAY_CSV_FILE_PATH = f"{BASIC_PATH}/core/api/input/yesterday_detect_IP_{date}.csv"  # File for the previous day's data
YESTERDAY_CSV_FILE_PATH = f"{BASIC_PATH}/core/api/input/yesterday_detect_IP_{yesterday_date}.csv"  # File to remove duplicate IP entries

# Temp files
CREATE_TEMP_CSV_FILE_NAME = f"{BASIC_PATH}/core/api/output/create_IP_{date}.csv"
DELETE_TEMP_CSV_FILE_NAME = f"{BASIC_PATH}/core/api/output/delete_IP_{date}.csv"
CREATE_TEMP_JSON_FILE_NAME = f"{BASIC_PATH}/core/api/output/create_IP_{date}.json"
DELETE_TEMP_JSON_FILE_NAME = f"{BASIC_PATH}/core/api/output/delete_IP_{date}.json"

# Delete file paths
OUT_FOLDER = f"{BASIC_PATH}/core/api/output"  # Folder path for files to be changed
INPUT_FOLDER = f"{BASIC_PATH}/core/api/input"  # Folder path for files to be changed
EXCEPT_FILES = NEXTDAY_CSV_FILE_PATH  # File names to be retained

NEW_GROUP_NAME = f"C2_{UPDATEDAY}"
DELET_GROUP_NAME = f"C2_{SEVEN_DAYS_AGO}"

ip_data = set()

# CIP DATA
CRIMINALIP_API_KEY = ""
# content
BASE_URL = "https://api.criminalip.io/"
ENDPOINT = "v1/banner/search"
HEADERS = {"x-api-key": CRIMINALIP_API_KEY, "Cache-Control": "no-cache"}

# todo #Fortigate
TARGET = ""
TOKEN = ""
POLICYID = ""

FTG_BASE_URL = f"https://{TARGET}/api/v2/cmdb/firewall"
FTG_HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
