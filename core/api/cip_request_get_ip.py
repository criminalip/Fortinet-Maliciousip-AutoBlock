import requests
import json
import logging
import time
import csv
from fire_config import LOG_FILE_NAME, BASE_URL, ENDPOINT, HEADERS, date, ip_data, CSV_FILE_PATH


# Initialize logger
logging.basicConfig(
    filename=LOG_FILE_NAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Global constants
MAX_RETRY_COUNT = 70
RETRY_DELAY_SECONDS = 2
errcode_list = []


def handle_exception(err, err_type, retry_func):
    """Function for unified error handling"""
    logging.error(f"{err_type}: {err}")
    time.sleep(RETRY_DELAY_SECONDS)
    retry_func()


def check_payload(now_query, offset):
    """Function to verify the payload to be sent"""
    return {"query": now_query, "offset": offset}


def process_query(url, c2_name, payload, COUNT=0):
    """Function to collect IP data for the received query"""
    global MAX_RETRY_COUNT
    if COUNT >= MAX_RETRY_COUNT:
        logging.error(
            "Maximum retry count reached. Please check the server for verification."
        )
        process_query(url, c2_name, payload, COUNT + 1)
    try:
        response2_json = requests.request("GET", url, headers=HEADERS, params=payload)
        logging.info(f"check payload:{payload}, response2_json: {response2_json}")
        response2_json.raise_for_status()

        data = response2_json.json()
        logging.info(f"now status:{data['status']}")
        assert data["status"] == 200
        result = data["data"]["result"]

        for item in result:
            ip_address = item["ip_address"]
            logging.info([str(date), ip_address])

            if ip_address not in ip_data:
                with open(CSV_FILE_PATH, "a", newline="") as file:
                    writer = csv.writer(file)
                    if not ip_data:
                        writer.writerow(["Date", "IP Address"])

                    writer.writerow([str(date), ip_address])

                ip_data.add(ip_address)

        logging.info(f"Number of deduplicated IPs: {len(ip_data)}")

    except json.JSONDecodeError as json_err:
        handle_exception(
            json_err,
            "JSONDecodeError",
            lambda: process_query(url, c2_name, payload, COUNT + 1),
        )
    except requests.exceptions.HTTPError as err:
        handle_exception(
            err, "HTTPError", lambda: process_query(url, c2_name, payload, COUNT + 1)
        )
    except requests.exceptions.ChunkedEncodingError as chunked_err:
        handle_exception(
            chunked_err,
            "ChunkedEncodingError",
            lambda: process_query(url, c2_name, payload, COUNT + 1),
        )
    except requests.exceptions.ConnectionError as connect_err:
        handle_exception(
            connect_err,
            "ConnectionError",
            lambda: process_query(url, c2_name, payload, COUNT + 1),
        )
    except requests.exceptions.RequestException as e:
        handle_exception(
            e,
            "RequestException",
            lambda: process_query(url, c2_name, payload, COUNT + 1),
        )
    except AssertionError as err:
        handle_exception(
            err,
            "AssertionError",
            lambda: process_query(url, c2_name, payload, COUNT + 1),
        )
    except Exception as err:
        handle_exception(
            err, "Exception", lambda: process_query(url, c2_name, payload, COUNT + 1)
        )


def process_ioc(c2_name, query_list):
    """Function to calculate maximum execution count to check malicious tags"""
    global errcode_list, RETRY_DELAY_SECONDS
    for now_query in query_list:
        offset = 0
        while True:
            logging.info(f"Processing target C2: {c2_name}, Using query: {now_query}")

            payload = check_payload(now_query, offset)
            time.sleep(RETRY_DELAY_SECONDS)

            try:
                response = requests.get(BASE_URL+ENDPOINT, headers=HEADERS, params=payload)
                logging.info(
                    "check query %s/ check offset %d / Current server status response: %s",
                    now_query,
                    offset,
                    response,
                )
                response.raise_for_status()
                data = response.json()

                assert data["status"] == 200
                logging.info("result total_count: %d", data["data"]["count"])

                total_count = int(data["data"]["count"] / 10) + 1
                logging.info("count: %d", total_count)

                for count in range(total_count):
                    offset = count * 10

                    if offset > 9900:
                        logging.error(
                            "Reached maximum offset value and attempting to output the next query."
                        )
                        break
                    payload = check_payload(now_query, offset)
                    time.sleep(RETRY_DELAY_SECONDS)
                    process_query(BASE_URL+ENDPOINT, c2_name, payload)

            except json.JSONDecodeError as json_err:
                handle_exception(json_err, "JSONDecodeError", lambda: None)
            except requests.exceptions.HTTPError as err:
                handle_exception(err, "HTTPError", lambda: None)
            except requests.exceptions.ChunkedEncodingError as chunked_err:
                handle_exception(chunked_err, "ChunkedEncodingError", lambda: None)
            except requests.exceptions.ConnectionError as connect_err:
                handle_exception(connect_err, "ConnectionError", lambda: None)
            except requests.exceptions.RequestException as e:
                handle_exception(e, "RequestException", lambda: None)
            except AssertionError as err:
                handle_exception(err, "AssertionError", lambda: None)
            except Exception as err:
                handle_exception(err, "Exception", lambda: None)
            else:
                break
