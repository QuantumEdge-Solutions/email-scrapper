import csv
from urllib.parse import urlparse
import argparse


def get_domain(url):
    """Extract the domain from a given URL."""
    if not urlparse(url).scheme:
        url = "http://" + url

    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def extract_http_https_websites(file_path, output_csv_file, output_text_file):
    """Extract and filter HTTP/HTTPS websites from a CSV file, then save them to a text file and CSV file."""
    data_list = []
    http_https_websites = set()  # Use a set to avoid duplicate domains
    excluded_domains = ['google', 'facebook', 'twitter', 'instagram', 'linkedin', 'pinterest', 'snapchat']

    try:
        with open(file_path, mode='r', newline='', encoding='utf-8', errors='replace') as file:
            reader = csv.DictReader(file)
            for row in reader:
                website = row.get('website', '').strip()
                # print(website)

                # Ignore rows with empty or None website fields
                if not website:
                    continue

                # Process the website URL
                domain = get_domain(website)

                # Exclude domains containing any of the excluded keywords
                if not any(keyword in domain for keyword in excluded_domains):
                    data = {
                        'title': row.get('title', ''),
                        'totalScore': row.get('totalScore', ''),
                        'reviewsCount': row.get('reviewsCount', ''),
                        'city': row.get('city', ''),
                        'address': row.get('address', ''),
                        'website': domain,  # Save only the domain
                        'phone': row.get('phone', ''),
                        'categoryName': row.get('categoryName', '')
                    }
                    data_list.append(data)
                    http_https_websites.add(domain)  # Add the domain to the set

        # Write domains to a text file
        with open(output_text_file, mode='w', encoding='utf-8') as file:
            for website in sorted(http_https_websites):
                file.write(website + '\n')

        # Write filtered data to a new CSV file
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['title', 'totalScore', 'reviewsCount', 'address', 'website', 'phone', 'categoryName']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return http_https_websites


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Extract and filter HTTP/HTTPS websites from a CSV file.")
    parser.add_argument('file_name', type=str, help="The name of the CSV file to process (without extension).")

    args = parser.parse_args()
    file_name = args.file_name

    # Construct paths based on the file_name argument
    file_path = f'{file_name}.csv'
    output_csv_file = f'{file_name}_filtered_data.csv'
    output_text_file = f'{file_name}_websites.txt'

    # Run the extraction process
    http_https_websites_data = extract_http_https_websites(file_path, output_csv_file, output_text_file)