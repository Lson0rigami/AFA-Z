"""Conexão e estrutura do banco SQLite do AFA Z.

As rotas em app.py chamam ``get_connection()`` sempre que precisam consultar
ou alterar dados. ``init_db()`` prepara um banco novo e também atualiza bancos
antigos que ainda não possuem as colunas mais recentes.
"""

import sqlite3


def get_connection():
    """Abre o database.db e configura linhas acessíveis pelo nome da coluna."""
    conn = sqlite3.connect("database.db")

    # Sem row_factory, uma consulta retornaria algo como (1, "Elly").
    # Com sqlite3.Row, podemos escrever usuario["id"] e usuario["nome"],
    # deixando o restante do código mais legível e menos dependente da ordem.
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Cria tabelas ausentes e executa as migrações simples do projeto."""
    conn = get_connection()
    cursor = conn.cursor()

    # IF NOT EXISTS permite executar a inicialização em toda abertura sem apagar
    # ou recriar uma tabela que já contém dados.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            senha_hash TEXT NOT NULL
        )
    """)

    # usuario_id é uma chave estrangeira: cada categoria aponta para seu dono.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)

    # A tarefa pertence à categoria. data_conclusao começa vazia e só recebe
    # um horário quando a rota concluir_tarefa for executada.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descricao TEXT,
            status TEXT NOT NULL DEFAULT 'pendente',
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            data_conclusao TEXT,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id)
        )
    """)

    # O feedback guarda a reflexão posterior à conclusão da tarefa.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarefa_id INTEGER NOT NULL,
            aprendeu TEXT,
            nao_aprendeu TEXT,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (tarefa_id) REFERENCES tarefas(id)
        )
    """)

    # CREATE TABLE IF NOT EXISTS não modifica uma tabela já existente. Por isso
    # usamos PRAGMA table_info para descobrir quais colunas um banco antigo tem.
    # O conjunto (set) permite testar a existência de uma coluna rapidamente.
    cursor.execute("PRAGMA table_info(tarefas)")
    colunas_tarefas = {coluna["name"] for coluna in cursor.fetchall()}

    if "data_conclusao" not in colunas_tarefas:
        cursor.execute("ALTER TABLE tarefas ADD COLUMN data_conclusao TEXT")

    cursor.execute("PRAGMA table_info(feedback)")
    colunas_feedback = {coluna["name"] for coluna in cursor.fetchall()}

    if "data_criacao" not in colunas_feedback:
        cursor.execute("ALTER TABLE feedback ADD COLUMN data_criacao TEXT")

    # Todas as criações e migrações são confirmadas juntas. Se esquecêssemos o
    # commit, alterações pendentes poderiam desaparecer ao fechar a conexão.
    conn.commit()
    conn.close()
