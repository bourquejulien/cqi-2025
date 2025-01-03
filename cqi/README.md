# CQI 2025 - Programmation

### Configuration de l'environnement (``bot``, ``game_runner``, ``game_server``)

```bash
python3 -m venv venv
source ./venv/bin.active
pip install -r requirements.txt
```

## ``Game server`` et ``Bots``

### Lancement du serveur de jeu

```bash
docker compose -f compose.base.yml up --build
```

### Lancement du serveur des tests

```bash
docker compose -f compose.base.yml -f compose.test.yml up --build
```

## Terraform

Prérequis :
- Être connecté à l'aide d'aws-cli.
- ``make apply`` pour déployer / modifier.
- ``make destroy`` pour détruire l'infra.

## Public

Scripts et info à placer dans un repo public séparé pour aider les équipes.

## Scripts

Scripts à usage interne permettant d'extraire l'``internal_key``, lister les logins des équipes, modifier les réglages du ``main_server`` (local et distant), pousser des images de tests sur tous les ECR.

## Main Server
Se lance localement, cependant une base de donnée Postgres doit également être lancée. Se connectera automatiquement l'instance RDS lorsque déployé. L'instance RDS n'est pas accessible hors AWS.

À exécuter à partir de ``/main_server`` :
```bash
docker compose  -f compose.postgres.yml up -d
```

Pour lancer le serveur :
```bash
go run .
```

## Game Runner

Lance automatiquement les images des équipes en tirant sur le ``main_server`` (``/internal/pop``). Le maximum de parties lancées simultanément est retourné par le ``main_server``.

Se connecte au ``main_server`` local lorsque lancé localement.

## Web Server

Se connecte au serveur local lorsque lancé localement (le ``main_server`` doit être lancé). Déployé automatiquement dans pages.

```bash
npm install
npm run dev
```
