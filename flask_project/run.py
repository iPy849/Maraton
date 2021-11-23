import json
import os
import random

from flask import (
    Flask, 
    request,
    render_template,
    redirect,
    url_for,
    session
)
from flask_wtf import CSRFProtect
import mysql.connector

from config import DevelopmentConfig
import util

# app = Flask(__name__, template_folder='./templates')
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
csrf = CSRFProtect()

db = None

@app.before_request
@csrf.exempt
def before_request():
    global db
    json_file = open('db_confs.json', 'r')
    _confs = json.load(json_file)
    db = None
    try:
        db = mysql.connector.connect(
            host=_confs['host'],
            user=_confs['user'],
            password=_confs['password'],
            database='Maraton'
        )
    except Exception:
        db = mysql.connector.connect(
            host=_confs['host'],
            user=_confs['user'],
            password=_confs['password']
        )
        util.create_schema(db)
        logout()
    del json_file
    del _confs


@app.route('/')
def index():
    global db
    data = dict()
    if 'user_session' in session:
        data['auth_vars'] = session['user_session']
    if 'user_group' in session:
        data['user_group'] = session['user_group']
        data['group_info'] = util.get_group_by_id(session['user_group'], db) 
    if 'user_last_session' in session:
        data['user_last_session'] = session['user_last_session']
        data['teams'] = util.get_session_teams(
                            session['user_last_session'],
                            db
                        )
    return render_template('index.html', **data)

@app.route('/api/group', methods=['GET'])
def get_group_by_user_id():
    if not 'user_session' in session:
        return util.json_handler(False, message='No se ha iniciado sesion aun')
    else:
        global db
        user_id = session['user_session'][0]
        cursor = db.cursor()
        cursor.execute(f'SELECT nombre, id FROM grupo WHERE usuario_id = {user_id} AND fecha_fin IS NULL')
        data = cursor.fetchall()
        return util.json_handler(True, data={
            'grupos': list(data)
        },
        message='Se extrajeron los grupos exitosamente')

@app.route('/<int:group_id>', methods=['GET'])
def get_group_by_id(group_id):
    if 'user_last_session' in session:
        end_session()

    session['user_group'] = group_id
    global db
    # Inicia nueva sesion para el grupo y la mete en sessions junto con el id del grupo
    cursor = db.cursor()
    query = f'INSERT INTO sesion (grupo_id) VALUE({group_id})'
    cursor.execute(query)
    db.commit()
    session['user_last_session'] = cursor.lastrowid
    return redirect(url_for('index'))

@app.route('/change_db', methods=['POST'])
@csrf.exempt
def change_db_settings():
    '''Cambia la configuracion de la base de datos y crea el schema en caso de ser necesario'''
    host = request.form.get('host')
    user = request.form.get('user')
    password = request.form.get('password')

    message = 'Error, no has mandado todos los parametros'

    if not None in [host, user, password]:
        os.remove('db_confs.json')
        file = open('db_confs.json', 'w+')
        _confs_str = json.dumps({
            'host': host,
            'user': user,
            'password': password
        })
        file.write(_confs_str)
        file.close()
        message = 'Cambio de direccion y credenciales de base de datos, exito'
        
        db = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        if not util.check_database_exists(db):
            util.create_schema(db)
            message = 'Cambio de direccion y credenciales de base de datos, creacion de schema, exito'

    return redirect(url_for('index'))

@app.route('/api/check_user/<email>', methods=['GET'])
def check_user_exists(email):
    '''Checa que exista un usuario'''
    global db
    cursor = db.cursor()
    cursor.execute(f'SELECT email FROM usuario WHERE email = \'{email}\'')
    data = cursor.fetchall()
    return util.json_handler(
        True,
        data={
            'exists': len(data) != 0
        } 
    )

