from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QHBoxLayout, QLabel, \
    QPushButton, QInputDialog, QLineEdit

from PIL.ImageQt import ImageQt


class ListWidget(QWidget):
    # Signal for other threads to use to add to list
    add_list_requested = pyqtSignal(str, str, 'PyQt_PyObject')
    LIST_MAX_LENGTH = 100
    
    def __init__(self, controller):
        super(ListWidget, self).__init__()
        self.controller = controller
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        self.add_list_requested.connect(self.add_live_tab)
        self._setup_tabs()

        self._people_dict = {}
        self._people_dict_pos = 0

    def _setup_tabs(self):
        self.tabs = QTabWidget()
        self.tab1_live = QListWidget()
        self.tab2_total = QListWidget()

        self.tabs.addTab(self.tab1_live, "Live Results")
        self.tabs.addTab(self.tab2_total, "People Identified")

        self.layout.addWidget(self.tabs)

    def add_live_tab(self, name, confidence, image_PIL):
        new_data = self.LiveResultBlock(name, confidence, image_PIL, self.controller)
        list_item = QListWidgetItem()
        
        self.tab1_live.addItem(list_item)
        self.tab1_live.setItemWidget(list_item, new_data)
        list_item.setSizeHint(new_data.sizeHint())
        self.controller.get_logger_gui().info("Adding data to live tab")
        
        self._add_to_total(name, image_PIL)
        self._remove_over_limit()

        self._edge_case()

    # Edge case of some buttons not being enabled due to concurrency issues
    def _edge_case(self):
        person_result_block = self.tab1_live.item(0)

        if self.tab1_live.itemWidget(person_result_block).get_button_status():
            self.enable_all_modify_button()
        
    
    def _remove_over_limit(self):
        self.controller.get_logger_gui().info("Removing list items if over limit")

        while self.tab1_live.count() > self.LIST_MAX_LENGTH:
            self.tab1_live.takeItem(0)

    def _add_to_total(self, name, image_PIL):
        if name in self._people_dict:
            index = self._people_dict[name]
            person_result_block = self.tab2_total.item(index)

            self.tab2_total.itemWidget(person_result_block).set_image(image_PIL)
            return

        new_data = self.TotalResultBlock(name, image_PIL, self.controller)
        list_item = QListWidgetItem()
        
        self.tab2_total.addItem(list_item)
        self.tab2_total.setItemWidget(list_item, new_data)

        self._people_dict[name] = self._people_dict_pos
        self._people_dict_pos = self._people_dict_pos + 1

        list_item.setSizeHint(new_data.sizeHint())

    def get_live_list_widget(self):
        return self.tab1_live

    def get_total_list_widget(self):
        return self.tab2_total

    def reset_total_list_dict(self):
        self._people_dict = {}
        self._people_dict_pos = 0

    def enable_all_modify_button(self):
        for i in range(self.tab1_live.count()):
            person_result_block = self.tab1_live.item(i)
            self.tab1_live.itemWidget(person_result_block).enable_button()



    class LiveResultBlock(QWidget):
        WIDTH = 400
        HEIGHT = 120

        def __init__(self, name, confidence, image_pil, controller):
            super(ListWidget.LiveResultBlock, self).__init__()
            self.controller = controller
            self.confidence = confidence
            self.name = name
            self.image_pil = image_pil
            self.image = None
            self._setup_block()

        def _setup_block(self):
            self.layout = QHBoxLayout()
            self.image_frame = QLabel(self)

            from PIL.ImageQt import ImageQt
            qim = ImageQt(self.image_pil)

            self.image = QPixmap.fromImage(qim)

            self.image_frame.setPixmap(self.image.scaled(self.WIDTH, self.HEIGHT, Qt.KeepAspectRatio))
            self.layout.addWidget(self.image_frame)

            self._setup_data()
            self._setup_buttons()

            self.setLayout(self.layout)

        def _setup_data(self):
            self.data_section = QWidget()
            self.data_section.setStyleSheet("border:1px solid rgb(0, 0, 0);")
            self.data_layout = QVBoxLayout()
            self.data_section.setLayout(self.data_layout)

            self.text_name = QLabel()
            self.text_name.setText("Name: " + self.name)
            text_confidence = QLabel()
            text_confidence.setText("Confidence: " + self.confidence)

            self.data_layout.addWidget(self.text_name)
            self.data_layout.addWidget(text_confidence)

            self.layout.addWidget(self.data_section)

        def _setup_buttons(self):
            self.button_section = QWidget()
            self.button_layout = QVBoxLayout()
            self.button_section.setLayout(self.button_layout)

            self.modify_button = QPushButton(self.button_section)
            self.modify_button.setDisabled(True)
            self.modify_button.setText("MODIFY")
            self.modify_button.clicked.connect(self._modify_label)

            self.button_layout.addWidget(self.modify_button)

            self.layout.addWidget(self.button_section)

        def _modify_label(self):
            """ Add new label of face to db"""
            new_name, ok_pressed = QInputDialog.getText(self, "New Face Label", "Name:", QLineEdit.Normal, self.name)

            if ok_pressed:
                self.text_name.setText("Name: " + new_name)
                self.controller.add_face_db(new_name, self.image_pil)
                self.controller.update_rec_model()

        def enable_button(self):
            self.modify_button.setDisabled(False)

        def get_button_status(self):
            return self.modify_button.isEnabled()


    class TotalResultBlock(QWidget):
        WIDTH = 400
        HEIGHT = 120

        def __init__(self, name, image_pil, controller):
            super(ListWidget.TotalResultBlock, self).__init__()
            self.controller = controller
            self.name = name
            self.image = image_pil
            self._setup_block()

        def _setup_block(self):
            self.layout = QHBoxLayout()
            self.image_frame = QLabel(self)

            self.set_image(self.image)

            self.layout.addWidget(self.image_frame)

            self._setup_data()

            self.setLayout(self.layout)

        def _setup_data(self):
            self.data_section = QWidget()
            self.data_section.setStyleSheet("border:1px solid rgb(0, 0, 0);")
            self.data_layout = QVBoxLayout()
            self.data_section.setLayout(self.data_layout)

            self.text_name = QLabel()
            self.text_name.setText("Name: " + self.name)
            
            newfont = QFont("Roboto Mono", 16, QFont.Bold) 
            self.text_name.setFont(newfont)
            # text_confidence = QLabel()
            # text_confidence.setText("Confidence: " + self.confidence)

            self.data_layout.addWidget(self.text_name)
            # self.data_layout.addWidget(text_confidence)

            self.layout.addWidget(self.data_section)

        def set_image(self, image):
            qim = ImageQt(image)
            image = QPixmap.fromImage(qim)

            self.image_frame.setPixmap(image.scaled(self.WIDTH, self.HEIGHT, Qt.KeepAspectRatio))
            
