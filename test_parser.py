import pytest
from bs4 import BeautifulSoup
from parser import PhpMyAdminScraper
from unittest.mock import MagicMock, patch
from example_html import HTML_LOGIN_PAGE, HTML_TABLE_PAGE


def test_get_token():
    """Тестирование извлечения токена."""
    parser = PhpMyAdminScraper()
    parser.session = MagicMock()

    parser.session.get.return_value.text = HTML_LOGIN_PAGE

    parser.get_token()

    assert parser.token == "abc123"
    parser.session.get.assert_called_once()


def test_login():
    """Тестирование авторизации"""
    parser = PhpMyAdminScraper()
    parser.session = MagicMock()
    parser.token = 'abc123'

    parser.session.post.return_value.text = 'Вы успешно вошли'
    parser.session.post.return_value.url = 'http://.../index.php?route=/main'

    parser.login()

    parser.session.post.assert_called_once()
    call_data = parser.session.post.call_args[1]['data']
    assert call_data['pma_username'] == 'test'
    assert call_data['pma_password'] == 'JHFBdsyf2eg8*'
    assert call_data['token'] == 'abc123'


def test_parse_table():
    """Тестирование взаимодействий с таблицей."""
    parser = PhpMyAdminScraper()

    soup = BeautifulSoup(HTML_TABLE_PAGE, 'html.parser')
    parser.table = soup.find('table', {'class': 'table_results'})

    with patch('builtins.print') as mocked_print:
        parser.print_table()

    printed_lines = []
    for call in mocked_print.call_args_list:
        if call.args:
            printed_lines.append(str(call.args[0]))

    output = " ".join(printed_lines)

    assert "1" in output
    assert "Иван" in output
    assert "2" in output
    assert "Пётр" in output
    assert "ID" in output or "id" in output
    assert "name" in output


def test_login_error():
    """Тестирование в случае ошибки авторизации."""
    parser = PhpMyAdminScraper()
    parser.session = MagicMock()
    parser.token = 'abc123'

    parser.session.post.return_value.text = 'Access denied'

    with pytest.raises(ValueError, match='Ошибка авторизации!'):
        parser.login()
