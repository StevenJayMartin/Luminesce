import faulthandler
faulthandler.enable(all_threads=True)

import json
import argparse
import logging
import os

from ui_app import LuminApp

# -----------------------------
# LOGGING SETUP
# -----------------------------
logging.basicConfig(
    filename="lumin.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
log = logging.getLogger("main")


# -----------------------------
# CONFIG + ARGPARSE
# -----------------------------
def load_config(path: str) -> dict:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        config = json.load(f)

    # sensible defaults if missing
    config.setdefault("model", "llama3.1")
    config.setdefault("ollama_url", "http://localhost:11434")
    config.setdefault("mic_device", 0)
    config.setdefault("listen_mode", "push_to_talk")  # or "always"

    # wake / control words
    config.setdefault("wake_words", ["hey lumin", "lumin"])
    config.setdefault("stop_words", ["stop", "cancel"])
    config.setdefault("clear_words", ["clear that", "reset"])
    config.setdefault("listen_again_words", ["listen again", "start over"])

    # STT tuning
    config.setdefault("vosk_model_path", "models/vosk")
    config.setdefault("silence_threshold", 3000)
    config.setdefault("silence_duration", 0.6)

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
        config["model"] = args.model
    if args.ollama:
        config["ollama_url"] = args.ollama
    if args.mic is not None:
        config["mic_device"] = args.mic
    if args.listen_mode:
        config["listen_mode"] = args.listen_mode

    log.debug(f"Final config: {config}")

    if args.mode == "tui":
        app = LuminApp(config=config)
        app.run()
    else:
        log.error(f"Unsupported mode: {args.mode}")


if __name__ == "__main__":
    main()
