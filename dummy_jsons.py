import json

# DUMMY_JSON = {
#     "state": "directions",
#     "data": {
#             "direction": "forward",
#             "distanceToNext": 200,
#             "distanceToEnd": 500
#         }
#     }

# Read DUMMY_JSON from dummy_json.json
with open('dummy_json.json', 'r') as file:
    DUMMY_JSON = json.load(file)
    


CARS_LIST = [
    {
        "carId": "hw_blue",
        "imageUrl": "https://fastpark.astroianu.dev/assets/blue.png"
    },
    {
        "carId": "rc_green",
        "imageUrl": "https://fastpark.astroianu.dev/assets/green.png"
    },
    {
        "carId": "rc_blue",
        "imageUrl": "https://fastpark.astroianu.dev/assets/lamborghini.png"
    },
    {
        "carId": "taxi",
        "imageUrl": "https://fastpark.astroianu.dev/assets/taxi.png"
    },
    {
        "carId": "turquoise",
        "imageUrl": "https://fastpark.astroianu.dev/assets/turquoise.png"
    },
    {
        "carId": "volvo",
        "imageUrl": "https://fastpark.astroianu.dev/assets/volvo.png"
    }
]
