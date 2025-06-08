# FMCSA-Carrier-Data-Scrapper
web scraping automation tool


# Firstlink MC Number Scraper 🚛📊

This project is a **web scraping automation tool** designed to collect detailed company information from the **FMCSA SAFER** system using a list or range of **MC (Motor Carrier)** numbers. It uses **Selenium** and **BeautifulSoup** to navigate and extract data, storing results in an Excel spreadsheet for further use.

## 🔍 Features

- **User-Prompted Range Input**: Enter a starting and ending MC number to generate a list (max 200).
- **Smart Filtering**: Only collects data for **active carriers** with **USDOT status = ACTIVE** and **Entity Type = CARRIER**.
- **Email Extraction**: Attempts to locate and extract associated contact email from FMCSA systems.
- **Registration Age Categorization**: Automatically categorizes MC records based on days since the latest MCS-150 form.
- **Excel Output**: Data is saved or updated in an Excel file on your Desktop.

## 📁 Output Example

Each row in the resulting Excel sheet contains:

- Legal Name, DBA Name  
- USDOT & MC Numbers  
- Status, Entity Type, and Registration Dates  
- Power Units, Drivers, and Cargo Carried  
- Operation Classification & Carrier Operation  
- Contact Info including Email  
- Registration Category (e.g. `<30 days`, `<60 days`, `3+ months`)

## 🧰 Technologies Used

- Python 3
- Selenium (with Chrome WebDriver)
- BeautifulSoup
- pandas & openpyxl
- ChromeDriverManager for auto-install

## ⚙️ How to Use

1. Clone the repo and install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
   *(Make sure you have Google Chrome installed.)*

2. Run the script:
   ```bash
   python Firstlink_Scraper.py
   ```

3. Enter a range of MC numbers when prompted (max 200 in trial version).

4. The output Excel file `safer_data.xlsx` will be saved to your Desktop.

## 🛠️ Installation Steps

1. Make sure you have Python 3 installed.
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 📌 Notes

- Trial version is limited to 200 MC numbers per run.
- Emails are not always available — this depends on the FMCSA database.
- Errors and skips are logged in the console output.
- For commercial/full access, contact: `info@firstlinkai.com`

## 📜 License

This project is provided as-is under a restricted use trial. Contact the developer for licensing options or full access.
