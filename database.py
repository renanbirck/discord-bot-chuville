import sqlite3
from datetime import datetime
from time import mktime
import logging
import config 

class Database:
    def __init__(self):
       logging.info(f"Construindo o objeto de acesso ao BD...")
       self.connection = sqlite3.connect(config.DB_FILE_NAME)
       self.cursor = self.connection.cursor()
       self.cursor.execute("CREATE TABLE IF NOT EXISTS RSS_Entries(\
                            entry_id INTEGER PRIMARY KEY,\
                            entry_title VARCHAR(500) NOT NULL,\
                            entry_publication_date VARCHAR(20) UNIQUE NOT NULL,\
                            entry_summary VARCHAR(5000),\
                            entry_link VARCHAR(500)\
                            )")
       logging.info(f"Sucesso! Podemos adicionar as entradas ao BD.")

    def put_entry(self, entry):

        timestamp = datetime.fromtimestamp(mktime(entry.published_parsed))
        logging.info(f"Adicionando entrada {entry.title} ao BD.")
        self.cursor.execute("INSERT INTO RSS_ENTRIES(entry_title, entry_publication_date, entry_summary, entry_link)\
                            VALUES(?, ?, ?, ?)", (entry.title, timestamp, entry.summary, entry.link))
        self.connection.commit()

    def __del__(self):
        self.connection.commit()
        self.connection.close()
        logging.info(f"Destruíndo o objeto de acesso ao BD.")
