import requests
import pandas as pd

# Insert your own client ID here
client_id = '13bfc82c-43d6-4d78-bee6-c4bfd1160ca8'
secret = '0536adf1-c67c-458f-876f-83f10f31acfb'

endpoint = 'https://frost.met.no/observations/v0.jsonld'
parameters = {
    'sources': 'SN18700,SN90450',
    'elements': 'air_temperature P1D,precipitation_amount P1D,wind_speed P1D',
    'referencetime': '2010-04-01/2010-04-03',
}
# Issue an HTTP GET request
r = requests.get(endpoint, parameters, auth=(client_id,''))
# Extract JSON data
json = r.json()

if r.status_code == 200:
    data = json['data']
    print('Data retrieved from frost.met.no!')
else:
    print('Error! Returned status code %s' % r.status_code)
    print('Message: %s' % json['error']['message'])
    print('Reason: %s' % json['error']['reason'])

df = pd.DataFrame()
for i in range(len(data)):
    row = pd.DataFrame(data[i]['observations'])
    row['referenceTime'] = data[i]['referenceTime']
    row['sourceId'] = data[i]['sourceId']
    df = df.append(row)

df = df.reset_index()

print(df.head())