@app.route('/api/create_group', methods=['GET'])
def create_group():
    global db
    data = request.args.get('data')
    data = json.loads(data)
    user_id = session['user_session'][0]
    cursor = db.cursor()
    # Creando grupo
    query = 'INSERT INTO grupo (nombre, usuario_id) VALUE(%s, %s)'
    value = (data['name'], user_id)
    cursor.execute(query, value)
    db.commit()
    group_id = cursor.lastrowid
    message = 'Grupo creado exitosamente'
    # Creando equipos
    for team in data['teamList']:
        query = 'INSERT INTO equipo (nombre, integrantes, grupo_id) VALUE(%s, %s, %s)'
        value = (team[0], int(team[1]), group_id)
        cursor.execute(query, value)
        db.commit()
    message += ', equipos creados exitosamente'
    return util.json_handler(True, message=message)
    
@app.route('/api/getQuestion', methods=['GET'])
def get_question():
    global db
    question_qty = util.get_question_qty(db)
    question = None
    while 1:
        possible_questions = [random.randint(0, question_qty) for _ in range(50)]
        for question_id in possible_questions:
            if not util.is_question_taken(session['user_last_session'], question_id, db):
                question = util.get_question_by_id(question_id, db)
                break
        if not question is None: break
    return util.json_handler(True,
        data=question,
        message='Pregunta extraida correctamente'
    )

@app.route('/end_round', methods=['GET'])
def register_question():
    global db
    question_id = request.args.get('question_id')
    team_id = request.args.get('team_id')
    result = request.args.get('result')

    query = f'INSERT INTO historial (sesion_id, pregunta_id, equipo_id, resultado) VALUE(%s, %s, %s, %s)'
    value = (
        session['user_last_session'],
        question_id,
        team_id,
        result
    )
    cursor = db.cursor()
    cursor.execute(query, value)
    db.commit()
    return util.json_handler(True)

@app.route('/team_session_statistics', methods=['GET'])
def team_session_statistics():
    global db
    session_id = request.args.get('session_id')
    team_id = request.args.get('team_id')
    results = util.get_exact_team_info_by_session(team_id, session_id, db)
    return util.json_handler(True, data=results, message='Informacion de equipo-sesion recuperada')

        
@app.route('/auth', methods=['POST'])
def auth():
    global db
    email = request.form.get('user_email', None)
    password = request.form.get('user_password', None)
    operation = request.form.get('auth_operation', None)
    if None in (email, password, operation):
        return redirect(url_for('index'))

    id = 0
    if operation == 'login':
        id = util.login_user(email, password, db)
    elif operation == 'register':
        id = util.register_user(email, password, db)
    if not id is None: 
        session['user_session'] = [id, email]
    return redirect(url_for('index'))
    
@app.route('/logout', methods=['GET'])
def logout():
    keys = list(session.keys())
    for key in keys:
        if key in ('csrf_token'): continue
        session.pop(key)
    return redirect(url_for('index'))
    
@app.route('/end_session', methods=['GET'])
def end_session():
    global db
    cursor = db.cursor()
    current_session = session.pop('user_last_session')
    session.pop('user_group')
    sql = f'UPDATE sesion SET fecha_fin = NOW() WHERE id = {current_session}'
    cursor.execute(sql)
    db.commit()
    return redirect(url_for('index'))

@app.route('/end_group/<int:group_id>', methods=['GET'])
def end_group(group_id):
    global db
    session.pop('user_last_session')
    session.pop('user_group')
    cursor = db.cursor()
    sql = f'UPDATE grupo SET fecha_fin = NOW() WHERE id = {group_id}'
    cursor.execute(sql)
    db.commit()
    return redirect(url_for('index'))

@app.route('/api/session_historial', methods=['GET'])
def session_historial():
    global db
    session_id = session['user_last_session']
    return util.json_handler(True, data=util.generate_session_resume(session_id, db))

@app.route('/api/group_historial', methods=['GET'])
def group_historial():
    global db
    user_group = session['user_group']
    return util.json_handler(True, data=util.generate_group_resume(user_group, db))


if __name__ == '__main__':
    csrf.init_app(app)
    app.run(
        host='localhost',
        port=8080
    )