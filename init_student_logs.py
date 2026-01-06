import os

# Die Liste der extrahierten Namen
student_names = [
    "Anastasia", "Carson", "Celine", "Corrina", "David", "Ella", "Emily",
    "Erin", "Eva", "Eveline", "Fiona", "Haoyu", "Henry", "Jason", "Jenna",
    "Julia", "Keyu", "Lawrence", "Leslie", "Lucas", "Lukas", "Marco",
    "Max", "Nico", "Niya", "Panpan", "Selina", "Sophie", "Tiffany",
    "Victoria", "Vincent", "Yang", "Yanghao", "Yanxi", "Yebai"
]


def create_student_folders(names):
    # Zielverzeichnis definieren
    base_dir = "logs"

    # Sicherstellen, dass das Hauptverzeichnis existiert
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        print(f"Verzeichnis '{base_dir}' wurde erstellt.")

    # Ordner für jeden Schüler erstellen
    count = 0
    for name in names:
        # Pfad für den einzelnen Schüler-Ordner erstellen
        folder_path = os.path.join(base_dir, name)

        try:
            # Erstellt den Ordner (exist_ok=True verhindert Fehler, falls er schon da ist)
            os.makedirs(folder_path, exist_ok=True)
            count += 1
        except OSError as e:
            print(f"Fehler beim Erstellen von {folder_path}: {e}")

    print(f"Erfolg: {count} Ordner wurden im Verzeichnis '{base_dir}' erstellt.")


if __name__ == "__main__":
    create_student_folders(student_names)