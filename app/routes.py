import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, session , flash
from functools import wraps
import bcrypt
from flask import flash, redirect, render_template

main = Blueprint('main', __name__)

def get_db_connection():
    conn = psycopg2.connect(
        database="sistema_comandas_db",
        user="postgres",
        password="cd9oR2MwUWAKxBo3",
        host="inwardly-luxuriant-jewfish.data-1.use1.tembo.io",
        port="5432"
    )
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        # Verificar se as credenciais correspondem ao administrador
        if email == 'admin@admin' and senha == 'admin':
            session['user_id'] = 'admin'  # Use um identificador especial para o admin
            return redirect('/admin/dashboard')  # Redirecionar para a página de administração

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

@main.route('/cadastro', methods=['GET', 'POST'])
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

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_id') == 'admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect('/login')  # Redirecionar para o login se não for admin

@main.route('/admin/clientes', methods=['GET'])
@login_required
def listar_clientes():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM Cliente")
        clientes = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('listar_clientes.html', clientes=clientes)
    except Exception as e:
        return f"Erro ao listar clientes: {str(e)}", 500

@main.route('/admin/pedidos', methods=['GET'])
@login_required
def listar_pedidos_admin():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT p.id_pedido, c.nome, p.data_pedido, p.valor_total
            FROM Pedido p
            JOIN Cliente c ON p.id_cliente = c.id_cliente
        """)
        pedidos = cur.fetchall()
        cur.close()
        conn.close()

        return render_template('listar_pedidos.html', pedidos=pedidos)
    except Exception as e:
        return f"Erro ao listar pedidos: {str(e)}", 500
    
@main.route('/admin/produtos', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        descricao = request.form['descricao']

        if not nome or not preco or not descricao:
            return "Todos os campos são obrigatórios!", 400

        try:
            preco = float(preco)
        except ValueError:
            return "O preço deve ser um número válido!", 400

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO Produto (nome, preco, descricao)
                        VALUES (%s, %s, %s)
                    """, (nome, preco, descricao))
                    conn.commit()

            return render_template('cadastrar_produto.html', success=True)
        except Exception as e:
            return render_template('cadastrar_produto.html', error=str(e))

    return render_template('cadastrar_produto.html')   

main.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')  