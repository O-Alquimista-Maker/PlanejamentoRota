# database_manager.py

import sqlite3
import calendar

NOME_BANCO_DADOS = 'database.db'

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

# database_manager.py

# ... (funções existentes: get_db_connection, buscar_todos_clientes, etc.) ...

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
        # É importante também excluir os agendamentos para manter a integridade referencial
        conn.execute('DELETE FROM planejamento WHERE id_cliente = ?', (id_cliente,))
        conn.execute('DELETE FROM clientes WHERE id = ?', (id_cliente,))
        conn.commit()
    finally:
        conn.close()

        # database_manager.py

# ... (funções existentes: get_db_connection, buscar_todos_clientes, etc.) ...

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
        # É importante também excluir os agendamentos para manter a integridade referencial
        conn.execute('DELETE FROM planejamento WHERE id_cliente = ?', (id_cliente,))
        conn.execute('DELETE FROM clientes WHERE id = ?', (id_cliente,))
        conn.commit()
    finally:
        conn.close()

def buscar_cliente_por_id(id_cliente):
    """Busca um único cliente pelo seu ID."""
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id_cliente,)).fetchone()
    conn.close()
    return cliente

def buscar_cliente_por_id(id_cliente):
    """Busca um único cliente pelo seu ID."""
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (id_cliente,)).fetchone()
    conn.close()
    return cliente

def buscar_planejamento_por_mes(ano, mes):
    """Busca e retorna o planejamento para um ano e mês específicos."""
    conn = get_db_connection()
    planejamento = conn.execute(
        'SELECT dia, id_cliente, equipe FROM planejamento WHERE ano = ? AND mes = ?', (ano, mes)
    ).fetchall()
    conn.close()
    return [dict(row) for row in planejamento]

def salvar_planejamento_mes(ano, mes, planejamento_do_mes):
    """Salva o planejamento de um mês, substituindo os dados existentes."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM planejamento WHERE ano = ? AND mes = ?', (ano, mes))
        
        if planejamento_do_mes:
            dados_para_inserir = [
                (ano, mes, item['dia'], item['id_cliente'], item.get('equipe')) 
                for item in planejamento_do_mes
            ]
            cursor.executemany(
                'INSERT INTO planejamento (ano, mes, dia, id_cliente, equipe) VALUES (?, ?, ?, ?, ?)',
                dados_para_inserir
            )
        
        conn.commit()
        return len(planejamento_do_mes)
    except Exception as e:
        conn.rollback()
        print(f"Erro ao salvar planejamento: {e}") # Log do erro no servidor
        raise e # Propaga a exceção para a rota tratar a resposta HTTP
    finally:
        conn.close()

