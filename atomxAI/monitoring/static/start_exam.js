let faceDetected = false;
let unauthorizedObjectDetected = false;
let gazeWarningLogged = false;
let videoStream = null;
let isMonitoring = false;
let multiplePeopleWarningLogged = false;
let logArray = []; // Array to store logs

const loadingBar = document.getElementById("loadingBar");
const contentContainer = document.getElementById("contentContainer");
const instructionsContainer = document.getElementById("instructionsContainer");
const googleFormContainer = document.getElementById("googleFormContainer");
const startExamButton = document.getElementById("startExamButton");
const endExamButton = document.getElementById("endExamButton");
const endExamForm = document.getElementById("endExamForm");
const timerDisplay = document.getElementById("timeRemaining");
const timerContainer = document.getElementById("timer");
const loadingSpinner = document.getElementById("loadingSpinner");

let timerInterval;

// Initially hide the content containers
contentContainer.style.display = 'none';
googleFormContainer.style.display = 'none';
endExamButton.style.display = 'none'; // Hide the End Exam button
loadingSpinner.style.display = 'none'; // Hide the loading spinner initially

// Show the Start Exam button after initial loading
setTimeout(() => {
    loadingBar.style.display = 'none'; // Hide the initial loading bar
    startExamButton.style.display = 'block'; // Show the Start Exam button
}, 5000); // 5000 milliseconds = 5 seconds

async function startMonitoring() {
    if (isMonitoring) return;

    isMonitoring = true;
    const video = document.getElementById("videoElement");
    const statusElement = document.getElementById("status");

    // Show the loading spinner
    loadingSpinner.style.display = 'flex';
    instructionsContainer.style.display = 'none'; // Hide instructions while loading

    try {
        // Load the BlazeFace model for face detection and Coco-SSD for object detection
        const faceModel = await blazeface.load();
        const objectModel = await cocoSsd.load();

        // Access the user's webcam
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });

        // If everything is loaded successfully, hide the spinner and show the content
        loadingSpinner.style.display = 'none';
        contentContainer.style.display = 'block';
        googleFormContainer.style.display = 'block'; // Show the Google Form

        videoStream = stream;
        video.srcObject = stream;
        video.play();
        statusElement.innerText = "Models loaded. Monitoring...";

        // Start the timer once the Google Form is displayed
        startTimer();

        // Lock the browser as soon as the monitoring starts
        lockBrowser();

        video.addEventListener("loadeddata", async () => {
            while (isMonitoring) {
                let logMessage = "";

                // Face detection
                const faces = await faceModel.estimateFaces(video, false);

                // Check for multiple faces on the screen
                if (faces.length > 1) {
                    if (!multiplePeopleWarningLogged) {
                        logMessage = "Warning: Multiple people detected!";
                        logActivity(logMessage, "high");
                        multiplePeopleWarningLogged = true; // Set log flag
                    }
                } else {
                    multiplePeopleWarningLogged = false; // Reset if only one person is in the frame
                }

                // Check if no face is detected
                if (faces.length === 0) {
                    if (faceDetected) {
                        logMessage = "No face detected. Please stay in front of the camera.";
                        logActivity(logMessage, "high");
                        faceDetected = false; // Reset log flag
                    }
                } else {
                    if (!faceDetected) {
                        logMessage = "Face detected. Monitoring...";
                        logActivity(logMessage, "low");
                        faceDetected = true; // Set log flag
                    }

                    // Check gaze direction if face is detected
                    const face = faces[0];
                    const rightEye = face.rightEye;
                    const leftEye = face.leftEye;

                    if (rightEye && leftEye) {
                        const eyeCenter = [
                            (rightEye[0] + leftEye[0]) / 2,
                            (rightEye[1] + leftEye[1]) / 2,
                        ];

                        // Adjust these thresholds based on your video dimensions
                        const gazeThresholdX = video.videoWidth / 5; // 20% of width
                        const gazeThresholdY = video.videoHeight / 5; // 20% of height

                        // Check if the gaze is outside the designated area
                        if (
                            eyeCenter[0] < gazeThresholdX ||
                            eyeCenter[0] > video.videoWidth - gazeThresholdX ||
                            eyeCenter[1] < gazeThresholdY ||
                            eyeCenter[1] > video.videoHeight - gazeThresholdY
                        ) {
                            if (!gazeWarningLogged) {
                                logMessage = "Warning: You are looking away from the screen!";
                                logActivity(logMessage, "medium");
                                gazeWarningLogged = true; // Set log flag
                            }
                        } else {
                            gazeWarningLogged = false; // Reset if looking back
                        }
                    }
                }

                // Object detection
                const predictions = await objectModel.detect(video);

                let foundUnauthorizedObject = false;

                predictions.forEach((prediction) => {
                    const objectName = prediction.class;

                    if (objectName === "cell phone" || objectName === "laptop") {
                        foundUnauthorizedObject = true;
                        if (!unauthorizedObjectDetected) {
                            logMessage = `Warning: Unauthorized object detected: ${objectName}`;
                            logActivity(logMessage, "high");
                            unauthorizedObjectDetected = true; // Set log flag
                        }
                    }
                });

                if (!foundUnauthorizedObject) {
                    unauthorizedObjectDetected = false; // Reset flag if no unauthorized objects found
                }

                await tf.nextFrame(); // Continue looping for real-time detection
            }
        });
    } catch (err) {
        console.log("Error during setup: ", err);
        statusElement.innerText = "Error setting up exam environment.";
        loadingSpinner.style.display = 'none'; // Hide spinner on error
    }

    // Tab switch or minimize detection
    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            logActivity(
                "Warning: You have switched tabs or minimized the browser!",
                "high"
            );
        }
    });
}

