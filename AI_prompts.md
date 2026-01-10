# Artikel
Rolle: Du bist ein Experte für die deutsche Sprache und Datenstrukturierung.
Aufgabe: Erstelle eine Liste von [HIER ANZAHL EINFÜGEN ZB 100] deutschen Substantiven zum Thema [HIER THEMA EINFÜGEN].
Anforderungen:

Die Wörter sollten eine Mischung aus den Artikeln "der", "die" und "das" sein.
Wähle Wörter, die für das Thema typisch sind (Niveau A1 bis B2).
Jedes Wort muss eine präzise englische Übersetzung haben. Bitte kein plural!
Formatierung: Gib das Ergebnis ausschließlich als valides JSON-Array aus. Nutze exakt diese Struktur für jedes Objekt:
JSON

{
  "word": "Beispielwort",
  "article": "der",
  "translation": "example word"
}

Wichtig: Gib keinen Einleitungstext, keine Erklärungen und keine Markdown-Code-Blöcke aus – nur den reinen JSON-Inhalt.

# Adjektive Deklination
Rolle: Du bist ein Experte für Deutsch als Fremdsprache (DaF) und spezialisiert auf die Erstellung von Lehrmaterialien.
Aufgabe: Erstelle eine JSON-Datei mit Übungssätzen zur deutschen Adjektivdeklination. Jeder Satz muss zwei Lücken haben: Eine für die Adjektivendung und eine für die Nomen-Endung (insbesondere für Genitiv -s/-es oder n-Deklination).
Thema der Übung: [HIER THEMA EINFÜGEN]
Anforderungen an die Sätze:

Die Kombination aus Adjektiv und Nomen muss logisch sinnvoll sein.
Variiere zwischen bestimmtem, unbestimmtem und Nullartikel.
Die Sätze sollten ein mittleres Sprachniveau (A1/A2/B1/B2) haben.
Technisches Format (Strikt einhalten):
Erstelle ein JSON-Array aus Objekten mit folgendem Aufbau:

prefix: Der Teil des Satzes bis zur ersten Lücke (inkl. Adjektivstamm).
middle: Der Teil zwischen den beiden Lücken (meist der Wortstamm des Nomens).
suffix: Der Rest des Satzes.
options1: 4 Optionen für das Adjektiv (z.B. ["-e", "-er", "-en", "-em"]).
correct1: Die richtige Endung für das Adjektiv.
options2: 4 Optionen für das Nomen (z.B. ["-", "-e", "-en", "-s"]). Nutze "-" für "keine Endung".
correct2: Die richtige Endung für das Nomen.
translation: Eine deutsche Übersetzung des gesamten korrekten Satzes zur Kontrolle.
Beispiel für die Struktur:
{
"prefix": "Wegen des stark",
"middle": " Regen",
"suffix": " wurde das Spiel abgesagt.",
"options1": ["-e", "-er", "-en", "-em"],
"correct1": "-en",
"options2": ["-", "-e", "-en", "-s"],
"correct2": "-s",
"translation": "Wegen des starken Regens wurde das Spiel abgesagt."
}
Bitte generiere jetzt [HIER ANZAHL EINFÜGEN ZB 100] verschiedene Sätze für das oben gewählte Thema.


# Präpositionen

Rolle: Du bist ein Experte für Deutsch als Fremdsprache (DaF) und erstellst digitales Lehrmaterial für ein Nachhilfeinstitut.
Aufgabe: Erstelle eine JSON-Datei für eine Übung zu deutschen Präpositionen (insbesondere Wechselpräpositionen und lokale Präpositionen). Jeder Satz hat genau eine Lücke für den korrekten Artikel.
Thema der Übung: [HIER THEMA EINFÜGEN]
Anforderungen an die Grammatik & Optik:

Jedes Nomen muss eine Farbe basierend auf seinem Genus erhalten:
Maskulin: #3b82f6 (Blau)
Feminin: #ef4444 (Rot)
Neutral: #10b981 (Grün)
Die Sätze sollten alltagsnah und logisch sinnvoll sein.
Es soll immer der Kasus (Dativ oder Akkusativ) nach der Präposition geübt werden.
Technisches Format (Strikt einhalten!):
Erstelle ein JSON-Array aus Objekten mit folgendem Aufbau:

prefix: Der Teil des Satzes vor der Lücke (endet meist mit der Präposition).
noun: Das Nomen, das nach der Lücke folgt (ohne Artikel).
noun_color: Der Hex-Code für die Farbe (siehe oben).
suffix: Der Rest des Satzes nach dem Nomen (z.B. ein Punkt oder weitere Satzteile).
options: Ein Array mit genau 4 Antwortmöglichkeiten (z.B. ["dem", "der", "den", "das"]).
correct: Die exakt richtige Antwort aus den Optionen.
translation: Eine vollständige Übersetzung des korrekten Satzes.
Beispiel für ein Objekt:
{
"prefix": "Das Buch liegt auf ",
"noun": "Tisch",
"noun_color": "#3b82f6",
"suffix": ".",
"options": ["dem", "der", "das", "den"],
"correct": "dem",
"translation": "Das Buch liegt auf dem Tisch."
}
Bitte generiere jetzt [HIER ANZAHL EINFÜGEN ZB 100] verschiedene Sätze für das oben gewählte Thema in diesem Format.
