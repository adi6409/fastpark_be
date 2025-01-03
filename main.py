from typing import Union
from fastapi import FastAPI
from fastapi.responses import FileResponse
import requests
from fastapi.middleware.cors import CORSMiddleware
import logging
from dummy_jsons import CARS_LIST, DUMMY_JSON
from inference import get_state


logging.basicConfig(filename="app.log", filemode='a')
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/appState")
def get_car_info(carId: Union[str, None] = None):
    return DUMMY_JSON


@app.get("/api/getCars")
def get_cars():
    return CARS_LIST


@app.get("/assets/{filename}")
def get_file(filename):
    return FileResponse("assets/" + filename)
