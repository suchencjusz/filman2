import requests

headers = {
    'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoxLCJpZCI6IjExODIzNzE2NTgzNDcwNjUzOTQiLCJpYXQiOjE3MDIzOTk1NjJ9.-7jLpvYAKHXagsJt5ADmGHGvt4Qtw5i87J7B_slda3w'
}

body_commands = [
    {
        "name": "configure channel",
        "description": "Ustawia kanał z powiadomieniami",
        "type": 1
    },
    {
        "name": "help",
        "description": "Pomoc",
        "type": 1
    },
    {
        "name": "tracker me",
        "description": "Monitoruje konto filmweb",
    },
    {
        "name": "tracker cancel",
        "description": "Anuluje monitorowanie konta filmweb i usuwa dane z bazy danych",
    },
    {
        "name": "tracker stop",
        "description": "Anuluje wysyłanie powiadomień na danym serwerze",
    },
    {
        "name": "tracker here",
        "description": "Dopisuje użytkownika do listy powiadomień na danym serwerze",
    },
    {
        "name": "info",
        "description": "Informacje o bocie",
    }
]

r = requests.post('https://discordbotlist.com/api/v1/bots/filman/commands', headers=headers, json=body_commands)

print(r.status_code)