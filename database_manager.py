import sqlite3
import os

# Esta variável será atualizada pelo app.py para apontar para o caminho correto.
NOME_BANCO_DADOS = 'database.db' 

def inicializar():
    """Garante que todas as tabelas necessárias existam no banco de dados."""
    try:
        # Usa a variável global que pode ter sido ajustada pelo app.py
        conexao = sqlite3.connect(NOME_BANCO_DADOS)
        cursor = conexao.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planejamento (
                ano INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                dia INTEGER NOT NULL,
                id_cliente INTEGER NOT NULL,
                equipe TEXT,
                lab_externo INTEGER DEFAULT 0,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id) ON DELETE CASCADE,
                PRIMARY KEY (ano, mes, dia, id_cliente)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_cliente TEXT NOT NULL,
                endereco TEXT,
                telefone TEXT
            )
        ''')
        
        print("Banco de dados e tabelas verificados/criados com sucesso.")
        conexao.commit()
        conexao.close()

    except Exception as e:
        print(f"Ocorreu um erro ao inicializar o banco de dados: {e}")

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados configurada para retornar dicionários."""
    conn = sqlite3.connect(NOME_BANCO_DADOS)
    conn.row_factory = sqlite3.Row
    return conn

def buscar_todos_clientes():
    """Busca e retorna todos os clientes ordenados por nome."""
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes ORDER BY nome_cliente').fetchall()
    conn.close()
    return clientes

def adicionar_cliente(nome_cliente, endereco, telefone):
    """Adiciona um novo cliente ao banco de dados."""
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO clientes (nome_cliente, endereco, telefone) VALUES (?, ?, ?)',
            (nome_cliente, endereco, telefone)
        )
        conn.commit()
    finally:
        conn.close()

def editar_cliente(id_cliente, nome_cliente, endereco, telefone):
    """Atualiza os dados de um cliente existente."""
    conn = get_db_connection()
    try:
        conn.execute(
            'UPDATE clientes SET nome_cliente = ?, endereco = ?, telefone = ? WHERE id = ?',
            (nome_cliente, endereco, telefone, id_cliente)
        )
        conn.commit()
    finally:
        conn.close()

def excluir_cliente(id_cliente):
    """Exclui um cliente e seus agendamentos associados."""
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM planejamento WHERE id_cliente = ?', (id_cliente,))
        conn.execute('DELETE FROM clientes WHERE id = ?', (id_cliente,))
        conn.commit()
    finally:
        conn.close()

def buscar_planejamento_por_mes(ano, mes):
    """Busca e retorna o planejamento, incluindo o status de lab_externo."""
    conn = get_db_connection()
    planejamento = conn.execute(
        'SELECT dia, id_cliente, equipe, lab_externo FROM planejamento WHERE ano = ? AND mes = ?', (ano, mes)
    ).fetchall()
    conn.close()
    return [dict(row) for row in planejamento]

def salvar_planejamento_mes(ano, mes, planejamento_do_mes):
    """Salva o planejamento de um mês, substituindo completamente os dados existentes para aquele mês."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Apaga todos os registros do mês antes de inserir os novos, prevenindo erros de chave única.
        cursor.execute('DELETE FROM planejamento WHERE ano = ? AND mes = ?', (ano, mes))
        
        if planejamento_do_mes:
            dados_para_inserir = [
                (ano, mes, item['dia'], item['id_cliente'], item.get('equipe'), 1 if item.get('lab_externo') else 0) 
                for item in planejamento_do_mes
            ]
            cursor.executemany(
                'INSERT INTO planejamento (ano, mes, dia, id_cliente, equipe, lab_externo) VALUES (?, ?, ?, ?, ?, ?)',
                dados_para_inserir
            )
        
        conn.commit()
        return len(planejamento_do_mes) if planejamento_do_mes else 0
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar planejamento: {e}")
        raise e
    finally:
        conn.close()

