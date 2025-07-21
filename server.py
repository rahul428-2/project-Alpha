from flask import Flask, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# --- Configuration ---
# A device is considered "inactive" if no heartbeat is received for this many seconds.
# This should be longer than the client's heartbeat interval to allow for network delays.
INACTIVITY_TIMEOUT = timedelta(seconds=15)

# In-memory dictionary to store device status
# Format: { 'mac_address': {'device_name': 'my-pc', 'last_seen': datetime_object} }
DEVICES = {}


@app.route('/heartbeat', methods=['POST'])
def receive_heartbeat():
    """Receives heartbeat from clients and updates their status."""
    try:
        data = request.json
        mac_address = data.get('mac_address')
        device_name = data.get('device_name')

        if not mac_address:
            return jsonify({"status": "error", "message": "MAC address is required"}), 400

        DEVICES[mac_address] = {
            "device_name": device_name,
            "last_seen": datetime.now()
        }

        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/')
def status_dashboard():
    """Displays the status of all tracked devices in an HTML table."""
    now = datetime.now()

    # Start of the HTML page with auto-refresh and basic styling
    html = """
    <html>
        <head>
            <title>Device Status Dashboard</title>
            <meta http-equiv="refresh" content="5">
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 40px; background-color: #f8f9fa; color: #343a40; }
                h1 { color: #007bff; }
                table { width: 100%; border-collapse: collapse; margin-top: 25px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); background-color: white; }
                th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #dee2e6; }
                th { background-color: #007bff; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .status-active { color: #28a745; font-weight: bold; }
                .status-inactive { color: #dc3545; font-weight: bold; }
                footer { margin-top: 20px; font-size: 0.8em; color: #6c757d; }
            </style>
        </head>
        <body>
            <h1>Device Status Dashboard</h1>
            <table>
                <thead>
                    <tr>
                        <th>Device Name</th>
                        <th>MAC Address</th>
                        <th>Status</th>
                        <th>Last Seen (IST)</th>
                    </tr>
                </thead>
                <tbody>
    """

    if not DEVICES:
        html += '<tr><td colspan="4" style="text-align:center; padding: 20px;">No devices have checked in yet.</td></tr>'
    else:
        # Sort devices by name for a consistent view
        sorted_mac_addresses = sorted(DEVICES.keys(), key=lambda mac: DEVICES[mac]['device_name'])

        for mac in sorted_mac_addresses:
            info = DEVICES[mac]
            time_since_last_seen = now - info['last_seen']

            if time_since_last_seen <= INACTIVITY_TIMEOUT:
                status = '<span class="status-active">Active</span>'
            else:
                status = '<span class="status-inactive">Inactive</span>'

            # Format time for readability
            last_seen_str = info['last_seen'].strftime("%Y-%m-%d %I:%M:%S %p")

            html += f"""
                <tr>
                    <td>{info.get('device_name', 'N/A')}</td>
                    <td>{mac}</td>
                    <td>{status}</td>
                    <td>{last_seen_str}</td>
                </tr>
            """

    html += f"""
                </tbody>
            </table>
            <footer>
                Page last updated at: {now.strftime("%Y-%m-%d %I:%M:%S %p")}
            </footer>
        </body>
    </html>
    """
    return html


if __name__ == '__main__':
    # Use host='0.0.0.0' to make the server accessible on your local network
    app.run(host='0.0.0.0', port=5001)