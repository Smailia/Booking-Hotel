import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "hotel.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    cursor = conn.cursor()

    cursor.executescript("""
        -- 1. Tipologie Camera
        CREATE TABLE IF NOT EXISTS Tipologie_Camera (
            ID_Tipologia    INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome            VARCHAR(50)  NOT NULL,
            Posti_Letto     INTEGER      NOT NULL,
            Descrizione     TEXT
        );

        -- 2. Camere
        CREATE TABLE IF NOT EXISTS Camere (
            ID_Camera       INTEGER PRIMARY KEY AUTOINCREMENT,
            Numero_Stanza   VARCHAR(10)  NOT NULL UNIQUE,
            Piano           INTEGER      NOT NULL,
            Stato           VARCHAR(20)  NOT NULL DEFAULT 'Libera'
                                CHECK(Stato IN ('Libera','Occupata','In Pulizia','Manutenzione')),
            FK_ID_Tipologia INTEGER      NOT NULL,
            FOREIGN KEY (FK_ID_Tipologia) REFERENCES Tipologie_Camera(ID_Tipologia)
        );

        -- 3. Tariffe Stagionali
        CREATE TABLE IF NOT EXISTS Tariffe_Stagionali (
            ID_Tariffa      INTEGER PRIMARY KEY AUTOINCREMENT,
            Data_Inizio     DATE         NOT NULL,
            Data_Fine       DATE         NOT NULL,
            Prezzo_Notte    REAL         NOT NULL CHECK(Prezzo_Notte > 0),
            FK_ID_Tipologia INTEGER      NOT NULL,
            FOREIGN KEY (FK_ID_Tipologia) REFERENCES Tipologie_Camera(ID_Tipologia)
        );

        -- 4. Ospiti
        CREATE TABLE IF NOT EXISTS Ospiti (
            ID_Ospite           INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome                VARCHAR(50)  NOT NULL,
            Cognome             VARCHAR(50)  NOT NULL,
            Email               VARCHAR(100) NOT NULL UNIQUE,
            Telefono            VARCHAR(20),
            Documento_Identita  VARCHAR(50)
        );

        -- 5. Canali Vendita
        CREATE TABLE IF NOT EXISTS Canali_Vendita (
            ID_Canale               INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome_Canale             VARCHAR(50) NOT NULL UNIQUE,
            Percentuale_Commissione REAL        NOT NULL DEFAULT 0
                                        CHECK(Percentuale_Commissione >= 0 AND Percentuale_Commissione <= 100)
        );

        -- 6. Prenotazioni
        CREATE TABLE IF NOT EXISTS Prenotazioni (
            ID_Prenotazione     INTEGER PRIMARY KEY AUTOINCREMENT,
            Data_CheckIn        DATE        NOT NULL,
            Data_CheckOut       DATE        NOT NULL,
            Stato_Prenotazione  VARCHAR(20) NOT NULL DEFAULT 'Confermata'
                                    CHECK(Stato_Prenotazione IN ('Confermata','Cancellata','Completata','In Attesa')),
            FK_ID_Ospite        INTEGER     NOT NULL,
            FK_ID_Camera        INTEGER     NOT NULL,
            FK_ID_Canale        INTEGER     NOT NULL,
            FOREIGN KEY (FK_ID_Ospite)  REFERENCES Ospiti(ID_Ospite),
            FOREIGN KEY (FK_ID_Camera)  REFERENCES Camere(ID_Camera),
            FOREIGN KEY (FK_ID_Canale)  REFERENCES Canali_Vendita(ID_Canale),
            CHECK(Data_CheckOut > Data_CheckIn)
        );

        -- 7. Pagamenti
        CREATE TABLE IF NOT EXISTS Pagamenti (
            ID_Pagamento        INTEGER PRIMARY KEY AUTOINCREMENT,
            Data_Pagamento      DATETIME    NOT NULL,
            Importo_Totale      REAL        NOT NULL CHECK(Importo_Totale > 0),
            Metodo_Pagamento    VARCHAR(30) NOT NULL
                                    CHECK(Metodo_Pagamento IN ('Carta di Credito','Contanti','Bonifico','PayPal')),
            FK_ID_Prenotazione  INTEGER     NOT NULL,
            FOREIGN KEY (FK_ID_Prenotazione) REFERENCES Prenotazioni(ID_Prenotazione)
        );

        -- 8. Servizi Extra
        CREATE TABLE IF NOT EXISTS Servizi_Extra (
            ID_Servizio     INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome_Servizio   VARCHAR(50) NOT NULL UNIQUE,
            Prezzo_Servizio REAL        NOT NULL CHECK(Prezzo_Servizio >= 0)
        );

        -- 9. Servizi Prenotati (tabella di giunzione N:M)
        CREATE TABLE IF NOT EXISTS Servizi_Prenotati (
            FK_ID_Prenotazione  INTEGER NOT NULL,
            FK_ID_Servizio      INTEGER NOT NULL,
            Quantita_Consumata  INTEGER NOT NULL DEFAULT 1 CHECK(Quantita_Consumata > 0),
            Data_Consumo        DATETIME NOT NULL,
            PRIMARY KEY (FK_ID_Prenotazione, FK_ID_Servizio),
            FOREIGN KEY (FK_ID_Prenotazione) REFERENCES Prenotazioni(ID_Prenotazione),
            FOREIGN KEY (FK_ID_Servizio)     REFERENCES Servizi_Extra(ID_Servizio)
        );

        -- 10. Staff Dipendenti
        CREATE TABLE IF NOT EXISTS Staff_Dipendenti (
            ID_Dipendente   INTEGER PRIMARY KEY AUTOINCREMENT,
            Nome            VARCHAR(50) NOT NULL,
            Cognome         VARCHAR(50) NOT NULL,
            Ruolo           VARCHAR(50) NOT NULL
                                CHECK(Ruolo IN ('Receptionist','Housekeeping','Manager','Concierge','Chef')),
            Turno           VARCHAR(20) NOT NULL
                                CHECK(Turno IN ('Mattina','Pomeriggio','Notte'))
        );

        -- 11. Registro Pulizie
        CREATE TABLE IF NOT EXISTS Registro_Pulizie (
            ID_Pulizia          INTEGER PRIMARY KEY AUTOINCREMENT,
            Data_Ora_Intervento DATETIME    NOT NULL,
            Stato_Pulizia       VARCHAR(20) NOT NULL DEFAULT 'In corso'
                                    CHECK(Stato_Pulizia IN ('In corso','Pulita','Da Pulire')),
            FK_ID_Camera        INTEGER     NOT NULL,
            FK_ID_Dipendente    INTEGER     NOT NULL,
            FOREIGN KEY (FK_ID_Camera)     REFERENCES Camere(ID_Camera),
            FOREIGN KEY (FK_ID_Dipendente) REFERENCES Staff_Dipendenti(ID_Dipendente)
        );

        -- 12. Recensioni
        CREATE TABLE IF NOT EXISTS Recensioni (
            ID_Recensione       INTEGER PRIMARY KEY AUTOINCREMENT,
            Punteggio_Stelle    INTEGER     NOT NULL CHECK(Punteggio_Stelle BETWEEN 1 AND 5),
            Commento            TEXT,
            Data_Recensione     DATE        NOT NULL,
            FK_ID_Prenotazione  INTEGER     NOT NULL UNIQUE,
            FOREIGN KEY (FK_ID_Prenotazione) REFERENCES Prenotazioni(ID_Prenotazione)
        );
    """)
    conn.commit()
    print("✅ Tabelle create con successo.")


