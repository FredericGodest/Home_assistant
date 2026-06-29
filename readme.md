# Venv
source .ai-home/bin/activate

# Démarrer
tmux new -s gw -d '~/AI-server/.ai-home/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000'

# Test
tmux ls
ss -tlnp | grep 8000
python test_api.py

# Logs / monitoring
tmux attach -t gw 

# Stopper
tmux kill-session -t gw

# Redémarrer
tmux kill-session -t gw 2>/dev/null; tmux new -s gw -d 'python -m uvicorn app:app --host 0.0.0.0 --port 8000'

# SQL
sqlite3 mistral.db "SELECT * FROM conversations;"

