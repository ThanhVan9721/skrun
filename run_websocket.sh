#!/bin/bash

# Thiết lập biến môi trường PATH nếu cần
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Thiết lập PYTHONPATH để bao gồm thư mục site-packages của người dùng
export PYTHONPATH=/home/admin/.local/lib/python3.9/site-packages

# Đảm bảo biến HOME được thiết lập
export HOME=/home/admin

# Thực thi script Python và ghi log
/usr/bin/python3 /home/admin/skrun/runweb.py >> /home/admin/skrun/websocket.log 2>&1

# Crontab: @reboot /home/admin/skrun/run_websocket.sh &