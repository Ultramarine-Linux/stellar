import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        # logging.FileHandler("umstellar.log"),
        logging.StreamHandler(sys.stdout)
    ]
)