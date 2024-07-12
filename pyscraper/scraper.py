import pandas as pd
import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# Function to decode the email address protected by Cloudflare
def email(string):
    r = int(string[:2], 16)
    email = ''.join([chr(int(string[i:i+2], 16) ^ r)
                     for i in range(2, len(string), 2)])
    return email

# Function to scrape the website and extract the required data
def scrape_and_extract(denominazione):
    # Construct the search query URL
    query = f"site:ufficiocamerale.it {denominazione}"
    search_url = f"https://www.google.com/search?q={query}"

    # Send a GET request to Google search
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()

        # Introduce random delay between 5 to 10 seconds
        time.sleep(random.uniform(5, 10))

        # Parse the HTML response
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the URL of the first search result
        result_url = soup.find('div', class_='g').find('a')['href']

        # Visit the found URL and extract the <strong> tag with id="field_pec"
        response = requests.get(result_url, headers=headers)
        response.raise_for_status()

        # Introduce random delay between 5 to 10 seconds
        time.sleep(random.uniform(5, 10))

        soup = BeautifulSoup(response.text, 'html.parser')
        field_pec_tag = soup.find('strong', id='field_pec')
        if field_pec_tag:
            # Extract the encoded email address
            encoded_email = field_pec_tag.find('a', class_='__cf_email__')['data-cfemail']
            
            # Print the encoded value
            encoded_value = email(encoded_email)
            print(f"Encoded value for {denominazione}: {encoded_value}")
            
            return encoded_value  # Return the decoded email address
        else:
            print(f"Error: <strong id='field_pec'> tag not found on {result_url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error requesting page: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Read input CSV file
input_csv = '1.csv'
output_csv = 'output.csv'

try:
    df = pd.read_csv(input_csv, delimiter=';')
except FileNotFoundError:
    print(f"Error: File '{input_csv}' not found.")
    exit(1)
except pd.errors.ParserError:
    print(f"Error: Failed to parse CSV file. Check delimiter and file format.")
    exit(1)

# Prepare output CSV file
with open(output_csv, mode='w', newline='', encoding='utf-8') as output_file:
    csv_writer = csv.writer(output_file)
    csv_writer.writerow(['N.', 'ID domanda', 'Denominazione', 'Encoded value'])

    # Process each row in the input CSV
    for index, row in df.iterrows():
        denominazione = row['Denominazione']
        print(f"Processing {denominazione}...")

        # Scrape and extract data
        encoded_value = scrape_and_extract(denominazione)

        # Write to output CSV
        if encoded_value:
            csv_writer.writerow([row['N.'], row['ID domanda'], denominazione, encoded_value])

        # Introduce additional random delay between 30 to 40 seconds
        time.sleep(random.uniform(30, 40))

print(f"Output saved to '{output_csv}'.")
