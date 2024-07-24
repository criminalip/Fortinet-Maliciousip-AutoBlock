import requests
import json
import re
import urllib3
import logging
import sys
from fire_config import LOG_FILE_NAME

# Disable SSL warnings at the beginning of your script
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    filename=LOG_FILE_NAME,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def check_name_exist_address(ipv4address, ftg_base_url, ftg_header):
    """API call to check the existence of an address object"""
    get_addresses_endpoint = f"/address/C2_{ipv4address}"
    get_addresses_url = ftg_base_url + get_addresses_endpoint

    response = requests.get(get_addresses_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        logging.info(f"Address 'C2_{ipv4address}' exists")
        return True

    elif response.status_code == 404:
        logging.info(f"Address 'C2_{ipv4address}' does not exist")
        return False

    else:
        logging.error(
            f"Failed to check Address, reason: {response.text} /  Response code: {response.status_code}"
        )
        return None


def add_address_object(address_name, ftg_base_url, ftg_header):
    """API call to create an address object"""
    add_ip_endpoint = "/address"
    add_addr_url = ftg_base_url + add_ip_endpoint
    payload = {"name": f"C2_{address_name}", "subnet": f"{address_name}/32"}

    json_payload = json.dumps(payload)
    response = requests.post(
        add_addr_url, headers=ftg_header, data=json_payload, verify=False
    )

    if response.status_code == 200:
        logging.info("Address object created successfully")

    else:
        logging.error(
            f"Failed to create Address object, reason: {response.text} /  Response code: {response.status_code}"
        )


def delete_address_object(address_name, ftg_base_url, ftg_header):
    """ """
    delete_address_endpoint = f"/address/{address_name}"
    delete_addr_url = ftg_base_url + delete_address_endpoint
    response = requests.delete(delete_addr_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        logging.info("Address object deleted successfully")

    else:
        logging.error(
            f"Failed to delete Address object, reason: {response.text} Response code: {response.status_code}"
        )


def check_get_group_info(select_date, ftg_base_url, ftg_header):
    """API call to retrieve and extract information about a specific group name"""
    _pattern = re.compile(rf"C2_{select_date}_\d+")
    check_group_endpoint = "/addrgrp"
    check_group_url = ftg_base_url + check_group_endpoint

    response = requests.get(check_group_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        logging.info(f"address groups infos {response.text}")
        data = response.json()["results"]
        matches = [item["name"] for item in data if _pattern.match(item["name"])]
        return matches

    elif response.status_code == 404:
        logging.info(f"Address group info error: {response.text}")
        return []

    else:
        logging.error(
            f"Error checking group info: {response.text} Response code: {response.status_code}"
        )
        return None


def check_get_group_members_info(select_date, ftg_base_url, ftg_header):
    """API call to retrieve information about members within a specific group"""
    _pattern = re.compile(rf"C2_{select_date}_\d+")
    check_group_endpoint = "/addrgrp"
    check_group_url = ftg_base_url + check_group_endpoint

    response = requests.get(check_group_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        logging.info(f"address groups infos {response.text}")
        data = response.json()["results"]
        filtered_data = [
            {
                "name": item["name"],
                "members": [member["name"] for member in item["member"]],
            }
            for item in data
            if _pattern.match(item["name"])
        ]
        return filtered_data

    elif response.status_code == 404:
        logging.info(f"Address group info error: {response.text}")
        return []

    else:
        logging.error(
            f"Error checking group info: {response.text} Response code: {response.status_code}"
        )
        return None


def check_address_group_existence(group_name, ftg_base_url, ftg_header):
    """API call to check the existence of an address group"""
    check_group_endpoint = f"/addrgrp/{group_name}"
    check_group_url = ftg_base_url + check_group_endpoint

    response = requests.get(check_group_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        logging.info(f"Address group '{group_name}' exists")
        return True

    elif response.status_code == 404:
        logging.info(f"Address group '{group_name}' does not exist")
        return False

    else:
        logging.error(
            f"Error checking address group: {response.text} Response code: {response.status_code}"
        )
        return None


def make_address_group(group_name, addresses_name, ftg_base_url, ftg_header):
    """API call to create a group for policy application"""
    add_group_endpoint = "/addrgrp"
    add_group_fortigate_url = ftg_base_url + add_group_endpoint
    members = [{"name": f"C2_{address_name}"} for address_name in addresses_name]
    address_group_data = {"name": group_name, "member": members}

    address_group_json = json.dumps(address_group_data)
    response = requests.post(
        add_group_fortigate_url,
        headers=ftg_header,
        data=address_group_json,
        verify=False,
    )

    if response.status_code == 200:
        logging.info("Address group created successfully")
        return True

    else:
        logging.error(
            f"Failed to create Address group, reason: {response.text} /  Response code: {response.status_code}"
        )
        logging.info(response.text)
        return False


def delete_address_group(group_name, ftg_base_url, ftg_header):
    """API call to delete a group"""
    delete_group_endpoint = f"/addrgrp/{group_name}"
    delete_group_url = ftg_base_url + delete_group_endpoint

    response = requests.delete(delete_group_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        logging.info("Address group deleted successfully")
        return True

    else:
        logging.error(
            f"Failed to delete Address group, reason: {response.text} /  Response code: {response.status_code}"
        )
        return False


def check_group_in_policy_dstaddr(policy_id, group_name, ftg_base_url, ftg_header):
    """API call to check the existence of a group within a policy's destination address"""
    check_policy_endpoint = f"/policy/{policy_id}"
    check_policy_url = ftg_base_url + check_policy_endpoint

    response = requests.get(check_policy_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        policy_data = response.json().get("results", [])

        if policy_data:
            dstaddr_groups = [
                addr["name"] for addr in policy_data[0].get("dstaddr", [])
            ]

            if group_name in dstaddr_groups:
                logging.info(f"Group '{group_name}' exists in policy's dstaddr")
                return True

            else:
                logging.info(
                    f"Group '{group_name}' does not exist in policy's dstaddr"
                )
                return False

        else:
            logging.info("Policy does not exist")
            return None

    else:
        logging.error(
            f"Error checking policy: {response.text} Response code: {response.status_code}"
        )
        return None


def update_group_in_policy(policy_id, group_name, ftg_base_url, ftg_header):
    """API call to add a group to a policy"""
    update_policy_endpoint = f"/policy/{policy_id}"
    policy_url = ftg_base_url + update_policy_endpoint
    new_dstaddr = {"name": f"{group_name}"}

    response = requests.get(policy_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        policy_data = response.json()["results"][0]
        if "dstaddr" in policy_data:
            policy_data["dstaddr"].append(new_dstaddr)
            logging.info(policy_data["dstaddr"])

            update_policy(policy_url, ftg_header, policy_data["dstaddr"])

    else:
        logging.error(
            f"Failed to retrieve policy information, reason: {response.text} /  Response code: {response.status_code}"
        )
        return False


def delete_group_in_policy(policy_id, group_name, ftg_base_url, ftg_header):
    """API call to delete a group from a policy"""
    check_delete = False
    update_policy_endpoint = f"/policy/{policy_id}"
    policy_url = ftg_base_url + update_policy_endpoint
    delete_dstaddr_name = group_name

    response = requests.get(policy_url, headers=ftg_header, verify=False)

    if response.status_code == 200:
        policy_data = response.json()["results"][0]
        policy_data["dstaddr"] = [
            addr
            for addr in policy_data["dstaddr"]
            if addr["name"] != delete_dstaddr_name
        ]

        check_delete = update_policy(policy_url, ftg_header, policy_data["dstaddr"])
        return check_delete

    else:
        logging.error(
            f"Failed to retrieve policy information, reason: {response.text} /  Response code: {response.status_code}"
        )
        return check_delete


def update_policy(policy_url, ftg_header, policy_data_dstaddr):
    """API call to update a policy"""
    update_response = requests.put(
        policy_url,
        headers=ftg_header,
        data=json.dumps({"dstaddr": policy_data_dstaddr}),
        verify=False,
    )

    if update_response.status_code == 200:
        logging.info("Policy dstaddr updated successfully")
        return True

    else:
        logging.error(
            f"Failed to update policy dstaddr, reason: {update_response.text} / Response code: {update_response.status_code}"
        )
        return False
