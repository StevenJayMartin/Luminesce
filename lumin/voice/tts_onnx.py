# lumin/voice/tts_onnx.py

import io
import re

import wave
from pathlib import Path

import numpy as np
import onnxruntime as ort


class OnnxTTS:
    """
    Melo/VITS ONNX TTS engine.

    Current limitations:
    - Words must exist in lexicon.txt
    - Punctuation handling not implemented
    - Unknown words are skipped
    """

    def __init__(self, model_dir="lumin/models/onnx"):

        self.model_dir = Path(model_dir)

        self.session = ort.InferenceSession(
            str(self.model_dir / "model.onnx")
        )

        self.tokens = self._load_tokens()
        self.lexicon = self._load_lexicon()

        self.blank_id = self.tokens.get("_", 0)

    # --------------------------------------------------
    # Load assets
    # --------------------------------------------------

    def _prepare_text(self, text: str) -> str:

        if not text:
            return ""

        lines = []
        in_code_block = False

        for line in text.splitlines():

            line = line.strip()

            if not line:
                continue

            if line.startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            if line.startswith("#"):
                continue

            if line.startswith("* "):
                line = line[2:]

            elif line.startswith("- "):
                line = line[2:]

            elif line.startswith("+ "):
                line = line[2:]

            line = line.replace("**", "")
            line = line.replace("__", "")
            line = line.replace("*", "")
            line = line.replace("_", "")
            line = line.replace("`", "")

            lines.append(line)

        text = " ".join(lines)

        return " ".join(text.split())

    def _load_tokens(self):

        tokens = {}

        with open(
            self.model_dir / "tokens.txt",
            encoding="utf-8"
        ) as f:

            for line in f:

                line = line.strip()

                if not line:
                    continue

                token, token_id = line.rsplit(" ", 1)

                tokens[token] = int(token_id)

        return tokens

    def _load_lexicon(self):

        lexicon = {}

        with open(
            self.model_dir / "lexicon.txt",
            encoding="utf-8"
        ) as f:

            for line in f:

                parts = line.strip().split()

                if len(parts) < 3:
                    continue

                word = parts[0].lower()

                phonemes = []
                tones = []

                for item in parts[1:]:

                    try:
                        tones.append(int(item))
                    except ValueError:
                        phonemes.append(item)

                lexicon[word] = {
                    "phonemes": phonemes,
                    "tones": tones,
                }

        return lexicon

    # --------------------------------------------------
    # Text -> model inputs
    # --------------------------------------------------

    def _word_to_sequence(self, word):

        original_word = word

        word = word.lower()

        # strip punctuation attached to words
        word = word.strip(
            ".,!?;:\"'()[]{}"
        )

        if not word:
            return [], []

        entry = self.lexicon.get(word)

        if not entry:
            print(
                "UNKNOWN WORD:",
                original_word,
                "->",
                word
            )
            return [], []

        token_ids = []
        tone_ids = []

        for phoneme, tone in zip(
            entry["phonemes"],
            entry["tones"]
        ):

            token = self.tokens.get(
                phoneme
            )

            if token is None:
                continue

            token_ids.append(token)
            tone_ids.append(tone)

        return token_ids, tone_ids
    
    
    def _build_inputs(self, text):

        print("BUILD INPUTS:", repr(text))

        token_sequence = []
        tone_sequence = []

        for word in text.lower().split():

            tokens, tones = self._word_to_sequence(word)
            print(
                f"{word:<20} {'OK' if tokens else 'MISSING'}"
            )

            token_sequence.extend(tokens)
            tone_sequence.extend(tones)

        if not token_sequence:
            raise ValueError(
                f"No words matched lexicon: {text}"
            )

        x = [self.blank_id]
        t = [0]

        for token, tone in zip(
            token_sequence,
            tone_sequence
        ):

            # add_blank = 1
            x.append(token)
            x.append(self.blank_id)

            t.append(tone)
            t.append(0)

        return (
            np.array([x], dtype=np.int64),
            np.array([t], dtype=np.int64),
        )

    # --------------------------------------------------
    # Synthesis
    # --------------------------------------------------

    def synthesize(self, text: str) -> bytes:

        text = self._prepare_text(text)

        if not text:
            print("EMPTY AFTER PREPARE")
            return b""

        x, tones = self._build_inputs(text)
        
        print("TEXT:", text)
        print("X:", x.tolist())
        print("TONES:", tones.tolist()) 

        outputs = self.session.run(
            None,
            {
                "x": x,
                "x_lengths": np.array(
                    [len(x[0])],
                    dtype=np.int64
                ),
                "tones": tones,
                "sid": np.array(
                    [0],
                    dtype=np.int64
                ),
                "noise_scale": np.array(
                    [0.667],
                    dtype=np.float32
                ),
                "length_scale": np.array(
                    [1.0],
                    dtype=np.float32
                ),
                "noise_scale_w": np.array(
                    [0.8],
                    dtype=np.float32
                ),
            }
        )

        audio = np.squeeze(outputs[0])

        peak = np.max(np.abs(audio))

        if peak > 0:
            audio = audio / peak

        # leave some headroom
        audio = audio * 0.85

        pcm = (audio * 32767).astype(np.int16)
       
        print("min:", audio.min())
        print("max:", audio.max())
        print("shape:", audio.shape)    

        wav_buffer = io.BytesIO()

        with wave.open(wav_buffer, "wb") as wav:

            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(44100)

            wav.writeframes(
                pcm.tobytes()
            )

        return wav_buffer.getvalue()