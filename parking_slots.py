import json
import os


PARKING_SLOTS_FILE = 'parking_slots.json'
if os.path.exists(PARKING_SLOTS_FILE):
    with open(PARKING_SLOTS_FILE, 'r') as file:
        parking_slots = json.load(file)

    print(parking_slots)
else:
    print(f"File {PARKING_SLOTS_FILE} not found.")
    exit(1)


def get_parking_slots():
    with open(PARKING_SLOTS_FILE, 'r') as file:
        parking_slots = json.load(file)
    return parking_slots

def update_parking_slots(parking_slots):
    with open(PARKING_SLOTS_FILE, 'w') as file:
        json.dump(parking_slots, file, indent=4)

def update_parking_slot(place_in_ls, status):
    parking_slots = get_parking_slots()
    parking_slots[place_in_ls] = status
    update_parking_slots(parking_slots)