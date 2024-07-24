# Fortinet-Maliciousip-AutoBlock

## Overview

Welcome to the [Criminal IP](https://criminalip.io) Integration with Fortinet Firewalls! 

This project automates the process of swiftly blocking malicious IP addresses identified by the Criminal IP service using Fortinet firewalls. By leveraging Criminal IP's real-time threat intelligence, the system retrieves and updates lists of identified malicious IPs. It then seamlessly creates and manages corresponding block rules on Fortinet firewalls.


</br>

## Key Features

- **Fetch Malicious IP List:** Retrieves the latest list of IP addresses classified as malicious from Criminal IP service.
   
- **Rule Creation:** Automatically generates block rules on Fortinet firewalls based on the malicious IP list obtained from Criminal IP.
   
- **Rule Management:** Periodically reviews, updates, or removes created block rules as necessary.

</br>

## Prerequisites

Before using this system, ensure you have the following:

- **Criminal IP API Key:** Obtain from [Criminal IP](https://www.criminalip.io/mypage/information) after logging in.
  
- **Fortigate Token:** Token value granted when creating a REST API Administrator account on Fortigate.
  
- **Fortigate Policy ID:** ID of the source-destination policy under Policy & Object > Firewall Policy in Fortigate.

</br>

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/criminalip/Fortinet-Maliciousip-AutoBlock.git
	```
2. fire_config.py settings:

| Setting             | Description                                     |
|---------------------|-------------------------------------------------|
| CRIMINALIP_API_KEY  | Insert your Criminal IP API KEY here.           |
| TARGET              | Insert the firewall address here.                |
| TOKEN               | Insert the Fortigate Token here.                 |
| POLICYID            | Put the Fortigate Policy ID here.                |

</br>

## Project Structure
```bash
📦Auto_malicious_ip_block
 ┣ 📂core
 ┃ ┣ 📂api
 ┃ ┃ ┣ 📂input
 ┃ ┃ ┣ 📂output
 ┃ ┃ ┣ 📜cip_request_get_ip.py
 ┃ ┃ ┗ 📜managefiles.py
 ┃ ┗ 📂fwb
 ┃ ┃ ┗ 📜_ftg_request_parm.py
 ┣ 📂log
 ┣ 📜cip_c2_detect_query.json
 ┣ 📜fire_config.py
 ┗ 📜main.py
```
</br>

## Usage
``` bash
python main.py
```





