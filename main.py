import requests
import tensorflow


resp = requests.get('https://api.tdameritrade.com/v1/marketdata/$DJI/movers')
if resp.status_code != 200:
    # This means something went wrong.
    raise ApiError('GET /tasks/ {}'.format(resp.status_code))
for todo_item in resp.json():
    print('{} {}'.format(todo_item['id'], todo_item['summary']))