// Timer function
function startTimer() {
    timerContainer.style.display = 'block'; // Show the timer display
    let remainingTime = timerDuration;

    // Update the timer display every second
    timerInterval = setInterval(() => {
        if (remainingTime <= 0) {
            clearInterval(timerInterval);
            logActivity("Time is up!", "high");
            stopMonitoring(); // Stop monitoring when time is up
            endExamForm.style.display = 'block'; // Show the End Exam form for submission
            endExamButton.style.display = 'none'; // Hide the End Exam button
            return;
        }

        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;
        timerDisplay.innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        remainingTime--;
    }, 1000); // Update every second
}

// Function to handle exam start button click
function handleStartExam() {
    requestFullScreen(); // Request full-screen mode
    startExamButton.style.display = 'none'; // Hide the Start Exam button
    endExamButton.style.display = 'block'; // Show the End Exam button
    startMonitoring(); // Start monitoring the exam process
}

// Fullscreen function
function requestFullScreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) { // Firefox
        elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) { // Chrome, Safari and Opera
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { // IE/Edge
        elem.msRequestFullscreen();
    }
}

function lockBrowser() {
    // Disable right-click context menu
    document.addEventListener("contextmenu", (event) => {
        event.preventDefault();
    });

    // Disable keyboard shortcuts for copying text (e.g., Ctrl+C, Ctrl+V, Ctrl+X)
    document.addEventListener("keydown", (event) => {
        if (
            event.ctrlKey &&
            (event.key === "c" || event.key === "v" || event.key === "x")
        ) {
            event.preventDefault(); // Prevent copy, paste, cut
        }
    });

    // Prevent text selection
    document.addEventListener("selectstart", (event) => {
        event.preventDefault(); // Prevent text selection
    });
}

function stopMonitoring() {
    isMonitoring = false;
    if (videoStream) {
        const tracks = videoStream.getTracks();
        tracks.forEach((track) => track.stop());
    }
    document.getElementById("videoElement").srcObject = null;
    document.getElementById("status").innerText = "Monitoring stopped.";
    clearInterval(timerInterval); // Clear the timer when stopping monitoring
}

// Log activity in the UI and store in logArray
function logActivity(message, severity) {
    const logElement = document.getElementById("log");
    const timestamp = new Date().toLocaleTimeString(); // Generate a timestamp
    const severityClass = `severity-${severity}`; // Define severity styles
    
    // Display the log on the screen
    const logEntry = document.createElement("div");
    logEntry.className = `log-entry ${severityClass}`; // Set severity class for styling
    logEntry.innerText = `[${timestamp}] ${message}`;
    logElement.appendChild(logEntry);
    
    // Store the log message along with its timestamp in the array
    logArray.push(`[${timestamp}] ${message}`);
}

// Function to handle exam end button click
function handleEndExam() {
    stopMonitoring(); // Stop monitoring the exam process
    endExamButton.style.display = 'none'; // Hide the End Exam button
    endExamForm.style.display = 'block'; // Show the End Exam form for submission
}

// Attach event listeners
startExamButton.addEventListener("click", handleStartExam);
endExamButton.addEventListener("click", handleEndExam);