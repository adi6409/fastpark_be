from dummy_jsons import *
import cv2
import numpy as np
import threading
from queue import Queue
from parking_slots import get_parking_slots
from navigation import get_navigation


def warp_parking_lot(image):
    """
    Warps a parking lot image to correct perspective distortion based on predefined dimensions and coordinates.
    """
    src_points = np.float32([
        [40, 1078], [600, 22], [1300, 24], [1896, 1078]
    ])
    real_width_cm = 125
    left_strip_height_cm = 200
    right_strip_height_cm = 195

    output_width = int(real_width_cm * 10)
    output_height = max(
        int(left_strip_height_cm * 10),
        int(right_strip_height_cm * 10)
    )

    dst_points = np.float32([
        [0, output_height], [0, 0], [output_width, 0], [output_width, output_height]
    ])

    warp_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    warped_image = cv2.warpPerspective(image, warp_matrix, (output_width, output_height))
    warped_image = cv2.resize(warped_image, (0, 0), fx=0.5, fy=0.5)
    return warped_image


def capture_frames(stream_url, frame_queue):
    """
    Continuously captures frames from the video stream and stores the latest frame in the queue.
    """
    cap = cv2.VideoCapture(stream_url)
    if not cap.isOpened():
        print("Error: Could not open video stream.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from stream.")
            break

        if not frame_queue.empty():
            frame_queue.get()  # Discard the older frame
        frame_queue.put(frame)

    cap.release()


# Load car templates
car_templates = {
    "hw_blue": [cv2.imread(f"cars/warped_cropped/hw_blue_{angle}.png", 0) for angle in range(0, 360, 90)],
    "rc_blue": [cv2.imread(f"cars/warped_cropped/rc_blue_{angle}.png", 0) for angle in range(0, 360, 90)],
    "rc_green": [cv2.imread(f"cars/warped_cropped/rc_green_{angle}.png", 0) for angle in range(0, 360, 90)],
    "taxi": [cv2.imread(f"cars/warped_cropped/taxi_{angle}.png", 0) for angle in range(0, 360, 45)],
    "turquoise": [cv2.imread(f"cars/warped_cropped/turquoise_{angle}.png", 0) for angle in range(0, 360, 90)],
    "volvo": [cv2.imread(f"cars/warped_cropped/volvo_{angle}.png", 0) for angle in range(0, 360, 45)],
}

for car_name, templates in car_templates.items():
    car_templates[car_name] = [cv2.resize(template, (0, 0), fx=0.5, fy=0.5) for template in templates]

threshold = 0.55
stream_url = "rtsp://172.30.166.67:8080/h264.sdp"


def process_stream(car_positions):
    frame_queue = Queue(maxsize=1)
    capture_thread = threading.Thread(target=capture_frames, args=(stream_url, frame_queue), daemon=True)
    capture_thread.start()
    count = 0
    parking_slots = get_parking_slots()
    scaled_parking_slots = []
    for slot in parking_slots:
        new_slot = slot.copy()
        new_slot["pos"] = [[int(x / 2) for x in pos] for pos in slot["pos"]]
        scaled_parking_slots.append(new_slot)
        
    while True:
        if frame_queue.empty():
            continue  # Wait for a frame

        frame = frame_queue.get()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        warped_frame = warp_parking_lot(gray_frame)
        output_frame = cv2.cvtColor(warped_frame, cv2.COLOR_GRAY2RGB)

        # Draw parking slots
        for slot in scaled_parking_slots:
            cv2.polylines(output_frame, [np.array(slot["pos"], np.int32)], isClosed=True, color=(0, 0, 255), thickness=2)


        for car_name, templates in car_templates.items():
            best_match = None
            best_score = -1
            best_box = None

            for template in templates:
                template_h, template_w = template.shape
                result = cv2.matchTemplate(warped_frame, template, cv2.TM_CCOEFF_NORMED)
                locations = np.where(result >= threshold)

                boxes = []
                scores = []
                for pt in zip(*locations[::-1]):
                    x1, y1 = pt
                    x2, y2 = x1 + template_w, y1 + template_h
                    if x2 <= warped_frame.shape[1] and y2 <= warped_frame.shape[0]:
                        boxes.append([x1, y1, x2, y2])
                        scores.append(result[y1, x1])

                if len(boxes) > 0:
                    best_index = np.argmax(scores)
                    match_score = scores[best_index]
                    if match_score > best_score:
                        best_score = match_score
                        best_box = boxes[best_index]

            if best_box:
                x1, y1, x2, y2 = best_box
                # Check if the middle of the car is on a parking slot. If it is, draw a red rectangle, otherwise draw a green one.
                middle_x = int((x1 + x2) // 2)
                middle_y = int((y1 + y2) // 2)

                car_on_parking_slot = False
                for slot in scaled_parking_slots:
                    if cv2.pointPolygonTest(np.array(slot["pos"], np.int32), (middle_x, middle_y), False) >= 0:
                        car_on_parking_slot = True
                        break
                if car_on_parking_slot:
                    cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    # Check if the car is set to true in the 
                else:
                    cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                cv2.putText(output_frame, car_name, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # add top left, top right, bottom right, bottom left coordinates to car_positions
                car_positions[car_name] = [x1, y1, x2, y2]
                
            

        
        # After inference, multiply everything back by 2 to get the correct coordinates

        output_frame = cv2.resize(output_frame, (0, 0), fx=2, fy=2)

        # Color the frame from gray

        # if count < 10:
        #     cv2.imwrite(f"frames/output_frame_{count}.png", output_frame)
        #     count += 1
        




def get_state(carId, car_positions):
    car = car_positions[carId]
    directions = get_navigation(car, carId)
    if len(directions) == 1:
        return {"state": "finished"}
    else:
        direction = directions[0].get("direction")
        return {
            "state": "directions",
            "data": {
                "direction": direction,
                "distanceToNext": directions[0].get("distance")
            }
        }
