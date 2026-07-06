# 🏠 AI Home Server

Un serveur léger pour gérer des interactions intelligentes à la maison. ⚡

---

## 🚀 **Démarrage rapide**

### 1️⃣ Activer l'environnement virtuel
```bash
source .ai-home/bin/activate
```

### 2️⃣ Lancer le serveur
```bash
tmux new -s gw -d 'python -m uvicorn app:app --host 0.0.0.0 --port 8000'
```
> Le serveur sera accessible sur `http://localhost:8000`.

---

## 🔍 **Vérifications et tests**

### Vérifier que le serveur est en cours d'exécution
```bash
tmux ls
ss -tlnp | grep 8000
```

### Exécuter les tests
```bash
python test_api.py
```

---

## 📊 **Logs et monitoring**
Pour surveiller les logs en temps réel :
```bash
tmux attach -t gw
```

---

## 🛑 **Arrêter le serveur**
```bash
tmux kill-session -t gw
```

---

## 🔄 **Redémarrer le serveur**
```bash
tmux kill-session -t gw 2>/dev/null; tmux new -s gw -d 'python -m uvicorn app:app --host 0.0.0.0 --port 8000'
```

---

## 🗃️ **Base de données (SQLite)**
Pour consulter les conversations enregistrées :
```bash
sqlite3 history_chat.db "SELECT * FROM conversations;"
```
