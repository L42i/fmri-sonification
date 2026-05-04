import csv


# Function to read AED file and convert to the desired format
def convert_to_custom_format(input_file, output_file):
  with open(input_file, mode='r') as infile, open(output_file, mode='w', newline='') as outfile:
    csv_reader = csv.reader(infile)
    csv_writer = csv.writer(outfile, delimiter=';')

    # Skip the header
    header = next(csv_reader)

    # Process each row
    row_number = 1  # Start row number from 1
    for row in csv_reader:
      # Extract Azimuth (a), Elevation (e), and Distance (d) from each row
      a = row[0]
      e = row[1]
      d = row[2]

      # Create the new formatted row
      new_row = [a, e, d, row_number, "ff000000", "0"]

      # Write the new formatted row to the output CSV
      csv_writer.writerow(new_row)

      # Increment row number
      row_number += 1


# Define input and output file names
input_filename = 'spatialization/aed.csv'  # Input file with AED coordinates
output_filename = 'spatialization/locations.csv'  # Output file name

# Call the conversion function
convert_to_custom_format(input_filename, output_filename)

print(f"Conversion completed! The new file is saved as '{output_filename}'.")