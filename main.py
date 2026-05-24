import mysql.connector

config = {
    'user': 'avnadmin',
    'password': 'AVNS_ZnIxYxJ3qVFJSrFoVoi',
    'host': 'booking-booking-hotel.j.aivencloud.com',
    'port': 22884, 
    'database': 'defaultdb',
    'ssl_ca': 'ca.pem' 
}

try:
    connection = mysql.connector.connect(**config)
    if connection.is_connected():
        print("Connesso a MySQL di Aiven con successo!")
        cursor = connection.cursor()
        
        # Lista di query SQL ordinate per dipendenza di chiavi esterne
        queries_tabelle = [
            # 1. Tipologie_Camera
            """
            CREATE TABLE IF NOT EXISTS Tipologie_Camera (
                ID_Tipologia INT AUTO_INCREMENT PRIMARY KEY,
                Nome VARCHAR(50) NOT NULL,
                Posti_Letto INT NOT NULL,
                Descrizione TEXT
            );
            """,
            
            # 2. Camere (Dipende da Tipologie_Camera)
            """
            CREATE TABLE IF NOT EXISTS Camera (
                ID_Camera INT AUTO_INCREMENT PRIMARY KEY,
                Numero_Stanza VARCHAR(10) NOT NULL,
                Piano INT NOT NULL,
                Stato VARCHAR(20) NOT NULL,
                FK_ID_Tipologia INT,
                FOREIGN KEY (FK_ID_Tipologia) REFERENCES Tipologie_Camera(ID_Tipologia) ON DELETE SET NULL
            );
            """,
            
            # 3. Tariffe_Stagionali (Dipende da Tipologie_Camera)
            """
            CREATE TABLE IF NOT EXISTS Tariffe_Stagionali (
                ID_Tariffa INT AUTO_INCREMENT PRIMARY KEY,
                Data_Inizio DATE NOT NULL,
                Data_Fine DATE NOT NULL,
                Prezzo_Notte DECIMAL(10,2) NOT NULL,
                FK_ID_Tipologia INT,
                FOREIGN KEY (FK_ID_Tipologia) REFERENCES Tipologie_Camera(ID_Tipologia) ON DELETE CASCADE
            );
            """,
            
            # 4. Staff_Dipendenti
            """
            CREATE TABLE IF NOT EXISTS Staff_Dipendenti (
                ID_Dipendente INT AUTO_INCREMENT PRIMARY KEY,
                Nome VARCHAR(50) NOT NULL,
                Cognome VARCHAR(50) NOT NULL,
                Ruolo VARCHAR(50) NOT NULL,
                Turno VARCHAR(20)
            );
            """,
            
            # 5. Ospiti
            """
            CREATE TABLE IF NOT EXISTS Ospiti (
                ID_Ospite INT AUTO_INCREMENT PRIMARY KEY,
                Nome VARCHAR(50) NOT NULL,
                Cognome VARCHAR(50) NOT NULL,
                Email VARCHAR(100) UNIQUE NOT NULL,
                Telefono VARCHAR(20),
                Documento_Identita VARCHAR(50) NOT NULL
            );
            """,
            
            # 6. Canali_Vendita
            """
            CREATE TABLE IF NOT EXISTS Canali_Vendita (
                ID_Canale INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Canale VARCHAR(50) NOT NULL,
                Percentuale_Commissione DECIMAL(4,2) NOT NULL
            );
            """,
            
            # 7. Servizi_Extra
            """
            CREATE TABLE IF NOT EXISTS Servizi_Extra (
                ID_Servizio INT AUTO_INCREMENT PRIMARY KEY,
                Nome_Servizio VARCHAR(50) NOT NULL,
                Prezzo_Servizio DECIMAL(10,2) NOT NULL
            );
            """,
            
            # 8. Registro_Pulizie (Dipende da Camera e Staff_Dipendenti)
            """
            CREATE TABLE IF NOT EXISTS Registro_Pulizie (
                ID_Pulizia INT AUTO_INCREMENT PRIMARY KEY,
                Data_Ora_Intervento DATETIME NOT NULL,
                Stato_Pulizia VARCHAR(20) NOT NULL,
                FK_ID_Camera INT,
                FK_ID_Dipendente INT,
                FOREIGN KEY (FK_ID_Camera) REFERENCES Camera(ID_Camera) ON DELETE CASCADE,
                FOREIGN KEY (FK_ID_Dipendente) REFERENCES Staff_Dipendenti(ID_Dipendente) ON DELETE SET NULL
            );
            """,
            
            # 9. Prenotazioni (Dipende da Ospiti, Camera e Canali_Vendita)
            """
            CREATE TABLE IF NOT EXISTS Prenotazioni (
                ID_Prenotazione INT AUTO_INCREMENT PRIMARY KEY,
                Data_CheckIn DATE NOT NULL,
                Data_CheckOut DATE NOT NULL,
                Stato_Prenotazione VARCHAR(20) NOT NULL,
                FK_ID_Ospite INT,
                FK_ID_Camera INT,
                FK_ID_Canale INT,
                FOREIGN KEY (FK_ID_Ospite) REFERENCES Ospiti(ID_Ospite) ON DELETE CASCADE,
                FOREIGN KEY (FK_ID_Camera) REFERENCES Camera(ID_Camera) ON DELETE CASCADE,
                FOREIGN KEY (FK_ID_Canale) REFERENCES Canali_Vendita(ID_Canale) ON DELETE SET NULL
            );
            """,
            
            # 10. Pagamenti (Dipende da Prenotazioni)
            """
            CREATE TABLE IF NOT EXISTS Pagamenti (
                ID_Pagamento INT AUTO_INCREMENT PRIMARY KEY,
                Data_Pagamento DATETIME NOT NULL,
                Importo_Totale DECIMAL(10,2) NOT NULL,
                Metodo_Pagamento VARCHAR(30) NOT NULL,
                FK_ID_Prenotazione INT,
                FOREIGN KEY (FK_ID_Prenotazione) REFERENCES Prenotazioni(ID_Prenotazione) ON DELETE CASCADE
            );
            """,
            
            # 11. Recensioni (Dipende da Prenotazioni)
            """
            CREATE TABLE IF NOT EXISTS Recensioni (
                ID_Recensione INT AUTO_INCREMENT PRIMARY KEY,
                Punteggio_Stelle INT NOT NULL CHECK (Punteggio_Stelle BETWEEN 1 AND 5),
                Commento TEXT,
                Data_Recensione DATE NOT NULL,
                FK_ID_Prenotazione INT,
                FOREIGN KEY (FK_ID_Prenotazione) REFERENCES Prenotazioni(ID_Prenotazione) ON DELETE CASCADE
            );
            """,
            
            # 12. Servizi_Prenotati (Tabella di giunzione N:M con Chiave Primaria Composta)
            """
            CREATE TABLE IF NOT EXISTS Servizi_Prenotati (
                FK_ID_Prenotazione INT,
                FK_ID_Servizio INT,
                Quantita_Consumata INT NOT NULL DEFAULT 1,
                Data_Consumo DATETIME NOT NULL,
                PRIMARY KEY (FK_ID_Prenotazione, FK_ID_Servizio),
                FOREIGN KEY (FK_ID_Prenotazione) REFERENCES Prenotazioni(ID_Prenotazione) ON DELETE CASCADE,
                FOREIGN KEY (FK_ID_Servizio) REFERENCES Servizi_Extra(ID_Servizio) ON DELETE CASCADE
            );
            """
        ]
        
        # Esecuzione sequenziale delle query
        print("Inizio creazione delle tabelle del database...")
        for i, query in enumerate(queries_tabelle, 1):
            cursor.execute(query)
            
        print("Tutte le 12 tabelle sono state verificate/create con successo!")
        
        # Mostra la lista finale per conferma
        cursor.execute("SHOW TABLES;")
        tabelle = cursor.fetchall()
        print("\nTabelle attualmente presenti nel tuo database Aiven:")
        for t in tabelle:
            print(f"- {t[0]}")
            
        # Chiudiamo in sicurezza
        cursor.close()
        connection.close()
        print("\nConnessione chiusa in sicurezza.")

except Exception as e:
    print(f"Errore durante l'esecuzione del codice: {e}")