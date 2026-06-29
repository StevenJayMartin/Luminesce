import sounddevice as sd
print(sd.query_devices())

sd.default.device = 1
sd.check_input_settings(device=1, samplerate=16000)
print("Mic OK")

import numpy as np

print("Recording 2 seconds...")
audio = sd.rec(44100*2, samplerate=44100, channels=1, dtype='int16')
sd.wait()

print("Max amplitude:", np.max(np.abs(audio)))
