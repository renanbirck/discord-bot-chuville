import sqlite3
from datetime import datetime
from time import mktime
import logging
import config 

class Database:
    def __init__(self):
       logging.info("Construindo o objeto de acesso ao BD...")
       self.connection = sqlite3.connect(config.DB_FILE_NAME)
       self.cursor = self.connection.cursor()
       self.cursor.execute("CREATE TABLE IF NOT EXISTS RSS_Entries(\
                            entry_id INTEGER PRIMARY KEY,\
                            entry_title VARCHAR(500) NOT NULL,\
                            entry_publication_date VARCHAR(20) UNIQUE NOT NULL,\
                            entry_summary VARCHAR(5000),\
                            entry_link VARCHAR(500),\
                            was_already_posted INTEGER\
                            )")
       logging.info("Sucesso! Podemos adicionar as entradas ao BD.")

    def put_entry(self, entry):

        timestamp = datetime.fromtimestamp(mktime(entry.published_parsed))
        logging.info("Adicionando entrada %s ao BD.", entry.title)
        self.cursor.execute("INSERT INTO RSS_ENTRIES(entry_title, entry_publication_date, entry_summary, entry_link, was_already_posted)\
                            VALUES(?, ?, ?, ?, 0)", (entry.title, timestamp, entry.summary, entry.link))
        self.connection.commit()

    def get_latest_headline(self):
        """ Pega a entrada mais recente do BD. """
        self.cursor.execute("SELECT entry_id, entry_title, entry_publication_date, entry_summary, entry_link, was_already_posted FROM RSS_Entries ORDER BY entry_publication_date DESC LIMIT 1")
        post_id, post_title, post_date, post_summary, post_link, was_already_posted = self.cursor.fetchone()
        return {"post_id": post_id, 
                "post_title": post_title,
                "post_date": post_date,
                "post_summary": post_summary,
                "post_link": post_link,
                "was_already_posted": was_already_posted}

    def mark_headline_as_read(self):
        """ Marca a entrada mais recente como já lida, ou seja, não iremos postar de novo. """
        self.cursor.execute("SELECT entry_id FROM RSS_Entries ORDER BY entry_publication_date DESC LIMIT 1")
        entry_id = self.cursor.fetchone() 
        logging.info("A entrada mais recente é %s. Vou marcar ela como lida!", entry_id)
        self.cursor.execute("UPDATE RSS_Entries SET was_already_posted = 1 WHERE entry_id = (?)", entry_id)

    def __del__(self):
        self.connection.commit()
        self.connection.close()
        logging.info("Destruíndo o objeto de acesso ao BD.")
