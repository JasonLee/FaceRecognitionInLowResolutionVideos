from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QToolButton, QDialog, QDialogButtonBox, QFormLayout, QComboBox, QLabel, QHBoxLayout

from database.database import delete_person, delete_face_image, get_all_people_names_unsafe, get_people_image


class RemovePeopleDialog(QDialog):
    def __init__(self, controller):
        super(RemovePeopleDialog, self).__init__()
        self.controller = controller

        self.people_name_combo_box = QComboBox()

        for name in get_all_people_names_unsafe():
            self.people_name_combo_box.addItem(name)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.select_accept)
        button_box.rejected.connect(self.select_reject)

        main_layout = QFormLayout()
        main_layout.addRow(self.people_name_combo_box)
        main_layout.addRow(button_box)

        self.setLayout(main_layout)
        self.setWindowTitle("Remove a Person from Database")

    def select_accept(self):
        delete_person(self.people_name_combo_box.currentText())
        self.controller.update_rec_model()
        self.accept()

    def select_reject(self):
        self.reject()


class RemoveFaceDialog(QDialog):
    def __init__(self, controller):
        super(RemoveFaceDialog, self).__init__()
        self.controller = controller

        self.face_label = QLabel()
        self.face_pixmap = QPixmap()

        self.button_box = QDialogButtonBox(QDialogButtonBox.Yes | QDialogButtonBox.No)
        self.button_box.accepted.connect(self.select_accept)
        self.button_box.rejected.connect(self.select_reject)

        self.people_name_combo_box = QComboBox()
        self.face_array = []
        self.face_array_index = 0

        self.people_name_combo_box.currentTextChanged.connect(self.update_image)

        for name in get_all_people_names_unsafe():
            self.people_name_combo_box.addItem(name)

        self.load_image()

        self.button_container = QWidget()
        self.button_layout = QHBoxLayout(self)
        self.button_container.setLayout(self.button_layout)

        button_left = QToolButton()
        button_left.setArrowType(Qt.LeftArrow)
        button_left.clicked.connect(self.left_arrow)

        button_right = QToolButton()
        button_right.setArrowType(Qt.RightArrow)
        button_right.clicked.connect(self.right_arrow)

        self.button_layout.addWidget(button_left)
        self.button_layout.addWidget(button_right)

        main_layout = QFormLayout()
        main_layout.addRow(self.people_name_combo_box)
        main_layout.addRow(self.face_label)
        main_layout.addRow(self.button_container)
        main_layout.addRow(self.button_box)

        self.setLayout(main_layout)
        self.setWindowTitle("Remove a face from database")

    def select_accept(self):
        delete_face_image(self.face_array[self.face_array_index])
        self.controller.update_rec_model()
        self.accept()

    def select_reject(self):
        self.reject()

    def left_arrow(self):
        if self.face_array_index == 0:
            return

        self.face_array_index -= 1
        self.load_image()

    def right_arrow(self):
        if self.face_array_index >= len(self.face_array) - 1:
            return

        self.face_array_index += 1
        self.load_image()

    def update_image(self):
        self.face_array = get_people_image(self.people_name_combo_box.currentText())
        self.face_array_index = 0
        self.load_image()

    def load_image(self):
        if len(self.face_array) == 0:
            self.face_pixmap = QPixmap()
            self.face_label.setPixmap(self.face_pixmap)
            self.button_box.button(QDialogButtonBox.Yes).setEnabled(False)
            return

        self.button_box.button(QDialogButtonBox.Yes).setEnabled(True)

        self.face_pixmap.loadFromData(self.face_array[self.face_array_index])
        self.face_label.setPixmap(self.face_pixmap)
