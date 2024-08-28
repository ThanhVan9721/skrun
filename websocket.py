import asyncio
import websockets
import subprocess
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

# Function to handle WebSocket commands
async def handle_command(websocket):
    global process, job_name
    async for message in websocket:
        if message == "1":
            job_name = "Tiktok"
            job_path = "tiktok.py"
            await run_job(websocket, process, job_name, job_path)
        elif message == "2":
            job_name = "Ninja"
            job_path = "ninja.py"
            await run_job(websocket, process, job_name, job_path)
        elif message == "stop":
            process.terminate()
            process.wait()
            process = None
            job_name = None
            await websocket.send("Job is stop.")

async def run_job(websocket, process, job_name, job_path):
    if process is None or process.poll() is not None:
        process = subprocess.Popen(['python3', job_path])
        for i in range(5, 0, -1):
            await websocket.send(f"Start later: {i}")
            await asyncio.sleep(1)
        await websocket.send(f"Start {job_name} job")
    else:
        await websocket.send(f"{job_name} is already running.")

# Function to check if ADB is connected
def check_adb_connection():
    try:
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
        devices_output = result.stdout.decode('utf-8').strip()
        if "List of devices attached" in devices_output:
            lines = devices_output.splitlines()[1:]
            for line in lines:
                if line.strip():
                    device_status = line.split()[-1]
                    if device_status == "unauthorized":
                        return False
                    elif device_status == "device":
                        return True
        return False
    except Exception as e:
        print(f"Error checking ADB connection: {e}")
        return False

# Function to check if there is an active Internet connection
def check_internet_connection():
    try:
        # Attempt to connect to a reliable external host (Google DNS)
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except OSError:
        return False

# Function to get the Raspberry Pi's LAN IP address
def get_lan_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

# Function to start the HTTP server
def start_http_server():
    with open('/home/admin/skrun/index_template.html', 'r') as file:
        html_template = file.read()

    ip_address = get_lan_ip()
    html_content = html_template.replace('{{IP_ADDRESS}}', ip_address)

    with open('/home/admin/skrun/index.html', 'w') as file:
        file.write(html_content)

    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('', 8000), handler)
    print(f"HTTP server started on http://{ip_address}:8000")
    subprocess.run(f'adb shell am start -a android.intent.action.VIEW -d "http://{ip_address}:8000"', shell=True)
    httpd.serve_forever()

# Function to start the WebSocket server
async def start_websocket_server(ip_address):
    async with websockets.serve(handle_command, ip_address, 8765):
        print(f"WebSocket server started on ws://{ip_address}:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    while True:
        if check_adb_connection() and check_internet_connection():
            print("ADB and Internet are both connected.")
            break
        else:
            print("Waiting for ADB and Internet connection...")
            asyncio.sleep(5)

    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True  # Ensure it exits when the main program exits
    http_thread.start()

    ip_address = get_lan_ip()
    asyncio.run(start_websocket_server(ip_address))