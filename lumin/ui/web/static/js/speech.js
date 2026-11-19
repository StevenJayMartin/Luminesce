// speech.js

let speechQueue = [];
let speechPlaying = false;
let speechStop = false;
let currentAudio = null;

function splitIntoChunks(text) {

    if (!text) {
        return [];
    }

    return text
        .split(/(?<=[.!?])/)
        .map(x => x.trim())
        .filter(x => x.length > 0);
}

function stopSpeech() {

    speechStop = true;

    speechQueue = [];

    if (currentAudio) {

        currentAudio.pause();

        currentAudio.currentTime = 0;

        currentAudio = null;
    }

    speechPlaying = false;
}

async function playChunk(text) {

    const response = await fetch(
        "/api/tts",
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json"
            },
            body: JSON.stringify({
                text: text
            })
        }
    );

    if (!response.ok) {
        throw new Error(
            `TTS failed: ${response.status}`
        );
    }

    const blob =
        await response.blob();

    const url =
        URL.createObjectURL(blob);

    const currentAudio =
        new Audio(url);

    await currentAudio.play();

    await new Promise(resolve => {

        currentAudio.onended = () => {

            URL.revokeObjectURL(url);

            resolve();
        };
    });
}

async function processSpeechQueue() {

    if (speechPlaying) {
        return;
    }

    speechPlaying = true;

    try {

        while (
            speechQueue.length > 0 &&
            !speechStop
        ) {

            const chunk =
                speechQueue.shift();

            console.log(
                "Speaking:",
                chunk
            );

            await playChunk(chunk);
        }

    } catch (err) {

        console.error(
            "Speech queue error:",
            err
        );

    } finally {

        speechPlaying = false;
    }
}

async function speakText(text) {

    speechStop = false;

    const chunks =
        splitIntoChunks(text);

    console.log(
        "Speech Chunks:",
        chunks
    );

    speechQueue.push(...chunks);

    processSpeechQueue();
}

function stopSpeech() {

    speechStop = true;

    speechQueue = [];
}

window.speakText = speakText;
window.stopSpeech = stopSpeech;

console.log(
    "speech.js queue mode loaded"
);