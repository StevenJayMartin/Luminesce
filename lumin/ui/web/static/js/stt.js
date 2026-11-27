// stt.js

let mediaRecorder = null;
let audioChunks = [];
let recording = false;

async function toggleRecording() {

    console.log("navigator", navigator);
    console.log("mediaDevices", navigator.mediaDevices);
    console.log("secure", window.isSecureContext);

    const btn =
        document.getElementById("record-btn");

    if (!recording) {


        if (
            !navigator.mediaDevices ||
            !navigator.mediaDevices.getUserMedia
        ) {
            alert(
                "Microphone access unavailable.\n" +
                "navigator.mediaDevices.getUserMedia not found."
            );
            return;
        }

        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });


        audioChunks = [];

        mediaRecorder =
            new MediaRecorder(stream);

        mediaRecorder.ondataavailable =
            event => {
                audioChunks.push(event.data);
            };

        mediaRecorder.onstop =
            uploadRecording;

        mediaRecorder.start();

        recording = true;

        btn.textContent = "Stop";

        console.log(
            "Recording started"
        );

    } else {

        mediaRecorder.stop();

        recording = false;

        btn.textContent = "Record";

        console.log(
            "Recording stopped"
        );
    }
}

async function uploadRecording() {

    const blob =
        new Blob(
            audioChunks,
            {
                type: "audio/webm"
            }
        );

    const formData =
        new FormData();

    formData.append(
        "file",
        blob,
        "recording.webm"
    );

    const response =
        await fetch(
            "/api/transcribe",
            {
                method: "POST",
                body: formData
            }
        );

    const result =
        await response.json();

    console.log(
        "Transcript:",
        result
    );

    if (
        result.success &&
        result.text
    ) {
        
        const input =
            document.getElementById(
                "chat-input"
            );

        input.value = result.text;
        input.focus();
    }
}

window.toggleRecording =
    toggleRecording;
