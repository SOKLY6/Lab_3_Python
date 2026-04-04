import logging

logging.basicConfig(
    filename="logs.log",
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер с указанным именем"""
    return logging.getLogger(name)
