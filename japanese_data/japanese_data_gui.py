import os
import time
import json
import urllib.request

SEC_PER_HR = 3600.0
MAX_AGE_HRS = 3
DATA_URL = 'https://services8.arcgis.com/JdxivnCyd1rvJTrY/arcgis/rest/services/v2_covid19_list_csv/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*&orderByFields=Date%20desc%2CNo%20desc&resultOffset=0&resultRecordCount=32000&resultType=standard&cacheHint=true'


class Dataset(object):
    def __init__(self, data):
        self.__dict__ = json.loads(data)

    def get_cases_by_feature(self, selected_feature):
        ret = dict()
        for f in self.features:
            # Check if selected feature is already in dict if not add it
            f = f['attributes']
            if f[selected_feature] not in ret:
                ret[f[selected_feature]] = list()
            ret[f[selected_feature]].append(f)
        return ret


def read_file(raw_url):
    response = urllib.request.urlopen(raw_url)
    data = response.read()
    return data.decode('utf-8')


def file_cache_fresh(file_path, max_age):
    last_change = os.path.getmtime(file_path)
    return time.time() < max_age + last_change


def get_xhr_from_link(url, save_path='./'):
    file_path = save_path + 'data.xhr'
    if os.path.isfile(file_path) and file_cache_fresh(file_path, SEC_PER_HR * MAX_AGE_HRS):
        body = ''
        with open(file_path, 'r') as f:
            body = f.read()
        f.close()
        return body
    else:
        body = read_file(url)
        with open(file_path, 'w') as f:
            f.write(body)
        f.close()
        return body


xhr_data = get_xhr_from_link(DATA_URL)
dataset = Dataset(xhr_data)
sorted_case_data = dataset.get_cases_by_feature('Prefecture')
pass
