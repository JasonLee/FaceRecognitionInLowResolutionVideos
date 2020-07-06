from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit, QMessageBox, QComboBox, QFileDialog, QLabel, QPushButton
from database.database import get_all_people_names, insert_people, insert_face_file

class AddingPeopleDialog(QDialog):
    def __init__(self, controller):
        super(AddingPeopleDialog, self).__init__()
        self.controller = controller

        self.line = QLineEdit()

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.select_accept)
        button_box.rejected.connect(self.select_reject)

        main_layout = QFormLayout()
        main_layout.addRow(self.line)
        main_layout.addRow(button_box)

        self.setLayout(main_layout)
        self.setWindowTitle("Add Person to Database")


    def select_accept(self):
        if self.line.text() in get_all_people_names():
            reset_prompt = QMessageBox(QMessageBox.Information, "Error", "Person already exists in DB.")
            reset_prompt.exec()
            return

        self.accept()

    def select_reject(self):
        self.reject()

class AddingFaceDialog(QDialog):
    def __init__(self, controller):
        super(AddingFaceDialog, self).__init__()
        self.controller = controller

        self.file_label = QLabel()
        self._file_upload = QPushButton("Open")
        self._file_upload.clicked.connect(self.open_file)

        self.people_name_combo_box = QComboBox()

        for name in get_all_people_names():
            self.people_name_combo_box.addItem(name)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.select_accept)
        button_box.rejected.connect(self.select_reject)

        main_layout = QFormLayout()
        main_layout.addRow(QLabel("Person: "),self.people_name_combo_box)
        main_layout.addRow(QLabel("File to Add: "), self._file_upload)
        main_layout.addRow(self.file_label)

        main_layout.addRow(button_box)

        self.setLayout(main_layout)
        self.setWindowTitle("Add Face to Database")


    def select_accept(self):
        if self.file_label.text() ==  "":
            reset_prompt = QMessageBox(QMessageBox.Information, "Warning", "No file was added")
            reset_prompt.exec()
            self.reject()
            return

        insert_face_file(self.people_name_combo_box.currentText(), self.file_label.text())
        self.accept()

    def select_reject(self):
        self.reject()

    def open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File (*.jpg) (*.png)", "C:", "Images(*.jpg *.png)")
        
        if file_path.endswith('.png') or file_path.endswith('.jpg'):
            self.file_label.setText(file_path)
        else:
            self.file_label.setText("")