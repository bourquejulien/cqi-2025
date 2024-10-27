# CQI 2025 - Programmation

## Configuration de l'environnement

```bash
python3 -m venv venv
source ./venv/bin.active
pip install -r requirements.txt
```

## Lançement du serveur de jeu
```bash
docker compose -f compose.test.yml up --build
```

## Lançement du serveur des tests
```bash
docker compose -f compose.base.yml -f compose.test.yml up --build
```
