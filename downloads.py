import requests
import config

dataset_url = config.DATASET_ADRESSES_URL
r = requests.get(dataset_url, stream=True)
with open("adresses-france.csv.gz",'wb') as f:
    f.write(r.content)