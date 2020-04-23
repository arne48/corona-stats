import os
import time
import json
import urllib.request

SEC_PER_HR = 3600.0
DATA_FILE_NAME = 'data.xhr'


class ArcGisWrapper(object):
    def __init__(self, url, save_path='./', max_age_hrs=3):
        self.max_age_hrs = max_age_hrs
        data = self._get_xhr_from_link(url, save_path=save_path)
        self.__dict__ = json.loads(data, parse_int=self._parse_to_string, parse_float=self._parse_to_string)

    def get_features_grouped_by_name(self, selected_feature):
        ret = dict()
        for f in self.features:
            # Check if selected feature is already in dict if not adding it
            f = f['attributes']
            if f[selected_feature] not in ret:
                ret[f[selected_feature]] = list()
            ret[f[selected_feature]].append(f)
        return ret

    def get_fields(self):
        ret = list()
        for f in self.fields:
            ret.append(f['name'])
        return ret

    # GUI only needs strings and mixups from datasource might screw with sorting functions later
    def _parse_to_string(self, param):
        return str(param)

    def _read_file(self, raw_url):
        response = urllib.request.urlopen(raw_url)
        data = response.read()
        return data.decode('utf-8')

    def _is_file_cache_fresh(self, file_path, max_age):
        last_change = os.path.getmtime(file_path)
        return time.time() < max_age + last_change

    def _get_xhr_from_link(self, url, save_path='./'):
        file_path = save_path + DATA_FILE_NAME
        if os.path.isfile(file_path) and self._is_file_cache_fresh(file_path, SEC_PER_HR * self.max_age_hrs):
            body = ''
            with open(file_path, 'r') as f:
                body = f.read()
            f.close()
            # Prevent NoneType ending up as keys in our dicts
            return body.replace(':null,', ':"N.A.",')
        else:
            # Prevent NoneType ending up as keys in our dicts
            body = self._read_file(url).replace(':null,', ':"N.A.",')
            with open(file_path, 'w') as f:
                f.write(body)
            f.close()
            return body
