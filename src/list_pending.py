import requests
import pprint

photos = requests.get('http://localhost:3000/photos/pending').json()

pprint.pprint(photos)
