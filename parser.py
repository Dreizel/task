import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

class PhpMyAdminScraper:
    """Класс отправляет HTTP запросы, конечная цель которых вывести таблицу users,
    в красивом виде."""

    def __init__(self):
        self.base_url = os.getenv('PM_URL')
        self.username = os.getenv('PM_USER')
        self.password = os.getenv('PM_PASSWORD')
        self.session = requests.Session()
        self.token = None
        self.table = None

    def __str__(self):
        if not self.table:
            return "<PhpMyAdminScraper: не загружена таблица. Запустите метод: run()>"
        else:
            rows = self.table.find('tbody').find_all('tr') if self.table else []
            return f"<PhpMyAdminScraper: подключено к testDB.users, строк: {len(rows)}>"

    def get_token(self):
        """Извлекает token для авторизации."""
        login_page = self.session.get(self.base_url)
        soup = BeautifulSoup(login_page.text, 'html.parser')
        token_input = soup.find('input', {'name': 'token'})

        if not token_input:
            raise ValueError("Не удалось найти токен!")

        self.token = token_input.get('value')

    def login(self):
        """Произвадет авторизацию пользователя."""
        login_data = {
            'pma_username': self.username,
            'pma_password': self.password,
            'token': self.token
        }

        response = self.session.post(f'{self.base_url}/index.php', data=login_data)

        if "Access denied" in response.text or "Login error" in response.text:
            raise ValueError('Ошибка авторизации!')

    def get_url_table(self):
        """Получает полный путь к таблице."""
        main_page = self.session.get(self.base_url)
        soup = BeautifulSoup(main_page.text, 'html.parser')
        db_url = soup.find('img', {'alt': 'Databases'}).find_parent('a').get('href')

        if not db_url:
            raise ValueError('Ссылка: db_url, не найдена!')

        databases_page = self.session.get(f'{self.base_url}/{db_url}')
        soup = BeautifulSoup(databases_page.text, 'html.parser')
        testdb_url = soup.find('tr', {'data-filter-row': 'TESTDB'}).find(
            'td', {'class': 'name'}
            ).find('a').get('href')

        if not testdb_url:
            raise ValueError('Ссылка: testdb_url, не найдена!')

        testdb_page = self.session.get(f'{self.base_url}/{testdb_url}')
        soup = BeautifulSoup(testdb_page.text, 'html.parser')
        users_link = soup.find('tr', {'id': 'row_tbl_1'}).find(
            'a', href=lambda x: x and 'table=users' in x
            )['href']

        if not users_link:
            raise ValueError("Ссылка: users_link не найдена!")

        users_table_page = self.session.get(f'{self.base_url}/{users_link}')
        soup = BeautifulSoup(users_table_page.text, 'html.parser')
        self.table = soup.find('table', {'class': 'table_results'})

        if not self.table:
            raise ValueError('Таблица: users, не найдена!')

    def print_table(self):
        """Выводит таблицу в красивом виде."""
        data = []
        tag_head = self.table.find('thead')
        if tag_head:
            headers = [
                th.get_text(strip=True)
                for th in tag_head.find_all('th', class_='column_heading')
            ]
        else:
            headers = ['ID', 'Name']

        tag_body = self.table.find('tbody')
        rows = tag_body.find_all('tr') if tag_body else []

        if not rows:
            print("Таблица пустая.")
            return

        for row in rows:
            cols = row.find_all('td')
            values = [col.get_text(strip=True) for col in cols if col.get_text(strip=True)]

            if len(values) >= 2:
                data.append([values[-2], values[-1]])

        col_widths = [
            max(len(str(row[i])) for row in [[h for h in headers]] + data)
            for i in range(2)
        ]
        col_widths = [max(w, 8) for w in col_widths]

        def format_row(cells, align='left'):
            formatted = []
            for i, cell in enumerate(cells):
                if align == 'center':
                    formatted.append(str(cell).center(col_widths[i]))
                elif align == 'right':
                    formatted.append(str(cell).rjust(col_widths[i]))
                else:
                    formatted.append(str(cell).ljust(col_widths[i]))
            return " │ ".join(formatted)


        print()
        print("┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐")
        print("│ " + format_row(headers, 'center') + " │")
        print("├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤")
        for row in data:
            print("│ " + format_row(row, 'left') + " │")
        print("└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘")
        print()

    def run(self):
        """Запуск всего скрипта."""
        self.get_token()
        self.login()
        self.get_url_table()
        self.print_table()
