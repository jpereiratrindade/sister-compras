document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.nav-link');
  const tabContents = document.querySelectorAll('.tab-content');
  const refreshBtn = document.getElementById('refresh-btn');
  const needsFilter = document.getElementById('needs-filter');

  // Modais
  const modalNeed = document.getElementById('modal-need');
  const modalEditNeed = document.getElementById('modal-edit-need');
  const modalAlternative = document.getElementById('modal-alternative');
  const modalDecision = document.getElementById('modal-decision');
  const modalAi = document.getElementById('modal-ai-analysis');
  const modalChat = document.getElementById('modal-ai-chat');

  const btnOpenNeed = document.getElementById('btn-open-need-modal');
  const btnOpenAlt = document.getElementById('btn-open-alt-modal');
  const btnOpenDec = document.getElementById('btn-open-dec-modal');
  const btnOpenChat = document.getElementById('btn-open-chat-modal');
  const btnCopyAi = document.getElementById('btn-copy-ai-suggestion');
  const btnAiSpecify = document.getElementById('btn-ai-specify-reqs');
  const btnPrintSelected = document.getElementById('btn-print-selected-shopping');
  const checkAllShopping = document.getElementById('check-all-shopping');

  const formNeed = document.getElementById('form-need');
  const formEditNeed = document.getElementById('form-edit-need');
  const formAlt = document.getElementById('form-alternative');
  const formDec = document.getElementById('form-decision');
  const formChatSend = document.getElementById('form-chat-send');

  const selectOllama = document.getElementById('select-ollama-model');

  let currentData = null;
  let lastAiAnalysisText = '';
  let lastAnalyzedNeedId = '';
  let chatHistoryList = [];

  // Tab switching
  tabs.forEach(button => {
    button.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('selected'));
      tabContents.forEach(c => c.classList.remove('active'));

      button.classList.add('selected');
      const targetId = `tab-${button.dataset.tab}`;
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });

  // Modal controls
  if (btnOpenNeed) btnOpenNeed.addEventListener('click', () => modalNeed.showModal());
  if (btnOpenAlt) btnOpenAlt.addEventListener('click', () => {
    populateNeedSelects();
    modalAlternative.showModal();
  });
  if (btnOpenDec) btnOpenDec.addEventListener('click', () => {
    populateNeedSelects();
    modalDecision.showModal();
  });
  if (btnOpenChat) btnOpenChat.addEventListener('click', () => modalChat.showModal());

  document.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const dialog = e.target.closest('dialog');
      if (dialog) dialog.close();
    });
  });

  // Load Ollama Models
  async function loadOllamaModels() {
    if (!selectOllama) return;
    try {
      const res = await fetch('/api/ollama/models');
      if (res.ok) {
        const data = await res.json();
        if (data.models && data.models.length > 0) {
          selectOllama.innerHTML = '';
          data.models.forEach(model => {
            const opt = document.createElement('option');
            opt.value = model;
            opt.textContent = model + (model === 'qwen2.5:14b' ? ' (Recomendado)' : '');
            if (model === 'qwen2.5:14b') opt.selected = true;
            selectOllama.appendChild(opt);
          });
        }
      }
    } catch (err) {
      console.warn('Ollama local offline ou não disponível:', err);
    }
  }

  function populateNeedSelects(targetNeedId = null) {
    const selAlt = document.getElementById('select-need-for-alt');
    const selDec = document.getElementById('select-need-for-dec');
    if (!selAlt || !selDec || !currentData || !currentData.needs) return;

    selAlt.innerHTML = '';
    selDec.innerHTML = '';

    currentData.needs.forEach(need => {
      const opt1 = document.createElement('option');
      opt1.value = need.id;
      opt1.textContent = `${need.id} - ${need.title}`;
      if (targetNeedId && need.id === targetNeedId) opt1.selected = true;
      selAlt.appendChild(opt1);

      const opt2 = document.createElement('option');
      opt2.value = need.id;
      opt2.textContent = `${need.id} - ${need.title}`;
      if (targetNeedId && need.id === targetNeedId) opt2.selected = true;
      selDec.appendChild(opt2);
    });
  }

  // Checkbox management for selective PDF export
  function updateSelectedCount() {
    const checked = document.querySelectorAll('.shopping-item-check:checked');
    const countSpan = document.getElementById('selected-shopping-count');
    if (countSpan) countSpan.textContent = checked.length;
  }

  if (checkAllShopping) {
    checkAllShopping.addEventListener('change', (e) => {
      const isChecked = e.target.checked;
      document.querySelectorAll('.shopping-item-check').forEach(ck => {
        ck.checked = isChecked;
      });
      updateSelectedCount();
    });
  }

  if (btnPrintSelected) {
    btnPrintSelected.addEventListener('click', () => {
      const checked = document.querySelectorAll('.shopping-item-check:checked');
      if (checked.length === 0) {
        alert('Selecione ao menos um item da tabela para imprimir a Lista de Compras.');
        return;
      }
      const ids = Array.from(checked).map(c => c.dataset.needId).join(',');
      window.open(`/api/reports/shopping-list?ids=${encodeURIComponent(ids)}`, '_blank');
    });
  }

  // Visual Editing & Deletion Functions
  window.openEditNeedModal = function(needId) {
    if (!currentData || !currentData.needs) return;
    const need = currentData.needs.find(n => n.id === needId);
    if (!need) return;

    document.getElementById('edit-need-id').value = need.id;
    document.getElementById('edit-need-title').value = need.title || '';
    document.getElementById('edit-need-category').value = need.category || 'Equipamentos Científicos';
    document.getElementById('edit-need-quantity').value = need.quantity || 1;
    document.getElementById('edit-need-priority').value = need.priority || 'Essencial';
    document.getElementById('edit-need-budget').value = need.estimated_budget || 0.0;
    document.getElementById('edit-need-responsible').value = need.responsible || 'Equipe de Pesquisa';
    document.getElementById('edit-need-description').value = need.description || '';

    if (modalEditNeed) modalEditNeed.showModal();
  };

  window.deleteNeed = async function(needId) {
    if (!confirm(`Tem certeza que deseja EXCLUIR a necessidade ${needId} do banco de dados?`)) {
      return;
    }
    try {
      const res = await fetch('/api/needs/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ need_id: needId })
      });
      if (res.ok) {
        await loadDashboardData();
      } else {
        alert('Erro ao excluir registro.');
      }
    } catch (err) {
      console.error('Falha na exclusão:', err);
    }
  };

  if (formEditNeed) {
    formEditNeed.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formEditNeed);
      const payload = {
        need_id: formData.get('need_id'),
        title: formData.get('title'),
        category: formData.get('category'),
        quantity: parseInt(formData.get('quantity'), 10),
        priority: formData.get('priority'),
        estimated_budget: parseFloat(formData.get('estimated_budget') || 0),
        responsible: formData.get('responsible'),
        description: formData.get('description')
      };

      try {
        const res = await fetch('/api/needs/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          modalEditNeed.close();
          await loadDashboardData();
        } else {
          alert('Erro ao atualizar registro.');
        }
      } catch (err) {
        console.error('Falha no envio da edição:', err);
      }
    });
  }

  // Chat Conversacional & Extração de Intenção com Confirmação Humana e RAG Multi-Turno
  if (formChatSend) {
    formChatSend.addEventListener('submit', async (e) => {
      e.preventDefault();
      const chatInput = document.getElementById('chat-input');
      const chatMessages = document.getElementById('chat-messages');
      const proposalContainer = document.getElementById('proposal-card-container');
      const messageText = chatInput.value.trim();
      if (!messageText) return;

      // Renderizar mensagem do usuário
      const userDiv = document.createElement('div');
      userDiv.style.alignSelf = 'flex-end';
      userDiv.style.background = 'var(--soft)';
      userDiv.style.border = '1px solid var(--line)';
      userDiv.style.padding = '8px 12px';
      userDiv.style.borderRadius = '8px';
      userDiv.innerHTML = `<strong>Você:</strong> ${messageText}`;
      chatMessages.appendChild(userDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // Adicionar ao histórico de conversação
      chatHistoryList.push({ role: 'user', content: messageText });

      chatInput.value = '';
      proposalContainer.innerHTML = '<div style="font-size:0.8rem; color:var(--blue); margin-top:8px;">Consultando banco de dados (RAG) e analisando histórico...</div>';

      try {
        const model = selectOllama ? selectOllama.value : 'qwen2.5:14b';
        const res = await fetch('/api/ollama/intent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: messageText, history: chatHistoryList, model: model })
        });

        if (res.ok) {
          const data = await res.json();
          const proposal = data.proposal || {};
          if (proposal.explanation) {
            chatHistoryList.push({ role: 'assistant', content: proposal.explanation });
          }
          renderActionProposal(proposal);
        } else {
          proposalContainer.innerHTML = '<div style="color:var(--red); font-size:0.8rem;">Erro ao interpretar instrução.</div>';
        }
      } catch (err) {
        proposalContainer.innerHTML = `<div style="color:var(--red); font-size:0.8rem;">Erro de comunicação: ${err.message}</div>`;
      }
    });
  }

  function renderActionProposal(proposal) {
    const proposalContainer = document.getElementById('proposal-card-container');
    const chatMessages = document.getElementById('chat-messages');
    proposalContainer.innerHTML = '';

    const action = proposal.action || 'create_need';
    const params = proposal.params || {};
    const explanation = proposal.explanation || 'Proposta de Ação';
    const options = proposal.options || [];

    // Tratar pedido de esclarecimento (ask_clarification)
    if (action === 'ask_clarification') {
      const askDiv = document.createElement('div');
      askDiv.style.background = '#fff8e6';
      askDiv.style.border = '1px solid #ffd591';
      askDiv.style.padding = '10px 12px';
      askDiv.style.borderRadius = '8px';
      askDiv.style.fontSize = '0.84rem';
      
      let optionsButtonsHtml = '';
      if (options && options.length > 0) {
        optionsButtonsHtml = '<div style="margin-top:8px; display:flex; flex-wrap:wrap; gap:6px;">';
        options.forEach(opt => {
          optionsButtonsHtml += `<button type="button" class="option-chip-btn" data-option="${opt}" style="background:var(--teal); color:#fff; border:none; padding:4px 10px; border-radius:12px; font-size:0.75rem; font-weight:bold; cursor:pointer;">⚡ ${opt}</button>`;
        });
        optionsButtonsHtml += '</div>';
      }

      askDiv.innerHTML = `<strong>Assistente IA:</strong> ${explanation}${optionsButtonsHtml}`;
      chatMessages.appendChild(askDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;

      // Event listener para os botões de opção interativos
      askDiv.querySelectorAll('.option-chip-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
          const selectedVal = e.target.dataset.option;
          const chatInput = document.getElementById('chat-input');
          chatInput.value = `Opção selecionada: ${selectedVal}`;
          formChatSend.requestSubmit();
        });
      });

      return;
    }

    let actionLabel = 'Cadastrar Nova Necessidade';
    let detailsHtml = '';

    if (action === 'create_need') {
      actionLabel = 'Cadastrar Nova Necessidade';
      const estBudget = params.estimated_budget ? ` | <strong>Orçamento Estimado:</strong> R$ ${params.estimated_budget.toFixed(2)}` : '';
      const descHtml = params.description ? `<br><strong>Descrição:</strong> ${params.description}` : '';
      detailsHtml = `<strong>Título:</strong> ${params.title || 'N/A'}<br>
                     <strong>Categoria:</strong> ${params.category || 'Equipamentos Científicos'} | <strong>Quantidade:</strong> ${params.quantity || 1}<br>
                     <strong>Prioridade:</strong> ${params.priority || 'Essencial'}${estBudget}${descHtml}`;
    } else if (action === 'update_need') {
      actionLabel = `Atualizar Necessidade Existente [${params.need_id || 'NED-001'}]`;
      const estBudget = params.estimated_budget ? ` | <strong>Novo Orçamento Est.:</strong> R$ ${params.estimated_budget.toFixed(2)}` : '';
      const descHtml = params.description ? `<br><strong>Nova Descrição:</strong> ${params.description}` : '';
      detailsHtml = `<strong>ID:</strong> ${params.need_id || 'NED-001'}<br>
                     <strong>Título:</strong> ${params.title || 'Inalterado'}${estBudget}${descHtml}`;
    } else if (action === 'delete_need') {
      actionLabel = `🗑️ Excluir Necessidade [${params.need_id || 'NED-001'}]`;
      detailsHtml = `<strong>ID para Exclusão:</strong> ${params.need_id || 'NED-001'}<br>
                     <span style="color:var(--red); font-weight:bold;">Atenção: Esta ação removerá permanentemente a necessidade e suas cotações do banco de dados.</span>`;
    } else if (action === 'add_quote') {
      actionLabel = 'Adicionar Cotação / Alternativa';
      detailsHtml = `<strong>Necessidade:</strong> ${params.need_id || 'NED-001'}<br>
                     <strong>Produto/Alternativa:</strong> ${params.title || 'Alternativa'}<br>
                     <strong>Fornecedor:</strong> ${params.supplier || 'Fornecedor N/A'} | <strong>Valor:</strong> R$ ${params.price || 0}`;
    } else if (action === 'make_decision') {
      actionLabel = 'Registrar Parecer de Decisão';
      detailsHtml = `<strong>Necessidade:</strong> ${params.need_id || 'NED-001'}<br>
                     <strong>Alternativa Escolhida:</strong> ${params.selected_alternative_id || 'ALT-01'}<br>
                     <strong>Justificativa:</strong> "${params.technical_justification || 'Conforme requisitos'}"`;
    } else if (action === 'update_status') {
      actionLabel = 'Atualizar Status da Compra';
      detailsHtml = `<strong>Necessidade:</strong> ${params.need_id || 'NED-001'}<br>
                     <strong>Novo Status:</strong> ${params.status || 'Adquirida'}`;
    }

    const card = document.createElement('div');
    card.className = 'proposal-card';
    card.innerHTML = `
      <div class="proposal-card-head">
        <strong>⚡ PROPOSTA DE AÇÃO DA IA (RAG Mapeado): ${actionLabel}</strong>
      </div>
      <p style="font-size:0.78rem; color:var(--muted); margin-bottom:6px;">${explanation}</p>
      <div class="proposal-card-body">
        ${detailsHtml}
      </div>
      <div class="proposal-card-actions">
        <button type="button" class="cancel-action-btn" id="btn-cancel-proposal">❌ Cancelar</button>
        <button type="button" class="confirm-action-btn" id="btn-confirm-proposal">✅ Confirmar e Gravar no Banco</button>
      </div>
    `;

    proposalContainer.appendChild(card);

    document.getElementById('btn-cancel-proposal').addEventListener('click', () => {
      proposalContainer.innerHTML = '';
      const cancelDiv = document.createElement('div');
      cancelDiv.style.color = 'var(--muted)';
      cancelDiv.style.fontSize = '0.8rem';
      cancelDiv.innerHTML = '<strong>Assistente IA:</strong> Ação cancelada pelo usuário.';
      chatMessages.appendChild(cancelDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    });

    document.getElementById('btn-confirm-proposal').addEventListener('click', async () => {
      proposalContainer.innerHTML = '<div style="font-size:0.8rem; color:var(--teal); font-weight:bold;">Gravando no Banco de Dados...</div>';
      
      let targetUrl = '/api/needs';
      let bodyPayload = params;

      if (action === 'update_need') targetUrl = '/api/needs/update';
      if (action === 'delete_need') targetUrl = '/api/needs/delete';
      if (action === 'add_quote') targetUrl = '/api/alternatives';
      if (action === 'make_decision') targetUrl = '/api/decisions';
      if (action === 'update_status') targetUrl = '/api/needs/status';

      try {
        const res = await fetch(targetUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(bodyPayload)
        });

        if (res.ok) {
          proposalContainer.innerHTML = '';
          const okDiv = document.createElement('div');
          okDiv.style.background = '#eaf7f5';
          okDiv.style.border = '1px solid var(--teal)';
          okDiv.style.padding = '10px';
          okDiv.style.borderRadius = '8px';
          okDiv.style.fontSize = '0.82rem';
          okDiv.innerHTML = `<strong>✅ Sucesso!</strong> Operação realizada no banco de dados com sucesso.`;
          chatMessages.appendChild(okDiv);
          chatMessages.scrollTop = chatMessages.scrollHeight;
          chatHistoryList = []; // Resetar histórico após conclusão com sucesso
          await loadDashboardData();
        } else {
          proposalContainer.innerHTML = '<div style="color:var(--red); font-size:0.8rem;">Erro ao gravar no banco.</div>';
        }
      } catch (err) {
        proposalContainer.innerHTML = `<div style="color:var(--red); font-size:0.8rem;">Erro: ${err.message}</div>`;
      }
    });
  }

  // Trigger AI Analysis
  window.triggerAiAnalysis = async function(needId) {
    lastAnalyzedNeedId = needId;
    const model = selectOllama ? selectOllama.value : 'qwen2.5:14b';
    document.getElementById('ai-modal-title').textContent = `Análise Técnica com ${model}`;
    document.getElementById('ai-loading').style.display = 'block';
    document.getElementById('ai-content-box').textContent = '';
    modalAi.showModal();

    try {
      const res = await fetch('/api/ollama/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ need_id: needId, model: model, mode: 'analyze' })
      });
      document.getElementById('ai-loading').style.display = 'none';
      if (res.ok) {
        const result = await res.json();
        lastAiAnalysisText = result.analysis || 'Sem resposta.';
        document.getElementById('ai-content-box').textContent = lastAiAnalysisText;
      } else {
        document.getElementById('ai-content-box').textContent = 'Erro ao consultar o Ollama. Verifique se o modelo está baixado.';
      }
    } catch (err) {
      document.getElementById('ai-loading').style.display = 'none';
      document.getElementById('ai-content-box').textContent = `Falha na requisição ao Ollama: ${err.message}`;
    }
  };

  // AI Specify Requirements
  if (btnAiSpecify) {
    btnAiSpecify.addEventListener('click', async () => {
      const titleInput = document.getElementById('need-title-input');
      if (!titleInput || !titleInput.value.trim()) {
        alert('Digite o título da necessidade primeiro.');
        return;
      }
      const model = selectOllama ? selectOllama.value : 'qwen2.5:14b';
      document.getElementById('ai-modal-title').textContent = `Especificação de Requisitos com ${model}`;
      document.getElementById('ai-loading').style.display = 'block';
      document.getElementById('ai-content-box').textContent = '';
      modalAi.showModal();

      try {
        const res = await fetch('/api/ollama/analyze', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            need_id: 'TEMP',
            model: model,
            mode: 'specify'
          })
        });
        document.getElementById('ai-loading').style.display = 'none';
        if (res.ok) {
          const result = await res.json();
          lastAiAnalysisText = result.analysis || '';
          document.getElementById('ai-content-box').textContent = lastAiAnalysisText;
        } else {
          document.getElementById('ai-content-box').textContent = 'Erro ao consultar o Ollama.';
        }
      } catch (err) {
        document.getElementById('ai-loading').style.display = 'none';
        document.getElementById('ai-content-box').textContent = `Erro: ${err.message}`;
      }
    });
  }

  // Update Status of Need (Purchased / Delivered)
  window.updateNeedStatus = async function(needId, newStatus) {
    try {
      const res = await fetch('/api/needs/status', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ need_id: needId, status: newStatus })
      });
      if (res.ok) {
        await loadDashboardData();
      } else {
        alert('Erro ao atualizar status do item.');
      }
    } catch (err) {
      console.error('Falha na atualização:', err);
    }
  };

  // Copy AI Suggestion to Decision Form
  if (btnCopyAi) {
    btnCopyAi.addEventListener('click', () => {
      const textJustification = document.getElementById('text-justification');
      if (textJustification && lastAiAnalysisText) {
        textJustification.value = lastAiAnalysisText;
        modalAi.close();
        populateNeedSelects(lastAnalyzedNeedId);
        modalDecision.showModal();
      }
    });
  }

  // Submit Nova Necessidade
  if (formNeed) {
    formNeed.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formNeed);
      const payload = {
        title: formData.get('title'),
        category: formData.get('category'),
        quantity: parseInt(formData.get('quantity'), 10),
        priority: formData.get('priority'),
        estimated_budget: parseFloat(formData.get('estimated_budget') || 0),
        responsible: formData.get('responsible'),
        description: formData.get('description') || ''
      };

      try {
        const res = await fetch('/api/needs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          modalNeed.close();
          formNeed.reset();
          await loadDashboardData();
        } else {
          alert('Erro ao cadastrar necessidade.');
        }
      } catch (err) {
        console.error('Falha no envio:', err);
      }
    });
  }

  // Submit Nova Cotação
  if (formAlt) {
    formAlt.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formAlt);
      const payload = {
        need_id: formData.get('need_id'),
        title: formData.get('title'),
        supplier: formData.get('supplier'),
        price: parseFloat(formData.get('price')),
        description: formData.get('description'),
        type: 'Produto Comercial'
      };

      try {
        const res = await fetch('/api/alternatives', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          modalAlternative.close();
          formAlt.reset();
          await loadDashboardData();
        } else {
          alert('Erro ao salvar cotação.');
        }
      } catch (err) {
        console.error('Falha no envio:', err);
      }
    });
  }

  // Submit Registrar Decisão
  if (formDec) {
    formDec.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formDec);
      const payload = {
        need_id: formData.get('need_id'),
        selected_alternative_id: formData.get('selected_alternative_id'),
        technical_justification: formData.get('technical_justification'),
        decided_by: formData.get('decided_by'),
        decision_date: new Date().toISOString().split('T')[0]
      };

      try {
        const res = await fetch('/api/decisions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          modalDecision.close();
          formDec.reset();
          await loadDashboardData();
        } else {
          alert('Erro ao registrar parecer.');
        }
      } catch (err) {
        console.error('Falha no envio:', err);
      }
    });
  }

  async function loadDashboardData() {
    try {
      const response = await fetch('/api/data');
      if (!response.ok) {
        throw new Error('Falha ao obter dados');
      }
      currentData = await response.json();
      renderData(currentData);
    } catch (err) {
      console.warn('Usando estado padrão de demonstração:', err);
      currentData = getFallbackData();
      renderData(currentData);
    }
  }

  function getFallbackData() {
    return {
      version: '0.4.0',
      projects: [{
        id: 'PROJ-PESQUISA-01',
        name: 'Projeto de Pesquisa e Desenvolvimento Tecnológico',
        lead_researcher: 'Pesquisador Responsável'
      }],
      needs: [{
        id: 'NED-001',
        project_id: 'PROJ-PESQUISA-01',
        title: 'Alimentar unidade computacional por 8h em operação de campo',
        category: 'Energia & Infraestrutura',
        quantity: 2,
        priority: 'Essencial',
        status: 'Decidida',
        responsible: 'Equipe de Infraestrutura',
        description: 'PowerStation Portátil LiFePO4 de no mínimo 500Wh para autonomia em campo.'
      }],
      decisions: [{
        id: 'DEC-001',
        need_id: 'NED-001',
        selected_alternative_id: 'ALT-01',
        technical_justification: 'A alternativa ALT-01 cumpre o requisito mandatório de 500Wh (possui 614Wh) e apresenta case estanque IP65 adequado ao ambiente de operação.',
        decided_by: 'Pesquisador Responsável',
        decision_date: '2026-07-29'
      }]
    };
  }

  function renderData(data) {
    const project = data.projects && data.projects[0];
    if (project) {
      document.getElementById('project-header-info').textContent =
        `Projeto: ${project.name} (${project.id}) · Responsável: ${project.lead_researcher}`;
    }

    const needs = data.needs || [];
    const decisions = data.decisions || [];
    const decisionMap = {};
    decisions.forEach(d => { decisionMap[d.need_id] = d; });

    // Update metrics
    document.getElementById('metric-needs-count').textContent = needs.length;
    document.getElementById('metric-decisions-count').textContent = decisions.length;
    document.getElementById('metric-pending-count').textContent = Math.max(0, needs.length - decisions.length);

    // Render Needs System Cards
    const container = document.getElementById('needs-list-container');
    container.innerHTML = '';

    needs.forEach(need => {
      const card = document.createElement('article');
      card.className = 'system-card';
      
      let alternativesHtml = '';
      if (need.alternatives && need.alternatives.length > 0) {
        alternativesHtml = '<div style="margin-top:8px; font-size:0.78rem; border-top:1px solid #dce7ef; padding-top:6px;"><strong>Cotações / Alternativas:</strong><ul style="margin-left:14px;">';
        need.alternatives.forEach(alt => {
          const priceText = alt.prices && alt.prices[0] ? ` — R$ ${alt.prices[0].unit_price.toFixed(2)} (${alt.supplier_or_source})` : '';
          alternativesHtml += `<li>${alt.id}: ${alt.title}${priceText}</li>`;
        });
        alternativesHtml += '</ul></div>';
      }

      const estBudgetCard = need.estimated_budget && need.estimated_budget > 0 ? ` · <strong>Orçamento Est.:</strong> R$ ${need.estimated_budget.toFixed(2)}` : '';
      const descCard = need.description ? `<p style="font-size:0.8rem; color:var(--muted); margin-top:4px; margin-bottom:6px;"><em>${need.description}</em></p>` : '';

      card.innerHTML = `
        <div class="system-card-head">
          <div>
            <h4>${need.title}</h4>
            <p><strong>Código:</strong> ${need.id} · <strong>Categoria:</strong> ${need.category}${estBudgetCard}</p>
          </div>
          <div style="display:flex; align-items:center; gap:6px;">
            <button type="button" class="ai-button" onclick="triggerAiAnalysis('${need.id}')" title="Analisar com IA local (qwen2.5:14b)">⚡ Analisar com IA</button>
            <button type="button" class="secondary-action" style="padding:4px 8px; font-size:0.72rem;" onclick="openEditNeedModal('${need.id}')">✏️ Editar</button>
            <button type="button" class="secondary-action" style="padding:4px 8px; font-size:0.72rem; color:var(--red);" onclick="deleteNeed('${need.id}')">🗑️ Excluir</button>
            <span class="status-pill ${need.status === 'Decidida' || need.status === 'Adquirida' || need.status === 'Entregue' ? 'healthy' : 'degraded'}">${need.status}</span>
          </div>
        </div>
        ${descCard}
        <div class="system-card-meta">
          <span>Quantidade: ${need.quantity} | Prioridade: ${need.priority}</span>
          <span>Responsável: ${need.responsible}</span>
        </div>
        ${alternativesHtml}
      `;
      container.appendChild(card);
    });

    // Render Table
    const tableBody = document.getElementById('needs-table-body');
    tableBody.innerHTML = '';
    needs.forEach(need => {
      const row = document.createElement('tr');
      row.innerHTML = `
        <td><strong>${need.id}</strong></td>
        <td>${need.title}</td>
        <td>${need.category}</td>
        <td>${need.quantity}</td>
        <td><span class="status-pill degraded">${need.priority}</span></td>
        <td><span class="status-pill healthy">${need.status}</span></td>
        <td>
          <button type="button" class="secondary-action" style="padding:4px 8px; font-size:0.72rem;" onclick="openEditNeedModal('${need.id}')">✏️ Editar</button>
          <button type="button" class="secondary-action" style="padding:4px 8px; font-size:0.72rem; color:var(--red);" onclick="deleteNeed('${need.id}')">🗑️ Excluir</button>
        </td>
      `;
      tableBody.appendChild(row);
    });

    // Render Decisions Timeline
    const timeline = document.getElementById('decisions-timeline');
    timeline.innerHTML = '';
    decisions.forEach(dec => {
      const item = document.createElement('div');
      item.className = 'timeline-item';
      item.innerHTML = `
        <div class="timeline-head">
          <strong>Decisão [${dec.id}] — Necessidade ${dec.need_id}</strong>
          <time>${dec.decision_date}</time>
        </div>
        <p><strong>Alternativa Selecionada:</strong> ${dec.selected_alternative_id}</p>
        <p><strong>Decidido por:</strong> ${dec.decided_by}</p>
        <p style="margin-top:6px; font-style:italic;">"${dec.technical_justification}"</p>
      `;
      timeline.appendChild(item);
    });

    // Render Shopping List Tab
    let totalBudget = 0.0;
    let purchasedCount = 0;
    let deliveredCount = 0;
    const shoppingTableBody = document.getElementById('shopping-table-body');
    shoppingTableBody.innerHTML = '';

    needs.forEach(need => {
      const dec = decisionMap[need.id];
      if (need.status === 'Adquirida') purchasedCount++;
      if (need.status === 'Entregue') deliveredCount++;

      let subtotal = 0.0;
      let altTitle = 'Aguardando Parecer';
      let isEstimated = false;

      if (dec && need.alternatives) {
        const alt = need.alternatives.find(a => a.id === dec.selected_alternative_id);
        if (alt) {
          altTitle = alt.title;
          if (alt.prices && alt.prices[0]) {
            subtotal = alt.prices[0].unit_price * need.quantity;
            totalBudget += subtotal;
          }
        }
      } else if (need.estimated_budget && need.estimated_budget > 0) {
        subtotal = need.estimated_budget * need.quantity;
        totalBudget += subtotal;
        isEstimated = true;
      }

      const subtotalDisplay = isEstimated ? `R$ ${subtotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })} <small style="color:var(--muted);">(Estimado)</small>` : `R$ ${subtotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;

      const row = document.createElement('tr');
      row.innerHTML = `
        <td style="text-align:center;"><input type="checkbox" class="shopping-item-check" data-need-id="${need.id}"></td>
        <td><strong>${need.id}</strong></td>
        <td>${need.title}<br><small style="color:var(--muted);">${altTitle}</small></td>
        <td>${need.category}</td>
        <td>${need.quantity}</td>
        <td><strong>${subtotalDisplay}</strong></td>
        <td><span class="status-pill ${need.status === 'Entregue' ? 'healthy' : (need.status === 'Adquirida' ? 'healthy' : 'degraded')}">${need.status}</span></td>
        <td>
          <button type="button" class="secondary-action" style="padding:3px 6px; font-size:0.7rem;" onclick="openEditNeedModal('${need.id}')">✏️ Editar</button>
          <button type="button" class="secondary-action" style="padding:3px 6px; font-size:0.7rem; color:var(--red);" onclick="deleteNeed('${need.id}')">🗑️ Excluir</button>
          <button type="button" class="secondary-action" style="padding:3px 6px; font-size:0.7rem; margin-top:2px;" onclick="updateNeedStatus('${need.id}', 'Adquirida')">Marcar Adquirida</button>
        </td>
      `;
      shoppingTableBody.appendChild(row);
    });

    document.querySelectorAll('.shopping-item-check').forEach(ck => {
      ck.addEventListener('change', updateSelectedCount);
    });
    updateSelectedCount();

    document.getElementById('shopping-total-budget').textContent = `R$ ${totalBudget.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
    document.getElementById('shopping-items-count').textContent = decisions.length;
    document.getElementById('shopping-purchased-count').textContent = purchasedCount;
    document.getElementById('shopping-delivered-count').textContent = deliveredCount;
  }

  if (refreshBtn) {
    refreshBtn.addEventListener('click', loadDashboardData);
  }

  if (needsFilter) {
    needsFilter.addEventListener('input', (e) => {
      const query = e.target.value.toLowerCase();
      const cards = document.querySelectorAll('.system-card');
      cards.forEach(card => {
        const text = card.textContent.toLowerCase();
        card.style.display = text.includes(query) ? 'flex' : 'none';
      });
    });
  }

  loadOllamaModels();
  loadDashboardData();
});
