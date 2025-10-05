import config 
import feedparser
import logging 

def main():
    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(config.RSS_URL)
    logging.info(f"O título do feed é {feed.feed.title}.")

    for (entry_number, entry) in enumerate(feed.entries):
        logging.info(f"A entrada {entry_number} tem o título {entry.title} e foi publicada em {entry.published}. Seu conteúdo é {entry.summary}. Mais informações em {entry.link}.")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)
    main()
