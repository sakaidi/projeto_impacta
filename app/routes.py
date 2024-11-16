import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps
import bcrypt
import logging
from flask import current_app

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
            flash("Você precisa estar logado para acessar esta página.", "error")
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
        
        if email == 'admin@admin' and senha == 'admin':
            session['user_id'] = 'admin'
            session['is_admin'] = True
            return redirect('/admin/dashboard')

        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id_cliente, senha_hash FROM Cliente WHERE email = %s", (email,))
            result = cur.fetchone()
            cur.close()
            conn.close()

            if result and bcrypt.checkpw(senha.encode('utf-8'), result[1].encode('utf-8')):
                session['user_id'] = result[0]
                session['is_admin'] = False
                return redirect('/fazer_pedido')
            else:
                flash("Email ou senha incorretos", "error")
                return redirect(url_for('main.login'))

        except Exception as e:
            flash(f"Erro ao fazer login: {str(e)}", "error")
            return redirect(url_for('main.login'))

    return render_template('login.html')

@main.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        telefone = request.form['telefone']
        senha = request.form['senha']

        if not nome or not email or not telefone or not senha:
            flash("Todos os campos são obrigatórios!", "error")
            return redirect(url_for('main.cadastro'))

        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO Cliente (nome, email, telefone, senha_hash)
                        VALUES (%s, %s, %s, %s)
                    """, (nome, email, telefone, senha_hash))
                    conn.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect('/login')
        except Exception as e:
            flash(f"Erro ao inserir dados: {str(e)}", "error")
            return redirect(url_for('main.cadastro'))

    return render_template('cadastro.html')

@main.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('user_id') == 'admin':
        return render_template('admin_dashboard.html')
    else:
        return redirect('/login')

@main.route('/admin/clientes', methods=['GET'])
@login_required
def listar_clientes():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Cliente")
                clientes = cur.fetchall()
        return render_template('partials/listar_clientes.html', clientes=clientes)
    except Exception as e:
        print(f"Erro ao listar clientes: {str(e)}")  # Log de erro no console
        return f"Erro ao listar clientes: {str(e)}", 500

@main.route('/admin/pedidos', methods=['GET'])
@login_required
def listar_pedidos_admin():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id_pedido, c.nome AS cliente_nome, p.data_pedido, p.valor_total, p.status
                    FROM Pedido p
                    JOIN Cliente c ON p.id_cliente = c.id_cliente
                """)
                pedidos = cur.fetchall()

                pedidos_detalhados = []
                for pedido in pedidos:
                    id_pedido = pedido[0]
                    cur.execute("""
                        SELECT pr.nome, ip.quantidade, ip.preco_unitario
                        FROM ItemPedido ip
                        JOIN Produto pr ON ip.id_produto = pr.id_produto
                        WHERE ip.id_pedido = %s
                    """, (id_pedido,))
                    itens = cur.fetchall()

                    pedidos_detalhados.append({
                        'id_pedido': id_pedido,
                        'cliente_nome': pedido[1],
                        'data_pedido': pedido[2],
                        'valor_total': pedido[3],
                        'status': pedido[4],
                        'itens': itens
                    })

        return render_template('partials/listar_pedidos.html', pedidos=pedidos_detalhados)

    except Exception as e:
        flash(f"Erro ao listar pedidos: {str(e)}", "error")
        return redirect(url_for('main.admin_dashboard'))

