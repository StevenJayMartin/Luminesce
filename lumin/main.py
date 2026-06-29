import faulthandler
faulthandler.enable(all_threads=True)

import json
import argparse
import logging
import os

from ui.tui.ui_app import LuminApp

# -----------------------------
# LOGGING SETUP
# -----------------------------
logging.basicConfig(
    filename="logs/lumin.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # Ensure grouped sections exist
    config.setdefault("ollama", {})
    config.setdefault("voice", {})
    config.setdefault("tools", {})
    config.setdefault("ui", {})
    config.setdefault("api", {})
    config.setdefault("tts", {})
    
    
    # -----------------------------
    # OLLAMA DEFAULTS
    # -----------------------------
    ollama_cfg = config["ollama"]
    ollama_cfg.setdefault("url", "http://localhost:11434")
    ollama_cfg.setdefault("model", "llama3.2:latest")

    # -----------------------------
    # VOICE DEFAULTS
    # -----------------------------
    voice_cfg = config["voice"]
    voice_cfg.setdefault("mic_device", 0)
    voice_cfg.setdefault("vosk_model_path", "models/vosk")
    voice_cfg.setdefault("silence_threshold", 3000)
    voice_cfg.setdefault("silence_duration", 0.6)
    voice_cfg.setdefault("listen_mode", "push_to_talk")
    voice_cfg.setdefault("tts_enabled", True)
    voice_cfg.setdefault("wake_words", ["hey lumin", "lumin"])
    voice_cfg.setdefault("stop_words", ["stop", "cancel"])
    voice_cfg.setdefault("clear_words", ["clear that", "reset"])
    voice_cfg.setdefault("listen_again_words", ["listen again", "start over"])

    # -----------------------------
    # TOOLS DEFAULTS
    # -----------------------------
    tools_cfg = config["tools"]
    tools_cfg.setdefault("enabled", True)
    tools_cfg.setdefault("list", [])
    tools_cfg.setdefault("search_engine", "duckduckgo")

    # -----------------------------
    # UI DEFAULTS
    # -----------------------------
    ui_cfg = config["ui"]
    ui_cfg.setdefault("stream_to_terminal", True)
    ui_cfg.setdefault("theme", "dark")
    ui_cfg.setdefault("animations", True)

    # -----------------------------
    # API DEFAULTS
    # -----------------------------
    api_cfg = config["api"]
    api_cfg.setdefault("enabled", False)
    api_cfg.setdefault("host", "0.0.0.0")
    api_cfg.setdefault("port", 8000)
    
    # -----------------------------
    # TTS DEFAULTS
    # -----------------------------
    tts_cfg = config["tts"]
    tts_cfg.setdefault("enabled", True)
    tts_cfg.setdefault("engine", "piper")
    tts_cfg.setdefault("piper_path", "piper/piper.exe")
    tts_cfg.setdefault("model_path", "lumin/models/en_US-ryan-high.onnx")

    return config

def parse_args():
    parser = argparse.ArgumentParser(description="Lumin — Local Light Bulb Assistant")
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to config file (default: config.json)"
    )
    parser.add_argument(
        "-m", "--model",
        help="Override model name from config.json"
    )
    parser.add_argument(
        "--ollama",
        help="Override Ollama base URL (e.g. http://localhost:11434)"
    )
    parser.add_argument(
        "--mic",
        type=int,
        help="Override microphone device index"
    )
    parser.add_argument(
        "--listen-mode",
        choices=["push_to_talk", "always"],
        help="Override listen_mode from config.json"
    )
    parser.add_argument(
        "--mode",
        choices=["tui"],
        default="tui",
        help="Run mode (currently only 'tui')"
    )
    return parser.parse_args()


# -----------------------------
# MAIN ENTRY
# -----------------------------
def main():
    args = parse_args()
    log.debug(f"Args: {args}")

    try:
        config = load_config(args.config)
    except Exception as e:
        log.exception("Failed to load config: %s", e)
        raise

    # apply CLI overrides
    if args.model:
        config["ollama"]["model"] = args.model

    if args.ollama:
        config["ollama"]["url"] = args.ollama

    if args.mic is not None:
        config["voice"]["mic_device"] = args.mic

    if args.listen_mode:
        config["voice"]["listen_mode"] = args.listen_mode

    # -----------------------------
    # TTS ENGINE LOADING
    # -----------------------------
    tts_cfg = config.get("tts", {})

    if not tts_cfg.get("enabled", True):    
        tts_engine = None

    else:
        engine = tts_cfg.get("engine", "piper")

        if engine == "piper":
            from voice.tts_piper import TTS
            tts_engine = TTS(
                piper_path=tts_cfg["piper_path"],
                model_path=tts_cfg["model_path"]
            )

        elif engine == "pyttsx3":
            from voice.tts_pyttsx3 import TTS
            tts_engine = TTS()

        else:
            raise ValueError(f"Unknown TTS engine: {engine}")


    log.debug(f"Final config: {config}")

    if args.mode == "tui":
        app = LuminApp(config=config, tts=tts_engine)
        app.run()
    else:
        log.error(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()
