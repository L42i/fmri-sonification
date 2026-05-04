import os
import csv


class Data:
  def __init__(self, directory='data/', headers=None):
    self.directory = directory
    self.headers = headers
    self.files_data = {}

  def read_csv_files(self):
    # List all the CSV files in the specified directory
    csv_files = [f for f in os.listdir(self.directory) if f.endswith('.csv')]

    for file in csv_files:
      file_path = os.path.join(self.directory, file)
      # Read each CSV file and store its content
      self.files_data[file] = self.parse_csv(file_path)

  def detect_type(self, value):
    """Auto-detect the type of each value (int, float, or string)"""
    try:
      # Try converting to integer
      return int(value)
    except ValueError:
      try:
        # Try converting to float
        return float(value)
      except ValueError:
        # Return as string if neither int nor float
        return value

  def parse_csv(self, file_path):
    """Parse a single CSV file and auto-detect types"""
    with open(file_path, mode='r', newline='', encoding='utf-8') as f:
      reader = csv.reader(f)
      data = [row for row in reader]

    # If headers are provided, treat the first row as headers
    if self.headers:
      return [
        {self.headers[i]: self.detect_type(row[i]) for i in range(len(self.headers))}
        for row in data
      ]
    else:
      return [
        [self.detect_type(value) for value in row] for row in data
      ]

  def get_data(self, file_name=None):
    """Retrieve data for a specific file or all files if no file name is given"""
    if file_name:
      return self.files_data.get(file_name)
    return self.files_data
