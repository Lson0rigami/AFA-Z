"""Aplicação principal do AFA Z.

Este arquivo liga as três partes centrais do projeto:

1. recebe requisições do navegador pelas rotas do Flask;
2. lê ou altera informações no SQLite;
3. devolve uma página HTML ou um redirecionamento.

Para entender o projeto, leia primeiro ``database.py`` e depois acompanhe as
rotas deste arquivo de cima para baixo. O guia completo está em
``docs/GUIA_DO_CODIGO.md``.
"""

import os
import secrets

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_connection, init_db


# Carrega as variáveis escritas no arquivo .env para o ambiente do Python.
# O .env real fica fora do Git; o .env.example mostra apenas quais chaves existem.
load_dotenv()

app = Flask(__name__)

# O Flask assina o cookie de sessão com esta chave. Em um servidor publicado,
# SECRET_KEY deve obrigatoriamente existir no ambiente. Para desenvolvimento
# local, geramos uma chave temporária quando não há .env; ao reiniciar o app,
# as sessões antigas deixam de valer, mas nenhuma chave previsível é publicada.
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Garante que as tabelas e as migrações simples existam antes da primeira rota.
init_db()


# ---------------------------------------------------------------------------
# ENTRADA, CADASTRO E AUTENTICAÇÃO
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Envia cada visitante ao lugar correto conforme a sessão."""
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    return redirect(url_for("login"))


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    """Exibe o formulário (GET) ou cria um usuário (POST)."""
    if request.method == "POST":
        # request.form contém os campos enviados pelo formulário HTML.
        nome = request.form["nome"]
        email = request.form["email"]
        senha = request.form["senha"]

        # Nunca guardamos a senha original. O hash permite conferir a senha no
        # login sem que seja possível recuperar o texto digitado pelo usuário.
        senha_hash = generate_password_hash(senha)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash) VALUES (?, ?, ?)",
            (nome, email, senha_hash)
        )

        # INSERT altera o banco, então precisa de commit antes de fechar.
        conn.commit()
        conn.close()

        # O padrão POST -> redirect -> GET evita reenviar o formulário quando
        # o usuário atualiza a página seguinte.
        return redirect(url_for("login"))

    return render_template("cadastro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Confere as credenciais e cria a sessão do usuário."""
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
        usuario = cursor.fetchone()
        conn.close()

        # A segunda condição só é testada se usuario existir. Isso evita tentar
        # acessar usuario["senha_hash"] quando o e-mail não foi encontrado.
        if usuario and check_password_hash(usuario["senha_hash"], senha):
            # A sessão fica em um cookie assinado pelo Flask. Guardamos apenas
            # os dados necessários para identificar o usuário nas próximas rotas.
            session["usuario_id"] = usuario["id"]
            session["usuario_nome"] = usuario["nome"]
            return redirect(url_for("dashboard"))

        return render_template(
            "login.html",
            erro="E-mail ou senha incorretos."
        ), 401

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Apaga os dados da sessão e encerra o acesso atual."""
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# PAINEL: CATEGORIAS, TAREFAS E DIÁRIO DO DIA
# ---------------------------------------------------------------------------

@app.route("/dashboard")
def dashboard():
    """Monta as três janelas principais do painel do usuário."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    # A URL pode ser /dashboard?categoria=3. type=int já converte o texto da
    # URL para inteiro e devolve None se o parâmetro não for válido.
    categoria_id = request.args.get("categoria", type=int)

    conn = get_connection()
    cursor = conn.cursor()

    # O filtro por usuario_id é o que impede um usuário de enxergar categorias
    # pertencentes a outra conta.
    cursor.execute(
        "SELECT * FROM categorias WHERE usuario_id = ? ORDER BY nome",
        (session["usuario_id"],)
    )
    categorias = cursor.fetchall()

    # next procura a categoria pedida na URL. Se ela não existir ou não
    # pertencer ao usuário, usamos a primeira categoria disponível.
    categoria_ativa = next(
        (categoria for categoria in categorias if categoria["id"] == categoria_id),
        categorias[0] if categorias else None
    )

    tarefas = []
    if categoria_ativa:
        cursor.execute("""
            SELECT * FROM tarefas
            WHERE categoria_id = ?
            ORDER BY
                CASE WHEN status = 'pendente' THEN 0 ELSE 1 END,
                data_criacao DESC
        """, (categoria_ativa["id"],))
        tarefas = cursor.fetchall()

    # Conta apenas as tarefas que ainda não foram concluídas nesta categoria.
    tarefas_pendentes_categoria = 0

    for tarefa in tarefas:
        if tarefa["status"] == "pendente":
            tarefas_pendentes_categoria += 1

    # COUNT calcula o número sem precisar trazer todas as tarefas para o Python.
    # O JOIN conecta cada tarefa à categoria e, por ela, ao dono da categoria.
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM tarefas
        JOIN categorias ON tarefas.categoria_id = categorias.id
        WHERE categorias.usuario_id = ? AND tarefas.status = 'pendente'
    """, (session["usuario_id"],))
    total_pendentes = cursor.fetchone()["total"]

    # Esta é a consulta mais complexa do projeto atual:
    # - JOIN encontra a categoria de cada tarefa;
    # - LEFT JOIN mantém a tarefa mesmo se ainda não existir feedback;
    # - a subconsulta pega apenas o feedback mais recente daquela tarefa;
    # - localtime compara a data usando o fuso do computador que executa o app.
    cursor.execute("""
        SELECT
            tarefas.id,
            tarefas.titulo,
            tarefas.data_conclusao,
            categorias.nome AS categoria_nome,
            feedback.aprendeu,
            feedback.nao_aprendeu
        FROM tarefas
        JOIN categorias ON tarefas.categoria_id = categorias.id
        LEFT JOIN feedback ON feedback.id = (
            SELECT feedback_recente.id
            FROM feedback AS feedback_recente
            WHERE feedback_recente.tarefa_id = tarefas.id
            ORDER BY feedback_recente.id DESC
            LIMIT 1
        )
        WHERE categorias.usuario_id = ?
          AND date(tarefas.data_conclusao, 'localtime') = date('now', 'localtime')
        ORDER BY tarefas.data_conclusao DESC
    """, (session["usuario_id"],))
    diario_hoje = cursor.fetchall()

    conn.close()

    # Cada nome à esquerda do sinal de igual vira uma variável disponível em
    # dashboard.html. Ex.: tarefas=tarefas permite usar {% for tarefa in tarefas %}.
    return render_template(
        "dashboard.html",
        categorias=categorias,
        categoria_ativa=categoria_ativa,
        tarefas=tarefas,
        diario_hoje=diario_hoje,
        total_pendentes=total_pendentes,
        tarefas_pendentes_categoria=tarefas_pendentes_categoria,
    )


# ---------------------------------------------------------------------------
# CATEGORIAS
# ---------------------------------------------------------------------------

@app.route("/categoria/nova", methods=["POST"])
def nova_categoria():
    """Cria uma categoria ligada ao usuário da sessão."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    nome_categoria = request.form["nome_categoria"]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO categorias (usuario_id, nome) VALUES (?, ?)",
        (session["usuario_id"], nome_categoria)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


