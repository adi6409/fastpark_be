from typing import Union
from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware
import logging


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
    return 
