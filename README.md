# Wieloagentowy model doboru płciowego u gupika (Poecilia reticulata) w środowiskach o niskiej i wysokiej presji drapieżniczej

Celem tego projektu, realizowanego w ramach pracy inżynierskiej, było zbadanie wpływu ornamentacji samców, w szczególności liczby oraz powierzchni czarnych i pomarańczowych plam na ciele, na ich sukces reprodukcyjny w dwóch odmiennych scenariuszach środowiskowych - wysokiej oraz niskiejpresji drapieżniczej. Cel ten został zrealizowany poprzez skonstruowanie modelu wieloagentowego oraz jego parametryzację.

## Struktura Projektu

Projekt został podzielony na 5 etapów, z których każdy posiada własną instrukcję uruchomienia (plik `README.md` wewnątrz folderu):

1.  **Etap 01: Model Bazowy** – Konstrukcja aplikacji i podstawowe interakcje gupików ze środowiskiem (bez preferencji i selekcji),
2.  **Etap 02: Parametryzacja etap 1** – optymalizacja parametrów fizjologii i środowiska dla populacji: Arima1, Arima5, Aripo1, Aripo6,
3.  **Etap 03: Model z Preferencjami** – rozszerzona wersja modelu o mechanizmy doboru płciowego i presję drapieżników,
4.  **Etap 04: Parametryzacja etap 2** – drugi stopień optymalizacji (preferencje i selekcja),
5.  **Etap 05: Wersja finalna** w W pełni zoptymalizowany model, gotowy do weryfikacji efektów symulacji.

### Wymagania
Do uruchomienia projektu wymagany jest Python oraz biblioteki wymienione w pliku `requirements.txt`. Główne narzędzie wizualizacyjne to **Solara**.

Instalacja bibliotek:
```bash
pip install -r requirements.txt