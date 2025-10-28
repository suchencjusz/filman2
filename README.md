![Black format](https://img.shields.io/badge/code%20style-black-000000.svg) ![GitHub License](https://img.shields.io/github/license/suchencjusz/filman2) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/suchencjusz/filman2) ![GitHub Action Docker](https://img.shields.io/github/actions/workflow/status/suchencjusz/filman2/docker-build.yml)  [![Codacy Badge](https://app.codacy.com/project/badge/Grade/804ea9aa4ef147688ce59a0ab4342a09)](https://app.codacy.com/gh/suchencjusz/filman2/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

# Funkcje

🎬 Funkcje które są dostępne:
- Informowanie o ocenach znajomych (seriale/filmy)
- Losowanie filmu do obejrzenia (z puli znajomych)

<!-- [![Bot discord](https://raw.githubusercontent.com/suchencjusz/filman2/refs/heads/main/readme/drive.png)](https://discord.com/oauth2/authorize?client_id=1182371658347065394&scope=bot&permissions=2147929152) -->

🚀 Planowane funkcje:
- Statyski (coś na zasadzie last.fm dla spotify),
- Sugerowanie filmu do obejrzenia (z puli znajomych, na podstawie ocen),
- Ocena gustu przez AI,

❓ Lista dostępnych komend i opcji jest dostępna pod komendą /help:
- /help filmweb
- /help configure

🤖 Przykładowa konfiguracja
- /configure channel text_channel:#ogólny -
Konfiguracja kanału z powiadomieniami
- /filmweb me filmweb_username: -
Uruchomienie śledzenie użytkownika

# Użycie

## 1. Zaproś bota
[Link z zaproszeniem bota na serwer discord](https://discord.com/oauth2/authorize?client_id=1182371658347065394&scope=bot&permissions=2147929152)

## 2. Hostuj u siebie (docker)
(todo)

Docker compose [docker-compose.yml](https://github.com/suchencjusz/filman2/blob/main/docker-compose.yml)

## 3. Uruchomienie Celery Worker

Projekt używa Celery z Redis jako brokerem do przetwarzania zadań w tle (np. scrapowania danych Filmweb).

### Wymagania
- Redis (domyślnie: `redis://localhost:6379/0`)
- Zmienne środowiskowe (opcjonalnie):
  - `REDIS_URL` - adres URL serwera Redis

### Uruchomienie workera

```bash
celery -A filman_server.celery_app worker -l info
```

Opcjonalne parametry:
- `-l debug` - bardziej szczegółowe logi
- `-l warning` - tylko ostrzeżenia i błędy
- `--concurrency=4` - liczba równoległych workerów (domyślnie: liczba CPU)

### Uruchomienie z własnym Redis

```bash
export REDIS_URL=redis://your-redis-host:6379/0
celery -A filman_server.celery_app worker -l info
```
