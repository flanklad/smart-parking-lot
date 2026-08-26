import logging

logger = logging.getLogger("smart_parking_lot")
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    file_handler = logging.FileHandler("parking.log")

    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
    )

    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)