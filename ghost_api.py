import requests # pip install requests
import jwt	# pip install pyjwt
from datetime import datetime as date

# Admin API key goes here
key = '60c71d772cc77223dcb90dc8:392420d07ba4c207d530275078de9630a17b0319e98843f50657fa77a429ce5e'

# Split the key into ID and SECRET
id, secret = key.split(':')

# Prepare header and payload
iat = int(date.now().timestamp())

header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
payload = {
    'iat': iat,
    'exp': iat + 5 * 60,
    'aud': '/v3/admin/'
}

# Create the token (including decoding secret)
token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

# Make an authenticated request to create a post
url = 'http://localhost:2368/ghost/api/v3/admin/posts/slug/welcome/?formats=html'
headers = {'Authorization': 'Ghost {}'.format(token)}
r = requests.get(url, headers=headers)

print(r.json()['posts'][0]['html'])