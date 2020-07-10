from GUI.ControllerModule import Controller
from database.database import init_database

if __name__ == '__main__':
    init_database()
    controller = Controller()