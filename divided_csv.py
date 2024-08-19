import pandas as pd
import os

def divide_csv(input_file, output_dir, num_parts=7):
    # Read the Excel file
    df = pd.read_excel(input_file)

    # Calculate the number of rows per part
    num_rows = len(df)
    rows_per_part = num_rows // num_parts

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Split the DataFrame into parts and save each part
    for i in range(num_parts):
        start_row = i * rows_per_part
        # Ensure the last part includes any remaining rows
        if i == num_parts - 1:
            end_row = num_rows
        else:
            end_row = (i + 1) * rows_per_part
        
        part_df = df.iloc[start_row:end_row]
        output_file = os.path.join(output_dir, f'part_{i+1}.csv')
        part_df.to_csv(output_file, index=False)

    print(f'Divided Excel file into {num_parts} parts and saved them in {output_dir}')

# Example usage
input_file = 'H:/upwork/whole usa/usama - california results.xlsx'  # Replace with your input Excel file path
output_dir = 'ca_output'  # Replace with the desired output directory

divide_csv(input_file, output_dir)
