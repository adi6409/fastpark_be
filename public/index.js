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
    try {
        const response = await fetch(`${apiUrlappstate}?carId=${carId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch appState: ${response.statusText}`);
        }

        const appState = await response.json();

        if (appState.state === "directions") {
            updateDirection(appState.data.direction);
            updateDistance(appState.data.distanceToNext);
        } else if (appState.state === "finished") {
            console.log("App State: finished");
            updateDirection("finished");
            updateDistance("");
        }

        return appState; // Ensure appState is returned
    } catch (error) {
        console.error("Error in getAppStateFromAPI:", error);
        return null; // Return null on failure to prevent crashes
    }
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

async function loopAPIRequests() {
    const carId = cars[currentCarIndex].carId; // Use the current car ID
    let isFinished = false; // Flag to stop the loop

    while (!isFinished) {
        try {
            console.log(`Fetching appState for carId: ${carId}`);
            const appState = await getAppStateFromAPI(carId);

            // If appState is finished, stop the loop
            if (appState && appState.state === "finished") {
                isFinished = true;
                console.log("Parking process finished. Stopping requests.");
                break; // Exit the loop immediately
            }

            // Optional: Delay to avoid spamming the server
            await new Promise(resolve => setTimeout(resolve, 1000));
        } catch (error) {
            console.error("Error in loopAPIRequests:", error);
        }
    }
    console.log("Exiting loopAPIRequests.");
}



function updateDistance(distance) {
    console.log(distance)
    document.getElementById('distanceId').innerText = distance;
}

function updateDirection(direction) {
    document.getElementById('directionId').src = directions[direction];
    document.getElementById('directionNameId').innerText = direction;
}