import os
import subprocess
import sys
import webbrowser
import requests
import shutil
import filecmp


# Add error handling
def handle_error(msg):
    print(f"Error: {msg}")
    sys.exit(1)


ignore_files = [".git", "API.MPYA", "update.py"]
updated_files = []

# Read API key from file
with open("API.MPYA", "r") as f:
    f.readline()  # discard first line
    f.readline()  # discard the second line
    secret_key = f.readline().strip()

# If API key is valid, open the website. (Open it if you want 😉)
if secret_key == "extratankz":
    webbrowser.open_new_tab("https://r.mtdv.me/mpya")

# List of URLs to try for updates
urls = [
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/mpya.py",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/mpya.pyw",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/requirements.txt",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/styles.py",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/install.bat",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/umbrella.ico",
]

# Download and install the updated file from each URL in the list
for url in urls:
    filename = os.path.join(os.getcwd(), url.split("/")[-1])
    try:
        r = requests.get(url)
        if r.status_code == 404:
            if os.path.exists(filename):
                os.remove(filename)
        else:
            with open(filename, "wb") as f:
                f.write(r.content)
            updated_files.append(filename)
    except requests.exceptions.RequestException:
        handle_error("Failed to download update")

if len(updated_files) == 0:
    print("No updated files found.")
    sys.exit(0)

# Scan through all downloaded files and delete file
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file in ignore_files:
            continue
        filepath = os.path.join(root, file)
        try:
            with open(filepath, "r") as f:
                if "404: Not Found" in f.readline():
                    os.remove(filepath)
        except:
            pass

# Compare original and updated files and backup/restore if needed
for filename in updated_files:
    backup_filename = f"{filename}.bak"
    if not os.path.exists(backup_filename):
        shutil.copy2(filename, backup_filename)
    try:
        if filecmp.cmp(backup_filename, filename, shallow=False):
            # The files are identical. No backup required.
            os.remove(backup_filename)
        else:
            # The files are different. Restore the backup.
            shutil.copy2(backup_filename, filename)
    except OSError as e:
        handle_error(f"Cannot compare files {backup_filename} and {filename}: {e}")

# Remove backup files
for root, dirs, files in os.walk(os.getcwd()):
    for file in files:
        if file in ignore_files:
            continue
        backup_file = os.path.join(root, f"{file}.bak")
        if os.path.exists(backup_file):
            os.remove(backup_file)
