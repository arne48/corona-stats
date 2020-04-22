from arcgis_wrapper import ArcGisWrapper

DATA_URL = 'https://services8.arcgis.com/JdxivnCyd1rvJTrY/arcgis/rest/services/v2_covid19_list_csv/FeatureServer/0/'\
           'query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&'\
           'outFields=*&orderByFields=Date%20desc%2CNo%20desc&resultOffset=0&'\
           'resultRecordCount=32000&resultType=standard&cacheHint=true'

dataset = ArcGisWrapper(DATA_URL)
sorted_case_data = dataset.get_features_grouped_by_name('Prefecture')
pass
