from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QListWidget, QListWidgetItem, QHBoxLayout, QLabel, \
    QPushButton, QInputDialog, QLineEdit


class ListWidget(QWidget):
    # Signal for other threads to use to add to list
    add_list_requested = pyqtSignal(str, str, str)
    LIST_MAX_LENGTH = 100
    
    def __init__(self, controller):
        super(ListWidget, self).__init__()
        self.controller = controller
        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        self.add_list_requested.connect(self.add_live_tab)
        self._setup_tabs()

    def _setup_tabs(self):
        self.tabs = QTabWidget()
        self.tab1_live = QListWidget()
        self.tab2_total = QListWidget()

        self.tabs.addTab(self.tab1_live, "Live Results")

        self.layout.addWidget(self.tabs)

    def add_live_tab(self, name, confidence, image):
        new_data = self.LiveResultBlock(name, confidence, image, self.controller)
        list_item = QListWidgetItem()
        self.tab1_live.addItem(list_item)
        self.tab1_live.setItemWidget(list_item, new_data)
        list_item.setSizeHint(new_data.sizeHint())
        self.controller.get_logger_gui().info("Adding data to live tab")

        self._remove_over_limit()
    
    def _remove_over_limit(self):
        self.controller.get_logger_gui().info("Removing list items if over limit")

        while self.tab1_live.count() > self.LIST_MAX_LENGTH:
            self.tab1_live.takeItem(0)
        

    def get_live_list_widget(self):
        return self.tab1_live

    class LiveResultBlock(QWidget):
        WIDTH = 400
        HEIGHT = 120

        def __init__(self, name, confidence, image, controller):
            super(ListWidget.LiveResultBlock, self).__init__()
            self.controller = controller
            self.confidence = confidence
            self.name = name
            self.image_path = image
            self._setup_block()

        def _setup_block(self):
            self.layout = QHBoxLayout()
            self.image_frame = QLabel(self)

            self.image_pixmap = QPixmap(self.image_path)

            self.image_frame.setPixmap(self.image_pixmap.scaled(self.WIDTH, self.HEIGHT, Qt.KeepAspectRatio))
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
            self.modify_button.setText("MODIFY")
            self.modify_button.clicked.connect(self._modify_label)

            self.button_layout.addWidget(self.modify_button)

            self.layout.addWidget(self.button_section)

        def _modify_label(self):
            """ Add new label of face to db"""
            new_name, ok_pressed = QInputDialog.getText(self, "New Face Label", "Name:", QLineEdit.Normal, self.name)

            if ok_pressed and new_name != self.name:
                self.text_name.setText("Name: " + new_name)
                self.controller.add_face_db(new_name, self.image_pixmap)
