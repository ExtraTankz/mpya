import requests
import os
import subprocess
import sys
import webbrowser

with open('API.MPYA', 'r') as f:
    f.readline() # discard first line
    f.readline() # discard the second line
    secret_key = f.readline().strip()

if secret_key == 'extratankz':
    webbrowser.open_new_tab('https://r.mtdv.me/mpya')

urls = ["https://raw.githubusercontent.com/ExtraTankz/mpya/main/mpya.py",
        "https://raw.githubusercontent.com/ExtraTankz/mpya/main/mpya.pyw"]

# Try to download and install the updated file from each URL in the list
for url in urls:
    filename = os.path.join(os.getcwd(), 'mpya-update.py')
    try:
        r = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(r.content)
        break
    except requests.exceptions.RequestException:
        pass

# Read the contents of the original and updated files line by line
for original_filename in ['mpya.py', 'mpya.pyw']:
    origin = os.path.join(os.getcwd(), original_filename)
    if not os.path.exists(origin):
        continue
    try:
        with open(origin, 'r') as f1, open(filename, 'r') as f2:
            lines_differ = False
            changes = []
            for line_num, (line1, line2) in enumerate(zip(f1, f2)):
                if line1 != line2:
                    lines_differ = True
                    changes.append(f'Line {line_num+1}: {line1.strip()} -> {line2.strip()}')
            if not lines_differ:
                print(f'{original_filename} and the updated file are identical')
            else:
                # Make sure any open file handles are closed before deleting or renaming files
                f1.close()
                f2.close()
                os.remove(origin)
                os.rename(filename, origin)
                # Create a changelog.txt file with the list of changes
                changelog_file = os.path.join(os.getcwd(), 'changelog.txt')
                with open(changelog_file, 'w') as f:
                    f.write('\n'.join(changes))
                print(f'{original_filename} has been updated.')
                print(f'Changelog.txt created with {len(changes)} changes.')
                # Install requirements and open a command prompt window
                subprocess.call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
                subprocess.call(['cmd', '/k'], cwd=os.getcwd())
            break
    except FileNotFoundError:
        print(f'{origin} not found')