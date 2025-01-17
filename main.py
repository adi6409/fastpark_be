from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import HTTPException
import requests
from fastapi.middleware.cors import CORSMiddleware
from dummy_jsons import CARS_LIST, DUMMY_JSON
from inference import get_state, process_stream
import mimetypes
import os
import threading


from fastapi.encoders import jsonable_encoder
import numpy as np

# Convert numpy.int64 to int
def custom_jsonable_encoder(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj



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
frame_processing_thread = threading.Thread(target=process_stream, args=(car_positions,), daemon=True)
frame_processing_thread.start()


custom_encoder = {
    np.integer: int,
    np.floating: float,
    np.ndarray: lambda obj: obj.tolist(),
}


@app.get("/api/appState")
def get_car_info(carId: Union[str, None] = None):
    try:
        result = get_state(carId, car_positions)
        # Use the corrected `custom_encoder`
        return jsonable_encoder(result, custom_encoder=custom_encoder)
    except Exception as e:
        print(e)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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