# macOS/Linux Quickstart

Confirm you are in the repo root:

```bash
pwd
test -f pyproject.toml && echo 'repo root OK'
```

Make scripts executable and run them:

```bash
chmod +x setup.sh run_demo.sh doctor.sh
./setup.sh
./run_demo.sh
```

Activate the virtual environment manually:

```bash
source .venv/bin/activate
```

If `python` is missing, try `python3`. If you see `permission denied`, rerun `chmod +x setup.sh run_demo.sh doctor.sh`.

Run tests:

```bash
python -m pytest tests -vv -s
```

Run the optional UI:

```bash
streamlit run app.py
```