@main.route('/admin/produtos', methods=['GET', 'POST'])
@login_required
def cadastrar_produto():
    if request.method == 'POST':
        nome = request.form['nome']
        preco = request.form['preco']
        descricao = request.form['descricao']

        if not nome or not preco or not descricao:
            flash("Todos os campos são obrigatórios!", "error")
            return redirect(url_for('main.cadastrar_produto'))

        try:
            preco = float(preco)
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO Produto (nome, preco, descricao)
                        VALUES (%s, %s, %s)
                    """, (nome, preco, descricao))
                    conn.commit()

            flash("Produto cadastrado com sucesso!", "success")
            return render_template('partials/produto_cadastrado.html', nome=nome)
        except ValueError:
            flash("O preço deve ser um número válido!", "error")
            return redirect(url_for('main.cadastrar_produto'))
        except Exception as e:
            flash(f"Erro ao cadastrar produto: {str(e)}", "error")
            return redirect(url_for('main.cadastrar_produto'))

    return render_template('partials/cadastrar_produto.html')

@main.route('/fazer_pedido', methods=['GET', 'POST'])
@login_required
def fazer_pedido():
    id_cliente = session['user_id']
    
    if request.method == 'POST':
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO Pedido (id_cliente) VALUES (%s) RETURNING id_pedido
                    """, (id_cliente,))
                    id_pedido = cur.fetchone()[0]
                    conn.commit()
            return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_pedido))
        except Exception as e:
            flash(f"Erro ao criar pedido: {str(e)}", "error")
            return redirect(url_for('main.fazer_pedido'))

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT p.id_pedido, p.data_pedido, p.status, p.valor_total
                    FROM Pedido p
                    WHERE p.id_cliente = %s
                """, (id_cliente,))
                pedidos = cur.fetchall()

        return render_template('fazer_pedido.html', pedidos=pedidos, id_cliente=id_cliente)

    except Exception as e:
        logging.error(f"Erro ao buscar pedidos: {str(e)}")
        flash("Erro ao buscar pedidos. Tente novamente.", "error")
        return redirect(url_for('main.index'))

@main.route('/pedido/<int:id_pedido>/itens', methods=['GET', 'POST'])
@login_required
def adicionar_itens_pedido(id_pedido):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id_produto, nome, preco FROM Produto")
                produtos = cur.fetchall()

                cur.execute("""
                    SELECT ip.id_item_pedido, p.nome, ip.quantidade, ip.preco_unitario
                    FROM ItemPedido ip
                    JOIN Produto p ON ip.id_produto = p.id_produto
                    WHERE ip.id_pedido = %s
                """, (id_pedido,))
                itens_adicionados = cur.fetchall()

                if request.method == 'POST':
                    if 'adicionar' in request.form:
                        id_produto = request.form['id_produto']
                        quantidade = request.form['quantidade']

                        cur.execute("SELECT preco FROM Produto WHERE id_produto = %s", (id_produto,))
                        preco_unitario = cur.fetchone()[0]

                        cur.execute("""
                            INSERT INTO ItemPedido (id_pedido, id_produto, quantidade, preco_unitario)
                            VALUES (%s, %s, %s, %s)
                        """, (id_pedido, id_produto, quantidade, preco_unitario))
                        conn.commit()

                        atualizar_valor_total(cur, id_pedido)

                        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_pedido))

                    elif 'editar' in request.form:
                        id_item = request.form['id_item']
                        quantidade = request.form['quantidade']

                        cur.execute("""
                            UPDATE ItemPedido
                            SET quantidade = %s
                            WHERE id_item_pedido = %s
                        """, (quantidade, id_item))
                        conn.commit()

                        atualizar_valor_total(cur, id_pedido)

                        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_pedido))

                    elif 'excluir' in request.form:
                        id_item = request.form['id_item']

                        cur.execute("""
                            DELETE FROM ItemPedido
                            WHERE id_item_pedido = %s
                        """, (id_item,))
                        conn.commit()

                        atualizar_valor_total(cur, id_pedido)

                        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_pedido))

        return render_template(
            'adicionar_itens_pedido.html', 
            produtos=produtos, 
            id_pedido=id_pedido, 
            itens_adicionados=itens_adicionados
        )

    except Exception as e:
        flash(f"Erro ao adicionar itens: {str(e)}", "error")
        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_pedido))

def atualizar_valor_total(cur, id_pedido):
    cur.execute("""
        SELECT SUM(ip.quantidade * ip.preco_unitario) 
        FROM ItemPedido ip 
        WHERE ip.id_pedido = %s
    """, (id_pedido,))
    novo_total = cur.fetchone()[0] or 0 

    cur.execute("""
        UPDATE Pedido 
        SET valor_total = %s 
        WHERE id_pedido = %s
    """, (novo_total, id_pedido))
    cur.connection.commit()

@main.route('/item/<int:id_item>/editar', methods=['POST'])
@login_required
def editar_item(id_item):
    try:
        quantidade = request.form['quantidade']

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE ItemPedido
                    SET quantidade = %s
                    WHERE id_item_pedido = %s
                """, (quantidade, id_item))
                conn.commit()

        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_item))
    except Exception as e:
        flash(f"Erro ao editar item: {str(e)}", "error")
        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_item))

