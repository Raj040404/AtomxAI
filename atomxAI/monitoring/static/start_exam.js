let faceDetected = false;
let unauthorizedObjectDetected = false;
let gazeWarningLogged = false;
let videoStream = null;
let isMonitoring = false;
let multiplePeopleWarningLogged = false;
let logArray = [];

const loadingBar = document.getElementById("loadingBar");
const contentContainer = document.getElementById("contentContainer");
const instructionsContainer = document.getElementById("instructionsContainer");
const examFormContainer = document.getElementById("examFormContainer");
const googleFormContainer = document.getElementById("googleFormContainer");
const startExamButton = document.getElementById("startExamButton");
const endExamButton = document.getElementById("endExamButton");
const timerDisplay = document.getElementById("timeRemaining");
const timerContainer = document.getElementById("timer");
const loadingSpinner = document.getElementById("loadingSpinner");

let timerInterval;

contentContainer.style.display = 'none';
if (examFormContainer) examFormContainer.style.display = 'none';
if (googleFormContainer) googleFormContainer.style.display = 'none';
endExamButton.style.display = 'none';
loadingSpinner.style.display = 'none';

setTimeout(() => {
    loadingBar.style.display = 'none';
    startExamButton.style.display = 'block';
}, 5000);

async function startMonitoring() {
    if (isMonitoring) return;

    isMonitoring = true;
    const video = document.getElementById("videoElement");
    const statusElement = document.getElementById("status");

    loadingSpinner.style.display = 'flex';
    instructionsContainer.style.display = 'none';

    try {
        const faceModel = await blazeface.load();
        const objectModel = await cocoSsd.load();
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });

        loadingSpinner.style.display = 'none';
        contentContainer.style.display = 'block';
        if (isCustomForm && examFormContainer) {
            examFormContainer.style.display = 'block';
        } else if (googleFormContainer) {
            googleFormContainer.style.display = 'block';
        }

        videoStream = stream;
        video.srcObject = stream;
        video.play();
        statusElement.innerText = "Models loaded. Monitoring...";

        startTimer();
        lockBrowser();

        video.addEventListener("loadeddata", async () => {
            while (isMonitoring) {
                let logMessage = "";
                const faces = await faceModel.estimateFaces(video, false);

                if (faces.length > 1) {
                    if (!multiplePeopleWarningLogged) {
                        logMessage = "Warning: Multiple people detected!";
                        logActivity(logMessage, "high");
                        multiplePeopleWarningLogged = true;
                    }
                } else {
                    multiplePeopleWarningLogged = false;
                }

                if (faces.length === 0) {
                    if (faceDetected) {
                        logMessage = "No face detected. Please stay in front of the camera.";
                        logActivity(logMessage, "high");
                        faceDetected = false;
                    }
                } else {
                    if (!faceDetected) {
                        logMessage = "Face detected. Monitoring...";
                        logActivity(logMessage, "low");
                        faceDetected = true;
                    }
                    const face = faces[0];
                    const rightEye = face.rightEye;
                    const leftEye = face.leftEye;
                    if (rightEye && leftEye) {
                        const eyeCenter = [(rightEye[0] + leftEye[0]) / 2, (rightEye[1] + leftEye[1]) / 2];
                        const gazeThresholdX = video.videoWidth / 5;
                        const gazeThresholdY = video.videoHeight / 5;
                        if (
                            eyeCenter[0] < gazeThresholdX ||
                            eyeCenter[0] > video.videoWidth - gazeThresholdX ||
                            eyeCenter[1] < gazeThresholdY ||
                            eyeCenter[1] > video.videoHeight - gazeThresholdY
                        ) {
                            if (!gazeWarningLogged) {
                                logMessage = "Warning: You are looking away from the screen!";
                                logActivity(logMessage, "medium");
                                gazeWarningLogged = true;
                            }
                        } else {
                            gazeWarningLogged = false;
                        }
                    }
                }

                const predictions = await objectModel.detect(video);
                let foundUnauthorizedObject = false;
                predictions.forEach((prediction) => {
                    if (prediction.class === "cell phone" || prediction.class === "laptop") {
                        foundUnauthorizedObject = true;
                        if (!unauthorizedObjectDetected) {
                            logMessage = `Warning: Unauthorized object detected: ${prediction.class}`;
                            logActivity(logMessage, "high");
                            unauthorizedObjectDetected = true;
                        }
                    }
                });
                if (!foundUnauthorizedObject) {
                    unauthorizedObjectDetected = false;
                }

                await tf.nextFrame();
            }
        });
    } catch (err) {
        console.log("Error during setup: ", err);
        statusElement.innerText = "Error setting up exam environment.";
        loadingSpinner.style.display = 'none';
    }

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            logActivity("Warning: You have switched tabs or minimized the browser!", "high");
        }
    });
}

