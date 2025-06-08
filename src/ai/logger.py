#src.ai.logger.py
import logging
import os

os.makedirs("logs", exist_ok=True )

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename="logs/zappy_logs.log",
    filemode="a"
)

logger = logging.getLogger("zappy_logger")
logger.info("Logger initialized.")
