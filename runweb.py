import subprocess

# Sử dụng screen
subprocess.Popen(['screen', '-dmS', 'websocket_session', 'python3', '/home/admin/skrun/websocket.py'])

# Hoặc sử dụng tmux
# subprocess.Popen(['tmux', 'new-session', '-d', '-s', 'websocket_session', 'python3', '/home/admin/skrun/websocket.py'])
