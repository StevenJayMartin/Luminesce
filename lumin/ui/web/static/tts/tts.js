export async function speakText(text) {
    const res = await fetch("/api/tts", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ text })
    });

    const data = await res.json();
    if (!data.ok) {
        console.error("TTS error:", data.error);
        return;
    }

    const pcm = Float32Array.from(data.pcm);
    playPCM(pcm);
}

function playPCM(pcm) {
    const wav = pcmToWav(pcm);
    const blob = new Blob([wav], { type: "audio/wav" });
    const url = URL.createObjectURL(blob);
    new Audio(url).play();
}

function pcmToWav(pcm) {
    const numSamples = pcm.length;
    const buffer = new ArrayBuffer(44 + numSamples * 2);
    const view = new DataView(buffer);

    // WAV header
    view.setUint32(0, 0x52494646, false);
    view.setUint32(4, 36 + numSamples * 2, true);
    view.setUint32(8, 0x57415645, false);
    view.setUint32(12, 0x666d7420, false);
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, 22050, true);
    view.setUint32(28, 22050 * 2, true);
    view.setUint16(32, 2, true);
    view.setUint16(34, 16, true);
    view.setUint32(36, 0x64617461, false);
    view.setUint32(40, numSamples * 2, true);

    let offset = 44;
    for (let i = 0; i < numSamples; i++) {
        view.setInt16(offset, pcm[i] * 32767, true);
        offset += 2;
    }

    return buffer;
}
