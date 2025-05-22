import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",  # Убедитесь, что пароль корректный
    "database": "fasionstore"  # Исправлена опечатка в названии БД
}

def get_db_connection():  # Исправлено название (bd -> db)
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print('Success')  # Исправлена опечатка
        return conn
    except Error as e:
        print(f'Error: {e}')
        return None

def get_user():
    conn = get_db_connection()  # Исправлено название функции
    if conn is None:
        return None  # Явный возврат None
    
    cursor = None  # Инициализация переменной
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT login, password_hesh FROM users')  # Явное указание столбцов
        users = cursor.fetchall()
        print(f'Users from db: {users}')
        return users
    except Error as e:
        print(f'Error to get users: {e}')
        return None  # Явный возврат None при ошибке
    finally:
        if cursor is not None:  # Безопасное закрытие курсора
            cursor.close()
        if conn.is_connected():  # Проверка подключения перед закрытием
            conn.close()

def get_user_by_credentials(login: str, password: str):
    conn = get_db_connection()
    if conn is None:
        return None
    
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id FROM users WHERE login = %s AND password_hesh = %s"
        cursor.execute(query, (login, password))
        return cursor.fetchone()
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if cursor: cursor.close()
        if conn.is_connected(): conn.close()

def get_staff_by_id(staff_id: int):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM users WHERE id = %s", (staff_id,))
            return cursor.fetchone()
    except Exception as e:
        print("Ошибка при получении сотрудника:", e)
        return None
    finally:
        conn.close()

# Обновление данных сотрудника
def update_staff(staff_id: int, user):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users SET full_name=%s, role=%s, login=%s, post=%s 
                WHERE id=%s
            """, (user.full_name, user.role, user.login, user.post, staff_id))
        conn.commit()
    except Exception as e:
        print("Ошибка обновления данных:", e)
        conn.rollback()
    finally:
        conn.close()

# Удаление сотрудника
def delete_staff(staff_id: int):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id=%s", (staff_id,))
        conn.commit()
    except Exception as e:
        print("Ошибка удаления:", e)
        conn.rollback()
    finally:
        conn.close()