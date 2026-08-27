import httpx
from bs4 import BeautifulSoup
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

LOGIN_PAGE_URL = "https://www.laczynasgwizdek.pl/" 
LOGIN_ACTION_URL = "https://www.laczynasgwizdek.pl/" 
CAST_URL = "https://www.laczynasgwizdek.pl/castReferee/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

USERNAME= os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

def extract_csrf_token(html_text: str) -> str | None:
    """Wyciąga token CSRF z wstrzykniętego kodu Reacta lub czystego HTML."""
    soup = BeautifulSoup(html_text, "lxml")
    
    login_app_div = soup.find("div", {"id": "loginApp"})
    if login_app_div and login_app_div.has_attr("data-csrf"):
        return login_app_div.get("data-csrf")
        
    token_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
    if token_input:
        return token_input.get("value")
        
    return None

def parse_obsada_html(html_text: str):
    """Parsuje tabelę z HTML-a i zwraca listę słowników z danymi meczów."""
    soup = BeautifulSoup(html_text, "lxml")
    table_body = soup.find("table", class_="custom-table")
    
    if not table_body:
        print("Błąd: Nie znaleziono tabeli meczów w HTML-u.")
        return []

    matches = []
    current_league = "Nieznana liga"

    tbody = table_body.find("tbody")
    if not tbody:
        return matches

    # Iterujemy po wierszach
    for row in tbody.find_all("tr"):
        
        # Sprawdzamy czy to separator z nazwą ligi
        league_header = row.find("td", class_="colorSeparator")
        if league_header:
            current_league = league_header.text.strip()
            continue

        # Sprawdzamy czy to wiersz z meczem
        match_id = row.get("data-match-id")
        if not match_id:
            continue

        cols = row.find_all("td")
        if len(cols) < 10:
            continue

        # Wyciągamy sędziego głównego
        main_ref_tag = cols[6].find("a", class_="referee-link")
        main_ref = main_ref_tag.text.strip() if main_ref_tag else "Brak"
        main_ref_id = main_ref_tag.get("data-referee-id") if main_ref_tag else None

        match_data = {
            "match_id": match_id,
            "league": current_league,
            "home_team": cols[1].text.strip(),
            "away_team": cols[2].text.strip(),
            "date": cols[3].text.strip(),
            "time": cols[4].text.strip(),
            "address": cols[5].text.strip(),
            "main_referee": main_ref,
            "main_referee_id": main_ref_id
        }
        
        matches.append(match_data)

    return matches

async def login_and_get_cast(username, password):
    """Odpowiada za całą warstwę sieciową i autoryzację."""
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        
        print("Pobieranie strony logowania...")
        response = await client.get(LOGIN_PAGE_URL)
        
        token = extract_csrf_token(response.text)
        if not token:
            print("Błąd: Nie znaleziono tokenu CSRF!")
            return None

        login_data = {
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": token,
        }
        
        # Ominięcie zabezpieczeń Django dla POST
        client.headers.update({"Referer": LOGIN_PAGE_URL})
        
        print("Wysyłanie danych logowania...")
        await client.post(LOGIN_ACTION_URL, data=login_data)

        print("Pobieranie obsady...")
        protected_response = await client.get(CAST_URL)
        
        return protected_response.text

if __name__ == "__main__":
    # Wpisz swój login/email i hasło
    USERNAME = os.getenv('USERNAME')
    PASSWORD = os.getenv('PASSWORD')

    print("Odpalam scrapera...")
    html_output = asyncio.run(login_and_get_cast(USERNAME, PASSWORD))

    if html_output:
        # Awaryjny zapis, żeby mieć podgląd pliku
        with open("obsada.html", "w", encoding="utf-8") as f:
            f.write(html_output)
        
        # Uruchomienie parsera
        parsed_matches = parse_obsada_html(html_output)
        print(f"\nWyciągnięto {len(parsed_matches)} meczów!")
        
        # Wypisanie 3 pierwszych wyników do konsoli w celu weryfikacji
        print("Pierwsze 3 mecze z bazy:\n")
        for m in parsed_matches[:3]:
            print(m)
            print("-" * 40)
    else:
        print("Coś wyjebało po drodze. Brak kodu HTML.")