@main.route('/item/<int:id_item>/excluir', methods=['POST'])
@login_required
def excluir_item(id_item):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM ItemPedido
                    WHERE id_item_pedido = %s
                """, (id_item,))
                conn.commit()

        flash("Item excluído com sucesso!", "success")
        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_item))
    except Exception as e:
        flash(f"Erro ao excluir item: {str(e)}", "error")
        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_item))

@main.route('/pedido/<int:id_pedido>/finalizar', methods=['POST'])
@login_required
def finalizar_pedido(id_pedido):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE Pedido
                    SET status = 'finalizado'
                    WHERE id_pedido = %s
                """, (id_pedido,))
                conn.commit()

        flash("Seu pedido foi criado com sucesso! Aguarde a confirmação.", "success")
        return redirect(url_for('main.index'))

    except Exception as e:
        flash(f"Erro ao finalizar pedido: {str(e)}", "error")
        return redirect(url_for('main.adicionar_itens_pedido', id_pedido=id_pedido))

# Renomeando a função para evitar conflito
@main.route('/finalizar_pagamento/<int:id_pedido>', methods=['POST'])
@login_required
def finalizar_pagamento(id_pedido):
    if not session.get('is_admin'):
        flash("Acesso negado!", "error")
        return redirect(url_for('main.index'))

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    UPDATE Pedido
                    SET status = 'Pago', data_pagamento = NOW()
                    WHERE id_pedido = %s
                """, (id_pedido,))
                conn.commit()

                flash("Pedido marcado como pago com sucesso!", "success")
        return redirect(url_for('main.listar_pagamentos'))

    except Exception as e:
        flash(f"Erro ao marcar pagamento: {str(e)}", "error")
        return redirect(url_for('main.listar_pagamentos'))      
    
         
@main.route('/admin/pedidos_por_cliente', methods=['GET'])
@main.route('/admin/pedidos_por_cliente', methods=['GET', 'POST'])
@login_required
def pedidos_por_cliente():
    current_app.logger.info(f"Usuário acessando pedidos_por_cliente: {session.get('user_id')}")
    if request.method == 'POST':
        id_pedido = request.form.get('id_pedido')
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE Pedido
                        SET status = 'pago'
                        WHERE id_pedido = %s
                    """, (id_pedido,))
                    conn.commit()
                    current_app.logger.info(f"Pedido {id_pedido} marcado como pago.")
        except Exception as e:
            current_app.logger.error(f"Erro ao marcar pedido como pago: {str(e)}")
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Obter todos os clientes e seus pedidos
                cur.execute("""
                    SELECT c.id_cliente, c.nome, p.id_pedido, p.data_pedido, p.valor_total, p.status
                    FROM Cliente c
                    LEFT JOIN Pedido p ON c.id_cliente = p.id_cliente
                """)
                pedidos = cur.fetchall()

                # Organizar os pedidos por cliente
                clientes = {}
                for pedido in pedidos:
                    id_cliente = pedido[0]
                    nome_cliente = pedido[1]
                    id_pedido = pedido[2]
                    data_pedido = pedido[3]
                    valor_total = pedido[4]
                    status = pedido[5]

                    if id_cliente not in clientes:
                        clientes[id_cliente] = {
                            'nome': nome_cliente,
                            'pedidos': []
                        }
                    if id_pedido:  # Verifica se há pedido
                        clientes[id_cliente]['pedidos'].append({
                            'id_pedido': id_pedido,
                            'data_pedido': data_pedido,
                            'valor_total': valor_total,
                            'status': status
                        })

        return render_template('partials/pedidos_por_cliente.html', clientes=clientes)
    except Exception as e:
        current_app.logger.error(f"Erro ao listar pedidos por cliente: {str(e)}")
        return "Erro ao listar pedidos por cliente.", 500




@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    flash("Você foi desconectado.", "success")
    return redirect('/login')