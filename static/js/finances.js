(function () {
    'use strict';

    // CSRF Token for Flask
    function getCsrfToken() {
    
    return '';
}

    // Global state
    let currentTransactions = [];
    let currentFiscalYearId = '';
    let budgetAllocations = [];
    let charts = {};

    // DOM elements
    const elements = {
        yearFilter: document.getElementById('yearFilter'),
        cashbookSearch: document.getElementById('cashbookSearch'),
        typeFilter: document.getElementById('typeFilter'),
        monthFilter: document.getElementById('monthFilter'),
        cashbookBody: document.getElementById('cashbookBody'),
        transactionForm: document.getElementById('transactionForm'),
        transactionModal: document.getElementById('transactionModal'),
        allocChart: document.getElementById('allocChart'),
        monthlyChart: document.getElementById('monthlyChart'),
        allocLegend: document.getElementById('allocLegend'),
        mandatoryAllocations: document.getElementById('mandatoryAllocations')
    };

    // Initialize
    async function init() {
        if (elements.yearFilter) {
            currentFiscalYearId = elements.yearFilter.value;
        }
        await loadInitialData();
        setupEventListeners();
        renderBudgetChart();
        renderMonthlyChart();
    }

    // Load initial data from template variables
    function loadInitialData() {
        // Try to get data from template variables if available
        const scriptData = document.querySelector('script[data-initial-data]');
        if (scriptData) {
            const data = JSON.parse(scriptData.dataset.initialData);
            currentTransactions = data.transactions || [];
            budgetAllocations = data.budget_allocations || [];
            renderCashbook(currentTransactions);
            updateKpiCards();
        }
    }

    // Load transactions for current fiscal year
    async function loadTransactions(fiscalYearId) {
        try {
            const url = `/finances/data?fy=${fiscalYearId}`;
            const response = await fetch(url);
            const data = await response.json();
            
            currentTransactions = data.transactions || [];
            budgetAllocations = data.budget_allocations || [];
            currentFiscalYearId = fiscalYearId;
            
            renderCashbook(currentTransactions);
            updateKpiCards();
            renderBudgetChart();
            renderMonthlyChart();
        } catch (error) {
            console.error('Error loading transactions:', error);
        }
    }

    // Render cashbook table
    function renderCashbook(transactions) {
        if (!elements.cashbookBody) return;

        const tbody = elements.cashbookBody;
        tbody.innerHTML = transactions.map(t => createTransactionRow(t)).join('');

        // Update footer
        const totals = calculateTotals(transactions);
        if (document.getElementById('rowCount')) {
            document.getElementById('rowCount').textContent = `${transactions.length} transactions shown`;
        }
        if (document.getElementById('totalCollections')) {
            document.getElementById('totalCollections').textContent = `Collections: ₱ ${totals.collections.toLocaleString()}`;
        }
        if (document.getElementById('totalDisbursements')) {
            document.getElementById('totalDisbursements').textContent = `Disbursements: ₱ ${totals.disbursements.toLocaleString()}`;
        }
    }

    function createTransactionRow(t) {
        const isCollection = t.transaction_type?.transaction_types === 'Collection';
        const statusClass = getStatusClass(t.transaction_status?.status_type);
        
        return `
            <tr>
                <td class="ps-4 small text-muted">${formatDate(t.transaction_date)}</td>
                <td class="small fw-semibold">${escapeHtml(t.transaction_description)}</td>
                <td><span class="badge rounded-pill bg-light text-dark border" style="font-size:.72rem;">${escapeHtml(t.category_type?.category_type || 'N/A')}</span></td>
                <td class="small"><code>${escapeHtml(t.document_type?.document_types || '')}-${escapeHtml(t.transaction_docuNumber.split('-').pop() || '')}</code></td>
                <td><span class="badge rounded-pill 
                    ${isCollection ? 'bg-success' : 'bg-danger'} 
                    bg-opacity-10 border 
                    ${isCollection ? 'border-success text-success' : 'border-danger text-danger'}" 
                    style="font-size:.72rem;">${escapeHtml(t.transaction_type?.transaction_types || 'N/A')}</span></td>
                <td class="fw-bold 
                    ${isCollection ? 'text-success' : 'text-danger'}">
                    ${isCollection ? '+' : '-'} ₱ ${parseFloat(t.transaction_amount).toLocaleString()}
                </td>
                <td class="small text-muted">₱ ${parseFloat(t.transaction_running_balance).toLocaleString()}</td>
                <td><span class="badge rounded-pill ${statusClass}" style="font-size:.7rem;">${escapeHtml(t.transaction_status?.status_type || 'N/A')}</span></td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button class="btn btn-outline-primary edit-btn" data-id="${t.id}" data-bs-toggle="modal" data-bs-target="#transactionModal" title="Edit">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger delete-btn" data-id="${t.id}" data-doc="${escapeHtml(t.transaction_docuNumber)}" title="Delete">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }

    function calculateTotals(transactions) {
        return transactions.reduce((totals, t) => {
            const amount = parseFloat(t.transaction_amount);
            if (t.transaction_type?.transaction_types === 'Collection') {
                totals.collections += amount;
            } else {
                totals.disbursements += amount;
            }
            return totals;
        }, { collections: 0, disbursements: 0 });
    }

    function updateKpiCards() {
        const totals = calculateTotals(currentTransactions);
        const balance = totals.collections - totals.disbursements;

        const kpiElements = {
            totalCollectionsKPI: document.getElementById('totalCollectionsKPI'),
            totalDisbursementsKPI: document.getElementById('totalDisbursementsKPI'),
            currentBalance: document.getElementById('currentBalance'),
            dvCount: document.getElementById('dvCount')
        };

        if (kpiElements.totalCollectionsKPI) {
            kpiElements.totalCollectionsKPI.textContent = `₱ ${totals.collections.toLocaleString()}`;
        }
        if (kpiElements.totalDisbursementsKPI) {
            kpiElements.totalDisbursementsKPI.textContent = `₱ ${totals.disbursements.toLocaleString()}`;
        }
        if (kpiElements.currentBalance) {
            kpiElements.currentBalance.textContent = `₱ ${balance.toLocaleString()}`;
        }
        if (kpiElements.dvCount) {
            const dvCount = currentTransactions.filter(t => t.transaction_type?.transaction_types === 'Disbursement').length;
            kpiElements.dvCount.textContent = `${dvCount} DVs`;
        }
    }

    // Charts
    function renderBudgetChart() {
        if (!elements.allocChart) return;
        
        const canvas = elements.allocChart;
        const ctx = canvas.getContext('2d');
        
        if (charts.allocChart) {
            charts.allocChart.destroy();
        }

        const data = budgetAllocations.map(alloc => ({
            label: `${alloc.category_type?.category_type || 'Other'}${alloc.budget_mandatory_percent ? ` (${alloc.budget_mandatory_percent}%)` : ''}`,
            amount: parseFloat(alloc.budget_amount),
            color: ['#198754', '#fd7e14', '#dc3545', '#0d6efd', '#6f42c1', '#20c997'][budgetAllocations.indexOf(alloc) % 6]
        })).filter(item => item.amount > 0);

        renderLegend(data);
        renderMandatoryBadges(data);

        charts.allocChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.map(d => d.label),
                datasets: [{ 
                    data: data.map(d => d.amount), 
                    backgroundColor: data.map(d => d.color), 
                    borderWidth: 2, 
                    borderColor: '#fff' 
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: { 
                    legend: { display: false },
                    tooltip: {
                        callbacks: { 
                            label: ctx => ' ₱ ' + ctx.parsed.toLocaleString()
                        }
                    }
                }
            }
        });
    }

    function renderLegend(data) {
        if (!elements.allocLegend) return;
        elements.allocLegend.innerHTML = data.map(item => `
            <span class="d-flex align-items-center gap-1 small">
                <span style="width:10px;height:10px;border-radius:2px;background:${item.color};display:inline-block;"></span>
                <span style="font-size:.75rem;">${item.label}</span>
            </span>
        `).join('');
    }

    function renderMandatoryBadges(data) {
        if (!elements.mandatoryAllocations) return;
        
        const mandatory = data.filter(item => item.label.includes('%'));
        elements.mandatoryAllocations.innerHTML = `
            <p class="small fw-bold text-muted text-uppercase mb-2" style="font-size:.7rem;letter-spacing:.6px;">Mandatory Allocations (RA 7160)</p>
            <div class="d-flex gap-2 flex-wrap">
                ${mandatory.map(item => `
                    <span class="badge rounded-pill" style="background:${item.color}20;color:${item.color.replace(/..\$/, '77)')};font-size:.78rem;font-weight:500;">
                        ${item.label} — ₱ ${item.amount.toLocaleString()}
                    </span>
                `).join('') || '<span class="text-muted small">No mandatory allocations</span>'}
            </div>
        `;
    }

    function renderMonthlyChart() {
        if (!elements.monthlyChart) return;
        
        const canvas = elements.monthlyChart;
        const ctx = canvas.getContext('2d');
        
        if (charts.monthlyChart) {
            charts.monthlyChart.destroy();
        }

        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const revenue = new Array(12).fill(0);
        const expenses = new Array(12).fill(0);

        currentTransactions.forEach(t => {
            const date = new Date(t.transaction_date);
            const monthIdx = date.getMonth();
            const amount = parseFloat(t.transaction_amount);
            
            if (t.transaction_type?.transaction_types === 'Collection') {
                revenue[monthIdx] += amount;
            } else {
                expenses[monthIdx] += amount;
            }
        });

        charts.monthlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: months,
                datasets: [
                    { 
                        label: 'Revenue', 
                        data: revenue, 
                        backgroundColor: '#19875488', 
                        borderColor: '#198754', 
                        borderWidth: 1.5, 
                        borderRadius: 4 
                    },
                    { 
                        label: 'Expenses', 
                        data: expenses, 
                        backgroundColor: '#dc354588', 
                        borderColor: '#dc3545', 
                        borderWidth: 1.5, 
                        borderRadius: 4 
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { display: false }, ticks: { autoSkip: false } },
                    y: { 
                        grid: { color: '#f0f0f0' }, 
                        ticks: { 
                            callback: v => '₱' + Math.round(v/1000) + 'k' 
                        }
                    }
                }
            }
        });
    }

    // Event listeners
    function setupEventListeners() {
        // Year filter
        if (elements.yearFilter) {
            elements.yearFilter.addEventListener('change', (e) => {
                loadTransactions(e.target.value);
            });
        }

        // Filters
        if (elements.cashbookSearch) {
            elements.cashbookSearch.addEventListener('input', filterCashbook);
        }
        if (elements.typeFilter) {
            elements.typeFilter.addEventListener('change', filterCashbook);
        }
        if (elements.monthFilter) {
            elements.monthFilter.addEventListener('change', filterCashbook);
        }

        // Form submission
        if (elements.transactionForm) {
            elements.transactionForm.addEventListener('submit', handleSaveTransaction);
        }

        // Button clicks
        document.addEventListener('click', handleButtonClicks);

        // Modal reset
        if (elements.transactionModal) {
            elements.transactionModal.addEventListener('hidden.bs.modal', resetModal);
        }
    }

    function filterCashbook() {
        const q = elements.cashbookSearch ? elements.cashbookSearch.value.toLowerCase() : '';
        const type = elements.typeFilter ? elements.typeFilter.value : '';
        const month = elements.monthFilter ? elements.monthFilter.value : '';

        const filtered = currentTransactions.filter(t => {
            const desc = (t.transaction_description || '').toLowerCase();
            const cat = (t.category_type?.category_type || '').toLowerCase();
            const doc = (t.transaction_docuNumber || '').toLowerCase();
            const tMonth = new Date(t.transaction_date).toLocaleString('default', { month: 'long' });
            
            return (!q || desc.includes(q) || cat.includes(q) || doc.includes(q)) &&
                   (!type || t.transaction_type?.transaction_types === type) &&
                   (!month || tMonth === month);
        });

        renderCashbook(filtered);
    }

    function handleButtonClicks(e) {
        const editBtn = e.target.closest('.edit-btn');
        if (editBtn) {
            const id = editBtn.dataset.id;
            loadTransactionForEdit(id);
            updateModalTitle('Edit');
            return;
        }

        const deleteBtn = e.target.closest('.delete-btn');
        if (deleteBtn) {
            const id = deleteBtn.dataset.id;
            const doc = deleteBtn.dataset.doc;
            if (confirm(`Delete transaction ${doc}? This cannot be undone.`)) {
                deleteTransaction(id);
            }
        }
    }

    function updateModalTitle(mode) {
        const titleEl = document.getElementById('modalTitle');
        const iconEl = document.getElementById('modalIcon');
        if (titleEl && iconEl) {
            if (mode === 'Edit') {
                titleEl.innerHTML = '<i class="bi bi-pencil-fill me-2 text-primary" id="modalIcon"></i>Edit Transaction';
                iconEl.className = 'bi bi-pencil-fill me-2 text-primary';
            } else {
                titleEl.innerHTML = '<i class="bi bi-plus-circle-fill me-2 text-success" id="modalIcon"></i>Record New Transaction';
                iconEl.className = 'bi bi-plus-circle-fill me-2 text-success';
            }
        }
    }

    async function loadTransactionForEdit(id) {
        try {
            const response = await fetch(`/edit_transaction/${id}`);
            if (!response.ok) throw new Error('Failed to load transaction');
            
            const transaction = await response.json();
            populateForm(transaction);
        } catch (error) {
            console.error('Error loading transaction:', error);
            alert('Error loading transaction data');
        }
    }

    function populateForm(transaction) {
        document.getElementById('transaction_id').value = transaction.id || '';
        document.getElementById('fiscal_year_id').value = transaction.fiscal_year_id || '';
        document.getElementById('transaction_type_id').value = transaction.transaction_type_id || '';
        document.getElementById('transaction_category_id').value = transaction.transaction_category_id || '';
        document.getElementById('transaction_status_id').value = transaction.transaction_status_id || '';
        document.getElementById('transaction_date').value = transaction.transaction_date ? new Date(transaction.transaction_date).toISOString().split('T')[0] : '';
        document.getElementById('transaction_amount').value = transaction.transaction_amount || '';
        document.getElementById('transaction_description').value = transaction.transaction_description || '';
        document.getElementById('is_deposited').checked = transaction.is_deposited == 1;
        document.getElementById('deposited_date').value = transaction.deposited_date || '';
    }

    async function handleSaveTransaction(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const transactionId = formData.get('transaction_id');
        const url = transactionId ? '/update_transaction' : '/add_transaction';
        
        const saveBtn = document.getElementById('saveTransaction');
        const btnText = document.getElementById('saveBtnText');
        
        if (saveBtn) {
            saveBtn.disabled = true;
            btnText.textContent = 'Saving...';
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (response.ok) {
                const modal = bootstrap.Modal.getInstance(elements.transactionModal);
                if (modal) modal.hide();
                
                await loadTransactions(currentFiscalYearId);
            } else {
                const errorText = await response.text();
                throw new Error(errorText);
            }
        } catch (error) {
            console.error('Error saving transaction:', error);
            alert(`Error: ${error.message}`);
        } finally {
            if (saveBtn) {
                saveBtn.disabled = false;
                btnText.textContent = transactionId ? 'Update Transaction' : 'Save Transaction';
            }
        }
    }

    async function deleteTransaction(id) {
        try {
            const response = await fetch(`/delete_transaction/${id}`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken()
                }
            });

            if (response.ok) {
                await loadTransactions(currentFiscalYearId);
            } else {
                const errorText = await response.text();
                throw new Error(errorText);
            }
        } catch (error) {
            console.error('Error deleting transaction:', error);
            alert(`Error: ${error.message}`);
        }
    }

    function resetModal() {
        if (elements.transactionForm) {
            elements.transactionForm.reset();
        }
        document.getElementById('transaction_id').value = '';
        updateModalTitle('Add');
        document.getElementById('saveBtnText').textContent = 'Save Transaction';
    }

    // Utility functions
    function formatDate(dateString) {
        try {
            return new Date(dateString).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });
        } catch {
            return dateString;
        }
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    function getStatusClass(status) {
        if (!status) return 'bg-secondary';
        if (status === 'Deposited' || status === 'Paid') return 'bg-success';
        if (status === 'Pending') return 'bg-warning text-dark';
        return 'bg-secondary';
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();