import logging
import os
from venv import logger

os.makedirs("logs", exist_ok=True )

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="logs/zappy_logs.log",
    filemode="a"
)

logger = logging.getLogger("zappy_logger")