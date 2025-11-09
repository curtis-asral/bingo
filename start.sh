#!/bin/bash

SESSION_NAME="flask_app"
PORT=5000
VENV_DIR="./venv"

# ----- Check if virtual environment is active -----
if [[ -z "$VIRTUAL_ENV" ]]; then
    if [[ -f "$VENV_DIR/bin/activate" ]]; then
        echo "🔹 Activating virtual environment from $VENV_DIR..."
        source "$VENV_DIR/bin/activate"
    else
        echo "❌ Virtual environment not found at $VENV_DIR."
        echo "👉 Please create it with: python3 -m venv venv"
        exit 1
    fi
fi

# ----- Check if port is already in use -----
if lsof -ti :$PORT >/dev/null 2>&1; then
    echo "⚠️ Port $PORT is in use. Killing existing process..."
    kill -9 $(lsof -ti :$PORT)
    sleep 5
fi

# ----- Kill any existing tmux session -----
tmux kill-session -t $SESSION_NAME 2>/dev/null

# ----- Start tmux session with Gunicorn -----
tmux new-session -d -s $SESSION_NAME "echo '🚀 Starting Gunicorn on port $PORT...'; gunicorn -c gunicorn.conf.py app:app"

# ----- Split pane for ngrok -----
tmux split-window -v -t $SESSION_NAME "sleep 2; echo '🌐 Starting ngrok tunnel...'; ngrok http $PORT"

# ----- Arrange panes evenly -----
tmux select-layout -t $SESSION_NAME even-vertical

# ----- Attach to session -----
tmux attach -t $SESSION_NAME
