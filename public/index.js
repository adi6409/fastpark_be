let currentCarIndex = 0;
let cars;

const directions = { "forward": "assets/arrow-forward.png", "left": "assets/arrow-left.png", "right": "assets/arrow-right.png" , "finished": "assets/finished-parking.jpg"}

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

async function getAppStateFromAPI(carId) {
    return fetch(apiUrlappstate + `?carId=${carId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(appState => {
            if (appState['state'] === 'directions') {
                updateDirection(appState['data']['direction']);
                updateDistance(appState['data']['distanceToNext']);
            } else if (appState['state'] === 'finished') {
                console.log('Finished');
                updateDirection('finished');
                updateDistance("");
            }
            console.log('App State:', appState);
            return appState; // Return the appState
        })
        .catch(error => {
            console.error('Error:', error);
            return null; // Handle errors gracefully
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

async function startGuidedParking() {
    const carId = cars[currentCarIndex].carId; // Define `carId` in this scope
    console.log(`carId: ${carId}`);
    document.getElementById('loaderContainer').style = "display: none;";
    document.getElementById('carGuideContent').style = "display: flex;";
    await loopAPIRequests(carId); // Pass the carId to the function
}

async function loopAPIRequests(carId) {
    let isFinished = false; // Flag to track the 'finished' state
    while (!isFinished) {
        console.log("Fetching App State for carId:", carId);
        const appState = await getAppStateFromAPI(carId);

        // Check if the state is 'finished'
        if (appState && appState.state === "finished") {
            isFinished = true; // Exit the loop
            console.log("Finished parking! Stopping requests.");
        }

        // Add a delay before the next request
        if (!isFinished) {
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
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