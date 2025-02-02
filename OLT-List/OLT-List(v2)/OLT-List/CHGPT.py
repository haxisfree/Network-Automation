from netmiko import ConnectHandler
from getpass import getpass
import re
import time
import openpyxl
import os
from colorama import init, Fore, Style
import datetime

# Initialize Colorama
init()

# Constants
DESCRIPTION_FILENAME = "List Of Description.txt"
RELATIVE_PATH = os.path.dirname(__file__)
DESCRIPTION_FILE_PATH = os.path.join(RELATIVE_PATH, DESCRIPTION_FILENAME)
DNS_LIST = ['pppoe7.dc2.rou', 'pppoe4.col.rou']

def get_excel_file():
    """Get the Excel file path from the user or use the default."""
    excel_file_path = input("Enter Excel file path or press ENTER to use the default: ")
    if not excel_file_path:
        for filename in os.listdir(RELATIVE_PATH):
            if filename.endswith(".xlsx"):
                excel_file_path = os.path.join(RELATIVE_PATH, filename)
                break
        else:
            raise FileNotFoundError("No Excel file found in the directory.")
    return excel_file_path

def parse_excel_file(excel_file_path):
    """Parse the Excel file to extract sub-interface lists."""
    workbook = openpyxl.load_workbook(excel_file_path)
    sheet = workbook.active
    
    pppoe7_subif, pppoe4_subif = [], []

    for row in sheet.iter_rows(min_row=2, max_col=1):
        cell_value = row[0].value
        if "C1002.07" in cell_value:
            sub_int = re.search(r"\d*/\d*/\d*\.\d*", cell_value)
            if sub_int:
                pppoe7_subif.append(sub_int.group())
        elif "C1002.04" in cell_value:
            sub_int = re.search(r"\d*/\d*/\d*\.\d*", cell_value)
            if sub_int:
                pppoe4_subif.append(sub_int.group())

    return pppoe7_subif, pppoe4_subif

def prompt_overwrite_file(file_path):
    """Prompt the user to overwrite or append to the file if it exists."""
    if os.path.exists(file_path):
        choice = input(f"File '{file_path}' exists. Overwrite? (y/n): ").lower()
        if choice in ['y', 'yes']:
            open(file_path, 'w').close()  # Overwrite file
        elif choice in ['n', 'no']:
            pass  # Append to existing file
        else:
            print("Invalid choice. Defaulting to append mode.")

class NetworkConnection:
    """Handle network connections using Netmiko."""

    def __init__(self):
        self.username = None
        self.password = None

    def establish_connection(self):
        """Prompt for credentials and test connection."""
        attempts = 3
        for _ in range(attempts):
            try:
                self.username = input("Enter your username: ")
                self.password = getpass("Enter your password: ")
                test_device = {
                    "device_type": "cisco_ios",
                    "host": "l22.dc1.swi",
                    "username": self.username,
                    "password": self.password,
                }
                with ConnectHandler(**test_device) as conn:
                    conn.disconnect()
                return True
            except Exception as e:
                print(f"Connection failed: {e}. Attempts remaining: {attempts - 1}")
        raise ConnectionError("Unable to establish connection after 3 attempts.")

def fetch_subinterfaces(device_info, command):
    """Fetch and parse sub-interface information from the device."""
    with ConnectHandler(**device_info) as conn:
        output = conn.send_command(command)
    sub_int_list = {}
    for line in output.splitlines():
        columns = re.split(r"\s+", line.strip())
        if len(columns) >= 4 and columns[1] == "up" and columns[2] == "up":
            sub_int = re.search(r"\d*/\d*/\d*\.\d*", columns[0])
            if sub_int:
                sub_int_list[sub_int.group()] = columns[3]
    return sub_int_list

def compare_and_write(file_path, conf_sub_ints, excel_sub_ints, dns):
    """Compare device sub-interfaces with Excel and write results to a file."""
    deficiencies = set(conf_sub_ints) - set(excel_sub_ints)
    unconfigured = set(excel_sub_ints) - set(conf_sub_ints)

    with open(file_path, 'a') as file:
        file.write(f"\n{'=' * 40} {datetime.datetime.now()} {'=' * 40}\n")
        file.write(f"{'-' * 50} {dns} {'-' * 50}\n")

        file.write("Configured sub-interfaces not in Excel:\n")
        for sub_int in deficiencies:
            file.write(f"{sub_int}  {conf_sub_ints[sub_int]}\n")

        file.write("\nUnconfigured sub-interfaces in Excel:\n")
        for sub_int in unconfigured:
            file.write(f"{sub_int}\n")

def main():
    start_time = time.time()

    # File and Excel setup
    prompt_overwrite_file(DESCRIPTION_FILE_PATH)
    excel_file_path = get_excel_file()
    pppoe7_subif, pppoe4_subif = parse_excel_file(excel_file_path)

    # Establish network connection
    connection = NetworkConnection()
    if not connection.establish_connection():
        print("Exiting script.")
        return

    for dns in DNS_LIST:
        device_info = {
            "device_type": "cisco_ios",
            "host": dns,
            "username": connection.username,
            "password": connection.password,
        }
        command = "show int desc | include .TEH.OLT" if "7" in dns else "show int desc | include .PRD.OLT"
        conf_sub_ints = fetch_subinterfaces(device_info, command)

        if "7" in dns:
            compare_and_write(DESCRIPTION_FILE_PATH, conf_sub_ints, pppoe7_subif, dns)
        else:
            compare_and_write(DESCRIPTION_FILE_PATH, conf_sub_ints, pppoe4_subif, dns)

    print("\nScript completed successfully!")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    main()
