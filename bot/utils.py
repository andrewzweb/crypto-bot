from io import BytesIO
import gzip
import json


def convert_data(received_raw_data):
    clean_data = []
    try:
        buff = BytesIO(received_raw_data)
        f = gzip.GzipFile(fileobj=buff)
        res = f.read().decode('utf-8')
        clean_data = json.loads(res)
    except:
        print('Error convert data')

    return clean_data
