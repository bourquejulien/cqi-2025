## Bot

**Réalisé par Marc-Antoine Manningham**

## Déploiement

```bash
docker buildx build --push --platform linux/amd64,linux/arm64 -t brqu/test:latest .
```
