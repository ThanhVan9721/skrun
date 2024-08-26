import subprocess

subprocess.Popen(['tmux', 'new-session', '-d', '-s', 'websocket_session', 'python3', '/home/admin/skrun/websocket.py'])
