let currentCarIndex = 0;
let cars;

const directions = { "forward": "assets/arrow-forward.png", "left": "assets/arrow-left.png", "right": "assets/arrow-right.png" , "finihsed": "assets/finished-verafication.png"}

const apiUrlgetcars = '/api/getCars';
const apiUrlappstate = '/api/appState';

function getCarListFromAPI() {
    fetch(apiUrlgetcars)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(userData => {
            // Process the retrieved user data
            console.log('User Data:', userData);
            cars = userData;
            changeCar("next");
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function getAppStateFromAPI(carId) {
    fetch(apiUrlappstate + `?carId=${carId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(appState => {
            if (appState['state'] == 'directions') {
                updateDirection(appState['data']['direction'])
                updateDistance(appState['data']['distanceToNext'])
            }
            else if(appState['state'] == 'finished'){
                updateDirection('finished');
                updateDistance("");
            }
            console.log('App State:', appState);
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

getCarListFromAPI();


function changeCar(direction) {
    if (direction === 'prev') {
        currentCarIndex = (currentCarIndex - 1 + cars.length) % cars.length;
    } else {
        currentCarIndex = (currentCarIndex + 1) % cars.length;
    }
    carjson = cars[currentCarIndex];
    console.log(carjson);
    document.getElementById('carImage').src = carjson["imageUrl"];
    document.getElementById('carId').innerText = carjson['carId'];
}

function enterParkingLot() {
    document.getElementById('mainContent').style = "display: none;";
    document.getElementById('loaderContainer').style = "display: flex;"
    startGuidedParking();
}

function startGuidedParking() {
    let carId = cars[currentCarIndex].carId
    console.log(`carId: ${carId}`)
    getAppStateFromAPI(carId)
    document.getElementById('loaderContainer').style = "display: none;";
    document.getElementById('carGuideContent').style = "display: flex;";
}

function loopAPIRequests() {
    while (true) {
        getAppStateFromAPI(carId);
    }
}

function updateDistance(distance) {
    console.log(distance)
    document.getElementById('distanceId').innerText = distance;
}

function updateDirection(direction) {
    document.getElementById('directionId').src = directions[direction];
    document.getElementById('directionNameId').innerText = direction;
}