import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from urllib.parse import urlparse, urljoin
from requests.exceptions import ConnectTimeout, ReadTimeout, RequestException
import time
import argparse

def get_domain(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def is_valid_email(email):
    """Check if the email should be included based on its domain."""
    excluded_domains = {'sentry.io', 'sentry.wixpress.com', 'sentry-next.wixpress.com'}
    domain = email.split('@')[-1]
    return domain not in excluded_domains

def extract_emails_from_page(page_source, max_emails=4):
    """Extract email addresses from the page source, ignoring those with excluded domains, and limit the number of emails."""
    ignored_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_regex, page_source)
    
    # Filter and limit the number of emails
    filtered_emails = []
    for email in emails:
        if len(filtered_emails) >= max_emails:
            break
        domain = email.split('@')[-1]
        if not any(domain.endswith(ext) for ext in ignored_extensions) and is_valid_email(email):
            filtered_emails.append(email)
    
    return set(filtered_emails)

def fetch_emails_with_bs4(url, max_emails=4, retries=3, delay=5):
    """Fetch and extract emails from a page using BeautifulSoup with retry logic."""
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)  # Set a timeout of 10 seconds
            soup = BeautifulSoup(response.text, 'html.parser')
            page_source = soup.prettify()  # Format the HTML for regex
            return extract_emails_from_page(page_source, max_emails=max_emails)
        except (ConnectTimeout, ReadTimeout) as e:
            print(f"Timeout error fetching {url} with BeautifulSoup: {e}")
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
            else:
                return set()
        except RequestException as e:
            print(f"Error fetching with BeautifulSoup: {e}")
            return set()

def fetch_emails_from_page(driver, url, max_emails=4):
    """Fetch and extract emails from a page using Selenium with a page load timeout."""
    try:
        driver.set_page_load_timeout(10)  # Set page load timeout to 10 seconds
        driver.get(url)
        page_source = driver.page_source
        return extract_emails_from_page(page_source, max_emails=max_emails)
    except TimeoutException as e:
        print(f"Timeout while loading {url} with Selenium: {e}")
        return set()
    except Exception as e:
        print(f"Error fetching with Selenium: {e}")
        return set()

def scrape_url(url, max_emails=4):
    domain = get_domain(url)
    emails = fetch_emails_with_bs4(url, max_emails=max_emails)
    
    if not emails:
        try:
            # Check various pages
            for path in ['/contact-us', '/contact', '/about-us', '/about']:
                page_url = urljoin(domain, path)
                emails = fetch_emails_with_bs4(page_url, max_emails=max_emails)
                if emails:
                    break
            
            # If no emails found, use Selenium
            if not emails:
                options = Options()
                options.headless = True
                driver = webdriver.Chrome(service=Service("chromedriver.exe"), options=options)
                try:
                    for path in ['/contact-us', '/contact', '/about-us', '/about']:
                        page_url = urljoin(domain, path)
                        emails = fetch_emails_from_page(driver, page_url, max_emails=max_emails)
                        if emails:
                            break
                finally:
                    driver.quit()
    
        except Exception as e:
            print(f"Error scraping {url}: {e}")
        
    return url, emails

def run_scraper(urls, max_emails=4):
    email_dict = {}
    max_workers = 30  # Adjust based on your system capabilities
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(scrape_url, url, max_emails=max_emails): url for url in urls}
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                url, emails = future.result()
                email_dict[url] = list(emails)
            except Exception as e:
                print(f"Error processing {url}: {e}")
        
    return email_dict

def read_websites_from_txt(file_path):
    """Read website URLs from a text file and return a list of URLs."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file if line.strip()]

def read_data_from_csv(file_path):
    """Read the entire DataFrame from a CSV file and return it."""
    return pd.read_csv(file_path)

def process_emails(df, email_data):
    """Integrate email data with the original DataFrame, preserving all other columns."""
    # List of emails to reject
    rejected_emails = {'user@domain.com', 'email@example.com', 'user@gmail.com', 'email@email.com'}

    # Convert email data to DataFrame
    email_records = []
    for website, emails in email_data.items():
        # Filter out rejected emails
        filtered_emails = [email for email in emails if email not in rejected_emails]
        
        # Only include rows with at least one valid email
        if filtered_emails:
            email_records.append({'website': website, 'emails': filtered_emails})
    
    # If no valid email records, return the original DataFrame unchanged
    if not email_records:
        return df

    email_df = pd.DataFrame(email_records)

    # Define the number of email columns
    max_emails = 4
    email_columns = [f'email_{i+1}' for i in range(max_emails)]
    
    # Expand the email lists into separate columns
    email_expanded = pd.DataFrame(
        [emails + [None] * (max_emails - len(emails)) for emails in email_df['emails']],
        columns=email_columns,
        index=email_df.index
    )

    # Combine expanded email columns with the email_df
    email_df = email_df.drop(columns='emails')
    email_df = pd.concat([email_df, email_expanded], axis=1)

    # Merge with the original DataFrame
    combined_df = df.set_index('website').join(email_df.set_index('website'), how='left').reset_index()

    # Remove rows where no emails were found
    combined_df = combined_df.dropna(subset=email_columns, how='all')

    return combined_df


def write_emails_to_csv(df, output_file_path):
    """Write the combined DataFrame to a CSV file."""
    df.to_csv(output_file_path, index=False)

# Main script execution
if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract and filter HTTP/HTTPS websites from a CSV file.")
    parser.add_argument('file_name', type=str, help="The name of the CSV file to process (without extension).")

    args = parser.parse_args()
    file_name = args.file_name

    # Construct paths based on the file_name argument
    # Path to the text file containing websites, created by running the filter_csv.py script
    websites_txt_path = f'{file_name}_websites.txt'
    # Path to the CSV file with filtered data, also created by running the filter_csv.py script
    additional_csv_path = f'{file_name}_filtered_data.csv'
    # Path to the final output CSV file that will store the leads (website emails) collected during the process
    output_csv_path = f'{file_name}_website_emails.csv'

    # Read website URLs from text file
    urls = read_websites_from_txt(websites_txt_path)

    # Read the original DataFrame from CSV
    df = read_data_from_csv(additional_csv_path)

    # Run scraper
    email_data = run_scraper(urls, max_emails=4)

    # Process email data
    combined_df = process_emails(df, email_data)

    # Write results to CSV
    write_emails_to_csv(combined_df, output_csv_path)
