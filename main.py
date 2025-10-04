import config 
import feedparser
import logging 

def main():
    logging.info("Iniciando a leitura do feed.")
    feed = feedparser.parse(config.RSS_URL)
    logging.info(f"O título do feed é {feed.feed.title}.")

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p', level=logging.INFO)
    main()
