import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager


def generate_number_sequence():
    while True:
        try:
            # Prompting user for the first and last MC numbers
            first_number = int(input("Enter the first MC number: "))
            last_number = int(input("Enter the last MC number: "))

            # Validating that the first number is greater than the last
            if last_number <= first_number:
                print("Error: The first MC number must not exceed the second MC number. Please try again")
                continue

            # Generating the sequence of numbers
            number_sequence = list(range(first_number, last_number + 1))  # Generate descending list

            # Restricting the number of MCs to 100
            if len(number_sequence) > 200:
                print("Limited to 200 operations in trial version. Contact developer for full access. Email:info@firstlinkdispatch.com")
                return None

            # Writing the sequence to a text file
            with open("mc_numbers_list.txt", "w") as file:
                file.write(",".join(map(str, number_sequence)))

            print("The sequence has been written to mc_numbers_list.txt")
            input("Press Enter to continue...")  # Pause before proceeding
            return number_sequence
        except ValueError:
            print("Error: Please enter valid integers for MC numbers.")
        except Exception as e:
            print(f"Unexpected error: {e}")


def read_mc_numbers(file_path):
    print("Reading MC numbers from file...")
    mc_numbers = []
    extension = os.path.splitext(file_path)[1].lower()
    with open(file_path, "r", encoding='utf-8') as file:
        if extension == ".csv":
            reader = csv.reader(file)
            for row in reader:
                if row:
                    mc_numbers.extend([item.strip() for item in row if item.strip()])
        elif extension == '.txt':
            for line in file:
                line = line.strip()
                if line:
                    mc_numbers.extend(line.replace(',', ' ').split())
    print(f"Total MC numbers read: {len(mc_numbers)}")
    return mc_numbers


def get_company_info(driver, mc_number):
    print(f"Fetching company info for MC number: {mc_number}")
    driver.get("https://safer.fmcsa.dot.gov/CompanySnapshot.aspx")
    time.sleep(2)

    mc_radio_button = driver.find_element(By.XPATH, "//input[@name='query_param' and @value='MC_MX']")
    mc_radio_button.click()

    search_field = driver.find_element(By.NAME, "query_string")
    search_field.clear()
    search_field.send_keys(mc_number)
    search_field.send_keys(Keys.RETURN)
    time.sleep(3)

    return driver.page_source


def parse_data(driver, page_source, mc_number):
    soup = BeautifulSoup(page_source, 'html.parser')
    if "The record matching MC/MX Number" in page_source and "INACTIVE in the SAFER database." in page_source:
        print(f"MC number {mc_number} is inactive, skipping.")
        return None

    def get_text(tag):
        return tag.get_text(strip=True) if tag else ''

    fields_to_extract = {
        'Entity Type': 'Entity Type:',
        'USDOT Status': 'USDOT Status:',
        'Out of Service Date': 'Out of Service Date:',
        'USDOT Number': 'USDOT Number:',
        'MCS-150 Form Date': 'MCS-150 Form Date:',
        'MCS-150 Mileage (Year)': 'MCS-150 Mileage (Year):',
        'Operating Authority Status': 'Operating Authority Status:',
        'MC/MX/FF Number(s)': 'MC/MX/FF Number(s):',
        'Legal Name': 'Legal Name:',
        'DBA Name': 'DBA Name:',
        'Physical Address': 'Physical Address:',
        'Phone': 'Phone:',
        'Mailing Address': 'Mailing Address:',
        'DUNS Number': 'DUNS Number:',
        'Power Units': 'Power Units:',
        'Drivers': 'Drivers:'}

    data = {}
    for field, label in fields_to_extract.items():
        th = soup.find('th', string=label)
        if th:
            data_cell = th.find_next('td')
            data[field] = get_text(data_cell)
        else:
            data[field] = None
    def extract_nested_table_data(summary_text):
        table = soup.find('table', summary=summary_text)
        if not table:
            return []
        items = []
        for row in table.find_all('tr')[1:]:
            cells = row.find_all('td')
            if len(cells) == 2 and get_text(cells[0]) == 'X':
                items.append(get_text(cells[1]))
        return items

    data['Operation Classification'] = extract_nested_table_data('Operation Classification')
    data['Carrier Operation'] = extract_nested_table_data('Carrier Operation')
    data['Cargo Carried'] = extract_nested_table_data('Cargo Carried')
    data['MC Number'] = mc_number

    # Extracting emails
    dot_number = data['USDOT Number']
    if not dot_number:
        print(f"No valid data found for MC number {mc_number}, skipping email extraction.")
        return None

    url = f"http://ai.fmcsa.dot.gov/sms/safer_xfr.aspx?DOT={dot_number}&Form=SAFER"
    driver.get(url)
    try:
        carrier_registration_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="CarrierRegistration"]/a[1]')))
        carrier_registration_link.click()

        email = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="regBox"]/ul[1]/li[7]/span'))).text
    except Exception as e:
        print(f'No Email found!')
        email = None

    data['Email'] = email

    # Apply filtering logic
    if data.get('Entity Type') != "CARRIER":
        print(f"MC number {mc_number} skipped: Entity Type is not 'CARRIER'.")
        return None
    if data.get('USDOT Status') != "ACTIVE":
        print(f"MC number {mc_number} skipped: USDOT Status is not 'ACTIVE'.")
        return None

    # Calculate registration age in days
    mcs_150_date = data.get('MCS-150 Form Date')
    try:
        reg_date = datetime.strptime(mcs_150_date, "%m/%d/%Y")
        today = datetime.today()
        days_registered = (today - reg_date).days
        data['Days Registered'] = days_registered

        # Categorize the registration age
        if days_registered < 30:
            data['Registration Category'] = "<30 days"
        elif days_registered < 60:
            data['Registration Category'] = "<60 days"
        elif days_registered < 90:
            data['Registration Category'] = "<90 days"
        else:
            data['Registration Category'] = "3+ months"
    except (ValueError, TypeError):
        data['Days Registered'] = None
        data['Registration Category'] = None
        print(f"MC number {mc_number}: Unable to calculate registration days (invalid date format).")

    return data


def create_or_update_excel(file_path, data_dict_list):
    print(f"Creating or updating Excel file at: {file_path}")
    df = pd.DataFrame(data_dict_list)

    if os.path.exists(file_path):
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False, sheet_name="Company Info")
    else:
        with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False, sheet_name="Company Info")


def main():
    print("Starting the process...")
    number_sequence = generate_number_sequence()
    if not number_sequence:
        return

    mc_number_file_path = 'mc_numbers_list.txt'
    output_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "safer_data.xlsx")

    mc_numbers = read_mc_numbers(mc_number_file_path)

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    data_list = []
    try:
        for mc_number in mc_numbers:
            html_content = get_company_info(driver, mc_number)
            data = parse_data(driver, html_content, mc_number)
            if data:
                data_list.append(data)
                create_or_update_excel(output_file_path, data_list)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()
        if data_list:
            create_or_update_excel(output_file_path, data_list)
        print("Process completed...")


if __name__ == "__main__":
    main()
