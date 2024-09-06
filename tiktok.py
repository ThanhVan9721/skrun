import cv2
import numpy as np
import subprocess
import time
import os
from ultralytics import YOLO
import requests
import random
import pytesseract
from PIL import Image

model = YOLO('best.pt')  # Thay bằng mô hình bạn đã huấn luyện

# Đường dẫn đến thư mục lưu trữ ảnh
output_folder = "detected_images"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def capture_screen():
    """Lấy ảnh màn hình từ thiết bị Android qua ADB."""
    try:
        # Chạy lệnh adb để chụp ảnh màn hình
        result = subprocess.run(["adb", "exec-out", "screencap", "-p"], capture_output=True, check=True)
        screen_bytes = result.stdout

        # Chuyển đổi dữ liệu byte thành ảnh
        screen_np = np.frombuffer(screen_bytes, np.uint8)
        screen_img = cv2.imdecode(screen_np, cv2.IMREAD_COLOR)

        return screen_img

    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy lệnh ADB: {e}")
        return None
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")
        return None
    
def check_image(type_job, text):
    time.sleep(2)
    for _ in range(10):
        # Chụp ảnh màn hình từ điện thoại qua ADB
        img = capture_screen()
        if img is None:
            print("Không thể lấy ảnh màn hình từ thiết bị. Hãy kiểm tra kết nối ADB.")
            break
        # Dự đoán trên khung hình
        results = model(img)
        if any(result.boxes for result in results):
            for result in results:
                for box in result.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])  # Tọa độ của bounding box
                    class_id = int(box.cls[0])  # Lấy ID của lớp
                    name = model.names[class_id]  # Tên của đối tượng
                    if (type_job == name):
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        adb_click(center_x, center_y)
                        if type_job == 'Comment':
                            continue
                        return
                    if name == 'InputComment':
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        adb_click(center_x, center_y)
                        open_input_form()
                        adb_click(center_x, center_y)
                        input_form(text)
                        continue
                    if name == 'send':
                        center_x = (x1 + x2) / 2
                        center_y = (y1 + y2) / 2
                        adb_click(center_x, center_y)
                        return
        time.sleep(1)

def adb_click(center_x, center_y):
    adb_command = f"adb shell input tap {center_x} {center_y}"
    os.system(adb_command)

def process_action(action):
    action_map = {
        "like": "Tim",
        "follow": "Follow",
        "comment": "Comment",
        "Profile": "Profile"
    }
    return action_map.get(action, "Unknown action")

bearer_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9nYXRld2F5LmdvbGlrZS5uZXRcL2FwaVwvbG9naW4iLCJpYXQiOjE3MTc2NDM2MTcsImV4cCI6MTc0OTE3OTYxNywibmJmIjoxNzE3NjQzNjE3LCJqdGkiOiJUTXZKNlIyUXQ4RlBUcjN1Iiwic3ViIjoyNzE3NzcyLCJwcnYiOiJiOTEyNzk5NzhmMTFhYTdiYzU2NzA0ODdmZmYwMWUyMjgyNTNmZTQ4In0.ki9X4hZ8bk1PLBaPR-bZReXAvWQk4s6_Cv8lrSr3r4w"
headers = {
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'Authorization': f'Bearer {bearer_token}',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36',
    'Content-Type': 'application/json;charset=utf-8',
    'Accept': 'application/json, text/plain, */*',
    't': 'VFZSamVFOVVVVE5OVkdNd1RsRTlQUT09',
    'sec-ch-ua-platform': '"Android"',
    'Sec-Fetch-Site': 'same-site',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Dest': 'empty',
    'host': 'gateway.golike.net'
}
def open_url_in_tiktok(url):
    command = f'adb shell am start -a android.intent.action.VIEW -d "{url}"'
    os.system(command)

def open_input_form():
    os.system(f"adb shell ime enable com.android.adbkeyboard/.AdbIME")
    time.sleep(1)
    os.system(f"adb shell ime set com.android.adbkeyboard/.AdbIME")
    time.sleep(1)

def input_form(text):
    os.system(f"adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{text}'")
    time.sleep(1)
    os.system(f"adb shell ime reset")

def swipe_up():
    start_x = random.randint(400, 600)
    start_y = random.randint(1300, 1600)
    end_x = start_x
    end_y = random.randint(300, 600)
    duration = random.randint(200, 700)  # Thời gian vuốt ngẫu nhiên
    os.system(f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}")

# Hàm để vuốt màn hình xuống với tọa độ ngẫu nhiên
def swipe_down():
    start_x = random.randint(400, 600)
    start_y = random.randint(300, 600)
    end_x = start_x
    end_y = random.randint(1300, 1600)
    duration = random.randint(200, 700)  # Thời gian vuốt ngẫu nhiên
    os.system(f"adb shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}")

