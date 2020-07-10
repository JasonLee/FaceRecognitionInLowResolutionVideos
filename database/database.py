import sqlite3
import atexit

TEST_IMAGE = 'images/frame26.png'
TEST_IMAGE2 = 'images/823.png'

conn = sqlite3.connect('face.db')
conn.row_factory = lambda c, row: row[0]
cursor = conn.cursor()


def init_database():
    cursor.execute('''CREATE TABLE IF NOT EXISTS people(
                people_id INTEGER PRIMARY KEY, 
                people_name TEXT UNIQUE)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS face(
                face_id INTEGER PRIMARY KEY, 
                people_id INTEGER,
                image BLOB, 
                FOREIGN KEY (people_id) REFERENCES people (people_id) ON DELETE CASCADE)''')

    conn.commit()

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

    except conn.Error as error:
        # Should be a logging message
        print("Failed to insert a new person into the table: ", error)


def insert_face_file(people_name, filename):
    try:
        sqlite_insert_blob_query = """INSERT INTO face(people_id, image) VALUES (?, ?)"""

        people_id = get_people_id(people_name)

        if people_id is None:
            raise ValueError('Cannot find people in table with given name!')

        face_image = convert_to_binary_data(filename)

        # Convert data into tuple format
        data_tuple = (people_id, face_image)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()

    except conn.Error as error:
        print("Failed to insert face data into the table: ", error)

def insert_face_as_data(people_name, face_data):
    try:
        sqlite_insert_blob_query = """INSERT INTO face(people_id, image) VALUES (?, ?)"""

        people_id = get_people_id(people_name)

        if people_id is None:
            raise ValueError('Cannot find people in table with given name!')


        # Convert data into tuple format
        data_tuple = (people_id, face_data)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()

    except conn.Error as error:
        print("Failed to insert face data into the table: ", error)


def get_people_id(name):
    try:
        cursor.execute("""SELECT people_id FROM people WHERE people_name=?""", (name,))
    except conn.Error as error:
        print("Failed to insert blob data into sqlite table", error)

    return cursor.fetchone()

def get_people_image(name):
    try:
        cursor.execute("""SELECT face.image FROM face INNER JOIN people ON face.people_id = people.people_id WHERE people.people_name=?""", (name,))
    except conn.Error as error:
        print("Failed to get people image from table:", error)

    return cursor.fetchall()

def get_all_people_names():
    try:
        cursor.execute("""SELECT people.people_name FROM people WHERE people.people_id IN (SELECT people_id FROM face)""")
    except conn.Error as error:
        print("Failed to get people name from table:", error)

    return cursor.fetchall()

def get_all_people_names_unsafe():
    try:
        cursor.execute("""SELECT people.people_name FROM people""")
    except conn.Error as error:
        print("Failed to get people name from table:", error)

    return cursor.fetchall()

def get_all_people_and_image():
    try:
        cursor.execute("""SELECT people.people_name, face.image FROM face INNER JOIN people ON face.people_id = people.people_id""")
    except conn.Error as error:
        print("Failed to get people name and image from table: ", error)

    return cursor.fetchall()

def delete_person(name):
    try:
        sqlite_insert_blob_query = """DELETE FROM people WHERE people_name =?"""

        # Convert data into tuple format
        data_tuple = (name,)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()

    except conn.Error as error:
        print("Failed to delete person", error)

def delete_face_image(face_data):
    try:
        sqlite_insert_blob_query = """DELETE FROM face WHERE image =?"""

        # Convert data into tuple format
        data_tuple = (face_data,)

        cursor.execute(sqlite_insert_blob_query, data_tuple)
        conn.commit()

    except conn.Error as error:
        print("Failed to delete face", error)

def exit_handler():
    # Close db connect
    cursor.close()
    conn.close()
    print("Application has exited")


atexit.register(exit_handler)
