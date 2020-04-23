import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QComboBox, QStyleFactory, QLabel, QHBoxLayout, QGridLayout,
                             QCheckBox, QGroupBox, QTreeWidget, QBoxLayout, QTreeWidgetItem)
from arcgis_wrapper import ArcGisWrapper

DATA_URL = 'https://services8.arcgis.com/JdxivnCyd1rvJTrY/arcgis/rest/services/v2_covid19_list_csv/FeatureServer/0/'\
           'query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&'\
           'outFields=*&orderByFields=Date%20desc%2CNo%20desc&resultOffset=0&'\
           'resultRecordCount=32000&resultType=standard&cacheHint=true'


class JapanCoronaInfoWidget(QDialog):
    def __init__(self, parent=None):
        super(JapanCoronaInfoWidget, self).__init__(parent)

        self.dataset = ArcGisWrapper(DATA_URL)
        self.feature_names = self.dataset.get_fields()

        self.feature_checkboxes = dict()
        self._create_feature_selection_checkbox_group()
        self.data_treeview = QTreeWidget()
        self._update_treeview('Prefecture_Ja')

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
        self.setWindowTitle('Case Information for Japan')

    def _create_feature_selection_checkbox_group(self):
        self.feature_selection_groupbox = QGroupBox('Feature selection')
        self.feature_selection_groupbox.setCheckable(True)
        self.feature_selection_groupbox.setChecked(False)

        layout = QHBoxLayout()
        for f in self.feature_names:
            t = QCheckBox('{}'.format(f))
            t.setChecked(True)
            self.feature_checkboxes[f] = t
            layout.addWidget(t)
        self.feature_selection_groupbox.setLayout(layout)

    def _main_feature_changed(self, feature_name):
        self._update_treeview(str(feature_name))

    def _update_treeview(self, root_feature):
        case_data = self.dataset.get_features_grouped_by_name(root_feature)
        headers = self.feature_names.copy()
        headers.insert(0, root_feature)

        self.data_treeview.clear()
        self.data_treeview.setHeaderLabels(headers)
        for d in sorted(case_data):
            tree_root = QTreeWidgetItem(self.data_treeview)
            tree_root.setText(0, '{} ({})'.format(d, len(case_data[d])))
            for case in case_data[d]:
                sub_item = QTreeWidgetItem(tree_root)
                sub_item.setText(0, str(d))
                for column, case_item in enumerate(case):
                    sub_item.setText(column + 1, str(case[case_item]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gallery = JapanCoronaInfoWidget()
    gallery.show()
    sys.exit(app.exec_())
