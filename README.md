![GitHub License](https://img.shields.io/github/license/suchencjusz/filman2) ![GitHub commit activity](https://img.shields.io/github/commit-activity/m/suchencjusz/filman2) ![GitHub Action Docker](https://img.shields.io/github/actions/workflow/status/suchencjusz/filman2/docker-build.yml)

[Link z zaproszeniem bota na serwer](https://discord.com/oauth2/authorize?client_id=1182371658347065394&scope=bot&permissions=2147929152)


# Funkcje

🎬 Funkcje które są dostępne:
- Informowanie o ocenach znajomych (na ten moment tylko filmy)

[![Bot discord](https://raw.githubusercontent.com/suchencjusz/filman2/refs/heads/main/readme/drive.png)](https://discord.com/oauth2/authorize?client_id=1182371658347065394&scope=bot&permissions=2147929152)

🚀 Planowane funkcje:
- Statyski (coś na zasadzie last.fm dla spotify),
- Losowanie filmu do obejrzenia (z puli znajomych),
- Sugerowanie filmu do obejrzenia (z puli znajomych, na podstawie ocen),
- Ocena gustu przez AI,

❓ Lista dostępnych komend i opcji jest dostępna pod komendą /help:
- /help filmweb
- /help configure

🤖 Przykładowa konfiguracja
- /configure channel text_channel:#ogólny
Konfiguracja kanału z powiadomieniami
- /filmweb me filmweb_username:
Uruchomienie śledzenie użytkownika

# Dev

```
version: "3.6"

services:
  filman-server:
    container_name: filman-server
    image: suchencjusz/filman-server:main
    ports:
      - "8000:8000"

    environment:
      - MYSQL_HOST=domain
      - MYSQL_USER=user
      - MYSQL_PASSWORD=password
      - MYSQL_DATABASE=db
    restart: unless-stopped
    extra_hosts:
      - "host.docker.internal:host-gateway"

  filman-discord:
    depends_on:
      - filman-server
    container_name: filman-discord
    image: suchencjusz/filman-discord:main

    environment:
      - DISCORD_TOKEN=******
    restart: unless-stopped

  filman-crawler:
    depends_on:
      - filman-server
    container_name: filman-crawler
    image: suchencjusz/filman-crawler:main

    environment:
      - CORE_ENDPOINT=http://filman-server:8000
    restart: unless-stopped
```
