import requests

url = "http://localhost:8001/filmweb/add/movie"  # replace with your actual server URL
data = {
    "id": 123  # replace with your actual movie ID
}
response = requests.post(url, json=data)

print(response.json())