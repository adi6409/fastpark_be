import cv2
import numpy as np

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

    return warped_image


FRAME_PATH = 'video-6.jpg'

frame = cv2.imread(FRAME_PATH)
warped_frame = warp_parking_lot(frame)
cv2.imshow('Warped Parking Lot', warped_frame)
cv2.waitKey(0)
warped_frame_path = f'warped_{FRAME_PATH}'
cv2.imwrite(warped_frame_path, warped_frame)
print(f"Warped image saved as {warped_frame_path}")