import csv


def get_dataset_extent(file_path):
  global_min = None
  global_max = None

  with open(file_path, newline='', encoding='utf-8') as f:
    reader = csv.reader(f)

    for row in reader:
      for value in row:
        try:
          num = float(value)
          if global_min is None or num < global_min:
            global_min = num
          if global_max is None or num > global_max:
            global_max = num
        except (ValueError, TypeError):
          # skip non-numeric values
          continue

  return global_min, global_max


if __name__ == "__main__":
  min_val, max_val = get_dataset_extent("data/timecourses_hc.csv")
  print("hc")
  print(f"Min value: {min_val}")
  print(f"Max value: {max_val}")

  min_val, max_val = get_dataset_extent("data/timecourses_sz.csv")
  print("sz")
  print(f"Min value: {min_val}")
  print(f"Max value: {max_val}")
