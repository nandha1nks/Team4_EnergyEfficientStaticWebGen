import requests
import os
def uploadVideo(path):
    if not os.path.exists(path):
        return '#'
    with open(path, 'rb') as f:
        payload = {'path': str(path)}
        r = requests.post('http://localhost:3000/upload', data=payload, files={'video': f})
        if r.status_code == 200:
            res = r.json()
            return res['link']
        else:
            return "#"
