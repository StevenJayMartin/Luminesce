ui/tui
(venv) PS C:\HOME_Scripts\Luminesce> ...
python -m lumin.main --model="mistral:7b" --llm-mode=chat --config="lumin/config.json"

ui/web
(venv) sjm@pop-os:~/Luminesce$ ...
uvicorn lumin.ui.web.app:app --host 0.0.0.0 --port 8000

email: stevenjaymartin@gmail.com