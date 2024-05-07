import sqlite3
from requests import get
from datetime import datetime

# Funkcja do utworzenia bazy danych i tabeli, jeśli nie istnieją
def create_database_and_table_if_not_exists():
    connection = sqlite3.connect('waluty.db')
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS waluty(
         id INTEGER PRIMARY KEY AUTOINCREMENT,
         data_pobrania DATE,
         data_kursu DATE,
         pelna_nazwa_waluty TEXT,
         kod_waluty TEXT,
         kurs_zakupu NUMERIC,
         kurs_sprzedazy NUMERIC
    )''')
    connection.commit()
    connection.close()


# Funkcja do połączenia z bazą danych SQLite
def connect_to_database():
    connection = sqlite3.connect('waluty.db')
    return connection


# Funkcja do sprawdzenia, czy dane już istnieją w bazie
def check_if_data_exists(connection, date, code, bid):
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM waluty WHERE data_pobrania=? AND UPPER(kod_waluty)=? AND kurs_zakupu=?', (date, code.upper(), bid))
    result = cursor.fetchone()
    return result is not None


# Funkcja do dodania danych do bazy danych
def add_data_to_database(connection, date, effective_date, currency_name, code, bid, ask):
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO waluty(data_pobrania, data_kursu, pelna_nazwa_waluty, kod_waluty, kurs_zakupu, kurs_sprzedazy) VALUES(?, ?, ?, ?, ?, ?)',
        (date, effective_date, currency_name, code, bid, ask))
    connection.commit()


# URL do API NBP
waluty_url = 'http://api.nbp.pl/api/exchangerates/rates/C/{code}/{date}/'

# Pobranie bieżącej daty
download_date = datetime.now().strftime('%Y-%m-%d')

# Utworzenie bazy danych i tabeli, jeśli nie istnieją
create_database_and_table_if_not_exists()

# Pobieranie danych od użytkownika
# table = input('Podaj typ tabeli (A, B, lub C): ')
code = input('Podaj trzyliterowy kod waluty (standard ISO 4217): ').upper()  # Konwersja na duże litery
date = input('Podaj datę w formacie "YYYY-MM-DD": ')

# Formatowanie URL
waluty_url = waluty_url.format(code=code, date=date)

# Wysłanie zapytania do API NBP
response = get(waluty_url)

# Sprawdzenie czy odpowiedź jest poprawna
if response.status_code == 200:
    # Jeśli odpowiedź jest poprawna, pobieramy dane JSON
    waluty = response.json()
    bid_value = waluty['rates'][0]['bid']
    ask_value = waluty['rates'][0]['ask']

    # Połączenie z bazą danych
    connection = connect_to_database()

    # Sprawdzenie, czy dane już istnieją w bazie
    if not check_if_data_exists(connection, download_date, code, bid_value):
        # Wyświetlenie danych pobranych z API przed dodaniem ich do bazy danych
        print("Dane pobrane z API:")
        print(f"Data pobrania: {download_date}")
        print(f"Data kursu: {waluty['rates'][0]['effectiveDate']}")
        print(f"Nazwa waluty: {waluty['currency']}")
        print(f"Kod waluty: {code}")
        print(f"Kurs zakupu: {bid_value}")
        print(f"Kurs sprzedaży: {ask_value}")
        # Jeśli dane nie istnieją, dodaj je do bazy danych
        add_data_to_database(connection, download_date, waluty['rates'][0]['effectiveDate'], waluty['currency'], code, bid_value, ask_value)

        print(f"Dane dodane do bazy danych.")
    else:
        # Jeśli dane już istnieją, wyświetl odpowiedni komunikat
        print(f"Dane już istnieją w bazie danych.")

    # Zamknięcie połączenia z bazą danych
    connection.close()
else:
    # Jeśli odpowiedź nie jest poprawna, wyświetlamy komunikat o błędzie
    print(f'Wystąpił błąd podczas pobierania danych: {response.status_code}')
