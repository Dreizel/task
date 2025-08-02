import logging
from parser import PhpMyAdminScraper

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# Работаем с логами.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Основная функция запуска скрипта."""
    try:
        logger.info(f'{GREEN}Запуск...{RESET}')
        test = PhpMyAdminScraper()
        test.run()
        logger.info(f'{GREEN}Скрипт выполнен успешно!{RESET}')
    except Exception as e:
        logger.error(f"{RED}Ошибка при выполнении: {e}{RESET}")
        raise


if __name__ == '__main__':
    main()
