import string
import requests
import gzip
import shutil
import config


def download_file(file_url: string, filename: string) -> None:
    r = requests.get(file_url, stream=True)
    with open(filename,'wb') as f:
        f.write(r.content)

def convert_gz_to_csv(gz_filename: string, csv_filename: string) -> None:
    with gzip.open(gz_filename, 'rb') as f_in:
        with open(csv_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

if __name__ == '__main__':
    dataset_url = config.DATASET_ADRESSES_URL
    gz_filename = 'adresses-france.csv.gz'
    csv_filename = 'adresses-france.csv'

    download_file(dataset_url, gz_filename)
    convert_gz_to_csv(gz_filename, csv_filename)