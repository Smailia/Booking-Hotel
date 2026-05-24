from flask import Flask, jsonify, request
from flask_cors import CORS
from database import get_connection

app = Flask(__name__)
CORS(app)

# ===== CAMERE =====
@app.route('/api/camere', methods=['GET'])
def lista_camere():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, t.Nome AS nome_tipologia, t.Posti_Letto, t.Descrizione
            FROM Camera c
            JOIN Tipologie_Camera t ON c.FK_ID_Tipologia = t.ID_Tipologia
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/camere/<int:id>', methods=['GET'])
def dettaglio_camera(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.*, t.Nome AS nome_tipologia, t.Posti_Letto, t.Descrizione
            FROM Camera c
            JOIN Tipologie_Camera t ON c.FK_ID_Tipologia = t.ID_Tipologia
            WHERE c.ID_Camera = %s
        """, (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result is None:
            return jsonify({"errore": "Camera non trovata"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/camere', methods=['POST'])
def nuova_camera():
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Camera (Numero_Stanza, Piano, Stato, FK_ID_Tipologia) VALUES (%s, %s, %s, %s)",
            (dati['Numero_Stanza'], dati['Piano'], dati['Stato'], dati['FK_ID_Tipologia'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Camera creata"}), 201
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/camere/<int:id>', methods=['PUT'])
def modifica_camera(id):
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Camera SET Numero_Stanza=%s, Piano=%s, Stato=%s, FK_ID_Tipologia=%s WHERE ID_Camera=%s",
            (dati['Numero_Stanza'], dati['Piano'], dati['Stato'], dati['FK_ID_Tipologia'], id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Camera modificata"}), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/camere/<int:id>', methods=['DELETE'])
def elimina_camera(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Registro_Pulizie WHERE FK_ID_Camera = %s", (id,))
        cursor.execute("DELETE FROM Servizi_Prenotati WHERE FK_ID_Prenotazione IN (SELECT ID_Prenotazione FROM Prenotazioni WHERE FK_ID_Camera = %s)", (id,))
        cursor.execute("DELETE FROM Pagamenti WHERE FK_ID_Prenotazione IN (SELECT ID_Prenotazione FROM Prenotazioni WHERE FK_ID_Camera = %s)", (id,))
        cursor.execute("DELETE FROM Recensioni WHERE FK_ID_Prenotazione IN (SELECT ID_Prenotazione FROM Prenotazioni WHERE FK_ID_Camera = %s)", (id,))
        cursor.execute("DELETE FROM Prenotazioni WHERE FK_ID_Camera = %s", (id,))
        cursor.execute("DELETE FROM Camera WHERE ID_Camera = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Camera eliminata"}), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== TIPOLOGIE CAMERA =====
@app.route('/api/tipologie', methods=['GET'])
def lista_tipologie():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Tipologie_Camera")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== OSPITI =====
@app.route('/api/ospiti', methods=['GET'])
def lista_ospiti():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Ospiti")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/ospiti/<int:id>', methods=['GET'])
def dettaglio_ospite(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Ospiti WHERE ID_Ospite = %s", (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result is None:
            return jsonify({"errore": "Ospite non trovato"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/ospiti', methods=['POST'])
def nuovo_ospite():
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Ospiti (Nome, Cognome, Email, Telefono, Documento_Identita) VALUES (%s, %s, %s, %s, %s)",
            (dati['Nome'], dati['Cognome'], dati['Email'], dati['Telefono'], dati['Documento_Identita'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Ospite creato"}), 201
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/ospiti/<int:id>', methods=['PUT'])
def modifica_ospite(id):
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Ospiti SET Nome=%s, Cognome=%s, Email=%s, Telefono=%s, Documento_Identita=%s WHERE ID_Ospite=%s",
            (dati['Nome'], dati['Cognome'], dati['Email'], dati['Telefono'], dati['Documento_Identita'], id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Ospite modificato"}), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/ospiti/<int:id>', methods=['DELETE'])
def elimina_ospite(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Servizi_Prenotati WHERE FK_ID_Prenotazione IN (SELECT ID_Prenotazione FROM Prenotazioni WHERE FK_ID_Ospite = %s)", (id,))
        cursor.execute("DELETE FROM Pagamenti WHERE FK_ID_Prenotazione IN (SELECT ID_Prenotazione FROM Prenotazioni WHERE FK_ID_Ospite = %s)", (id,))
        cursor.execute("DELETE FROM Recensioni WHERE FK_ID_Prenotazione IN (SELECT ID_Prenotazione FROM Prenotazioni WHERE FK_ID_Ospite = %s)", (id,))
        cursor.execute("DELETE FROM Prenotazioni WHERE FK_ID_Ospite = %s", (id,))
        cursor.execute("DELETE FROM Ospiti WHERE ID_Ospite = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Ospite eliminato"}), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== PRENOTAZIONI =====
@app.route('/api/prenotazioni', methods=['GET'])
def lista_prenotazioni():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, o.Nome AS nome_ospite, o.Cognome AS cognome_ospite,
                   c.Numero_Stanza
            FROM Prenotazioni p
            JOIN Ospiti o ON p.FK_ID_Ospite = o.ID_Ospite
            JOIN Camera c ON p.FK_ID_Camera = c.ID_Camera
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/prenotazioni/<int:id>', methods=['GET'])
def dettaglio_prenotazione(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.*, o.Nome AS nome_ospite, o.Cognome AS cognome_ospite,
                   c.Numero_Stanza
            FROM Prenotazioni p
            JOIN Ospiti o ON p.FK_ID_Ospite = o.ID_Ospite
            JOIN Camera c ON p.FK_ID_Camera = c.ID_Camera
            WHERE p.ID_Prenotazione = %s
        """, (id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result is None:
            return jsonify({"errore": "Prenotazione non trovata"}), 404
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/prenotazioni', methods=['POST'])
def nuova_prenotazione():
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO Prenotazioni 
            (Data_CheckIn, Data_CheckOut, Stato_Prenotazione, FK_ID_Ospite, FK_ID_Camera, FK_ID_Canale) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (dati['Data_CheckIn'], dati['Data_CheckOut'], dati['Stato_Prenotazione'],
             dati['FK_ID_Ospite'], dati['FK_ID_Camera'], dati['FK_ID_Canale'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Prenotazione creata"}), 201
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/prenotazioni/<int:id>', methods=['PUT'])
def modifica_prenotazione(id):
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE Prenotazioni SET Data_CheckIn=%s, Data_CheckOut=%s, 
            Stato_Prenotazione=%s WHERE ID_Prenotazione=%s""",
            (dati['Data_CheckIn'], dati['Data_CheckOut'], dati['Stato_Prenotazione'], id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Prenotazione modificata"}), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/prenotazioni/<int:id>', methods=['DELETE'])
def elimina_prenotazione(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Servizi_Prenotati WHERE FK_ID_Prenotazione = %s", (id,))
        cursor.execute("DELETE FROM Pagamenti WHERE FK_ID_Prenotazione = %s", (id,))
        cursor.execute("DELETE FROM Recensioni WHERE FK_ID_Prenotazione = %s", (id,))
        cursor.execute("DELETE FROM Prenotazioni WHERE ID_Prenotazione = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Prenotazione eliminata"}), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== RECENSIONI =====
@app.route('/api/recensioni', methods=['GET'])
def lista_recensioni():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT r.*, o.Nome AS nome_ospite, o.Cognome AS cognome_ospite
            FROM Recensioni r
            JOIN Prenotazioni p ON r.FK_ID_Prenotazione = p.ID_Prenotazione
            JOIN Ospiti o ON p.FK_ID_Ospite = o.ID_Ospite
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

@app.route('/api/recensioni', methods=['POST'])
def nuova_recensione():
    try:
        dati = request.get_json()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Recensioni (Punteggio_Stelle, Commento, Data_Recensione, FK_ID_Prenotazione) VALUES (%s, %s, %s, %s)",
            (dati['Punteggio_Stelle'], dati['Commento'], dati['Data_Recensione'], dati['FK_ID_Prenotazione'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"messaggio": "Recensione aggiunta"}), 201
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== STAFF =====
@app.route('/api/staff', methods=['GET'])
def lista_staff():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Staff_Dipendenti")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== PAGAMENTI =====
@app.route('/api/pagamenti', methods=['GET'])
def lista_pagamenti():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT pg.*, o.Nome AS nome_ospite, o.Cognome AS cognome_ospite
            FROM Pagamenti pg
            JOIN Prenotazioni p ON pg.FK_ID_Prenotazione = p.ID_Prenotazione
            JOIN Ospiti o ON p.FK_ID_Ospite = o.ID_Ospite
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== TARIFFE STAGIONALI =====
@app.route('/api/tariffe', methods=['GET'])
def lista_tariffe():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.*, tc.Nome AS nome_tipologia
            FROM Tariffe_Stagionali t
            JOIN Tipologie_Camera tc ON t.FK_ID_Tipologia = tc.ID_Tipologia
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== SERVIZI EXTRA =====
@app.route('/api/servizi', methods=['GET'])
def lista_servizi():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Servizi_Extra")
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

# ===== REGISTRO PULIZIE =====
@app.route('/api/pulizie', methods=['GET'])
def lista_pulizie():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT rp.*, c.Numero_Stanza,
                   sd.Nome AS nome_dipendente, sd.Cognome AS cognome_dipendente
            FROM Registro_Pulizie rp
            JOIN Camera c ON rp.FK_ID_Camera = c.ID_Camera
            JOIN Staff_Dipendenti sd ON rp.FK_ID_Dipendente = sd.ID_Dipendente
        """)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"errore": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)