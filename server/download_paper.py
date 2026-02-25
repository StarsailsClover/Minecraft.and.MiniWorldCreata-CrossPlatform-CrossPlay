import json
import urllib.request
import os
import sys

# Get script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Read builds info
builds_path = os.path.join(script_dir, 'paper', 'builds.json')
with open(builds_path, 'r') as f:
    data = json.load(f)

# Get the latest build
latest_build = data['builds'][-1]
build_number = latest_build['build']
jar_name = latest_build['downloads']['application']['name']

print(f"Latest build: {build_number}")
print(f"JAR name: {jar_name}")

# Construct download URL
download_url = f"https://api.papermc.io/v2/projects/paper/versions/1.20.6/builds/{build_number}/downloads/{jar_name}"
print(f"Download URL: {download_url}")

# Download the jar
output_path = os.path.join(script_dir, 'paper', jar_name)
print(f"Downloading to: {output_path}")

urllib.request.urlretrieve(download_url, output_path)
print(f"Downloaded successfully!")

# Also save as paper.jar for convenience
import shutil
shutil.copy(output_path, os.path.join(script_dir, "paper", "paper.jar"))
print("Copied to paper.jar")
