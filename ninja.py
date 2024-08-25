import os
import cv2
import numpy as np
import time
from ultralytics import YOLO
import math

# Tải mô hình YOLOv8 đã huấn luyện
model = YOLO('/home/admin/skrun/best-1.pt')  # Thay bằng mô hình bạn đã huấn luyện

import subprocess

def capture_screen():
    """Lấy ảnh màn hình từ thiết bị Android qua ADB."""
    result = subprocess.run(["adb", "exec-out", "screencap", "-p"], stdout=subprocess.PIPE)
    screen_bytes = result.stdout
    screen_np = np.frombuffer(screen_bytes, np.uint8)
    screen_img = cv2.imdecode(screen_np, cv2.IMREAD_COLOR)
    return screen_img


def calculate_distance(point1, point2):
    """Tính toán khoảng cách Euclidean giữa hai điểm."""
    return math.sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def process_frame(img):
    """Xử lý khung hình, tìm các đối tượng Cot và Cau, và tính toán khoảng cách."""
    results = model(img)
    cot_boxes = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])  # Lấy ID của lớp
            name = model.names[class_id]  # Tên của đối tượng
            if name == "Cot":
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cot_boxes.append((x1, y1, x2, y2))

    cot_distance = None
    if len(cot_boxes) >= 2:
        center_x_1 = (cot_boxes[0][0] + cot_boxes[0][2]) / 2
        center_y_1 = (cot_boxes[0][1] + cot_boxes[0][3]) / 2
        cot1_x2_y1 = (center_x_1, center_y_1)

        center_x_2 = (cot_boxes[1][0] + cot_boxes[1][2]) / 2
        center_y_2 = (cot_boxes[1][1] + cot_boxes[1][3]) / 2
        cot2_x1_y1 = (center_x_2, center_y_2)
        
        cot_distance = calculate_distance(cot1_x2_y1, cot2_x1_y1)
        print(f"Khoảng cách giữa hai đối tượng 'Cot': {cot_distance} pixels")

    return cot_distance
def calculate_hold_time(pixels_required, increase_per_step=1, time_per_step=0.01):
    """
    Tính thời gian giữ màn hình cần thiết để đạt được số pixel yêu cầu.

    :param pixels_required: Số pixel yêu cầu.
    :param increase_per_step: Số pixel tăng lên sau mỗi bước (mặc định là 1px).
    :param time_per_step: Thời gian cho mỗi bước (mặc định là 0.01 giây).
    :return: Thời gian giữ màn hình (tính bằng giây).
    """
    if increase_per_step <= 0 or time_per_step <= 0:
        raise ValueError("Số pixel tăng lên và thời gian mỗi bước phải lớn hơn 0.")

    hold_time = pixels_required * time_per_step
    return hold_time

def long_press_on_screen(cot_distance):
    """Nhấn giữ màn hình ở một điểm bất kỳ trong một thời gian nhất định."""
    print(cot_distance)
    duration = calculate_hold_time(cot_distance, increase_per_step=1, time_per_step=0.00023)
    # if cot_distance > 700:
    #     duration = calculate_hold_time(cot_distance, increase_per_step=1, time_per_step=0.00035)
    # if cot_distance > 600:
    #     duration = calculate_hold_time(cot_distance, increase_per_step=1, time_per_step=0.00023)
    # if cot_distance > 550:
    #     duration = calculate_hold_time(cot_distance, increase_per_step=1, time_per_step=0.0002)
    # if cot_distance <= 550:
    #     duration = calculate_hold_time(cot_distance, increase_per_step=1, time_per_step=0.0004)
    hold_time_milliseconds = int(duration * 1000)
    print(duration)
    os.system(f"adb shell input swipe 540 960 540 960 {hold_time_milliseconds}")

def main():
    while True:
        img = capture_screen()  # Liên tục chụp ảnh màn hình
        cot_distance = process_frame(img)

        if cot_distance is not None:
            print(f"Nhấn giữ màn hình do khoảng cách đạt yêu cầu.")
            long_press_on_screen(cot_distance)  # Nhấn giữ màn hình
        
        time.sleep(1.06)
        

if __name__ == "__main__":
    main()
