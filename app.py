import psycopg2
import os
from flask import Flask, render_template, request, redirect, url_for, session
from functools import wraps
import bcrypt

app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)

# Função para criar uma nova conexão com o banco de dados
def get_db_connection():
    conn = psycopg2.connect(
        database="sistema_comandas_db",
        user="postgres",
        password="cd9oR2MwUWAKxBo3",
        host="inwardly-luxuriant-jewfish.data-1.use1.tembo.io",
        port="5432"
    )
    return conn

# Decorador para proteger as rotas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
    

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id_cliente, senha_hash FROM Cliente WHERE email = %s", (email,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result and bcrypt.checkpw(senha.encode('utf-8'), result[1].encode('utf-8')):
                session['user_id'] = result[0]
                return redirect('/fazer_pedido')
            else:
                return "Email ou senha incorretos", 400

        except Exception as e:
            return f"Erro ao fazer login: {str(e)}", 500

    return render_template('login.html')




@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']

        if not nome or not email or not telefone or not senha:
            return "Todos os campos são obrigatórios!", 400

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Cliente (nome, email, telefone, senha_hash)
                VALUES (%s, %s, %s, %s)
            """, (nome, email, telefone, senha_hash))
            conn.commit()
            cur.close()
            conn.close()
            return redirect('/login')
        except Exception as e:
            return f"Erro ao inserir dados: {str(e)}", 500

    return render_template('cadastro.html')
  

if __name__ == "__main__":
    app.run(debug=True)
