# SmokePowerLatch

Czujka dymu, która sprzętowo odcina zasilanie sieciowe drukarki 3D – bez udziału sterownika drukarki.
Schematy KiCad, opis kolejnych stopni zabezpieczenia i obudowy do druku. Pełna dokumentacja jest po
angielsku: [README.md](README.md).

## Zalecane rozwiązanie: 24/5 + czujka dymu (etap A5)

- **PS1 24 V** zasila drukarkę (Duet 2 WiFi, SSR grzałki stołu 230 V) i dostaje sieć tylko przez przekaźnik **K1**.
- **PS2 5 V** (zasilacz czuwania) działa zawsze: zasila Duet w czuwaniu i cewkę K1. Na panel przedni idzie
  tylko niskie napięcie.
- **Moduł czujki** (SD119, przetwornica 5→12 V, przekaźnik nadzoru zasilania K3) wisi wysoko w obudowie
  i trójżyłową wiązką oddaje sygnał **OK** (5 V), który zasila cewkę K1. Duet (`M80`/`M81`, PS_ON) przełącza
  jej drugi koniec.
- **Dym, brak zasilania czujki albo przerwany przewód wiązki → zanika OK → K1 odpada** i drukarka traci
  zasilanie sieciowe bez udziału Dueta.
- **SW1 dwubiegunowy.** Wtyczkę można włożyć odwrotnie, więc K1 w jednym przewodzie zatrzymuje prąd, ale faza
  może zostać na odbiornikach. Następny krok to dwa niezależne przekaźniki K1 + K2 (nie jeden dwubiegunowy –
  sklejenie jednego styku unieruchomiłoby oba bieguny). Szczegóły:
  [Breaking one pole or both](docs/stages.md#breaking-one-pole-or-both-sw1-k1-and-k2).

## Jak powstawał pomysł: stopnie zabezpieczenia A0 → A7

Od gołego układu (**Firestarter**) każdy etap dodaje jedno zabezpieczenie, aż do **Paranoid** – z opisem,
po co i jak skutecznie chroni: [docs/stages.md](docs/stages.md).

## Uwaga

Projekt studyjny – **niezbudowany i nietestowany na sprzęcie**. Napięcie sieciowe zabija: część 230 V musi
zbudować i sprawdzić osoba z uprawnieniami. Wydrukowana obudowa nie jest certyfikowaną obudową sieciową.

Licencja: sprzęt i dokumentacja [CERN-OHL-P-2.0](LICENSE), skrypty [MIT](LICENSE-MIT).
