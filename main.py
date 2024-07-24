import time
import os
import logging
from fire_config import (
    LOG_FILE_NAME,
    QUERY_FILE_NAME,
    CSV_FILE_PATH,
    NEXTDAY_CSV_FILE_PATH,
    YESTERDAY_CSV_FILE_PATH,
    CREATE_TEMP_CSV_FILE_NAME,
    CREATE_TEMP_JSON_FILE_NAME,
    DELETE_TEMP_CSV_FILE_NAME,
    DELETE_TEMP_JSON_FILE_NAME,
    NEW_GROUP_NAME,
    POLICYID,
    SEVEN_DAYS_AGO,
    OUT_FOLDER,
    INPUT_FOLDER,
    EXCEPT_FILES,
    OLD_LOG_FILE,
    FTG_BASE_URL,
    FTG_HEADERS,
)
from core.api.cip_request_get_ip import process_ioc
from core.api.managefiles import (
    QueryData,
    find_unique_ip_addresses,
    create_csv_file,
    convert_csv_to_json,
    filter_old_data_and_get_ip_addresses,
    extract_and_save_to_json,
    merge_files_and_create_nextday_file,
    delete_files_in_folder,
    remove_file_with_log,
)
from core.fwb._ftg_request_parm import (
    check_name_exist_address,
    add_address_object,
    make_address_group,
    check_group_in_policy_dstaddr,
    update_group_in_policy,
    check_get_group_members_info,
    check_address_group_existence,
    delete_group_in_policy,
    delete_address_group,
    delete_address_object,
)

logging.basicConfig(
    filename=LOG_FILE_NAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
)


def load_queries(query_file_name):
    return QueryData.from_file(query_file_name)


def chunk_list(lst, chunk_size):
    """Function to divide a list into chunks of specified size"""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def check_new_ip_address(CSV_FILE_PATH, YESTERDAY_CSV_FILE_PATH):
    """Function to check for new IP address data"""
    logging.info("CSV file is ready.")
    new_ip_list = find_unique_ip_addresses(CSV_FILE_PATH, YESTERDAY_CSV_FILE_PATH)
    logging.info(f"Unique IP addresses: {new_ip_list}")
    if new_ip_list:
        create_csv_file(new_ip_list, CREATE_TEMP_CSV_FILE_NAME)
        convert_csv_to_json(CREATE_TEMP_CSV_FILE_NAME, CREATE_TEMP_JSON_FILE_NAME)
    return new_ip_list


def check_delete_ip_address(YESTERDAY_CSV_FILE_PATH):
    """Function to check for IP addresses that need deletion"""
    delete_ip_list = filter_old_data_and_get_ip_addresses(YESTERDAY_CSV_FILE_PATH)
    logging.info(f"IP addresses to delete: {delete_ip_list}")

    if delete_ip_list:
        create_csv_file(delete_ip_list, DELETE_TEMP_CSV_FILE_NAME)
        extract_and_save_to_json(DELETE_TEMP_CSV_FILE_NAME, DELETE_TEMP_JSON_FILE_NAME)
    return delete_ip_list


def check_already_blocked_ip_address(ip_list):
    """Function to check IP addresses already blocked"""
    existing_ips = []
    non_existing_ips = []
    for ipv4address in ip_list:
        if check_name_exist_address(ipv4address, FTG_BASE_URL, FTG_HEADERS):
            existing_ips.append(ipv4address)
        else:
            non_existing_ips.append(ipv4address)

    return existing_ips, non_existing_ips


def add_ip_address_in_friewall(block_list):
    """Function to add IP addresses to the firewall for blocking"""
    for ip in block_list:
        add_address_object(ip, FTG_BASE_URL, FTG_HEADERS)
        time.sleep(0.5)


def handle_failure(func_name):
    """Function to handle errors"""
    if func_name == "check_address_group_existence":
        logging.error(f"{func_name} failed / The group to delete does not currently exist.")
    elif func_name == "check_group_in_policy_dstaddr":
        logging.error(
            f"{func_name} failed / The group exists but is not reflected in the policy's destination address."
        )
    elif func_name == "delete_group_in_policy":
        logging.error(
            f"{func_name} failed / Unable to delete the group from the policy."
        )
    elif func_name == "delete_address_group":
        logging.error(f"{func_name} failed / Cannot delete a group that belongs to a policy.")


