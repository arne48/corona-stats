import sys
import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QComboBox, QLabel, QHBoxLayout, QGridLayout,
                             QCheckBox, QGroupBox, QTreeWidget, QTreeWidgetItem)
from arcgis_wrapper import ArcGISWrapper

DATA_URL = 'https://services8.arcgis.com/JdxivnCyd1rvJTrY/arcgis/rest/services/v2_covid19_list_csv/FeatureServer/0/'\
           'query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&'\
           'outFields=*&orderByFields=Date%20desc%2CNo%20desc&resultOffset=0&'\
           'resultRecordCount=32000&resultType=standard&cacheHint=true'


class JapanCoronaInfoWidget(QDialog):
    def __init__(self, data_url, parent=None, window_title='Default'):
        super(JapanCoronaInfoWidget, self).__init__(parent)

        self.dataset = ArcGISWrapper(data_url)
        self._adjust_attributes()
        self.feature_names = self.dataset.get_fields()
        self.sorting_feature_name = self.feature_names[0]

        self.feature_checkboxes = dict()
        self._create_feature_selection_checkbox_group()
        self._connect_feature_selection_checkboxes()
        self.data_treeview = QTreeWidget()
        self._update_treeview()

        sort_combo_box = QComboBox()
        sort_combo_box.addItems(self.feature_names)

        sort_label = QLabel('&Sort by:')
        sort_label.setBuddy(sort_combo_box)

        top_layout = QHBoxLayout()
        top_layout.addWidget(sort_label)
        top_layout.addWidget(sort_combo_box)

        main_layout = QGridLayout()
        main_layout.addLayout(top_layout, 0, 0)
        main_layout.addWidget(self.feature_selection_groupbox, 1, 0)
        main_layout.addWidget(self.data_treeview, 2, 0)

        sort_combo_box.activated[str].connect(self._main_feature_changed)

        self.setLayout(main_layout)
        self.setWindowTitle(window_title)

    def _adjust_attributes(self):
        for f in self.dataset.features:
            j_date = f['attributes']['Date']
            if j_date != 'N.A.':
                # Cut first 10 characters from json date to allow epoch conversion
                date_str = datetime.datetime.fromtimestamp(int(j_date[:10])).strftime('%x')
                f['attributes']['Date'] = date_str

    def _create_feature_selection_checkbox_group(self):
        self.feature_selection_groupbox = QGroupBox('Feature selection')
        self.feature_selection_groupbox.setCheckable(False)
        # self.feature_selection_groupbox.setChecked(False)

        layout = QHBoxLayout()
        for f in self.feature_names:
            t = QCheckBox('{}'.format(f))
            t.setChecked(True)
            self.feature_checkboxes[f] = {'handle': t, 'enabled': True}
            layout.addWidget(t)
        self.feature_selection_groupbox.setLayout(layout)

    def _update_checkbox_states(self):
        for cb in self.feature_checkboxes:
            if self.feature_checkboxes[cb]['handle'].checkState() == Qt.Checked:
                self.feature_checkboxes[cb]['enabled'] = True
            else:
                self.feature_checkboxes[cb]['enabled'] = False
        self._update_treeview()

    def _connect_feature_selection_checkboxes(self):
        for cb in self.feature_checkboxes:
            self.feature_checkboxes[cb]['handle'].stateChanged.connect(self._update_checkbox_states)

    def _main_feature_changed(self, feature_name):
        self.sorting_feature_name = feature_name
        self._update_treeview()

    def _create_treeview_headers(self, root_feature):
        self.data_treeview.clear()
        headers = self.feature_names.copy()

        # FIXME
        test_headers = headers.copy()
        for n, feature_name in enumerate(test_headers):
            # If column is disabled or sorting feature remove the column from header
            if self.feature_checkboxes[feature_name]['enabled'] is False:
                test_headers.pop(n)

        headers.insert(0, root_feature)
        self.data_treeview.setHeaderLabels(headers)

    def _fill_treeview(self, case_data):
        for d in sorted(case_data):
            tree_root = QTreeWidgetItem(self.data_treeview)
            tree_root.setText(0, '{} ({})'.format(d, len(case_data[d])))
            for case in case_data[d]:
                sub_item = QTreeWidgetItem(tree_root)
                sub_item.setText(0, str(d))
                # FIXME
                # offset = 0
                for column, case_item in enumerate(case):
                    sub_item.setText(column + 1, str(case[case_item]))
                    # FIXME
                    # if self.feature_checkboxes[case_item]['enabled'] is True:
                    #     sub_item.setText(column + 1 - offset, str(case[case_item]))
                    # else:
                    #     offset = offset + 1

    def _update_treeview(self):
        case_data = self.dataset.get_features_grouped_by_name(self.sorting_feature_name)
        self._create_treeview_headers(self.sorting_feature_name)
        self._fill_treeview(case_data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gallery = JapanCoronaInfoWidget(DATA_URL, window_title='Case Information for Japan')
    gallery.show()
    sys.exit(app.exec_())
