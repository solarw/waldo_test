import requests
import pprint

photos = requests.get('http://localhost:3000/photos/pending').json()

uuids = [i['uuid'] for i in photos]

requests.post(
    'http://localhost:3000/photos/process',
    json={
        'uuids': uuids
    }
)

print('uuids processed: ')
pprint.pprint(uuids)
