# Pré-CQI 2025 - Programmation

## Configuration de l'environnement

```bash
python3 -m venv venv
source ./venv/bin.active
pip install -r requirements.txt
```

## Exécution du serveur

En debug :
```bash
./app.py
```

En production :
```bash
./start.sh
# ou encore
docker compose up --build
```

## Déploiement

```bash
docker buildx build --push --platform linux/amd64,linux/arm64 -t brqu/latestoflatest:latest .
```
