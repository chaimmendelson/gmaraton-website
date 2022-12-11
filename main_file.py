import subprocess
import time

subprocess.run(["python3", "/home/elchairoy/gmaraton-website/server.py"])
while True:
    # Pull the latest code from the repository
    result = subprocess.run(["git", "pull"], cwd="/home/elchairoy/gmaraton-website", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check the output of the git pull command to see if there were any changes
    output = result.stdout.decode().strip()
    if "Already up to date." not in output:
        # Kill any previous run of the script
        subprocess.run(["pkill", "-f", "python3 /home/elchairoy/gmaraton-website/server.py"])

        # Run the script
        subprocess.run(["python3", "/home/elchairoy/gmaraton-website/server.py"])
    time.sleep(10)