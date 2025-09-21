from flask import Flask, render_template, request, jsonify, redirect, url_for
import calendar
from datetime import datetime
import json
import database_manager
import locale  # <-- 1. IMPORTAR A BIBLIOTECA LOCALE

# 2. DEFINIR O LOCALE PARA PORTUGUÊS DO BRASIL
# Isso garante que calendar.month_name use os nomes dos meses em português.
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    print("Locale pt_BR.UTF-8 não encontrado. Usando o locale padrão do sistema.")
    # Você pode tentar alternativas se a primeira falhar, dependendo do sistema operacional
    # locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252') # Para Windows

# Inicializa a aplicação Flask
app = Flask(__name__)

# --- ROTAS PRINCIPAIS (CALENDÁRIO) ---

@app.route('/')
def index_redirect():
    """
    Rota raiz. Redireciona o usuário para o calendário do mês e ano atuais.
    """
    hoje = datetime.today()
    return redirect(url_for('calendario_view', ano=hoje.year, mes=hoje.month))

@app.route('/<int:ano>/<int:mes>')
def calendario_view(ano, mes):
    """
    Rota principal que exibe o calendário. Agora com nomes de meses em português.
    """
    if mes < 1:
        return redirect(url_for('calendario_view', ano=ano - 1, mes=12))
    if mes > 12:
        return redirect(url_for('calendario_view', ano=ano + 1, mes=1))

    clientes = database_manager.buscar_todos_clientes()
    planejamento_mes = database_manager.buscar_planejamento_por_mes(ano, mes)

    planejamento_dict = {}
    for item in planejamento_mes:
        dia = item['dia']
        if dia not in planejamento_dict:
            planejamento_dict[dia] = []
        planejamento_dict[dia].append(item)

    cal = calendar.monthcalendar(ano, mes)
    mes_anterior, ano_anterior = (mes - 1, ano) if mes > 1 else (12, ano - 1)
    mes_proximo, ano_proximo = (mes + 1, ano) if mes < 12 else (1, ano + 1)

    # Agora, calendar.month_name[mes] retornará "Janeiro", "Fevereiro", etc.
    return render_template('index.html', 
                           ano=ano, 
                           mes=mes, 
                           nome_mes=calendar.month_name[mes].capitalize(), # Usamos capitalize() para "Janeiro" em vez de "janeiro"
                           calendario=cal, 
                           clientes=clientes,
                           planejamento_json=json.dumps(planejamento_dict),
                           nav_anterior={'ano': ano_anterior, 'mes': mes_anterior},
                           nav_proximo={'ano': ano_proximo, 'mes': mes_proximo},
                           gerenciar_clientes_url=url_for('gerenciar_clientes_view')
                          )

# ... (o resto do seu código app.py permanece o mesmo) ...

# --- ROTAS DA API (PARA JAVASCRIPT) ---

@app.route('/api/copiar_mes_anterior/<int:ano>/<int:mes>')
def copiar_mes_anterior(ano, mes):
    mes_anterior, ano_anterior = (mes - 1, ano) if mes > 1 else (12, ano - 1)
    planejamento_anterior = database_manager.buscar_planejamento_por_mes(ano_anterior, mes_anterior)
    return jsonify(planejamento_anterior)

@app.route('/api/salvar_planejamento', methods=['POST'])
def salvar_planejamento():
    dados = request.json
    ano = dados.get('ano')
    mes = dados.get('mes')
    planejamento_do_mes = dados.get('planejamento')

    if not all([ano, mes, planejamento_do_mes is not None]):
        return jsonify({"status": "erro", "mensagem": "Dados incompletos recebidos."}), 400

    try:
        num_salvos = database_manager.salvar_planejamento_mes(ano, mes, planejamento_do_mes)
        # Acessa o nome do mês já em português
        nome_mes_pt = calendar.month_name[mes].capitalize()
        mensagem = f"{num_salvos} agendamentos salvos para {nome_mes_pt}/{ano}."
        return jsonify({"status": "sucesso", "mensagem": mensagem})
    except Exception as e:
        return jsonify({"status": "erro", "mensagem": f"Erro interno do servidor: {e}"}), 500

# --- ROTAS PARA GERENCIAMENTO DE CLIENTES (CRUD) ---

@app.route('/clientes')
def gerenciar_clientes_view():
    clientes = database_manager.buscar_todos_clientes()
    return render_template('gerenciar_clientes.html', clientes=clientes)

@app.route('/clientes/adicionar', methods=['POST'])
def adicionar_cliente_action():
    nome = request.form.get('nome_cliente')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')
    
    if nome:
        database_manager.adicionar_cliente(nome, endereco, telefone)
        
    return redirect(url_for('gerenciar_clientes_view'))

@app.route('/clientes/editar/<int:id_cliente>', methods=['POST'])
def editar_cliente_action(id_cliente):
    nome = request.form.get('nome_cliente')
    endereco = request.form.get('endereco')
    telefone = request.form.get('telefone')

    if nome:
        database_manager.editar_cliente(id_cliente, nome, endereco, telefone)
        
    return redirect(url_for('gerenciar_clientes_view'))

@app.route('/clientes/excluir/<int:id_cliente>', methods=['POST'])
def excluir_cliente_action(id_cliente):
    database_manager.excluir_cliente(id_cliente)
    return redirect(url_for('gerenciar_clientes_view'))

# --- PONTO DE ENTRADA DA APLICAÇÃO ---
if __name__ == '__main__':
    app.run(debug=True)
