import os
import logging
import logging_loki
from multiprocessing import Queue
from dotenv import load_dotenv
load_dotenv()
handler = logging_loki.LokiQueueHandler(
    Queue(-1),
    url=os.environ.get("LOKI_API_ENDPOINT"), 
    tags={"application": "wibly"},
    #auth=("username", "password"),
    version="1",
)
def getLogger():
    logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
    logger = logging.getLogger("wibly")
    logger.addHandler(handler)
    return logger