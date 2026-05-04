import os

base_dir = "samples"

for root, dirs, files in os.walk(base_dir):
  for file in files:
    full_path = os.path.join(root, file)

    # Delete .reapeaks files
    if file.endswith(".reapeaks"):
      os.remove(full_path)
      print(f"Deleted: {full_path}")
      continue

    # Process .wav files
    if file.endswith(".wav"):
      # Expected format: "[type] [vowel] [pitch].wav"
      name_parts = file.replace(".wav", "").split()

      if len(name_parts) != 3:
        print(f"Skipping unexpected format: {file}")
        continue

      voice_type = name_parts[0]  # breathy | raspy | supported
      new_name = f"{voice_type}.wav"
      new_path = os.path.join(root, new_name)

      # Avoid overwriting files
      counter = 1
      while os.path.exists(new_path):
        new_name = f"{voice_type}_{counter}.wav"
        new_path = os.path.join(root, new_name)
        counter += 1

      os.rename(full_path, new_path)
      print(f"Renamed: {full_path} -> {new_path}")
