import os
import time
import logging
import urllib.request

SEC_PER_HR = 3600.0
MAX_AGE_HRS = 3


def read_file(raw_url):
    response = urllib.request.urlopen(raw_url)
    data = response.read()
    return data.decode('utf-8')


def file_cache_fresh(file_path, max_age):
    last_change = os.path.getmtime(file_path)
    return time.time() < max_age + last_change


def get_file_from_link(url, save_path='./'):
    raw_url = url.replace('https://github.com', 'https://raw.githubusercontent.com').replace('/blob', '')
    file_path = save_path + raw_url.rsplit('/', 1)[-1]
    if os.path.isfile(file_path) and file_cache_fresh(file_path, SEC_PER_HR * MAX_AGE_HRS):
        logging.info('No need to download files')
        pass
    else:
        logging.info('Downloading File')
        body = read_file(raw_url)
        with open(file_path, 'w') as f:
            f.write(body)
        f.close()
    return file_path
