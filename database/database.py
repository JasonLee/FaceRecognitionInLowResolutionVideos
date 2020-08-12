import sqlite3
import atexit

conn = sqlite3.connect('face.db')

# Format result list to contain just data requested
conn.row_factory = lambda c, row: row[0]
cursor = conn.cursor()
controller = None


def init_database(controller_obj):
    global controller
    controller = controller_obj

    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute('''CREATE TABLE IF NOT EXISTS people(
                people_id INTEGER PRIMARY KEY, 
                people_name TEXT UNIQUE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS face(
                face_id INTEGER PRIMARY KEY, 
                people_id INTEGER,
                image BLOB, 
                FOREIGN KEY (people_id) REFERENCES people (people_id) ON DELETE CASCADE)''')

    conn.commit()
    controller.get_logger_system().info("Table has been created if necessary")

    # Bind closing of application to a function
    atexit.register(exit_handler)


def convert_to_binary_data(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        blob_data = file.read()
    return blob_data


def insert_people(name):
    try:
        sqlite_insert_person_query = '''INSERT INTO people(people_name) VALUES (?)'''

        data = (name,)
        # https://bit.ly/3imr3mA
        cursor.execute(sqlite_insert_person_query, data)
        conn.commit()
        controller.get_logger_system().info("Inserted People into DB")

    except conn.Error as error:
        # Should be a logging message
        controller.get_logger_system().error("Failed to insert a new person into the table: ", error)


def insert_face_file(people_name, filename):
    try:
        sqlite_insert_blob_query = """INSERT INTO face(people_id, image) VALUES (?, ?)"""

        people_id = get_people_id(people_name)

        if people_id is None:
            controller.get_logger_system().error("Cannot find people in table with given name!")
            raise ValueError('Cannot find people in table with given name!')

        face_image = convert_to_binary_data(filename)

        # Convert data into tuple format
        data_tuple = (people_id, face_image)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()

    except conn.Error as error:
        controller.get_logger_system().error("Failed to insert face data into the table:", error)


def insert_face_as_data(people_name, face_data):
    try:
        sqlite_insert_blob_query = """INSERT INTO face(people_id, image) VALUES (?, ?)"""

        people_id = get_people_id(people_name)
        print(people_name, people_id)

        if people_id is None:
            controller.get_logger_system().error('Cannot find people in table with given name!')
            raise ValueError('Cannot find people in table with given name!')

        # Convert data into tuple format
        data_tuple = (people_id, face_data)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()
        controller.get_logger_system().info("Inserted face image into DB")

    except conn.Error as error:
        controller.get_logger_system().error("Failed to insert face data into the table: ", error)


def get_people_id(name):
    try:
        cursor.execute("""SELECT people_id FROM people WHERE people_name=?""", (name,))
        controller.get_logger_system().info("Got people ID from DB")
    except conn.Error as error:
        controller.get_logger_system().error("Failed to people id from DB", error)

    return cursor.fetchone()


def get_people_image(name):
    try:
        cursor.execute(
            """SELECT face.image FROM face INNER JOIN people ON face.people_id = people.people_id WHERE 
            people.people_name=?""",
            (name,))

        controller.get_logger_system().info("Get face images for person from DB")
    except conn.Error as error:
        controller.get_logger_system().error("Failed to get people image from table:", error)

    return cursor.fetchall()


def get_all_people_names():
    try:
        cursor.execute(
            """SELECT people.people_name FROM people WHERE people.people_id IN (SELECT people_id FROM face)""")
        controller.get_logger_system().info("Get all people names from DB, if they have a face image")
    except conn.Error as error:
        controller.get_logger_system().error("Failed to get people name from table:", error)

    return cursor.fetchall()


def get_all_people_names_unsafe():
    try:
        cursor.execute("""SELECT people.people_name FROM people""")
        controller.get_logger_system().info("Get all people names from DB, even if they don't have a face image")
    except conn.Error as error:
        controller.get_logger_system().error("Failed to get people name from table:", error)

    return cursor.fetchall()


def get_all_people_and_image():
    try:
        cursor.execute(
            """SELECT people.people_name, face.image FROM face INNER JOIN people ON face.people_id = people.people_id""")
        controller.get_logger_system().info("Get all people and their face images")
    except conn.Error as error:
        controller.get_logger_system().error("Failed to get people name and image from table: ", error)

    return cursor.fetchall()


def delete_person(name):
    try:
        sqlite_insert_blob_query = """DELETE FROM people WHERE people_name =?"""

        data_tuple = (name,)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()
        controller.get_logger_system().info("Delete a person from DB")

    except conn.Error as error:
        controller.get_logger_system().error("Failed to delete person", error)


def delete_face_image(face_data):
    try:
        sqlite_insert_blob_query = """DELETE FROM face WHERE image =?"""

        data_tuple = (face_data,)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()
        controller.get_logger_system().info("Delete face data")

    except conn.Error as error:
        controller.get_logger_system().error("Failed to delete face data", error)


def exit_handler():
    # Close db connect
    cursor.close()
    conn.close()
    controller.get_logger_system().info("DB connection has been closed")

