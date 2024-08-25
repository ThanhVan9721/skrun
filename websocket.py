import asyncio
import websockets
import subprocess
import socket
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading
import os
import signal
# Global variables to store PIDs
tiktok_process = None
ninja_process = None

# Function to handle WebSocket commands
async def handle_command(websocket, path):
    global tiktok_process, ninja_process
    global tiktok_pid, ninja_pid
    async for message in websocket:
        if message == "check_adb":
            adb_connected = check_adb_connection()
            if adb_connected:
                await websocket.send("ADB connected")
            else:
                await websocket.send("ADB not connected")
        elif message == "1":
            if tiktok_process is None or tiktok_process.poll() is not None:
                tiktok_process = subprocess.Popen(['lxterminal', '-e', 'python3', 'tiktok.py'])
                tiktok_pid = tiktok_process.pid
                await asyncio.gather(*(websocket.send(f"Start later: {i}") for i in range(5, 0, -1)))
                await websocket.send("Start Tiktok job")
            else:
                await websocket.send("Tiktok job is already running.")
        elif message == "2":
            if ninja_process is None or ninja_process.poll() is not None:
                ninja_process = subprocess.Popen(['lxterminal', '-e', 'python3', 'ninja.py'])
                ninja_pid = ninja_process.pid
                await asyncio.gather(*(websocket.send(f"Start later: {i}") for i in range(5, 0, -1)))
                await websocket.send("Start Ninja")
            else:
                await websocket.send("Ninja is already running.")
        elif message == "stop_1":
            if tiktok_pid:
                try:
                    subprocess.call(['pkill', '-f', 'lxterminal.*python3 tiktok.py'])
                    tiktok_pid = None
                    await websocket.send("Tiktok stopped")
                except OSError:
                    await websocket.send("Tiktok is not running")
                await websocket.send("Stopped Tiktok")
            else:
                await websocket.send("Tiktok is not running.")
        elif message == "stop_2":
            if ninja_pid:
                try:
                    os.kill(ninja_pid, signal.SIGTERM)
                    ninja_pid = None
                    await websocket.send("Ninja stopped")
                except OSError:
                    await websocket.send("Ninja is not running")
                await websocket.send("Stopped Ninja")
            else:
                await websocket.send("Ninja is not running.")

# Function to check if ADB is connected
def check_adb_connection():
    try:
        result = subprocess.run(['adb', 'devices'], stdout=subprocess.PIPE)
        devices_output = result.stdout.decode('utf-8').strip()
        # Kiểm tra xem có dòng "List of devices attached" trong output hay không
        if "List of devices attached" in devices_output:
            # Lấy tất cả các dòng sau dòng "List of devices attached"
            lines = devices_output.splitlines()[1:]
            for line in lines:
                # Nếu dòng không rỗng, kiểm tra trạng thái thiết bị
                if line.strip():
                    device_status = line.split()[-1]
                    # Nếu có thiết bị nhưng chưa được ủy quyền
                    if device_status == "unauthorized":
                        return False
                    # Nếu có thiết bị và đã được ủy quyền
                    elif device_status == "device":
                        return True
        return False
    except Exception as e:
        print(f"Error checking ADB connection: {e}")
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
    # Read the HTML template
    with open('index_template.html', 'r') as file:
        html_template = file.read()

    # Replace placeholder with actual IP address
    ip_address = get_lan_ip()
    html_content = html_template.replace('{{IP_ADDRESS}}', ip_address)

    # Write the updated HTML content to index.html
    with open('index.html', 'w') as file:
        file.write(html_content)

    # Start the HTTP server
    handler = SimpleHTTPRequestHandler
    httpd = HTTPServer(('', 8000), handler)
    print(f"HTTP server started on http://{ip_address}:8000")
    httpd.serve_forever()

# Function to start the WebSocket server
async def start_websocket_server(ip_address):
    async with websockets.serve(handle_command, ip_address, 8765):
        print(f"WebSocket server started on ws://{ip_address}:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    # Start the HTTP server in a new thread
    http_thread = threading.Thread(target=start_http_server)
    http_thread.daemon = True  # Ensure it exits when the main program exits
    http_thread.start()

    # Start the WebSocket server
    ip_address = get_lan_ip()
    asyncio.run(start_websocket_server(ip_address))
