def rename_countries(data_frame, change_dict):
    for old_name in change_dict:
        data_frame.rename(index={old_name: change_dict[old_name]}, inplace=True)
        df_new = data_frame.loc[data_frame['Country/Region'] == old_name]
        df_new['Country/Region'] = change_dict[old_name]
        data_frame.update(df_new)
    return data_frame


def sanitize_data(data_in):
    # Remove non important columns
    data_out = data_in.sort_values(by=['Country/Region'], ignore_index=True)
    data_out = data_out.drop(['Province/State', 'Lat', 'Long'], 1)

    # Merge by 'Country/Region'
    header = list(data_out.columns.values)
    aggregation_fun = {header[0]: 'first'}
    aggregation_fun.update({itm: 'sum' for itm in header[1:]})
    data_out = data_out.groupby(data_out['Country/Region']).aggregate(aggregation_fun)

    # Fix Country names
    country_mapping = {'Taiwan*': 'Taiwan',
                       'Korea, South': 'South Korea',
                       'US': 'USA'}
    data_out = rename_countries(data_out, country_mapping)

    return data_out, header[1:]


def get_data_of_country(data, country):
    return data.loc[data['Country/Region'] == country].to_numpy()[0][1:]


def get_names_of_countries(data):
    return data.to_numpy()[:, 0]
