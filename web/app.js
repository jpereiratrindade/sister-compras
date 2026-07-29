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
  const modalProject = document.getElementById('modal-project');
  const modalAi = document.getElementById('modal-ai-analysis');
  const modalChat = document.getElementById('modal-ai-chat');

  const btnOpenNeed = document.getElementById('btn-open-need-modal');
  const btnOpenNeed2 = document.getElementById('btn-open-need-modal-2');
  const btnOpenAlt = document.getElementById('btn-open-alt-modal');
  const btnOpenAlt2 = document.getElementById('btn-open-alt-modal-2');
  const btnOpenDec = document.getElementById('btn-open-dec-modal');
  const btnOpenDec2 = document.getElementById('btn-open-dec-modal-2');
  const btnOpenProject = document.getElementById('btn-open-project-modal');
  const btnOpenChat = document.getElementById('btn-open-chat-modal');
  const btnCopyAi = document.getElementById('btn-copy-ai-suggestion');
  const btnAiSpecify = document.getElementById('btn-ai-specify-reqs');
  const btnPrintSelected = document.getElementById('btn-print-selected-shopping');
  const btnExportCsv = document.getElementById('btn-export-needs-csv');
  const checkAllShopping = document.getElementById('check-all-shopping');

  // Controles de Filtro da Tabela de Necessidades
  const tabNeedsSearch = document.getElementById('tab-needs-search');
  const filterCategory = document.getElementById('filter-need-category');
  const filterPriority = document.getElementById('filter-need-priority');
  const filterStatus = document.getElementById('filter-need-status');

  // Controles de Filtro da Aba de Decisões
  const tabDecisionsSearch = document.getElementById('tab-decisions-search');

  const formNeed = document.getElementById('form-need');
  const formEditNeed = document.getElementById('form-edit-need');
  const formAlt = document.getElementById('form-alternative');
  const formDec = document.getElementById('form-decision');
  const formProject = document.getElementById('form-project');
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

  function prefillLeadResearcherInForms() {
    const leadName = (currentData && currentData.projects && currentData.projects[0] && currentData.projects[0].lead_researcher) ? currentData.projects[0].lead_researcher : 'José Pedro Trindade';

    const responsibleInput = document.querySelector('form#form-need input[name="responsible"]');
    if (responsibleInput && (!responsibleInput.value || responsibleInput.value === 'Equipe de Pesquisa')) {
      responsibleInput.value = leadName;
    }

    const decidedByInput = document.querySelector('form#form-decision input[name="decided_by"]');
    if (decidedByInput && (!decidedByInput.value || decidedByInput.value === 'Pesquisador Responsável')) {
      decidedByInput.value = leadName;
    }
  }

  // Global functions for decision modal opening
  window.openDecisionModal = function(targetNeedId = null) {
    populateNeedSelects(targetNeedId);
    prefillLeadResearcherInForms();
    if (modalDecision) modalDecision.showModal();
  };

  window.openAlternativeModal = function(targetNeedId = null) {
    populateNeedSelects(targetNeedId);
    if (modalAlternative) modalAlternative.showModal();
  };

  window.openNeedModal = function() {
    prefillLeadResearcherInForms();
    if (modalNeed) modalNeed.showModal();
  };

  // Modal controls
  if (btnOpenNeed) btnOpenNeed.addEventListener('click', () => window.openNeedModal());
  if (btnOpenNeed2) btnOpenNeed2.addEventListener('click', () => window.openNeedModal());
  if (btnOpenAlt) btnOpenAlt.addEventListener('click', () => window.openAlternativeModal());
  if (btnOpenAlt2) btnOpenAlt2.addEventListener('click', () => window.openAlternativeModal());
  if (btnOpenDec) btnOpenDec.addEventListener('click', () => window.openDecisionModal());
  if (btnOpenDec2) btnOpenDec2.addEventListener('click', () => window.openDecisionModal());
  if (btnOpenChat) btnOpenChat.addEventListener('click', () => modalChat.showModal());

  if (btnOpenProject) {
    btnOpenProject.addEventListener('click', () => {
      const proj = (currentData && currentData.projects && currentData.projects[0]) ? currentData.projects[0] : {};
      const leadInput = document.getElementById('project-lead-researcher-input');
      const nameInput = document.getElementById('project-name-input');

      if (leadInput) leadInput.value = proj.lead_researcher || 'José Pedro Trindade';
      if (nameInput) nameInput.value = proj.name || 'Projeto de Pesquisa e Desenvolvimento Tecnológico';

      if (modalProject) modalProject.showModal();
    });
  }

  document.querySelectorAll('.close-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const dialog = e.target.closest('dialog');
      if (dialog) dialog.close();
    });
  });

  // Exportar Necessidades para CSV
  if (btnExportCsv) {
    btnExportCsv.addEventListener('click', () => {
      if (!currentData || !currentData.needs || currentData.needs.length === 0) {
        alert('Nenhuma necessidade disponível para exportação.');
        return;
      }
      let csvContent = "data:text/csv;charset=utf-8,";
      csvContent += "Código,Título/Necessidade,Categoria,Quantidade,Prioridade,Status,Orçamento Estimado (R$),Responsável,Descrição Técnica\n";

      currentData.needs.forEach(n => {
        const title = `"${(n.title || '').replace(/"/g, '""')}"`;
        const cat = `"${(n.category || '').replace(/"/g, '""')}"`;
        const prio = `"${(n.priority || '').replace(/"/g, '""')}"`;
        const st = `"${(n.status || '').replace(/"/g, '""')}"`;
        const resp = `"${(n.responsible || '').replace(/"/g, '""')}"`;
        const desc = `"${(n.description || '').replace(/"/g, '""')}"`;
        const estBudget = (n.estimated_budget || 0).toFixed(2);

        csvContent += `${n.id},${title},${cat},${n.quantity || 1},${prio},${st},${estBudget},${resp},${desc}\n`;
      });

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `necessidades_sister_compras_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    });
  }

  // Bind filter change listeners
  [tabNeedsSearch, filterCategory, filterPriority, filterStatus].forEach(el => {
    if (el) {
      el.addEventListener('input', () => {
        if (currentData) renderNeedsTable(currentData.needs || []);
      });
      el.addEventListener('change', () => {
        if (currentData) renderNeedsTable(currentData.needs || []);
      });
    }
  });

  if (tabDecisionsSearch) {
    tabDecisionsSearch.addEventListener('input', () => {
      if (currentData) renderDecisionsTimeline(currentData.decisions || [], currentData.needs || []);
    });
  }

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

  function updateAlternativesDropdown() {
    const selDec = document.getElementById('select-need-for-dec');
    const selAltDec = document.getElementById('select-alt-for-dec');
    if (!selDec || !selAltDec || !currentData || !currentData.needs) return;

    selAltDec.innerHTML = '';
    const selectedNeedId = selDec.value;
    const need = currentData.needs.find(n => n.id === selectedNeedId);

    if (need && need.alternatives && need.alternatives.length > 0) {
      need.alternatives.forEach(alt => {
        const opt = document.createElement('option');
        opt.value = alt.id;
        const priceText = alt.prices && alt.prices[0] ? ` (R$ ${alt.prices[0].unit_price.toFixed(2)})` : '';
        opt.textContent = `${alt.id}: ${alt.title}${priceText} — ${alt.supplier_or_source || 'N/A'}`;
        selAltDec.appendChild(opt);
      });
    } else {
      const opt = document.createElement('option');
      opt.value = 'ALT-ESTIMADO';
      opt.textContent = 'Aprovação por Orçamento Estimado (Especificação Técnica Aprovada)';
      selAltDec.appendChild(opt);
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

    selDec.removeEventListener('change', updateAlternativesDropdown);
    selDec.addEventListener('change', updateAlternativesDropdown);
    updateAlternativesDropdown();
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
    document.getElementById('edit-need-responsible').value = need.responsible || (currentData.projects && currentData.projects[0] ? currentData.projects[0].lead_researcher : 'José Pedro Trindade');
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

  // Submit Edição do Projeto & Pesquisador Responsável
  if (formProject) {
    formProject.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(formProject);
      const payload = {
        lead_researcher: formData.get('lead_researcher'),
        name: formData.get('name')
      };

      try {
        const res = await fetch('/api/project/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (res.ok) {
          modalProject.close();
          await loadDashboardData();
        } else {
          alert('Erro ao atualizar dados do pesquisador responsável.');
        }
      } catch (err) {
        console.error('Falha na atualização do projeto:', err);
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
        window.openDecisionModal(lastAnalyzedNeedId);
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
        lead_researcher: 'José Pedro Trindade'
      }],
      needs: [{
        id: 'NED-001',
        project_id: 'PROJ-PESQUISA-01',
        title: 'Alimentar unidade computacional por 8h em operação de campo',
        category: 'Energia & Infraestrutura',
        quantity: 2,
        priority: 'Essencial',
        status: 'Decidida',
        responsible: 'José Pedro Trindade',
        description: 'PowerStation Portátil LiFePO4 de no mínimo 500Wh para autonomia em campo.'
      }],
      decisions: [{
        id: 'DEC-001',
        need_id: 'NED-001',
        selected_alternative_id: 'ALT-01',
        technical_justification: 'A alternativa ALT-01 cumpre o requisito mandatório de 500Wh (possui 614Wh) e apresenta case estanque IP65 adequado ao ambiente de operação.',
        decided_by: 'José Pedro Trindade',
        decision_date: '2026-07-29'
      }]
    };
  }

  function renderNeedsTable(needs) {
    const tableBody = document.getElementById('needs-table-body');
    if (!tableBody) return;
    tableBody.innerHTML = '';

    const query = tabNeedsSearch ? tabNeedsSearch.value.trim().toLowerCase() : '';
    const catVal = filterCategory ? filterCategory.value : '';
    const prioVal = filterPriority ? filterPriority.value : '';
    const stVal = filterStatus ? filterStatus.value : '';

    const filtered = needs.filter(need => {
      if (catVal && need.category !== catVal) return false;
      if (prioVal && need.priority !== prioVal) return false;
      if (stVal && need.status !== stVal) return false;
      if (query) {
        const fullText = `${need.id} ${need.title} ${need.category} ${need.responsible} ${need.description || ''}`.toLowerCase();
        if (!fullText.includes(query)) return false;
      }
      return true;
    });

    if (filtered.length === 0) {
      tableBody.innerHTML = '<tr><td colspan="9" style="text-align:center; padding:24px; color:var(--muted);">*Nenhuma necessidade encontrada para os filtros selecionados.*</td></tr>';
      return;
    }

    filtered.forEach(need => {
      const row = document.createElement('tr');
      const estBudgetStr = need.estimated_budget && need.estimated_budget > 0 ? `R$ ${need.estimated_budget.toFixed(2)}` : 'R$ 0,00';

      row.innerHTML = `
        <td><strong>${need.id}</strong></td>
        <td>
          <div style="font-weight:bold; color:var(--navy);">${need.title}</div>
          ${need.description ? `<small style="color:var(--muted); display:block; font-size:0.75rem;">${need.description}</small>` : ''}
        </td>
        <td>${need.category}</td>
        <td>${need.quantity}</td>
        <td><strong>${estBudgetStr}</strong></td>
        <td><span class="status-pill degraded">${need.priority}</span></td>
        <td><span class="status-pill healthy">${need.status}</span></td>
        <td><small style="color:var(--muted); font-weight:600;">${need.responsible}</small></td>
        <td style="white-space:nowrap;">
          <button type="button" class="ai-button" style="padding:3px 7px; font-size:0.7rem;" onclick="triggerAiAnalysis('${need.id}')" title="Analisar com IA local (qwen2.5:14b)">⚡ IA</button>
          <button type="button" class="secondary-action" style="padding:3px 6px; font-size:0.7rem;" onclick="openEditNeedModal('${need.id}')">✏️ Editar</button>
          <button type="button" class="secondary-action" style="padding:3px 6px; font-size:0.7rem; color:var(--red);" onclick="deleteNeed('${need.id}')">🗑️ Excluir</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  }

  function renderDecisionsTimeline(decisions, needs) {
    const timelineContainer = document.getElementById('decisions-timeline');
    if (!timelineContainer) return;
    timelineContainer.innerHTML = '';

    const query = tabDecisionsSearch ? tabDecisionsSearch.value.trim().toLowerCase() : '';
    const needsMap = {};
    needs.forEach(n => { needsMap[n.id] = n; });

    const filtered = decisions.filter(dec => {
      if (!query) return true;
      const targetNeed = needsMap[dec.need_id] || {};
      const fullText = `${dec.id} ${dec.need_id} ${targetNeed.title || ''} ${dec.decided_by} ${dec.technical_justification}`.toLowerCase();
      return fullText.includes(query);
    });

    if (filtered.length === 0) {
      timelineContainer.innerHTML = `
        <div style="text-align:center; padding:48px 24px; background:#f8fafc; border:1px dashed #cbd5e1; border-radius:12px; margin-top:12px;">
          <div style="font-size:2.4rem; margin-bottom:8px;">📋</div>
          <h3 style="margin:0 0 6px 0; color:var(--navy); font-size:1.1rem;">Nenhum Parecer Técnico Registrado</h3>
          <p style="margin:0 0 16px 0; font-size:0.85rem; color:var(--muted);">Registre a aprovação humana de uma cotação para formalizar o parecer técnico e gerar a trilha de auditoria.</p>
          <button type="button" class="primary-action" onclick="window.openDecisionModal();" style="display:inline-flex; align-items:center; gap:6px;">
            + Registrar Primeiro Parecer Técnico
          </button>
        </div>
      `;
      return;
    }

    filtered.forEach(dec => {
      const need = needsMap[dec.need_id] || { title: 'Necessidade não encontrada', category: 'N/A' };
      let selectedAltTitle = dec.selected_alternative_id;
      let supplierName = 'N/A';

      if (need.alternatives) {
        const alt = need.alternatives.find(a => a.id === dec.selected_alternative_id);
        if (alt) {
          selectedAltTitle = alt.title;
          supplierName = alt.supplier_or_source || 'N/A';
        }
      }

      const card = document.createElement('article');
      card.style.background = '#fff';
      card.style.border = '1px solid #e2e8f0';
      card.style.borderRadius = '12px';
      card.style.padding = '20px';
      card.style.boxShadow = '0 4px 14px rgba(9,37,75,0.04)';
      card.style.display = 'flex';
      card.style.flexDirection = 'column';
      card.style.gap = '12px';

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #edf2f7; padding-bottom:10px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <span style="background:var(--teal); color:#fff; font-size:0.75rem; font-weight:bold; padding:4px 10px; border-radius:12px;">✅ Decisão Humana Validada</span>
            <strong style="color:var(--navy); font-size:0.9rem;">${dec.id}</strong>
            <span style="color:var(--muted); font-size:0.8rem;">· ${dec.decision_date}</span>
          </div>
          <div>
            <button type="button" class="ai-button" onclick="triggerAiAnalysis('${dec.need_id}')" style="padding:4px 10px; font-size:0.75rem;" title="Reanalisar conformidade técnica com IA (qwen2.5:14b)">
              ⚡ Reanalisar com IA
            </button>
          </div>
        </div>

        <div>
          <span style="font-size:0.78rem; font-weight:bold; color:var(--teal); text-transform:uppercase;">Necessidade Vinculada</span>
          <h4 style="margin:2px 0 0 0; font-size:1.05rem; color:var(--navy); font-weight:700;">${need.id} — ${need.title}</h4>
        </div>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; background:#f8fafc; padding:12px; border-radius:8px; border:1px solid #e2e8f0; font-size:0.83rem;">
          <div>
            <strong style="color:var(--navy); display:block; margin-bottom:2px;">Alternativa / Cotação Aprovada:</strong>
            <span style="color:#09254b; font-weight:600;">${dec.selected_alternative_id}: ${selectedAltTitle}</span>
          </div>
          <div>
            <strong style="color:var(--navy); display:block; margin-bottom:2px;">Aprovado por:</strong>
            <span style="color:#09254b;">${dec.decided_by}</span>
          </div>
        </div>

        <div style="background:#eaf7f5; border-left:4px solid var(--teal); padding:12px 16px; border-radius:0 8px 8px 0; font-size:0.85rem; color:#0c3634;">
          <strong style="display:block; margin-bottom:4px; font-size:0.78rem; text-transform:uppercase; color:#0e5d59;">Parecer & Justificativa Técnica:</strong>
          <span style="font-style:italic; line-height:1.5;">"${dec.technical_justification}"</span>
        </div>
      `;

      timelineContainer.appendChild(card);
    });
  }

  function renderData(data) {
    const project = data.projects && data.projects[0];
    if (project) {
      const headerEl = document.getElementById('project-header-info');
      if (headerEl) {
        headerEl.textContent = `Projeto: ${project.name} (${project.id}) · Pesquisador: ${project.lead_researcher || 'José Pedro Trindade'}`;
      }
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

      const estBudgetHtml = need.estimated_budget && need.estimated_budget > 0 ? `<strong>Orçamento Est.:</strong> R$ ${need.estimated_budget.toFixed(2)}` : '';
      const descCard = need.description ? `<div style="font-size:0.83rem; color:#475569; line-height:1.5; background:#f8fafc; padding:10px 12px; border-radius:8px; border:1px solid #e2e8f0; word-break:break-word;"><strong style="color:#334155;">Descrição Técnica:</strong> ${need.description}</div>` : '';

      card.innerHTML = `
        <!-- Header Top: ID + Status + Budget -->
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #edf2f7; padding-bottom:8px;">
          <div style="display:flex; align-items:center; gap:8px;">
            <strong style="color:var(--teal); font-size:0.88rem;">${need.id}</strong>
            <span class="status-pill ${need.status === 'Decidida' || need.status === 'Adquirida' || need.status === 'Entregue' ? 'healthy' : 'degraded'}">${need.status}</span>
          </div>
          <div style="font-size:0.8rem; color:var(--navy); font-weight:600;">
            ${estBudgetHtml}
          </div>
        </div>

        <!-- Title & Category (Full Width) -->
        <div style="width:100%;">
          <h3 style="margin:0 0 4px 0; font-size:1.05rem; font-weight:700; color:var(--navy); line-height:1.35; word-break:break-word;">${need.title}</h3>
          <div style="font-size:0.8rem; color:var(--muted);"><strong>Categoria:</strong> ${need.category}</div>
        </div>

        <!-- Description Box -->
        ${descCard}

        <!-- Meta Info -->
        <div style="display:flex; justify-content:space-between; font-size:0.78rem; color:var(--muted); border-top:1px solid #f1f5f9; padding-top:8px; margin-top:auto;">
          <span><strong>Qtd:</strong> ${need.quantity} | <strong>Prioridade:</strong> ${need.priority}</span>
          <span><strong>Responsável:</strong> ${need.responsible}</span>
        </div>

        <!-- Actions Toolbar -->
        <div style="display:flex; justify-content:flex-end; align-items:center; gap:8px; padding-top:6px; border-top:1px dashed #e2e8f0;">
          <button type="button" class="ai-button" onclick="triggerAiAnalysis('${need.id}')" title="Analisar com IA local (qwen2.5:14b)">⚡ Analisar com IA</button>
          <button type="button" class="secondary-action" style="padding:4px 10px; font-size:0.75rem;" onclick="openEditNeedModal('${need.id}')">✏️ Editar</button>
          <button type="button" class="secondary-action" style="padding:4px 10px; font-size:0.75rem; color:var(--red);" onclick="deleteNeed('${need.id}')">🗑️ Excluir</button>
        </div>

        ${alternativesHtml}
      `;
      container.appendChild(card);
    });

    // Render Needs Table with Filters
    renderNeedsTable(needs);

    // Render Decisions Timeline with Interactive Cards & Search
    renderDecisionsTimeline(decisions, needs);

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