def populate_tables(conn):
    cursor = conn.cursor()

    # --- Tipologie Camera ---
    tipologie = [
        ("Standard",  2, "Camera standard con letto matrimoniale e bagno privato."),
        ("Deluxe",    2, "Camera spaziosa con vista giardino e arredi eleganti."),
        ("Suite",     2, "Suite di lusso con salotto separato e vasca idromassaggio."),
        ("Family",    4, "Camera familiare con due letti e area giochi per bambini."),
        ("Junior Suite", 2, "Junior suite con angolo living e terrazzo privato."),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Tipologie_Camera (Nome, Posti_Letto, Descrizione) VALUES (?,?,?)",
        tipologie
    )

    # --- Camere ---
    camere = [
        ("101", 1, "Libera",       1),
        ("102", 1, "Occupata",     2),
        ("103", 1, "Libera",       1),
        ("201", 2, "Libera",       3),
        ("202", 2, "In Pulizia",   2),
        ("203", 2, "Libera",       4),
        ("301", 3, "Occupata",     5),
        ("302", 3, "Libera",       3),
        ("401", 4, "Libera",       4),
        ("402", 4, "Manutenzione", 1),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Camere (Numero_Stanza, Piano, Stato, FK_ID_Tipologia) VALUES (?,?,?,?)",
        camere
    )

    # --- Tariffe Stagionali ---
    tariffe = [
        ("2025-01-01", "2025-03-31",  80.00, 1),
        ("2025-04-01", "2025-06-30", 100.00, 1),
        ("2025-07-01", "2025-08-31", 130.00, 1),
        ("2025-09-01", "2025-12-31",  90.00, 1),
        ("2025-01-01", "2025-03-31", 110.00, 2),
        ("2025-04-01", "2025-06-30", 140.00, 2),
        ("2025-07-01", "2025-08-31", 180.00, 2),
        ("2025-01-01", "2025-12-31", 250.00, 3),
        ("2025-01-01", "2025-12-31", 150.00, 4),
        ("2025-01-01", "2025-12-31", 200.00, 5),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Tariffe_Stagionali (Data_Inizio, Data_Fine, Prezzo_Notte, FK_ID_Tipologia) VALUES (?,?,?,?)",
        tariffe
    )

    # --- Ospiti ---
    ospiti = [
        ("Mario",    "Rossi",     "mario.rossi@email.it",    "3331234567", "CI AB1234567"),
        ("Giulia",   "Bianchi",   "giulia.bianchi@email.it", "3479876543", "PA CD8765432"),
        ("Luca",     "Verdi",     "luca.verdi@email.it",     "3201112233", "CI EF1122334"),
        ("Anna",     "Ferrari",   "anna.ferrari@email.it",   "3884445566", "PA GH4455667"),
        ("Marco",    "Conti",     "marco.conti@email.it",    "3557778899", "CI IL7788990"),
        ("Sofia",    "Ricci",     "sofia.ricci@email.it",    "3110001122", "PA MN0011223"),
        ("Paolo",    "Mancini",   "paolo.mancini@email.it",  "3663334455", "CI OP3344556"),
        ("Elena",    "Gallo",     "elena.gallo@email.it",    "3996667788", "PA QR6677889"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Ospiti (Nome, Cognome, Email, Telefono, Documento_Identita) VALUES (?,?,?,?,?)",
        ospiti
    )

    # --- Canali Vendita ---
    canali = [
        ("Sito Diretto",   0.00),
        ("Booking.com",   15.00),
        ("Expedia",       18.00),
        ("Airbnb",        12.00),
        ("Telefono",       0.00),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Canali_Vendita (Nome_Canale, Percentuale_Commissione) VALUES (?,?)",
        canali
    )

    # --- Prenotazioni ---
    prenotazioni = [
        ("2025-06-01", "2025-06-05", "Confermata",  1, 1, 1),
        ("2025-06-10", "2025-06-14", "Confermata",  2, 2, 2),
        ("2025-07-01", "2025-07-07", "Confermata",  3, 3, 3),
        ("2025-07-15", "2025-07-20", "Confermata",  4, 4, 1),
        ("2025-08-01", "2025-08-10", "Confermata",  5, 5, 4),
        ("2025-05-01", "2025-05-03", "Completata",  6, 6, 2),
        ("2025-05-10", "2025-05-12", "Completata",  7, 7, 1),
        ("2025-04-20", "2025-04-22", "Cancellata",  8, 8, 3),
    ]
    cursor.executemany(
        """INSERT OR IGNORE INTO Prenotazioni
           (Data_CheckIn, Data_CheckOut, Stato_Prenotazione, FK_ID_Ospite, FK_ID_Camera, FK_ID_Canale)
           VALUES (?,?,?,?,?,?)""",
        prenotazioni
    )

    # --- Pagamenti ---
    pagamenti = [
        ("2025-06-01 14:00:00", 400.00, "Carta di Credito", 1),
        ("2025-06-10 15:30:00", 560.00, "PayPal",           2),
        ("2025-07-01 12:00:00", 900.00, "Carta di Credito", 3),
        ("2025-07-15 16:00:00", 750.00, "Contanti",         4),
        ("2025-08-01 11:00:00",1170.00, "Bonifico",         5),
        ("2025-05-01 09:00:00", 160.00, "Carta di Credito", 6),
        ("2025-05-10 10:00:00", 160.00, "Contanti",         7),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Pagamenti (Data_Pagamento, Importo_Totale, Metodo_Pagamento, FK_ID_Prenotazione) VALUES (?,?,?,?)",
        pagamenti
    )

    # --- Servizi Extra ---
    servizi = [
        ("Colazione",          15.00),
        ("Parcheggio",         10.00),
        ("Spa",                50.00),
        ("Transfer Aeroporto", 35.00),
        ("Noleggio Bici",      20.00),
        ("Lavanderia",         25.00),
        ("Baby Sitter",        30.00),
        ("Cena Romantica",     80.00),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Servizi_Extra (Nome_Servizio, Prezzo_Servizio) VALUES (?,?)",
        servizi
    )

    # --- Servizi Prenotati ---
    servizi_prenotati = [
        (1, 1, 4, "2025-06-02 08:00:00"),
        (1, 2, 4, "2025-06-02 09:00:00"),
        (2, 1, 4, "2025-06-11 08:00:00"),
        (2, 3, 1, "2025-06-12 10:00:00"),
        (3, 1, 6, "2025-07-02 08:00:00"),
        (3, 4, 2, "2025-07-01 18:00:00"),
        (4, 5, 3, "2025-07-16 09:00:00"),
        (5, 7, 2, "2025-08-03 20:00:00"),
    ]
    cursor.executemany(
        """INSERT OR IGNORE INTO Servizi_Prenotati
           (FK_ID_Prenotazione, FK_ID_Servizio, Quantita_Consumata, Data_Consumo)
           VALUES (?,?,?,?)""",
        servizi_prenotati
    )

    # --- Staff Dipendenti ---
    staff = [
        ("Francesca", "Neri",    "Receptionist", "Mattina"),
        ("Roberto",   "Bruno",   "Housekeeping", "Mattina"),
        ("Chiara",    "Costa",   "Receptionist", "Pomeriggio"),
        ("Antonio",   "Russo",   "Manager",      "Mattina"),
        ("Valentina", "Marino",  "Concierge",    "Pomeriggio"),
        ("Davide",    "Esposito","Housekeeping",  "Notte"),
        ("Laura",     "Romano",  "Chef",         "Mattina"),
        ("Simone",    "Colombo", "Housekeeping", "Pomeriggio"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO Staff_Dipendenti (Nome, Cognome, Ruolo, Turno) VALUES (?,?,?,?)",
        staff
    )

    # --- Registro Pulizie ---
    pulizie = [
        ("2025-05-20 09:00:00", "Pulita",   1, 2),
        ("2025-05-20 10:00:00", "Pulita",   3, 2),
        ("2025-05-20 11:00:00", "In corso", 5, 8),
        ("2025-05-19 09:00:00", "Pulita",   2, 6),
        ("2025-05-19 10:30:00", "Pulita",   4, 2),
        ("2025-05-18 14:00:00", "Pulita",   6, 8),
        ("2025-05-21 09:00:00", "Da Pulire",7, 2),
    ]
    cursor.executemany(
        """INSERT OR IGNORE INTO Registro_Pulizie
           (Data_Ora_Intervento, Stato_Pulizia, FK_ID_Camera, FK_ID_Dipendente)
           VALUES (?,?,?,?)""",
        pulizie
    )

    # --- Recensioni ---
    recensioni = [
        (5, "Soggiorno eccellente, staff gentilissimo!",         "2025-05-03", 6),
        (4, "Camera pulita e comoda, colazione ottima.",          "2025-05-12", 7),
    ]
    cursor.executemany(
        """INSERT OR IGNORE INTO Recensioni
           (Punteggio_Stelle, Commento, Data_Recensione, FK_ID_Prenotazione)
           VALUES (?,?,?,?)""",
        recensioni
    )

    conn.commit()
    print("✅ Dati di esempio inseriti con successo.")


if __name__ == "__main__":
    # Se il DB esiste già, lo elimina per ripartire puliti
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🗑️  Database precedente eliminato.")

    conn = get_connection()
    create_tables(conn)
    populate_tables(conn)
    conn.close()
    print(f"✅ Database pronto in: {DB_PATH}")
