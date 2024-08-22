from loguru import logger

logger.add("logs/debug.log", format="{time} {level} {message}", level="DEBUG")
log = logger
