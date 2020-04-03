import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,\
    QLineEdit, QLabel, QPushButton, QVBoxLayout, QRadioButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from map_api import return_map, toponym_to_ll


# constants
MAP_SIZE = 550, 450
SCREEN_SIZE = 810, 500


class MyWidget(QMainWindow, QApplication):
    def __init__(self):

        # переменные, определяющие текущее положение карты
        # масштаб - self.z
        # lonlat - долгота, широта
        # тип карты - map
        self.lonlat = [0, 0]
        self.z = 12
        self.map_type = 'map'

        # метки на карте
        self.tags = []

        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(*SCREEN_SIZE)

        # ввод соординат
        self.coordinates_search = QLineEdit(self)
        self.coordinates_search.resize(150, 20)
        self.coordinates_search.move(625, 50)

        self.csearsh_label = QLabel(self)
        self.csearsh_label.setText("• Поиск по \n(координатам/названию объекта):")
        self.csearsh_label.move(625, 20)
        self.csearsh_label.resize(self.csearsh_label.sizeHint())

        # кнопка подтверждения ввода
        self.submut_csearch = QPushButton(self)
        self.submut_csearch.setText("SUBMIT")
        self.submut_csearch.move(625, 80)
        self.submut_csearch.resize(75, 30)
        self.submut_csearch.clicked.connect(self.csearch)

        # тип карты (схема/спутник/гибрид)
        self.skl_rbutton = QRadioButton(self)
        self.skl_rbutton.move(625, 120)
        self.skl_rbutton.setText('тип "Схема"')
        self.skl_rbutton.setChecked(True)
        self.skl_rbutton.toggled.connect(self.map_type_changed)

        self.sat_rbutton = QRadioButton(self)
        self.sat_rbutton.move(625, 140)
        self.sat_rbutton.setText('тип "Спутник"')
        self.sat_rbutton.toggled.connect(self.map_type_changed)

        self.hybrid_rbutton = QRadioButton(self)
        self.hybrid_rbutton.move(625, 160)
        self.hybrid_rbutton.setText('тип "Гибрид"')
        self.hybrid_rbutton.toggled.connect(self.map_type_changed)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.skl_rbutton)
        self.verticalLayout.addWidget(self.sat_rbutton)
        self.verticalLayout.addWidget(self.hybrid_rbutton)

        # сброс меток поиска
        self.tags_clean = QPushButton(self)
        self.tags_clean.setText('delete tags')
        self.tags_clean.resize(self.tags_clean.sizeHint())
        self.tags_clean.move(625, 450)
        self.tags_clean.clicked.connect(self.tags_clean_function)

        # карта
        self.main_map = QLabel(self)
        self.main_map.move(30, 30)
        self.main_map.resize(*MAP_SIZE)

        # QPixmap для карты
        self.main_pixmap = QPixmap()
        self.update_map()

    def update_map(self, lonlat=None):
        if lonlat is None:
            ll = self.lonlat
        else:
            ll = lonlat

        data = return_map(*ll, self.z, self.map_type, self.tags, MAP_SIZE)
        if data is not None:
            self.main_pixmap.loadFromData(data)
            self.main_map.setPixmap(self.main_pixmap)
            return True
        return False
        # True - запрос выполнен, False - нет
        # Нужно для csearch (update lonlat or not)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp and self.z < 17:
            self.z += 1
            self.update_map()
        elif event.key() == Qt.Key_PageDown and self.z > 1:
            self.z -= 1
            self.update_map()

        # изменение долготы [-180; 180]
        elif event.key() in [Qt.Key_D, Qt.Key_A]:
            step = 360 / 2 ** (self.z - 1)
            # уменьшение или увеличение долготы
            k = 1 if event.key() == Qt.Key_D else -1

            # шаг
            self.lonlat[0] += k * step
            self.lonlat[0] = (self.lonlat[0] + 180) % 360 - 180
            self.update_map()

        # изменение широты [-90; 90]
        elif event.key() in [Qt.Key_W, Qt.Key_S]:
            step = 180 / 2 ** (self.z - 1)
            # уменьшение или увеличение широты
            k = 1 if event.key() == Qt.Key_W else -1

            # шаг
            self.lonlat[1] += k * step
            self.lonlat[1] = (self.lonlat[1] + 90) % 180 - 90
            self.update_map()

    def map_type_changed(self):
        if self.sat_rbutton.isChecked():
            self.map_type = "sat"
        elif self.skl_rbutton.isChecked():
            self.map_type = "map"
        elif self.hybrid_rbutton.isChecked():
            self.map_type = "sat,skl"
        self.update_map()

    def csearch(self):
        # поиск по координатам
        try:
            lon, lat = map(float, self.coordinates_search.text().split())
        # поиск по топониму
        except ValueError:
            response = toponym_to_ll(self.coordinates_search.text())
            # ничего не нашел
            if not response:
                return

            lon, lat = response
            self.tags.append(f'{lon},{lat}')

        if self.update_map(lonlat=[lon, lat]):
            self.lonlat = [lon, lat]
        else:
            pass

    def tags_clean_function(self):
        self.tags.clear()
        self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
