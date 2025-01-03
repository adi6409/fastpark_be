import cv2
import numpy as np
from parking_slots import get_parking_slots



def warp_parking_lot(image):
    """
    Warps a parking lot image to correct perspective distortion based on predefined dimensions and coordinates.
    
    Parameters:
        image (numpy.ndarray): The input image loaded with cv2.imread.
    
    Returns:
        numpy.ndarray: The warped image with corrected perspective.
    """
    # Source points: Coordinates of the parking lot strips
    src_points = np.float32([
        [40, 1078],      # Left strip bottom left
        [600, 22],       # Left strip top left
        [1300, 24],      # Right strip top right
        [1896, 1078]     # Right strip bottom right
    ])

    # Real-world dimensions of the parking lot (in cm)
    real_width_cm = 125  # Width of the parking lot
    left_strip_height_cm = 200  # Left strip height
    right_strip_height_cm = 195  # Right strip height

    # Output dimensions based on real-world sizes
    output_width = int(real_width_cm * 10)  # Convert cm to pixels (10 pixels/cm)
    output_height = max(
        int(left_strip_height_cm * 10),  # Use the taller height for the canvas
        int(right_strip_height_cm * 10)
    )

    # Destination points
    dst_points = np.float32([
        [0, output_height],         # Bottom-left (left strip)
        [0, 0],                     # Top-left (left strip)
        [output_width, 0],          # Top-right (right strip)
        [output_width, output_height]  # Bottom-right (right strip)
    ])

    # Compute the perspective transformation matrix
    warp_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

    # Apply the warp transformation
    warped_image = cv2.warpPerspective(image, warp_matrix, (output_width, output_height))

    # After warping the image, make it smaller to improve performance
    warped_image = cv2.resize(warped_image, (0, 0), fx=0.5, fy=0.5)

    return warped_image

# Load the main image (frame)
frame = cv2.imread('/Users/astroianu/Downloads/car_rotations/video-6.jpg', 0)  # Replace with your frame image

frame = warp_parking_lot(frame)

output_frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)  # Convert to color for visualization

# Load all car templates (organized by car name)
# Preload all car templates
car_templates = {
    "hw_blue": [cv2.imread(f"cars/warped_cropped/hw_blue_{angle}.png", 0) for angle in range(0, 360, 90)],
    "rc_blue": [cv2.imread(f"cars/warped_cropped/rc_blue_{angle}.png", 0) for angle in range(0, 360, 90)],
    "rc_green": [cv2.imread(f"cars/warped_cropped/rc_green_{angle}.png", 0) for angle in range(0, 360, 90)],
    "taxi": [cv2.imread(f"cars/warped_cropped/taxi_{angle}.png", 0) for angle in range(0, 360, 90)],
    "turquoise": [cv2.imread(f"cars/warped_cropped/turquoise_{angle}.png", 0) for angle in range(0, 360, 90)],
    "volvo": [cv2.imread(f"cars/warped_cropped/volvo_{angle}.png", 0) for angle in range(0, 360, 90)],
}

car_templates["rc_blue"].append(cv2.imread(f"cars/warped_cropped/rc_blue_360.png", 0))

# Similar to what we do to the frame, we resize all templates to improve performance
for car_name, templates in car_templates.items():
    car_templates[car_name] = [cv2.resize(template, (0, 0), fx=0.5, fy=0.5) for template in templates]


# Define matching threshold
threshold = 0.55

# Perform template matching for each car

# Store the average time taken and maximum time taken to match a template for every car
times = {}
max_times = {}

# For the above two dictionaries, the key is the car name and the value is a list of times taken to match each template

# Perform template matching for each car
total_start = cv2.getTickCount()
detected_cars = []
for car_name, templates in car_templates.items():
    best_match = None
    best_score = -1
    best_box = None

    for template in templates:
        template_h, template_w = template.shape

        # Perform template matching
        time_start = cv2.getTickCount()
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)

        # Get all locations above the threshold
        locations = np.where(result >= threshold)
        time_end = cv2.getTickCount()
        print(f"Time taken to match {car_name}: {(time_end - time_start) / cv2.getTickFrequency()}s")
        print(f"Found {len(locations[0])} matches for one template of {car_name}")

        # Store matches as a list of coordinates
        boxes = []
        scores = []
        for pt in zip(*locations[::-1]):  # Switch x and y coordinates
            x1, y1 = pt
            x2, y2 = x1 + template_w, y1 + template_h

            # Validate bounds to ensure no out-of-bounds error
            if x2 <= frame.shape[1] and y2 <= frame.shape[0]:
                boxes.append([x1, y1, x2, y2])
                scores.append(result[y1, x1])

        # Update the best match for this template
        if len(boxes) > 0:
            best_index = np.argmax(scores)
            match_score = scores[best_index]
            if match_score > best_score:
                best_score = match_score
                best_box = boxes[best_index]

    # Draw the best match for the car
    if best_box:
        x1, y1, x2, y2 = best_box
        cv2.rectangle(output_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(output_frame, car_name, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        # Add the car name and coordinates to the detected_cars list
        detected_cars.append({
            "name": car_name,
            "pos": [x1, y1, x2, y2]
        })
    else:
        print(f"No valid matches for {car_name}")



    
total_end = cv2.getTickCount()
print(f"Total time taken: {(total_end - total_start) / cv2.getTickFrequency()}s")

# Show the result
cv2.imshow('Multi-Car Detection', output_frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