function startTimer() {
    timerContainer.style.display = 'block';
    let remainingTime = timerDuration;

    timerInterval = setInterval(() => {
        if (remainingTime <= 0) {
            clearInterval(timerInterval);
            logActivity("Time is up!", "high");
            stopMonitoring();
            handleEndExam();
            return;
        }

        const minutes = Math.floor(remainingTime / 60);
        const seconds = remainingTime % 60;
        timerDisplay.innerText = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        remainingTime--;
    }, 1000);
}

function requestFullScreen() {
    const elem = document.documentElement;
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) {
        elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) {
        elem.msRequestFullscreen();
    }
}

function lockBrowser() {
    document.addEventListener("contextmenu", (event) => event.preventDefault());
    document.addEventListener("keydown", (event) => {
        if (
            event.ctrlKey &&
            (event.key === "c" || event.key === "v" || event.key === "x")
        ) {
            event.preventDefault();
        }
    });
    document.addEventListener("selectstart", (event) => event.preventDefault());
}

function stopMonitoring() {
    isMonitoring = false;
    if (videoStream) {
        videoStream.getTracks().forEach((track) => track.stop());
    }
    document.getElementById("videoElement").srcObject = null;
    document.getElementById("status").innerText = "Monitoring stopped.";
    clearInterval(timerInterval);
    contentContainer.style.display = 'none';
    if (examFormContainer) examFormContainer.style.display = 'none';
    if (googleFormContainer) googleFormContainer.style.display = 'none';
    endExamButton.style.display = 'none';
}

function logActivity(message, severity) {
    const logElement = document.getElementById("log");
    const timestamp = new Date().toLocaleTimeString();
    const severityClass = `severity-${severity}`;
    
    const logEntry = document.createElement("div");
    logEntry.className = `log-entry ${severityClass}`;
    logEntry.innerText = `[${timestamp}] ${message}`;
    logElement.appendChild(logEntry);
    
    logArray.push(`[${timestamp}] ${message}`);
}

function handleStartExam() {
    requestFullScreen();
    startExamButton.style.display = 'none';
    endExamButton.style.display = 'block';
    startMonitoring();
}

function handleEndExam() {
    let answers = {};
    if (isCustomForm && examFormContainer) {
        const form = document.getElementById("examForm");
        const formData = new FormData(form);
        formData.forEach((value, key) => {
            const questionNum = key.split('_')[1];
            const questionText = form.querySelector(`input[name="${key}"]`).previousElementSibling.innerText.split('. ')[1];
            answers[questionText] = value;
        });
    }

    stopMonitoring();
    fetch(`/exam/${roomCode}/${rollNumber}/end_exam/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log: logArray, answers })
    }).then(response => {
        if (response.ok) {
            window.location.href = "/";
        } else {
            console.error('Failed to submit exam:', response.statusText);
        }
    }).catch(error => {
        console.error('Error submitting exam:', error);
    });
}

startExamButton.addEventListener("click", handleStartExam);
endExamButton.addEventListener("click", handleEndExam);