def make_group_object(chunked_ips):
    """Function to create groups for holding address objects"""
    generated_group_names = []
    for idx, ip_chunk in enumerate(chunked_ips):
        group_name = f"{NEW_GROUP_NAME}_{idx + 1}"
        generated_group = make_address_group(group_name, ip_chunk, FTG_BASE_URL, FTG_HEADERS)
        if generated_group:
            generated_group_names.append(group_name)
    for name in generated_group_names:
        exit_group = check_group_in_policy_dstaddr(POLICYID, name, FTG_BASE_URL, FTG_HEADERS)
        if exit_group is False:
            update_group_in_policy(POLICYID, name, FTG_BASE_URL, FTG_HEADERS)


def delete_ip_list_in_friewall(delete_ip_list):
    """Function to delete blocked IP data from the firewall"""
    if delete_ip_list:
        delete_groups = check_get_group_members_info(SEVEN_DAYS_AGO, FTG_BASE_URL, FTG_HEADERS)
        for group in delete_groups:
            delete_block_after_7_days(POLICYID, group["name"], group["members"])


def delete_block_after_7_days(POLICYID, DELET_GROUP_NAME, delete_ip_list):
    """Function to delete blocked rules after 7 days"""
    check_address_group = check_address_group_existence(DELET_GROUP_NAME, FTG_BASE_URL, FTG_HEADERS)
    if not check_address_group:
        handle_failure("check_address_group_existence")

    check_group_in_policy = (
        check_group_in_policy_dstaddr(POLICYID, DELET_GROUP_NAME, FTG_BASE_URL, FTG_HEADERS)
        if check_address_group
        else False
    )
    if check_address_group and not check_group_in_policy:
        handle_failure("check_group_in_policy_dstaddr")
    check_delete_group_in_policy = (
        delete_group_in_policy(POLICYID, DELET_GROUP_NAME, FTG_BASE_URL, FTG_HEADERS)
        if check_group_in_policy
        else False
    )
    if check_group_in_policy and not check_delete_group_in_policy:
        handle_failure("delete_group_in_policy")
    check_delete_address_group = (
        delete_address_group(DELET_GROUP_NAME, FTG_BASE_URL, FTG_HEADERS)
        if check_delete_group_in_policy
        else False
    )
    if check_delete_group_in_policy and not check_delete_address_group:
        handle_failure("delete_address_group")

    if check_delete_address_group:
        for ip in delete_ip_list:
            delete_address_object(ip, FTG_BASE_URL, FTG_HEADERS)


def main():
    queries = load_queries(QUERY_FILE_NAME)
    for c2_name, query_list in queries.data.items():
        process_ioc(c2_name, query_list)

    if os.path.exists(CSV_FILE_PATH):
        new_ip_list = check_new_ip_address(CSV_FILE_PATH, YESTERDAY_CSV_FILE_PATH)
        delete_ip_list = check_delete_ip_address(YESTERDAY_CSV_FILE_PATH)

    merge_files_and_create_nextday_file(
        CREATE_TEMP_CSV_FILE_NAME, YESTERDAY_CSV_FILE_PATH, NEXTDAY_CSV_FILE_PATH
    )
    logging.info("Files merged and next day file created.")

    if new_ip_list:
        existing_ips, non_existing_ips = check_already_blocked_ip_address(new_ip_list)
        logging.info(f"Number of pre-existing IPs: {len(existing_ips)}")
        logging.info(f"Total IPs added to the firewall today: {len(non_existing_ips)}")
        if non_existing_ips:
            add_ip_address_in_friewall(non_existing_ips)
            chunked_ips = list(chunk_list(non_existing_ips, 600))
            make_group_object(chunked_ips)
        delete_ip_list_in_friewall(delete_ip_list)
    else:
        delete_ip_list_in_friewall(delete_ip_list)

    # delete files
    delete_files_in_folder(OUT_FOLDER)
    delete_files_in_folder(INPUT_FOLDER, EXCEPT_FILES)
    remove_file_with_log(OLD_LOG_FILE)


if __name__ == "__main__":
    main()
