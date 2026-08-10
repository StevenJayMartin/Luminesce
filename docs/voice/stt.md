# Speech‑to‑Text (Vosk)

Luminesce uses Vosk for offline STT.

---

## Installation

Download a Vosk model:

```
vosk-model-small-en-us-0.15
```

Place it in:

```
lumin/models/vosk/
```

---

## Configuration

```
voice:
  stt_model: "vosk-model-small-en-us-0.15"
```

---

## Wake Word

Luminesce supports passive wake‑word detection.

