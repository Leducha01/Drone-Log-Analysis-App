

### O projekcie
Prosta aplikacja webowa do analizy logów telemetrycznych z dronów DJI (format `.csv`). Zamienia surowe dane lotu w czytelne wykresy i rysuje trasę na mapie. Aplikacja testowana przy użyciu logów z drona DJI Mini 4 Pro.

### Tech Stack
* **Backend:** Python 3 (Flask)
* **Baza danych:** SQLite (baza `telemetry.db` generuje się automatycznie)
* **Frontend:** HTML/CSS (Bootstrap 5)
* **Wizualizacja:** Chart.js (wykresy) & Leaflet.js (mapy GPS)

### Kluczowe funkcje
* **Przetwarzanie danych:** Wczytywanie i filtrowanie plików CSV z aplikacji DJI Fly oraz automatyczna konwersja jednostek (np. z MPH na km/h)
* **Geolokalizacja:** Obliczanie pokonanego dystansu na podstawie koordynatów GPS oraz rysowanie trasy na mapie OpenStreetMap.
* **Dashboard i UX:** Interaktywne wykresy parametrów (wysokość, prędkość, bateria, wiatr) z funkcją przełączania układu na jednokolumnowy dla lepszej czytelności
---
### Zrzuty ekranu

*<img width="2844" height="1676" alt="drone1" src="https://github.com/user-attachments/assets/3b6e08ac-9ce0-4b92-96b4-ea02c8f5c3b0" />*

*<img width="2646" height="1608" alt="drone2" src="https://github.com/user-attachments/assets/e19cf180-0d9a-4a81-8448-3166319a25ce" />*
---
### Szybki start (Lokalnie)
Jeśli posiadasz własny log z lotu DJI w formacie `.csv`, możesz przetestować narzędzie u siebie:

1. Sklonuj repozytorium: `git clone https://github.com/Leducha01/dji-log-analyzer.git`
2. Zainstaluj biblioteki: `pip install Flask`
3. Uruchom serwer: `python app.py`
4. Otwórz w przeglądarce adres `http://127.0.0.1:5000` i wgraj swój plik.
