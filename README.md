# email-scrapper

### 1. Install Requirements

  ```bash
    pip install -r requirements.txt
  ```

### 2. Run `filter_csv.py`

- Execute the `filter_csv.py` script
- using command line:
  ```bash
    python filter_csv.py {{file_name}} # file_name is the name of the file to be filtered without .csv extension
  ```
- This will generate the filtered data CSV and a text file containing the websites.

### 3. Run `selenium_script.py`

- Execute the `selenium_script.py` script.
- ```bash
    python selenium_script.py {{file_name}} # file_name is the name of the file to be filtered without .csv extension
  ```
    - This will process the filtered data and generate the final leads in the specified output CSV file.
 
### 4. Move chromedriver.exe to project directory

## Notes

- The scripts should be run in the order specified above to ensure proper functionality.
