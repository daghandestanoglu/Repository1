# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error

def get_connection():
    """MySQL veritabanına bağlantı oluşturur ve döndürür."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',         # MySQL kurulurken belirlediğin kullanıcı adı
            password='Mysqlsifr123!',  # Kendi MySQL root şifreni buraya yaz!
            database='okul_projesi'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"MySQL Bağlantı Hatası: {e}")
        return None