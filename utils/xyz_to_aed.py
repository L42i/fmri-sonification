import csv
import math
import os

input_csv = "spatialization/normalized_xyz.csv"  # <-- your source file
output_csv = "spatialization/aed.csv"

os.makedirs(os.path.dirname(output_csv), exist_ok=True)

with open(input_csv, "r", newline="") as infile, open(output_csv, "w", newline="") as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ["azimuth", "elevation", "distance"]
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        x = float(row["X"])
        y = float(row["Y"])
        z = float(row["Z"])

        # Distance
        r = math.sqrt(x**2 + y**2 + z**2)

        # Azimuth: 0° at (0,1), clockwise toward (1,0)
        azimuth_rad = math.atan2(x, y)
        azimuth_deg = (math.degrees(azimuth_rad) + 360) % 360

        # Elevation: angle from horizontal plane
        horiz_dist = math.sqrt(x**2 + y**2)
        elevation_rad = math.atan2(z, horiz_dist)
        elevation_deg = math.degrees(elevation_rad)

        # Clamp elevation to [-45, 45]
        elevation_deg = max(-45, min(45, elevation_deg))

        writer.writerow({
            "azimuth": azimuth_deg,
            "elevation": elevation_deg,
            "distance": r
        })

print(f"Saved AED data to {output_csv}")