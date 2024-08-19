import csv
from urllib.parse import urlparse

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
                website = row.get('Website', '').strip()
                # print(website)
                # Ignore rows with empty or None website fields
                if not website:
                    continue
                
                # Process the website URL
                domain = get_domain(website)

                # Exclude domains containing any of the excluded keywords
                if not any(keyword in domain for keyword in excluded_domains):
                    data = {
                        'Business Name': row.get('Business Name', ''),
                        'Rating': row.get('Rating', ''),
                        'RatingCount': row.get('RatingCount', ''),
                        # 'city': row.get('city', ''),
                        'Address': row.get('Address', ''),
                        'Website': domain,  # Save only the domain
                        'Phone': row.get('Phone', ''),
                        'Keyword': row.get('Keyword', '')
                    }
                    data_list.append(data)
                    http_https_websites.add(domain)  # Add the domain to the set

        # Write domains to a text file
        with open(output_text_file, mode='w', encoding='utf-8') as file:
            for website in sorted(http_https_websites):
                file.write(website + '\n')

        # Write filtered data to a new CSV file
        with open(output_csv_file, mode='w', newline='', encoding='utf-8') as file:
            fieldnames = ['Business Name', 'Rating', 'RatingCount','Address', 'Website', 'Phone', 'Keyword']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_list)

    except UnicodeDecodeError as e:
        print(f"Error reading the file: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return http_https_websites

# Path to the input CSV file that contains the websites to process
file_path = 'H:/upwork/ca_output/part_3.csv'  
# Path to the output CSV file where filtered data will be saved for use in the Selenium script
output_csv_file = 'H:/upwork/ca_output/part_3_filtered_data.csv'
# Path to the output text file that will store all the websites found in the input CSV
output_text_file = 'H:/upwork/ca_output/part_3_http_https_websites.txt' 
http_https_websites_data = extract_http_https_websites(file_path, output_csv_file, output_text_file)
# print(http_https_websites_data)
