// static/tts/tts.js
import * as ort from "/static/onnx/ort.min.mjs";

let sessionPromise = null;

async function getSession() {
    if (!sessionPromise) {
        sessionPromise = ort.InferenceSession.create("/static/onnx/model.onnx", {
            executionProviders: ["wasm"],
            graphOptimizationLevel: "all"
        });
    }
    return sessionPromise;
}

// TODO: replace with real tokenizer using tokens.txt / lexicon.txt
function textToIds(text) {
    // Dummy: map each character to its char code, truncated
    const codes = Array.from(text).map(c => c.charCodeAt(0)).slice(0, 256);
    const arr = new Int32Array(codes.length);
    arr.set(codes);
    return arr;
}

export async function speakText(text) {
    if (!text || !text.trim()) return;

    const session = await getSession();

    const ids = textToIds(text);
    const input = new ort.Tensor("int32", ids, [1, ids.length]);

    const outputs = await session.run({ input_ids: input });
    // Assume single output named "audio" or first output
    const firstKey = Object.keys(outputs)[0];
    const pcmTensor = outputs[firstKey];

    const pcm = pcmTensor.data; // Float32Array

    playPCM(pcm);
}

function playPCM(pcm) {
    const wavBuffer = pcmToWav(pcm, 22050);
    const blob = new Blob([wavBuffer], { type: "audio/wav" });
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.play();
}

function pcmToWav(pcm, sampleRate) {
    const numSamples = pcm.length;
    const buffer = new ArrayBuffer(44 + numSamples * 2);
    const view = new DataView(buffer);

    // RIFF header
    writeString(view, 0, "RIFF");
    view.setUint32(4, 36 + numSamples * 2, true);
    writeString(view, 8, "WAVE");

    // fmt chunk
    writeString(view, 12, "fmt ");
    view.setUint32(16, 16, true);      // PCM chunk size
    view.setUint16(20, 1, true);       // audio format = PCM
    view.setUint16(22, 1, true);       // channels = 1
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true); // byte rate
    view.setUint16(32, 2, true);       // block align
    view.setUint16(34, 16, true);      // bits per sample

    // data chunk
    writeString(view, 36, "data");
    view.setUint32(40, numSamples * 2, true);

    // PCM samples
    let offset = 44;
    for (let i = 0; i < numSamples; i++) {
        let s = Math.max(-1, Math.min(1, pcm[i]));
        view.setInt16(offset, s * 0x7fff, true);
        offset += 2;
    }

    return buffer;
}

function writeString(view, offset, str) {
    for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
    }
}
