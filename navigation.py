from parking_slots import get_parking_slots, update_parking_slot, update_parking_slots
import math


def get_navigation(car, carId):
    if is_not_assigned(carId):
        middle_pixel_car = get_middle_of_bbox(car)
        parking_slots_pixel = update_closest_empty_ps(middle_pixel_car, carId)
        return get_directions(middle_pixel_car, parking_slots_pixel)
    else:
        # Get the assigned parking slot of the car and return the directions to it
        parking_slots = get_parking_slots()
        for parking_slot in parking_slots:
            if parking_slot["assignedTo"] == carId:
                return get_directions(get_middle_of_bbox(car), get_middle_of_bbox(parking_slot["pos"]))
    return None


def is_not_assigned(carId):
    parking_slots = get_parking_slots()
    for parking_slot in parking_slots:
        if parking_slot["assignedTo"] == carId:
            return False
    return True


def get_directions(middle_pixel_car, parking_slots_pixel):
    x, y = get_distance(middle_pixel_car, parking_slots_pixel)
    directions = [create_dictionary(x, y)]
    return directions


def update_closest_empty_ps(middle_pixel_car, carId):
    parking_slots = get_parking_slots()
    min_count = find_min_distance_ps(middle_pixel_car, parking_slots)
    status = parking_slots[min_count]
    status["isNavigatedTo"] = True
    status["assignedTo"] = carId
    update_parking_slot(min_count, status)
    return get_middle_of_bbox(parking_slots[min_count]["pos"])


def get_middle_of_bbox(ls):
    if not isinstance(ls, (list, tuple)) or len(ls) != 4:
        raise ValueError(f"Input must be a list or tuple with exactly 4 numeric values, but got: {ls}")
    
    # Validate each element
    try:
        x1, y1, x2, y2 = [float(coord) for coord in ls]
    except ValueError as e:
        raise ValueError(f"Invalid value in input coordinates: {ls}. Details: {e}")
    
    # Calculate middle of the bounding box
    middle_x = (x1 + x2) / 2
    middle_y = (y1 + y2) / 2
    return middle_x, middle_y


def find_min_distance_ps(middle_pixel_car, parking_slots):
    min_distance = float('inf')
    min_count = -1
    for count, parking_slot in enumerate(parking_slots):
        if is_empty(parking_slot):
            distance = create_distance(parking_slot, middle_pixel_car)
            if distance < min_distance:
                min_distance = distance
                min_count = count
    if min_count == -1:
        raise ValueError("No empty parking slot found.")
    return min_count


def is_empty(parking_slot):
    return not (parking_slot.get("isNavigatedTo", False) or parking_slot.get("isTaken", False))


def create_distance(parking_slot, car):
    middle_pixel_ps = get_middle_of_bbox(parking_slot["pos"])
    return get_distance_from_car_to_parking(car, middle_pixel_ps)


def get_distance_from_car_to_parking(car, parking):
    return math.sqrt((car[0] - parking[0]) ** 2 + (car[1] - parking[1]) ** 2)


def get_distance(car, parking_slot):
    x = parking_slot[0] - car[0]
    y = parking_slot[1] - car[1]
    return x, y


def create_dictionary(x, y):
    d1 = {
        "direction": "forward",
        "distance": y
    }
    direction = "right" if x < 0 else "left"
    d2 = {
        "direction": direction,
        "distance": abs(x)
    }
    if y > 20:
        return d2
    else:
        return d1, d2
