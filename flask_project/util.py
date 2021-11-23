import hashlib
import random

from flask import (
    jsonify,
    session
)
import mysql.connector


def json_handler(success, data=None, message=None):
    '''Envuelve las respuestas de api'''
    response = {
        'success': success,
    }

    if data:
        response['data'] = data
    if message:
        response['message'] = message
    return jsonify(response)


def check_database_exists(db):
    '''revisa que exista la base de datos maraton'''
    if isinstance(db, mysql.connector.MySQLConnection):
        cursor = db.cursor()
        cursor.execute('SHOW DATABASES')
        data = cursor.fetchall()
        return ('Maraton',) in data
    else:
        raise Exception('Wrong data type')
        

def create_schema(db):
    cursor = db.cursor()

    # Aqui se hace el schema de las bd schema.sql
    with open('schema.sql', 'r') as schema_file:
        for line in schema_file.readlines():
            if line.startswith('--'): continue
            cursor.execute(str(line))
        schema_file.close()
    
    # Aqui se hace el dump de las preguntas desde dump.sql
    with open('dump.sql', 'r') as schema_file:
        for line in schema_file.readlines():
            if line.startswith('--'): continue
            cursor.execute(str(line))
            db.commit()
        schema_file.close()
    

def encrypt_MD5(value):
    enconded_value = str(value).encode()
    return hashlib.md5(enconded_value).hexdigest()


def register_user(email, password, db):
    '''Registra un usuario'''
    cursor = db.cursor()
    query = 'INSERT INTO usuario (email, password) VALUE(%s, %s)'
    values = (email, password)
    cursor.execute(query, values)
    db.commit()
    return cursor.lastrowid


def login_user(email, password, db):
    '''Ingreso de usuario'''
    cursor = db.cursor()
    query = f'SELECT id FROM usuario WHERE email=\'{email}\' AND password=\'{password}\''
    cursor.execute(query)
    data = cursor.fetchall()
    if data:
        return data[0][0]
    else:
        return None

def get_session_teams(session_id, db):
    cursor = db.cursor()
    cursor.execute(f'SELECT equipo.id, equipo.nombre FROM sesion LEFT JOIN \
        grupo ON sesion.grupo_id = grupo.id \
        LEFT JOIN equipo ON equipo.grupo_id = grupo.id \
        WHERE sesion.id = {session_id}'
    )
    data = cursor.fetchall()
    teams = [ {'id': r[0], 'name': r[1]} for r in data]

    # Se revuelven los equipos
    for i in range(len(teams)):
        newVal = random.randint(0, len(teams) - 1)
        oldVal = teams[i]
        teams[i] = teams[newVal]
        teams[newVal] = oldVal

    return teams

def get_group_by_id(group_id, db):
    cursor = db.cursor()
    cursor.execute(f'SELECT nombre, fecha_inicio, fecha_fin FROM grupo WHERE id = {group_id} LIMIT 1')
    data = cursor.fetchall()
    return {
        'nombre': data[0][0],
        'fecha_inicio': data[0][1],
        'fecha_fin': data[0][2]
    }

def get_exact_team_info_by_session(team_id, session_id, db):
    resultados = dict()
    queries = [
        (f'SELECT count(*) as `rondas_ganadas` FROM historial WHERE sesion_id={session_id} AND equipo_id={team_id} AND resultado=-2', 'ganadas'),
        (f'SELECT count(*) as `rondas_perdidas` FROM historial WHERE sesion_id={session_id} AND equipo_id={team_id} AND resultado=-1', 'perdidas'),
        (f'SELECT count(*) as `rondas_robadas` FROM historial WHERE sesion_id={session_id} AND resultado={team_id}', 'robadas')
    ]
    for query in queries:
        cursor = db.cursor()
        cursor.execute(query[0])
        data = cursor.fetchall()
        resultados[query[1]] = data[0][0]
    resultados['total'] = resultados['ganadas'] - resultados['perdidas'] + resultados['robadas']
    cursor.execute(f'SELECT integrantes FROM equipo WHERE id = {team_id}')
    data = cursor.fetchall()
    resultados['integrantes'] = data[0][0]
    return resultados

def get_question_qty(db):
    cursor = db.cursor()
    cursor.execute('SELECT count(*) FROM pregunta')
    data = cursor.fetchall()
    return data[0][0]

def is_question_taken(group_id, question_id, db):
    cursor = db.cursor()
    cursor.execute(
        f'''
            SELECT {question_id} IN (SELECT historial.pregunta_id FROM historial
            LEFT JOIN sesion ON historial.sesion_id= sesion.id
            LEFT JOIN grupo ON sesion.grupo_id = grupo.id
            WHERE grupo.id = {group_id}) as `preguntado`;
        '''
    )
    data = cursor.fetchall()
    return data[0][0]

def get_question_by_id(question_id, db):
    pregunta = dict()
    # Encontrar pregunta
    cursor = db.cursor()
    cursor.execute(f'SELECT * FROM pregunta WHERE id = {question_id}')
    data = cursor.fetchall()
    pregunta['id'] = data[0][0]
    pregunta['pregunta'] = data[0][1]
    pregunta['respuesta'] = data[0][2]

    # Encontrar tema
    cursor.execute(f'SELECT * FROM tema WHERE id = {data[0][3]}')
    data = cursor.fetchall()
    pregunta['tema'] = data [0][1]
    return pregunta

def generate_session_resume(session_id, db):
    pregunta = dict()
    # Encontrar pregunta
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT
        historial.id as `id`,
        equipo.nombre as `equipo`,
        pregunta.contenido as `pregunta`,
        (CASE
            WHEN historial.resultado = -1 THEN 'perdido'
            WHEN historial.resultado = -2 THEN 'ganado'
            ELSE (SELECT nombre FROM equipo WHERE id = historial.resultado LIMIT 1)
        END) AS `resultado`
        FROM historial
        LEFT JOIN pregunta ON historial.pregunta_id = pregunta.id
        LEFT JOIN equipo ON historial.equipo_id = equipo.id
        WHERE sesion_id = {session_id}
        ORDER BY id
    ''')
    data = cursor.fetchall()
    results = []
    for entry in data:
        newEntry = dict()
        for i, key in enumerate(['id', 'equipo', 'pregunta', 'resultado']):
            newEntry[key] = entry[i]
        results.append(newEntry)
    return results

def generate_group_resume(group_id, db):
    cursor = db.cursor()
    cursor.execute(f'''
        SELECT * FROM sesion
        WHERE sesion.grupo_id = {group_id}
        ORDER BY fecha_fin desc
    ''')
    sessions_id = cursor.fetchall()
    print(sessions_id)
    data = [generate_session_resume(session_id[0], db) for session_id in sessions_id]
    return data
    