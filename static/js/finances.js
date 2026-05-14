(function () {
    /* ── Allocation Doughnut ── */
    const allocData = {
        labels: ['Development Fund (20%)', 'SK Fund (10%)', 'Calamity Fund (5%)', 'Salaries & Wages', 'Operations', 'Discretionary'],
        amounts: [250000, 125000, 62500, 350000, 220000, 242500],
        colors: ['#198754', '#fd7e14', '#dc3545', '#0d6efd', '#6f42c1', '#20c997'],
    };
    const legend = document.getElementById('allocLegend');
    allocData.labels.forEach((l, i) => {
        legend.innerHTML += `<span class="d-flex align-items-center gap-1 small">
            <span style="width:10px;height:10px;border-radius:2px;background:${allocData.colors[i]};display:inline-block;"></span>
            <span style="font-size:.75rem;">${l}</span></span>`;
    });
    new Chart(document.getElementById('allocChart'), {
        type: 'doughnut',
        data: {
            labels: allocData.labels,
            datasets: [{ data: allocData.amounts, backgroundColor: allocData.colors, borderWidth: 2, borderColor: '#fff' }]
        },
        options: {
            responsive: true, maintainAspectRatio: false, cutout: '62%',
            plugins: { legend: { display: false }, tooltip: {
                callbacks: { label: ctx => ' ₱ ' + ctx.parsed.toLocaleString() }
            }}
        }
    });

    /* ── Monthly Revenue vs Expense Chart ── */
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const revenue  = [85000, 72000, 91000, 88000, 0, 0, 0, 0, 0, 0, 0, 0];
    const expenses = [60000, 55000, 80000, 72000, 0, 0, 0, 0, 0, 0, 0, 0];
    new Chart(document.getElementById('monthlyChart'), {
        type: 'bar',
        data: {
            labels: months,
            datasets: [
                { label: 'Revenue', data: revenue, backgroundColor: '#19875488', borderColor: '#198754', borderWidth: 1.5, borderRadius: 4 },
                { label: 'Expenses', data: expenses, backgroundColor: '#dc354588', borderColor: '#dc3545', borderWidth: 1.5, borderRadius: 4 }
            ]
        },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { autoSkip: false } },
                y: { grid: { color: '#f0f0f0' }, ticks: { callback: v => '₱' + (v/1000).toFixed(0) + 'k' } }
            }
        }
    });

    /* ── Cashbook Transactions (mock data) ── */
    const transactions = [
        { date:'April 22, 2026', month:'April', desc:'IRA Release — 1st Quarter', category:'IRA', docType:'OR', docNo:'OR-00451', type:'Collection', amount:150000, status:'Deposited' },
        { date:'April 20, 2026', month:'April', desc:'Barangay Clearance Fees', category:'Clearance Fees', docType:'OR', docNo:'OR-00450', type:'Collection', amount:1250, status:'Deposited' },
        { date:'April 18, 2026', month:'April', desc:'Business Permit Fees', category:'Permits & Licenses', docType:'OR', docNo:'OR-00449', type:'Collection', amount:3200, status:'Deposited' },
        { date:'April 15, 2026', month:'April', desc:'Electricity Bill — Barangay Hall', category:'Utilities', docType:'DV', docNo:'DV-00038', type:'Disbursement', amount:5400, status:'Paid' },
        { date:'April 12, 2026', month:'April', desc:'Senior Citizen Event Supplies', category:'Social Services', docType:'DV', docNo:'DV-00037', type:'Disbursement', amount:12000, status:'Pending' },
        { date:'March 30, 2026', month:'March', desc:'Salaries — March 2026', category:'Salaries & Wages', docType:'PR', docNo:'PR-00012', type:'Disbursement', amount:45000, status:'Paid' },
        { date:'March 25, 2026', month:'March', desc:'Road Drainage Repair — Purok 3', category:'Development Projects', docType:'DV', docNo:'DV-00036', type:'Disbursement', amount:28000, status:'Paid' },
        { date:'March 15, 2026', month:'March', desc:'Barangay Clearance Fees', category:'Clearance Fees', docType:'OR', docNo:'OR-00448', type:'Collection', amount:950, status:'Deposited' },
        { date:'February 28, 2026', month:'February', desc:'IRA Release — Feb', category:'IRA', docType:'OR', docNo:'OR-00447', type:'Collection', amount:75000, status:'Deposited' },
        { date:'February 20, 2026', month:'February', desc:'Water Bill — Brgy Hall', category:'Utilities', docType:'DV', docNo:'DV-00035', type:'Disbursement', amount:1800, status:'Paid' },
        { date:'January 31, 2026', month:'January', desc:'Salaries — January 2026', category:'Salaries & Wages', docType:'PR', docNo:'PR-00011', type:'Disbursement', amount:45000, status:'Paid' },
        { date:'January 10, 2026', month:'January', desc:'IRA Release — Jan', category:'IRA', docType:'OR', docNo:'OR-00446', type:'Collection', amount:75000, status:'Deposited' },
    ];

    let balance = 0;
    const withBalance = transactions.slice().reverse().map(t => {
        balance += t.type === 'Collection' ? t.amount : -t.amount;
        return { ...t, balance };
    }).reverse();

    function renderCashbook(rows) {
        const tbody = document.getElementById('cashbookBody');
        tbody.innerHTML = '';
        let totalC = 0, totalD = 0;
        rows.forEach(t => {
            totalC += t.type === 'Collection' ? t.amount : 0;
            totalD += t.type === 'Disbursement' ? t.amount : 0;
            const isCol = t.type === 'Collection';
            const statusColor = t.status === 'Deposited' || t.status === 'Paid' ? 'bg-success' : 'bg-warning text-dark';
            tbody.innerHTML += `
                <tr>
                    <td class="ps-4 small text-muted">${t.date}</td>
                    <td class="small fw-semibold">${t.desc}</td>
                    <td><span class="badge rounded-pill bg-light text-dark border" style="font-size:.72rem;">${t.category}</span></td>
                    <td class="small"><code>${t.docType}-${t.docNo.split('-')[1]}</code></td>
                    <td><span class="badge rounded-pill ${isCol ? 'bg-success' : 'bg-danger'} bg-opacity-10 border ${isCol ? 'border-success text-success' : 'border-danger text-danger'}" style="font-size:.72rem;">${t.type}</span></td>
                    <td class="fw-bold ${isCol ? 'text-success' : 'text-danger'}">${isCol ? '+' : '-'} ₱ ${t.amount.toLocaleString()}</td>
                    <td class="small text-muted">₱ ${t.balance.toLocaleString()}</td>
                    <td><span class="badge rounded-pill ${statusColor}" style="font-size:.7rem;">${t.status}</span></td>
                </tr>`;
        });
        document.getElementById('rowCount').textContent = rows.length + ' transactions shown';
        document.getElementById('totalCollections').textContent = 'Collections: ₱ ' + totalC.toLocaleString();
        document.getElementById('totalDisbursements').textContent = 'Disbursements: ₱ ' + totalD.toLocaleString();
    }
    renderCashbook(withBalance);

    function filterCashbook() {
        const q = document.getElementById('cashbookSearch').value.toLowerCase();
        const type = document.getElementById('typeFilter').value;
        const month = document.getElementById('monthFilter').value;
        const filtered = withBalance.filter(t =>
            (!q || t.desc.toLowerCase().includes(q) || t.category.toLowerCase().includes(q) || t.docNo.toLowerCase().includes(q)) &&
            (!type || t.type === type) &&
            (!month || t.month === month)
        );
        renderCashbook(filtered);
    }
    document.getElementById('cashbookSearch').addEventListener('input', filterCashbook);
    document.getElementById('typeFilter').addEventListener('change', filterCashbook);
    document.getElementById('monthFilter').addEventListener('change', filterCashbook);

    /* ── Monthly Accountability Report ── */
    const marData = [
        { month: 'January 2026', col: 75000, dis: 45000, dvs: 4, ors: 3, submitted: 'Feb 5, 2026', status: 'Accepted' },
        { month: 'February 2026', col: 72000, dis: 55000, dvs: 5, ors: 4, submitted: 'Mar 4, 2026', status: 'Accepted' },
        { month: 'March 2026', col: 91000, dis: 80000, dvs: 9, ors: 6, submitted: 'Apr 3, 2026', status: 'Under Review' },
        { month: 'April 2026', col: 0, dis: 0, dvs: 0, ors: 0, submitted: '—', status: 'Pending' },
    ];
    const marBody = document.getElementById('marBody');
    marData.forEach(r => {
        const net = r.col - r.dis;
        const statusMap = { 'Accepted': 'bg-success', 'Under Review': 'bg-warning text-dark', 'Pending': 'bg-secondary' };
        marBody.innerHTML += `
            <tr>
                <td class="ps-4 fw-semibold small">${r.month}</td>
                <td class="text-success fw-bold small">₱ ${r.col.toLocaleString()}</td>
                <td class="text-danger fw-bold small">₱ ${r.dis.toLocaleString()}</td>
                <td class="fw-bold small ${net >= 0 ? 'text-primary' : 'text-danger'}">₱ ${net.toLocaleString()}</td>
                <td class="small">${r.dvs}</td>
                <td class="small">${r.ors}</td>
                <td class="small text-muted">${r.submitted}</td>
                <td><span class="badge rounded-pill ${statusMap[r.status]}" style="font-size:.72rem;">${r.status}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-dark py-0 px-2" style="font-size:.75rem;" ${r.status === 'Pending' ? 'disabled' : ''}>
                        <i class="bi bi-eye me-1"></i>View
                    </button>
                </td>
            </tr>`;
    });

    /* ── Save Transaction (mock) ── */
    document.getElementById('saveTransaction').addEventListener('click', () => {
        const desc = document.getElementById('txDesc').value.trim();
        const amount = document.getElementById('txAmount').value;
        if (!desc || !amount) {
            alert('Please fill in Description and Amount.');
            return;
        }
        const modal = bootstrap.Modal.getInstance(document.getElementById('transactionModal'));
        modal.hide();
        // Reset form
        ['txDesc','txAmount','txDocNo','txRemarks'].forEach(id => document.getElementById(id).value = '');
        // Show success toast (simple alert for now — wire to Flask flash later)
        setTimeout(() => alert('Transaction recorded! (Connect to /finances/add route to persist.)'), 300);
    });

})();
