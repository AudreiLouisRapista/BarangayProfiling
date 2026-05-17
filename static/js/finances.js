(function () {

    /* ── Allocation Doughnut Chart ── */
    const allocLabels  = typeof budgetAllocations !== 'undefined' ? budgetAllocations : [];
    const allocAmounts = typeof budgetAmounts !== 'undefined' ? budgetAmounts : [];
    const allocColors  = [
        '#198754', '#fd7e14', '#dc3545',
        '#0d6efd', '#6f42c1', '#20c997',
        '#ffc107', '#0dcaf0', '#6c757d', '#d63384'
    ];

    const allocLegend = document.getElementById('allocLegend');
    if (allocLegend) {
        allocLabels.forEach((label, i) => {
            allocLegend.innerHTML += `
                <span class="d-flex align-items-center gap-1 small">
                    <span style="width:10px;height:10px;border-radius:2px;
                                 background:${allocColors[i % allocColors.length]};
                                 display:inline-block;"></span>
                    <span style="font-size:.75rem;">${label}</span>
                </span>`;
        });
    }

    const allocCanvas = document.getElementById('allocChart');
    if (allocCanvas) {
        if (allocAmounts.length > 0) {
            new Chart(allocCanvas, {
                type: 'doughnut',
                data: {
                    labels: allocLabels,
                    datasets: [{
                        data: allocAmounts,
                        backgroundColor: allocColors.slice(0, allocAmounts.length),
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
                                label: ctx => ' ₱ ' + Number(ctx.parsed).toLocaleString()
                            }
                        }
                    }
                }
            });
        } else {
            // No allocations yet — show placeholder
            allocCanvas.parentElement.innerHTML = `
                <div class="d-flex align-items-center justify-content-center h-100 text-muted small">
                    <i class="bi bi-pie-chart me-2"></i> No budget allocations recorded yet.
                </div>`;
        }
    }

    /* ── Monthly Revenue vs Expenses Bar Chart ── */
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    const revenue  = (typeof monthlyData !== 'undefined' && monthlyData.revenue)
                     ? monthlyData.revenue
                     : Array(12).fill(0);
    const expenses = (typeof monthlyData !== 'undefined' && monthlyData.expenses)
                     ? monthlyData.expenses
                     : Array(12).fill(0);

    const monthlyCanvas = document.getElementById('monthlyChart');
    if (monthlyCanvas) {
        new Chart(monthlyCanvas, {
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
                    x: {
                        grid: { display: false },
                        ticks: { autoSkip: false }
                    },
                    y: {
                        grid: { color: '#f0f0f0' },
                        ticks: {
                            callback: v => '₱' + (v / 1000).toFixed(0) + 'k'
                        }
                    }
                }
            }
        });
    }

    /* ── Cashbook Search & Filter ── */
    const searchInput = document.getElementById('cashbookSearch');
    const typeFilter  = document.getElementById('typeFilter');
    const monthFilter = document.getElementById('monthFilter');
    const rowCount    = document.getElementById('rowCount');

    function filterCashbook() {
        const q     = searchInput ? searchInput.value.toLowerCase() : '';
        const type  = typeFilter  ? typeFilter.value  : '';
        const month = monthFilter ? monthFilter.value : '';

        const rows = document.querySelectorAll('#cashbookBody tr[data-type]');
        let visible = 0;

        rows.forEach(row => {
            const rowType   = row.dataset.type   || '';
            const rowMonth  = row.dataset.month  || '';
            const rowSearch = row.dataset.search || '';

            const matchSearch = !q     || rowSearch.includes(q);
            const matchType   = !type  || rowType  === type;
            const matchMonth  = !month || rowMonth === month;

            if (matchSearch && matchType && matchMonth) {
                row.style.display = '';
                visible++;
            } else {
                row.style.display = 'none';
            }
        });

        if (rowCount) {
            rowCount.textContent = visible + ' transaction(s) shown';
        }
    }

    if (searchInput) searchInput.addEventListener('input',  filterCashbook);
    if (typeFilter)  typeFilter.addEventListener('change',  filterCashbook);
    if (monthFilter) monthFilter.addEventListener('change', filterCashbook);

    /* ── Show/hide deposit fields based on Transaction Type ── */
    const txTypeSelect  = document.getElementById('txTypeSelect');
    const depositFields = document.getElementById('depositFields');

    function toggleDepositFields() {
        if (!txTypeSelect || !depositFields) return;
        const selected = txTypeSelect.options[txTypeSelect.selectedIndex];
        const label    = selected ? selected.text : '';
        if (label.includes('Collection')) {
            depositFields.classList.remove('d-none');
        } else {
            depositFields.classList.add('d-none');
            // Clear deposit fields when hidden
            const checkbox = document.getElementById('isDeposited');
            const dateInput = depositFields.querySelector('input[type="date"]');
            if (checkbox)  checkbox.checked = false;
            if (dateInput) dateInput.value  = '';
        }
    }

    if (txTypeSelect) {
        txTypeSelect.addEventListener('change', toggleDepositFields);
        toggleDepositFields(); // run on load
    }

    /* ── Auto-dismiss flash alerts ── */
    const DURATION = 5000;
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            alert.classList.remove('show');
            setTimeout(() => alert.remove(), 500);
        }, DURATION);
    });

})();