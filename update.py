import os
import subprocess
import sys
import webbrowser
import requests
import shutil


# Add error handling
def handle_error(msg):
    print(f"Error: {msg}")
    if "Failed to download file" not in msg:
        sys.exit(1)

# Read API key from file
with open("API.MPYA", "r") as f:
    f.readline()  # discard first line
    f.readline()  # discard the second line
    secret_key = f.readline().strip()

# If API key is valid, open the website (commented out since it may interfere with script execution)
if secret_key == "extratankz":
    pass
    # webbrowser.open_new_tab("https://r.mtdv.me/mpya")

# List of URLs to try for updates
urls = [
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/mpya.py",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/mpya.pyw",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/requirements.txt",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/styles.py",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/install.bat",
    "https://raw.githubusercontent.com/ExtraTankz/mpya/main/umbrella.ico",
]

# Download the updated version of update.py from your repository
update_url = "https://raw.githubusercontent.com/ExtraTankz/mpya/main/update.py"  # change to your repo URL
update_file = "update_new.py"
try:
    r = requests.get(update_url)
    r.raise_for_status()
    with open(update_file, "wb") as f:
        f.write(r.content)
except requests.exceptions.RequestException:
    handle_error("Failed to download update")

# Modify the contents of update_new.py to include the new code
with open(update_file, "r") as f:
    content = f.read()
    content = content.replace("urls =[", f"urls = {urls}\n\n")
    with open(update_file, "w") as wf:
        wf.write(content)

# Download and update contents of other files
for url in urls:
    file_name = url.split("/")[-1]
    try:
        r = requests.get(url)
        r.raise_for_status()
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(r.text)
    except requests.exceptions.RequestException:
        handle_error(f"Failed to download file: {file_name}")

# Run the new version of the script
subprocess.Popen(["python", update_file], close_fds=True)

# Rename the old update.py file to update_old.py
old_file = "update.py"
if os.path.exists(old_file):
    old_backup = "update_old.py"
    if os.path.exists(old_backup):
        os.remove(old_backup)
    os.rename(old_file, old_backup)

# Rename the new update_new.py file to update.py once the script has finished executing
if os.path.exists(update_file):
    while True:
        try:
            os.rename(update_file, old_file)
            break
        except OSError:
            pass
else:
    handle_error("Update failed")