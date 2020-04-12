import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QLineEdit, QLabel, QPushButton, QVBoxLayout, QRadioButton
from PyQt5.QtWidgets import QPlainTextEdit, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from map_api import return_map, toponym_info


# constants
MAP_SIZE = 550, 450
SCREEN_SIZE = 810, 500


class MyWidget(QMainWindow):
    def __init__(self):

        # переменные, определяющие текущее положение карты
        # масштаб - self.z
        # lonlat - долгота, широта
        # тип карты - map
        self.lonlat = [0, 0]
        self.z = 12
        self.map_type = 'map'

        self.address = ''

        # метки на карте
        self.tag = ''
    
        # ответ Я.Карт
        self.response = None

        # Индекс
        self.index = 'Отс.'

        # Подставлять ли индекс
        self.is_index = False

        super().__init__()
        self.initUI()

    def initUI(self):
        self.resize(*SCREEN_SIZE)
        self.setMaximumSize(*SCREEN_SIZE)
        self.setMinimumSize(*SCREEN_SIZE)

        # ввод соординат
        self.coordinates_search = QLineEdit(self)
        self.coordinates_search.resize(165, 20)
        self.coordinates_search.move(625, 85)

        self.csearsh_label = QLabel(self)
        self.csearsh_label.setText("• Поиск по \n(координатам/названию\nобъекта):")
        self.csearsh_label.move(625, 30)
        self.csearsh_label.resize(self.csearsh_label.sizeHint())

        # кнопка подтверждения ввода
        self.submit_csearch = QPushButton(self)
        self.submit_csearch.setText("SUBMIT")
        self.submit_csearch.move(625, 110)
        self.submit_csearch.resize(75, 30)
        self.submit_csearch.clicked.connect(self.csearch)

        # тип карты (схема/спутник/гибрид)
        self.skl_rbutton = QRadioButton(self)
        self.skl_rbutton.move(625, 150)
        self.skl_rbutton.setText('тип "Схема"')
        self.skl_rbutton.setChecked(True)
        self.skl_rbutton.resize(self.skl_rbutton.sizeHint())
        self.skl_rbutton.toggled.connect(self.map_type_changed)

        self.sat_rbutton = QRadioButton(self)
        self.sat_rbutton.move(625, 170)
        self.sat_rbutton.setText('тип "Спутник"')
        self.sat_rbutton.resize(self.sat_rbutton.sizeHint())
        self.sat_rbutton.toggled.connect(self.map_type_changed)

        self.hybrid_rbutton = QRadioButton(self)
        self.hybrid_rbutton.move(625, 190)
        self.hybrid_rbutton.setText('тип "Гибрид"')
        self.hybrid_rbutton.resize(self.hybrid_rbutton.sizeHint())
        self.hybrid_rbutton.toggled.connect(self.map_type_changed)

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.addWidget(self.skl_rbutton)
        self.verticalLayout.addWidget(self.sat_rbutton)
        self.verticalLayout.addWidget(self.hybrid_rbutton)

        # сброс меток поиска
        self.tags_clean = QPushButton(self)
        self.tags_clean.setText('Сброс')
        self.tags_clean.resize(self.tags_clean.sizeHint())
        self.tags_clean.move(625, 470)
        self.tags_clean.clicked.connect(self.tags_clean_function)

        # Поле вывода полного адреса объекта
        self.address_field = QPlainTextEdit(self)
        self.address_field.setReadOnly(True)
        self.address_field.setMaximumWidth(165)
        self.address_field.setMaximumHeight(205)
        self.address_field.resize(self.address_field.sizeHint())
        self.address_field.move(625, 265)
        self.address_label = QLabel(self)
        self.address_label.setText('Полный адрес объекта:')
        self.address_label.resize(self.address_label.sizeHint())
        self.address_label.move(625, 220)
        self.index_checkbox = QCheckBox(self)
        self.index_checkbox.setText('Вывод индекса')
        self.index_checkbox.resize(self.index_checkbox.sizeHint())
        self.index_checkbox.stateChanged.connect(self.revert_index_state)
        self.index_checkbox.move(625, 240)

        # карта
        self.main_map = QLabel(self)
        self.main_map.move(30, 30)
        self.main_map.resize(*MAP_SIZE)

        # QPixmap для карты
        self.main_pixmap = QPixmap()
        self.update_map()
    
    def do_address(self, address, index):
        return ', '.join(filter(bool, [address,
                (f'Индекс: {index}' if self.is_index else '')])) + '.'
    
    def revert_index_state(self):
        self.is_index = bool(1 - self.is_index)
        text = self.do_address(self.address, self.index)
        self.address_field.setPlainText(text)

    def update_map(self, lonlat=None, address='', index=None, tag=None):
        if lonlat is None:
            lonlat = self.lonlat[:]
        
        if not address:
            address = self.address
        
        if index is None:
            index = self.index
        
        if not tag:
            tag = self.tag

        data = return_map(*lonlat, self.z, self.map_type, tag, MAP_SIZE)
        if data is not None:
            self.main_pixmap.loadFromData(data)
            self.main_map.setPixmap(self.main_pixmap)
            self.address_field.setPlainText(self.do_address(self.address, self.index))
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
        if all([i.isdecimal() for i in self.coordinates_search.text().split()]):
            lon, lat = map(float, self.coordinates_search.text().split())
        # поиск по топониму
        else:
            response = toponym_info(self.coordinates_search.text())
            # ничего не нашел
            if not response:
                return
            lon, lat = response['pos']
            address = response['address']
            index = response['index']
            tag = f'{lon},{lat}'

        if self.update_map(lonlat=[lon, lat], address=address, index=index, tag=tag):
            self.lonlat = [lon, lat]
            self.address = address
            self.index = index
            self.tag = tag
            self.main_map.setFocus()

    def tags_clean_function(self):
        self.tag = ''
        self.address = ''
        self.index = 'Отс.'
        self.update_map()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
