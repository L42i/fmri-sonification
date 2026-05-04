import pandas as pd
import numpy as np


# Load the CSV file with the vector data
def load_vectors(file_path):
  # Assuming the CSV file has headers "X", "Y", "Z"
  df = pd.read_csv(file_path)
  return df


# Calculate the magnitude (length) of each vector
def calculate_magnitude(df):
  return np.sqrt(df['X'] ** 2 + df['Y'] ** 2 + df['Z'] ** 2)


# Normalize vectors by scaling them according to the longest vector
def normalize_vectors(df):
  # Calculate magnitudes of all vectors
  magnitudes = calculate_magnitude(df)

  # Find the longest vector
  max_magnitude = magnitudes.max()

  # Normalize the vectors (scale each vector by the ratio of max magnitude to its own magnitude)
  df['X'] = df['X'] / max_magnitude
  df['Y'] = df['Y'] / max_magnitude
  df['Z'] = df['Z'] / max_magnitude

  return df


# Save the normalized vectors to a new CSV file
def save_normalized_vectors(df, output_file):
  df.to_csv(output_file, index=False)


def main():
  input_file = 'spatialization/xyz.csv'  # Replace with your input file path
  output_file = 'spatialization/normalized_xyz.csv'  # Replace with desired output file path

  # Load the vectors
  df = load_vectors(input_file)

  # Normalize the vectors
  normalized_df = normalize_vectors(df)

  # Save the normalized vectors to a new CSV file
  save_normalized_vectors(normalized_df, output_file)

  print(f"Normalized vectors saved to {output_file}")


if __name__ == "__main__":
  main()