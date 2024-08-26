import subprocess
import os
import time

def run_websocket_in_terminal():
    try:
        # Chờ 10 giây để đảm bảo môi trường GUI đã sẵn sàng
        time.sleep(10)
        
        # Kiểm tra biến môi trường DISPLAY
        display = os.getenv('DISPLAY')
        if not display:
            print("DISPLAY variable is not set. Setting DISPLAY to :0")
            os.environ['DISPLAY'] = ':0'

        # Mở lxterminal và chạy websocket.py
        subprocess.Popen(['lxterminal', '--command', 'python3 /home/admin/skrun/websocket.py'])
        print("lxterminal opened and websocket.py is running.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure that you have a GUI available and that you are not running this script in a headless environment.")
        print("If you are using SSH, ensure X forwarding is enabled with 'ssh -X username@hostname'.")
        print("You may also try running 'xhost +' to allow connections to the X server.")

if __name__ == "__main__":
    run_websocket_in_terminal()