@app.route("/categoria/<int:categoria_id>")
def ver_categoria(categoria_id):
    """Valida uma categoria e a abre selecionada no painel."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    # A condição usuario_id evita IDOR: trocar o número da categoria na URL
    # não pode dar acesso a dados de outra pessoa.
    cursor.execute(
        "SELECT * FROM categorias WHERE id = ? AND usuario_id = ?",
        (categoria_id, session["usuario_id"])
    )
    categoria = cursor.fetchone()
    conn.close()

    if categoria is None:
        return "Categoria não encontrada", 404

    return redirect(url_for("dashboard", categoria=categoria_id))


# ---------------------------------------------------------------------------
# TAREFAS E FEEDBACK
# ---------------------------------------------------------------------------

@app.route("/tarefa/nova", methods=["POST"])
def nova_tarefa():
    """Cria uma tarefa somente dentro de uma categoria do usuário atual."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    categoria_id = request.form["categoria_id"]
    titulo = request.form["titulo"]
    descricao = request.form.get("descricao", "")

    conn = get_connection()
    cursor = conn.cursor()

    # Não confiamos cegamente no categoria_id oculto do formulário: qualquer
    # pessoa pode alterar HTML pelo navegador. O banco confirma o proprietário.
    cursor.execute(
        "SELECT id FROM categorias WHERE id = ? AND usuario_id = ?",
        (categoria_id, session["usuario_id"])
    )

    if cursor.fetchone() is None:
        conn.close()
        return "Categoria não encontrada", 404

    cursor.execute(
        "INSERT INTO tarefas (categoria_id, titulo, descricao) VALUES (?, ?, ?)",
        (categoria_id, titulo, descricao)
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard", categoria=categoria_id))


@app.route("/tarefa/<int:tarefa_id>/concluir", methods=["POST"])
def concluir_tarefa(tarefa_id):
    """Marca a tarefa como feita e guarda quando isso aconteceu."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    # A tarefa não possui usuario_id diretamente. Por isso fazemos JOIN com
    # categorias para chegar ao dono e autorizar a operação.
    cursor.execute("""
        SELECT tarefas.id FROM tarefas
        JOIN categorias ON tarefas.categoria_id = categorias.id
        WHERE tarefas.id = ? AND categorias.usuario_id = ?
    """, (tarefa_id, session["usuario_id"]))

    if cursor.fetchone() is None:
        conn.close()
        return "Tarefa não encontrada", 404

    cursor.execute("""
        UPDATE tarefas
        SET status = 'feito', data_conclusao = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (tarefa_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("feedback_tarefa", tarefa_id=tarefa_id))


@app.route("/tarefa/<int:tarefa_id>/feedback", methods=["GET", "POST"])
def feedback_tarefa(tarefa_id):
    """Exibe ou salva a reflexão ligada a uma tarefa concluída."""
    if "usuario_id" not in session:
        return redirect(url_for("login"))

    conn = get_connection()
    cursor = conn.cursor()

    # Novamente usamos JOIN para garantir que a tarefa pertence à conta logada.
    cursor.execute("""
        SELECT tarefas.* FROM tarefas
        JOIN categorias ON tarefas.categoria_id = categorias.id
        WHERE tarefas.id = ? AND categorias.usuario_id = ?
    """, (tarefa_id, session["usuario_id"]))
    tarefa = cursor.fetchone()

    if tarefa is None:
        conn.close()
        return "Tarefa não encontrada", 404

    if request.method == "POST":
        aprendeu = request.form.get("aprendeu", "")
        nao_aprendeu = request.form.get("nao_aprendeu", "")

        # Procuramos um feedback anterior. Se existir, atualizamos; se não,
        # inserimos. Isso evita criar várias linhas ao reenviar o formulário.
        cursor.execute(
            "SELECT id FROM feedback WHERE tarefa_id = ? ORDER BY id DESC LIMIT 1",
            (tarefa_id,)
        )
        feedback_existente = cursor.fetchone()

        if feedback_existente:
            cursor.execute("""
                UPDATE feedback
                SET aprendeu = ?, nao_aprendeu = ?, data_criacao = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (aprendeu, nao_aprendeu, feedback_existente["id"]))
        else:
            cursor.execute("""
                INSERT INTO feedback (tarefa_id, aprendeu, nao_aprendeu, data_criacao)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (tarefa_id, aprendeu, nao_aprendeu))

        conn.commit()
        conn.close()

        return redirect(url_for("dashboard", categoria=tarefa["categoria_id"]))

    # Em uma requisição GET, um feedback existente preenche os campos da tela.
    cursor.execute(
        "SELECT * FROM feedback WHERE tarefa_id = ? ORDER BY id DESC LIMIT 1",
        (tarefa_id,)
    )
    feedback_existente = cursor.fetchone()
    conn.close()

    return render_template(
        "feedback.html",
        tarefa=tarefa,
        feedback_existente=feedback_existente
    )


if __name__ == "__main__":
    # FLASK_DEBUG=1 ativa recarregamento e mensagens detalhadas apenas no PC de
    # desenvolvimento. Nunca publique um servidor aberto com debug ativado.
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
