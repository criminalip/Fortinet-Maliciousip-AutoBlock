import csv
import json
import logging
import shutil
import os
from datetime import datetime
from fire_config import (
    LOG_FILE_NAME,
    yesterday_date,
    CHECK_CSV_FORMAT,
    date,
    BASIC_PATH,
    sevenday,
)


logging.basicConfig(
    filename=LOG_FILE_NAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class QueryData:
    def __init__(self, data):
        self.data = data

    @classmethod
    def from_file(cls, query_file_name):
        with open(query_file_name, "r") as query_file:
            data = json.load(query_file)
            for key, value in data["data"].items():
                data["data"][key] = [
                    item.replace("{% now_date %}", yesterday_date) for item in value
                ]
        return cls(data["data"])


def read_ip_addresses_from_file(filename):
    """Function to read IP address data from a file"""
    ip_set = set()
    if os.path.exists(filename):
        with open(filename, "r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                ip_set.add(row["IP Address"])
    else:
        logging.warning(f"File {filename} does not exist.")

    return ip_set


def find_unique_ip_addresses(today_filename, yesterday_filename):
    """Function to find unique IP addresses that are not duplicated"""
    today_ip_set = read_ip_addresses_from_file(today_filename)
    yesterday_ip_set = read_ip_addresses_from_file(yesterday_filename)

    unique_ip_addresses = []
    try:
        for ip_address in today_ip_set:
            if ip_address not in yesterday_ip_set:
                unique_ip_addresses.append(ip_address)

        logging.info("Unique IP addresses found successfully.")
        return unique_ip_addresses

    except Exception as e:
        logging.error(f"Error in finding unique IP addresses: {str(e)}")
        raise e


def create_csv_file(ip_addresses, temp_file_path):
    """Function to create a CSV file"""
    write_ip_addresses_to_csv(ip_addresses, temp_file_path)
    logging.info(f"CSV file {temp_file_path} created successfully.")


def write_ip_addresses_to_csv(ip_addresses, filename):
    """Function to write IP address data to a CSV file"""
    with open(filename, "w", newline="") as new_file:
        writer = csv.writer(new_file)
        writer.writerow(CHECK_CSV_FORMAT)

        for ip_address in ip_addresses:
            writer.writerow([date, ip_address])


def convert_csv_to_json(temp_file_path, temp_json_file_path):
    """Function to convert a CSV file to JSON format"""
    try:
        csv_data = []
        if not os.path.exists(temp_file_path):
            logging.info(f"CSV file {temp_file_path} does not exist.")
            return

        csv_data = []
        with open(temp_file_path, "r", newline="") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                csv_data.append(row)

        with open(temp_json_file_path, "w") as json_file:
            json.dump(csv_data, json_file, indent=4)

        logging.info(
            f"CSV file {temp_file_path} converted to JSON file {temp_json_file_path} successfully."
        )
    except Exception as e:
        logging.error(f"Error in converting CSV to JSON: {str(e)}")


def filter_old_data_and_get_ip_addresses(file_path, SEVEN_DAYS_AGO):
    """Function to extract IP addresses from the last seven days"""
    try:
        ip_addresses = []
        if not os.path.exists(file_path):
            logging.error(f"File not found: {file_path}")
            return ip_addresses

        with open(file_path, "r", newline="") as csv_file:
            csv_reader = csv.DictReader(csv_file)
            rows_to_remove = []
            for row in csv_reader:
                csv_date = datetime.strptime(row["Date"], "%Y-%m-%d")
                if csv_date < SEVEN_DAYS_AGO:
                    ip_addresses.append(row["IP Address"])
                    rows_to_remove.append(row)

            if rows_to_remove:
                for row in rows_to_remove:
                    del row["Date"], row["IP Address"]

        if not ip_addresses:
            logging.info("No old IP addresses found.")

        else:
            logging.info("old IP addresses filtered successfully.")

        return ip_addresses

    except Exception as e:
        logging.error(f"Error in filtering old IP addresses: {str(e)}")
        return []


def extract_and_save_to_json(DELETE_TEMP_CSV_FILE_NAME, DELETE_TEMP_JSON_FILE_NAME):
    """Function to extract and save IP list for deletion to a JSON file"""
    try:
        extracted_data = {}
        if os.path.exists(DELETE_TEMP_CSV_FILE_NAME):
            with open(DELETE_TEMP_CSV_FILE_NAME, "r", newline="") as delete_file:
                delete_reader = csv.DictReader(delete_file)
                for row in delete_reader:
                    ip_address = row.get("IP Address")
                    if ip_address:
                        key = f"C2_{ip_address}"
                        extracted_data[key] = row

            if not extracted_data:
                logging.info("No data to extract and save to JSON.")
                return

            with open(DELETE_TEMP_JSON_FILE_NAME, "w") as json_file:
                json.dump(extracted_data, json_file, indent=4)

            logging.info(
                f"Data extracted and saved to JSON file {DELETE_TEMP_JSON_FILE_NAME} successfully."
            )
        else:
            logging.info(
                f"{DELETE_TEMP_CSV_FILE_NAME} does not exist. JSON file not created."
            )

    except Exception as e:
        logging.error(f"Error in extracting and saving to JSON: {str(e)}")


def merge_files_and_create_nextday_file(
    CREATE_TEMP_CSV_FILE_NAME, yesterday_csv_file, nextday_csv_file
):
    """Function to merge files and create a file reflecting updated IP additions and deletions"""
    try:
        if not os.path.exists(CREATE_TEMP_CSV_FILE_NAME):
            try:
                shutil.copy2(yesterday_csv_file, nextday_csv_file)
                logging.info(f"CREATE_TEMP_CSV_FILE_NAME does not exist. Copied yesterday_csv_file to nextday_csv_file.")
                return
            except Exception as e:
                logging.error(f"Error in copying file: {e}")
        else:
            combined_data = []
            with open(CREATE_TEMP_CSV_FILE_NAME, 'r', newline='') as create_file:
                create_reader = csv.DictReader(create_file)
                for row in create_reader:
                    combined_data.append(row)
                    
            if os.path.exists(yesterday_csv_file):
                with open(yesterday_csv_file, 'r', newline='') as yesterday_file:
                    yesterday_reader = csv.DictReader(yesterday_file)
                    for row in yesterday_reader:
                        if 'Date' in row and datetime.strptime(row['Date'], '%Y-%m-%d') >= sevenday:
                            combined_data.append(row)

            with open(nextday_csv_file, 'w', newline='') as nextday_file:
                fieldnames = combined_data[0].keys() if combined_data else []  
                writer = csv.DictWriter(nextday_file, fieldnames=fieldnames)
                writer.writeheader()  
                writer.writerows(combined_data)

            logging.info(f"Files merged and next day file {nextday_csv_file} created successfully.")

    except Exception as e:
        logging.error(f"Error in merging files and creating next day file: {e}")



def delete_files_in_folder(folder_path, except_files=None):
    """Function to delete files in a folder, excluding specified files"""
    logging.info(f"Files to keep: {except_files}")

    try:
        files_to_delete = [
            file for file in os.listdir(folder_path)
            if not except_files or file != os.path.basename(except_files)
        ]

        for file in files_to_delete:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f"Deleted {file_path}")

    except Exception as e:
        logging.info(f"Error deleting files in {folder_path}: {str(e)}")


def check_file_existence(file_name):
    """Function to check if a file exists"""
    return os.path.exists(file_name)


def remove_file_with_log(file_name):
    """Function to delete old log files"""
    os.chdir(BASIC_PATH)
    if check_file_existence(file_name):
        os.remove(file_name)
        logging.info(f"{file_name} is deleted.")
    else:
        logging.info(f"{file_name} not exists, didn't delete")
