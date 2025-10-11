import feedparser
import logging
import config
import database

def get_new_events():

    db = database.Database()

    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(config.RSS_URL)
    logging.info(f"O título do feed é {feed.feed.title}.")

    for (entry_number, entry) in enumerate(feed.entries):
        logging.info(f"A entrada {entry_number} tem o título {entry.title} e foi publicada em {entry.published_parsed}. Seu conteúdo é {entry.summary}. Mais informações em {entry.link}.")
        try:       
            db.put_entry(entry)
        except:
            logging.info(f"A entrada da data {entry.published} já existe (não há nada de errado nisso, mas convém verificar).")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(funcName)s %(message)s', 
                        datefmt='%Y/%m/%d %I:%M:%S %p', 
                        level=logging.INFO)
    get_new_events()
