const Planejador = {
    config: {
        ano: null,
        mes: null,
        selectors: {
            clienteItem: '.cliente-item',
            statusIcon: '.status-icon',
            clienteAlocado: '.cliente-alocado',
            diaValido: '.dia-valido',
            equipeContainer: '.equipe-container',
            contadorEquipe: '.contador-equipe',
            copiarBtn: '#copiar-btn',
            salvarBtn: '#salvar-btn',
            scriptTag: '#planejador-script'
        }
    },

    elementos: {},

    estado: {
        planejamentoSalvo: null,
        todosClientes: {}
    },

    funcoes: {
        // Função auxiliar para notificações
        notificar(icon, title, text = '') {
            Swal.fire({
                icon: icon,
                title: title,
                text: text,
                timer: icon === 'success' ? 2000 : 4000,
                timerProgressBar: true,
                showConfirmButton: false
            });
        },

        atualizarStatusCliente(clienteId, agendado) {
            const icone = document.querySelector(`${Planejador.config.selectors.clienteItem}[data-id='${clienteId}'] ${Planejador.config.selectors.statusIcon}`);
            if (icone) {
                icone.className = `status-icon ${agendado ? 'agendado' : 'pendente'}`;
            }
        },

        atualizarContadorEquipe(dia, equipe) {
            const containerEquipe = document.querySelector(`.dia-valido[data-dia='${dia}'] .equipe-container[data-equipe='${equipe}']`);
            if (!containerEquipe) return;

            const contadorEl = containerEquipe.querySelector(Planejador.config.selectors.contadorEquipe);
            const totalClientes = containerEquipe.querySelectorAll(Planejador.config.selectors.clienteAlocado).length;

            if (contadorEl) {
                contadorEl.textContent = `(${totalClientes})`;
            }
        },

        criarElementoClienteAlocado(dia, equipe, clienteId, clienteNome, labExterno = false) {
            const containerEquipe = document.querySelector(`.dia-valido[data-dia='${dia}'] .equipe-container[data-equipe='${equipe}']`);
            if (!containerEquipe || containerEquipe.querySelector(`[data-cliente-id='${clienteId}']`)) return;

            const el = document.createElement('div');
            el.className = 'cliente-alocado';
            el.dataset.clienteId = clienteId;
            el.dataset.equipe = equipe;
            el.draggable = true;

            el.innerHTML = `
                <span class="cliente-nome">${clienteNome}</span>
                <input type="checkbox" class="lab-externo-check" title="Acompanhamento Lab. Externo">
            `;

            const checkbox = el.querySelector('.lab-externo-check');
            checkbox.checked = labExterno;

            if (labExterno) {
                const indicator = document.createElement('span');
                indicator.className = 'lab-externo-indicator';
                indicator.textContent = '★';
                el.prepend(indicator);
            }

            checkbox.addEventListener('change', (e) => {
                const indicator = el.querySelector('.lab-externo-indicator');
                if (e.target.checked) {
                    if (!indicator) {
                        const newIndicator = document.createElement('span');
                        newIndicator.className = 'lab-externo-indicator';
                        newIndicator.textContent = '★';
                        el.prepend(newIndicator);
                    }
                } else {
                    if (indicator) indicator.remove();
                }
            });

            el.querySelector('.cliente-nome').addEventListener('click', () => {
                Swal.fire({
                    title: 'Remover agendamento?',
                    text: `Deseja remover "${clienteNome}" deste dia?`,
                    icon: 'question',
                    showCancelButton: true,
                    confirmButtonColor: '#d33',
                    cancelButtonColor: '#3085d6',
                    confirmButtonText: 'Sim, remover!',
                    cancelButtonText: 'Cancelar'
                }).then((result) => {
                    if (result.isConfirmed) {
                        const dia = el.closest('.dia-valido').dataset.dia;
                        const equipe = el.dataset.equipe;
                        Planejador.funcoes.atualizarStatusCliente(clienteId, false);
                        el.remove();
                        Planejador.funcoes.atualizarContadorEquipe(dia, equipe);
                    }
                });
            });

            el.addEventListener('dragstart', (e) => {
                e.stopPropagation();
                e.dataTransfer.setData('text/plain', JSON.stringify({ id: clienteId, nome: clienteNome, labExterno: checkbox.checked }));
                setTimeout(() => el.style.display = 'none', 0);
            });
            el.addEventListener('dragend', (e) => {
                el.style.display = 'flex';
            });

            containerEquipe.appendChild(el);
            Planejador.funcoes.atualizarStatusCliente(clienteId, true);
            Planejador.funcoes.atualizarContadorEquipe(dia, equipe);
        },

        carregarPlanejamentoInicial() {
            const planejamento = Planejador.estado.planejamentoSalvo;
            if (!planejamento) return;
            for (const dia in planejamento) {
                planejamento[dia].forEach(item => {
                    const nomeCliente = Planejador.estado.todosClientes[item.id_cliente];
                    if (nomeCliente && item.equipe) {
                        Planejador.funcoes.criarElementoClienteAlocado(dia, item.equipe, item.id_cliente, nomeCliente, item.lab_externo);
                    }
                });
            }
        },

        async copiarDoMesAnterior() {
            const result = await Swal.fire({
                title: 'Copiar do Mês Anterior?',
                text: 'Isso substituirá qualquer agendamento não salvo na tela. Deseja continuar?',
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: '#aaa',
                confirmButtonText: 'Sim, copiar!',
                cancelButtonText: 'Cancelar'
            });

            if (!result.isConfirmed) return;

            try {
                const response = await fetch(`/api/copiar_mes_anterior/${Planejador.config.ano}/${Planejador.config.mes}`);
                if (!response.ok) throw new Error(`Erro na resposta do servidor: ${response.statusText}`);

                const planejamentoAnterior = await response.json();

                document.querySelectorAll('.cliente-alocado').forEach(el => el.remove());
                document.querySelectorAll('.status-icon').forEach(icon => icon.classList.replace('agendado', 'pendente'));
                document.querySelectorAll('.contador-equipe').forEach(cont => cont.textContent = '(0)');

                planejamentoAnterior.forEach(item => {
                    const nomeCliente = Planejador.estado.todosClientes[item.id_cliente];
                    if (nomeCliente && item.equipe) {
                        Planejador.funcoes.criarElementoClienteAlocado(item.dia, item.equipe, item.id_cliente, nomeCliente, item.lab_externo);
                    }
                });
                this.notificar('success', 'Copiado!', `${planejamentoAnterior.length} agendamentos copiados. Clique em "Salvar" para confirmar.`);
            } catch (error) {
                this.notificar('error', 'Erro ao Copiar', error.message);
            }
        },

        async salvarPlanejamentoAtual() {
            const planejamentoParaSalvar = [];
            document.querySelectorAll('.dia-valido .cliente-alocado').forEach(clienteEl => {
                planejamentoParaSalvar.push({
                    dia: parseInt(clienteEl.closest('.dia-valido').dataset.dia, 10),
                    id_cliente: parseInt(clienteEl.dataset.clienteId, 10),
                    equipe: clienteEl.dataset.equipe,
                    lab_externo: clienteEl.querySelector('.lab-externo-check').checked
                });
            });

            Planejador.elementos.salvarBtn.disabled = true;
            Planejador.elementos.salvarBtn.textContent = 'Salvando...';

            try {
                const response = await fetch('/api/salvar_planejamento', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ano: Planejador.config.ano,
                        mes: Planejador.config.mes,
                        planejamento: planejamentoParaSalvar
                    })
                });
                const result = await response.json();
                if (response.ok) {
                    this.notificar('success', 'Salvo!', result.mensagem);
                } else {
                    this.notificar('error', 'Erro ao Salvar', result.mensagem);
                }
            } catch (error) {
                this.notificar('error', 'Erro de Conexão', error.message);
            } finally {
                Planejador.elementos.salvarBtn.disabled = false;
                Planejador.elementos.salvarBtn.textContent = 'Salvar Planejamento';
            }
        }
    },

    init() {
        const scriptTag = document.querySelector(this.config.selectors.scriptTag);
        if (!scriptTag) {
            console.error('Tag de script com dados de inicialização não encontrada!');
            return;
        }

        this.config.ano = parseInt(scriptTag.dataset.ano, 10);
        this.config.mes = parseInt(scriptTag.dataset.mes, 10);

        try {
            this.estado.planejamentoSalvo = JSON.parse(scriptTag.dataset.planejamentoJson);
        } catch (e) {
            console.error("Erro ao analisar o JSON do planejamento:", e);
            this.estado.planejamentoSalvo = {};
        }

        this.elementos.copiarBtn = document.querySelector(this.config.selectors.copiarBtn);
        this.elementos.salvarBtn = document.querySelector(this.config.selectors.salvarBtn);

        this.estado.todosClientes = Object.fromEntries(
            [...document.querySelectorAll(this.config.selectors.clienteItem)].map(el => [el.dataset.id, el.dataset.nome])
        );

        this.funcoes.carregarPlanejamentoInicial();

        document.querySelectorAll(this.config.selectors.clienteItem).forEach(c => {
            c.addEventListener('dragstart', e => {
                e.dataTransfer.setData('text/plain', JSON.stringify({ id: e.target.dataset.id, nome: e.target.dataset.nome }));
            });
        });

        document.querySelectorAll(this.config.selectors.equipeContainer).forEach(container => {
            container.addEventListener('dragover', e => {
                e.preventDefault();
                container.classList.add('drag-over');
            });
            container.addEventListener('dragleave', () => container.classList.remove('drag-over'));
            container.addEventListener('drop', e => {
                e.preventDefault();
                container.classList.remove('drag-over');

                const dados = JSON.parse(e.dataTransfer.getData('text/plain'));
                const dia = container.closest(this.config.selectors.diaValido).dataset.dia;
                const equipe = container.dataset.equipe;

                const elArrastado = document.querySelector(`.cliente-alocado[data-cliente-id='${dados.id}'][style*='display: none']`);
                if (elArrastado) {
                    const diaOrigem = elArrastado.closest(this.config.selectors.diaValido).dataset.dia;
                    const equipeOrigem = elArrastado.dataset.equipe;
                    elArrastado.remove();
                    this.funcoes.atualizarContadorEquipe(diaOrigem, equipeOrigem);
                }

                this.funcoes.criarElementoClienteAlocado(dia, equipe, dados.id, dados.nome, dados.labExterno || false);
            });
        });

        this.elementos.copiarBtn.addEventListener('click', () => this.funcoes.copiarDoMesAnterior());
        this.elementos.salvarBtn.addEventListener('click', () => this.funcoes.salvarPlanejamentoAtual());
    }
};

document.addEventListener('DOMContentLoaded', () => {
    Planejador.init();
});
