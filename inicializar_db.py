import sqlite3

NOME_BANCO_DADOS = 'database.db'

def inicializar():
    """Garante que todas as tabelas necessárias existam no banco de dados."""
    try:
        conexao = sqlite3.connect(NOME_BANCO_DADOS)
        cursor = conexao.cursor()

        # Cria a tabela de planejamento se ela não existir
        # A chave primária composta (ano, mes, dia, id_cliente) impede duplicatas.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planejamento (
                ano INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                dia INTEGER NOT NULL,
                id_cliente INTEGER NOT NULL,
                equipe TEXT,
                FOREIGN KEY (id_cliente) REFERENCES clientes (id),
                PRIMARY KEY (ano, mes, dia, id_cliente)
            )
        ''')
        
        print("Tabela 'planejamento' verificada/criada com sucesso.")
        
        # Podemos adicionar verificações de outras tabelas aqui no futuro
        # Ex: cursor.execute(''' CREATE TABLE IF NOT EXISTS clientes (...) ''')

        conexao.commit()
        conexao.close()

    except Exception as e:
        print(f"Ocorreu um erro ao inicializar o banco de dados: {e}")

if __name__ == "__main__":
    inicializar()
