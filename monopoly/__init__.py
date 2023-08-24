import logging
import sys

logger = logging.getLogger("root")
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
