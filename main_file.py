import subprocess
import time

subprocess.run(["python3", "server.py"])
while True:
    print("Checking for updates...")
    # Pull the latest code from the repository
    result = subprocess.run(["git", "pull"], cwd="/home/elchairoy/gmaraton-website", stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Check the output of the git pull command to see if there were any changes
    output = result.stdout.decode().strip()
    print(output)
    if "Already up to date." not in output:
        ps = subprocess.run(["ps", "-ef"], stdout=subprocess.PIPE)
        pid = None
        for line in ps.stdout.decode().strip().split("\n"):
            if "python3 server.py" in line:
                pid = int(line.split()[1])
                break
        print(pid, "is the pid")
        if pid is not None:
            # Kill the previous run of the script
            print("Killing previous process")
            subprocess.run(["kill", str(pid)])

        # Run the script
        subprocess.run(["python3", "server.py"])
    time.sleep(10)