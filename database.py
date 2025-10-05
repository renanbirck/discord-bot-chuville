import sqlite3
DB_FILE_NAME='feed_contents.db'

class Database:
    def __init__(self):
       self.connection = sqlite3.connect(DB_FILE_NAME)
       self.cursor = self.connection.cursor() 

       self.cursor.execute("CREATE TABLE IF NOT EXISTS RSS_Entries(entry_id INTEGER, entry_title VARCHAR(500), entry_publication_date VARCHAR(20), entry_summary VARCHAR(5000)) ")
