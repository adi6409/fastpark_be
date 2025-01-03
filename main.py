from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
from fastapi.middleware.cors import CORSMiddleware
from dummy_jsons import CARS_LIST, DUMMY_JSON
from inference import get_state, process_stream
import mimetypes
import os
import threading


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create a thread that will run the constant frame processing and will update a dictionary with the carId as key and the position as value.
car_positions = {}
# frame_processing_thread = threading.Thread(target=process_stream, args=(car_positions,), daemon=True)
# In the frame processing we want to use cv2.imshow, which doesn't work in a thread. So we are gonna pass cam_disp as an argument and update it in the function.
cam_disp = None
frame_processing_thread = threading.Thread(target=process_stream, args=(car_positions, cam_disp), daemon=True)
frame_processing_thread.start()

@app.get("/api/appState")
def get_car_info(carId: Union[str, None] = None):
    return get_state(carId, car_positions)


@app.get("/api/getCars")
def get_cars():
    return CARS_LIST



# The following endpoint MUST also be able to serve subdirectories, like assets/icons/arrow.png
@app.get("/assets/{filename}")
def get_file(filename):
    return FileResponse("assets/" + filename)


# Serve .html, .css, .js files from the 'public' directory
@app.get("/{filename}")
def get_file(filename):
    if not os.path.exists("public/" + filename):
        print(f"File not found: {filename}")
        return "File not found.", 404
    return FileResponse("public/" + filename)

@app.get("/")
def get_index():
    return FileResponse("public/index.html")