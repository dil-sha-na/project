from db import connection

def create_doctor_tableIfNotExists():
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS doctors (doctor_id VARCHAR(255) PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), password VARCHAR(255))")
        connection.commit()
        print("Table created successfully")
    except Exception as e:
        print("Table creation failed. Error: ", e)
    finally:
        cursor.close()


def create_patient_tableIfNotExists():
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS patients (patient_id VARCHAR(255) PRIMARY KEY, name VARCHAR(255), age INT, blood_group VARCHAR(255), doctor_id VARCHAR(255), weight FLOAT, height FLOAT, disease VARCHAR(255),phone VARCHAR(255))")
        connection.commit()
        print("Table created successfully")
    except Exception as e:
        print("Table creation failed. Error: ", e)
    finally:
        cursor.close()


create_patient_tableIfNotExists()