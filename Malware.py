import os
import getpass
import sys
import requests
import socket
import time
from getmac import get_mac_address


def start_monitoring_client():
    """
    Initializes and runs the device monitoring client silently.
    """
    # --- Configuration: Change this URL to your server's IP address ---
    SERVER_URL = "http://127.0.0.1:5001/heartbeat"
    HEARTBEAT_INTERVAL = 5  # seconds

    def send_heartbeat():
        """Gets device info and sends it to the tracking server."""
        try:
            # Get device name and MAC address
            device_name = socket.gethostname()
            mac_address = get_mac_address()

            if not mac_address:
                return

            payload = {
                "device_name": device_name,
                "mac_address": mac_address
            }

            # Send the data as a POST request with a timeout
            response = requests.post(SERVER_URL, json=payload, timeout=10)
            # Raise an exception for bad status codes (e.g., 404, 500)
            response.raise_for_status()

        except requests.exceptions.RequestException:
            # Silently ignore network-related errors and retry after the interval
            pass
        except Exception:
            # Silently ignore other potential errors
            pass

    # --- Main Loop ---
    while True:
        send_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL)


def create_startup_batch(script_path=None, batch_name="run_on_startup.bat"):
    """
    Creates a batch file in the Windows Startup folder to run this script
    silently on system boot.
    """
    user = getpass.getuser()
    if script_path is None:
        script_path = os.path.abspath(sys.argv[0])

    # Get the path to the windowless Python executable (pythonw.exe)
    # This is key to running the script without a visible command prompt window.
    pythonw_path = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')

    startup_folder = rf"C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup"
    batch_file_path = os.path.join(startup_folder, batch_name)

    # Create the batch file only if it doesn't already exist
    if not os.path.exists(batch_file_path):
        # Command to run the script silently using pythonw.exe
        batch_cmd = f'"{pythonw_path}" "{script_path}"'
        with open(batch_file_path, "w") as bat_file:
            bat_file.write(batch_cmd)


if __name__ == "__main__":
    # First, ensure the startup batch file is created for persistence
    create_startup_batch()
