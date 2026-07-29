document.addEventListener('DOMContentLoaded', () => {
  const tabs = document.querySelectorAll('.nav-link');
  const tabContents = document.querySelectorAll('.tab-content');
  const refreshBtn = document.getElementById('refresh-btn');
  const needsFilter = document.getElementById('needs-filter');

  // Modais
  const modalNeed = document.getElementById('modal-need');
  const modalAlternative = document.getElementById('modal-alternative');
  const modalDecision = document.getElementById('modal-decision');
  const modalAi = document.getElementById('modal-ai-analysis');

  const btnOpenNeed = document.getElementById('btn-open-need-modal');
  const btnOpenAlt = document.getElementById('btn-open-alt-modal');
  const btnOpenDec = document.getElementById('btn-open-dec-modal');
  const btnCopyAi = document.getElementById('btn-copy-ai-suggestion');

  const formNeed = document.getElementById('form-need');
  const formAlt = document.getElementById('form-alternative');
  const formDec = document.getElementById('form-decision');

  const selectOllama = document.getElementById('select-ollama-model');

  let currentData = null;
  let lastAiAnalysisText = '';
  let lastAnalyzedNeedId = '';

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
        body: JSON.stringify({ need_id: needId, model: model })
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
        responsible: formData.get('responsible')
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
      version: '0.2.0',
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
        responsible: 'Equipe de Infraestrutura'
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

      card.innerHTML = `
        <div class="system-card-head">
          <div>
            <h4>${need.title}</h4>
            <p><strong>Código:</strong> ${need.id} · <strong>Categoria:</strong> ${need.category}</p>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <button type="button" class="ai-button" onclick="triggerAiAnalysis('${need.id}')" title="Analisar com IA local (qwen2.5:14b)">⚡ Analisar com IA</button>
            <span class="status-pill ${need.status === 'Decidida' ? 'healthy' : 'degraded'}">${need.status}</span>
          </div>
        </div>
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
