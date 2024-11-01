import psycopg2
from psycopg2 import Error

#На вход поступает запрос, на выход данные отправленные из БД
def base_promt(in_request):
    try:
        conn = psycopg2.connect(user="postgres",
                                    password="postgre",
                                    host="localhost",
                                    port="5432",
                                    database="bot_database")
        cursor = conn.cursor()
        sql_request = in_request
        cursor.execute(sql_request)
        conn.commit()
        return cursor.fetchall()

    except (Exception, Error) as error:
        print("Ошибка при работе с PostgreSQL", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Соединение с PostgreSQL закрыто")