def run_job(id_account):
    url_get_job = f"https://gateway.golike.net/api/advertising/publishers/tiktok/jobs?account_id={id_account}&data=null"
    job = requests.get(url_get_job, headers=headers)
    if job.status_code == 200:
        dataJob = job.json()
        infoJob = dataJob.get("data", {})
        infoJob_id = infoJob.get("id")
        print(f"Job ID: {infoJob_id}")
        infoJob_link = infoJob.get("link")
        print(f"Job Link: {infoJob_link}")
        infoJob_type = infoJob.get("type")
        comment_texts = ""
        if infoJob_type == "comment":
            comment_text = infoJob.get("comment_run", {})
            comment_texts = comment_text.get("message")
        print(f"Job Type: {infoJob_type}")
        infoJob_object_id = infoJob.get("object_id")
        open_url_in_tiktok(infoJob_link)
        action = process_action(infoJob_type)
        check_image(action, comment_texts)
        time.sleep(3)
        data = {
            "account_id": id_account,
            "ads_id": infoJob_id,
            "async": True
        }
        checkJob = requests.post("https://gateway.golike.net/api/advertising/publishers/tiktok/complete-jobs", headers=headers, json=data)
        if checkJob.status_code == 200 or checkJob.status_code == 201:
            print("Hoàn thành job")
        else:
            print(f"Hoàn thành job lỗi: {checkJob.text}")
            data_skip_job = {
                "account_id": id_account,
                "ads_id": infoJob_id,
                "object_id": infoJob_object_id,
                "type": infoJob_type
            }
            skipJob = requests.post("https://gateway.golike.net/api/advertising/publishers/tiktok/skip-jobs", headers=headers, json=data_skip_job)
            if skipJob.status_code == 200 or skipJob.status_code == 201:
                dataSkipJob = skipJob.json()
                print(dataSkipJob.get("message"))
            else:
                print(f"Bỏ qua job bị lỗi{skipJob.text}")
            return 0
        print(f"Dừng lại một chút")
    else:
        print(f"Không get job được {job.text}")

comment = [
    {"comment": "Wowww"},
    {"comment": "Haaaaa"},
    {"comment": "Haha"},
    {"comment": "Mlem"}
]
def get_random_comment():
    selected_comment = random.choice(comment)
    return selected_comment["comment"]

def perform_random_task():    
    task = random.choices([1, 2, 3, 4, 5, 6], weights=[20, 4, 0.5, 0.5, 0.5, 0.2], k=1)[0]
    if task == 1:
        print("Thực hiện vuốt lên")
        swipe_up()
    elif task == 2:
        print("Thực hiện vuốt xuống")
        swipe_down()
    elif task == 3:
        print("Thực hiện thả tim")
        check_image("Tim", "")
    elif task == 4:
        print("Thực hiện comment")
        random_comment =  get_random_comment()
        check_image("Comment", random_comment)

def execute_multiple_times():
    open_url_in_tiktok("https://www.tiktok.com/")
    random_count = random.randint(1, 5)  # Số lần ngẫu nhiên từ 2 đến 20
    print(f"Thực hiện tương tác {random_count} lần")
    for _ in range(random_count):
        sleepRd = random.randint(3, 10)
        time.sleep(sleepRd)
        perform_random_task()


def get_account(input_text):
    """Trích xuất văn bản và tọa độ tâm của các từ."""
    screen_img = capture_screen()
    if screen_img is not None:
        # Chuyển từ định dạng BGR sang RGB
        screen_img_rgb = cv2.cvtColor(screen_img, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(screen_img_rgb)

        # Nhận dữ liệu từ pytesseract (gồm thông tin bounding box)
        data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)

        # Lặp qua các từ nhận diện được
        num_items = len(data['text'])
        for i in range(num_items):
            if int(data['conf'][i]) > 0:  # Kiểm tra nếu độ tin cậy > 0
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                text = data['text'][i]
                if text == input_text:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    adb_click(center_x, center_y)
                    return True
    return False

def get_job_tiktok():
    url_get_tiktok_account = "https://gateway.golike.net/api/tiktok-account"
    account = requests.get(url_get_tiktok_account, headers=headers)
    if account.status_code == 200:
        data = account.json()
        for acc in data.get("data", {}):
            id_account = acc.get("id")
            username = acc.get("unique_username")
            check_acc(username, id_account)
    else:
        # Lỗi khi get list account
        print(f"Lỗi {account.status_code}: {account.text.encode('utf-8')}")

def check_acc(username, id_account):
    open_url_in_tiktok("https://www.tiktok.com/")
    check_image("Profile", "")
    check_image("Menu", "")
    check_image("Setting", "")
    swipe_up()
    time.sleep(1)
    swipe_up()
    time.sleep(1)
    swipe_up()
    time.sleep(3)
    check_image("SwithAcc", "")
    time.sleep(2)
    exits_acc = get_account(username)
    if exits_acc == True:
        for _ in range(5):
            print(username)
            execute_multiple_times()
            run_job(id_account)
    time.sleep(2)
for _ in range(2):
    get_job_tiktok()

print(f"End job")