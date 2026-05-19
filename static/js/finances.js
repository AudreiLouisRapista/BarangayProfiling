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

}
)();

/* ═══════════════════════════════════════════════════════════════════════════════
   PROFESSIONAL EXCEL EXPORT FUNCTIONS
   ═══════════════════════════════════════════════════════════════════════════════ */

function exportFullReport() {
    const wb = XLSX.utils.book_new();
    
    // ═══════════════════════════════════════════════════════════════════════
    // SHEET 1: SUMMARY
    // ═══════════════════════════════════════════════════════════════════════
    const wsSummary = XLSX.utils.aoa_to_sheet([]);
    
    // Title
    XLSX.utils.sheet_add_aoa(wsSummary, [
        ['REPUBLIC OF THE PHILIPPINES'],
        ['Province of {{ province_name|default("---") }}'],
        ['Municipality of {{ municipality_name|default("---") }}'],
        ['BARANGAY {{ barangay_name|default("---") }}'],
        [''],
        ['FINANCIAL MANAGEMENT REPORT'],
        ['Cashbook and Budget Accountability'],
        [''],
    ], { origin: 'A1' });
    
    // Merge title cells
    wsSummary['!merges'] = [
        { s: { r: 0, c: 0 }, e: { r: 0, c: 4 } },
        { s: { r: 1, c: 0 }, e: { r: 1, c: 4 } },
        { s: { r: 2, c: 0 }, e: { r: 2, c: 4 } },
        { s: { r: 3, c: 0 }, e: { r: 3, c: 4 } },
        { s: { r: 5, c: 0 }, e: { r: 5, c: 4 } },
        { s: { r: 6, c: 0 }, e: { r: 6, c: 4 } },
    ];
    
    // Report Metadata
    XLSX.utils.sheet_add_aoa(wsSummary, [
        ['Fiscal Year', fiscalYearData],
        ['Report Date', new Date().toLocaleDateString('en-PH')],
        ['Generated By', '{{ current_user.name|default("Admin") }}'],
        [''],
        ['─'.repeat(30)],
        [''],
    ], { origin: 'A9' });
    
    // Summary KPIs
    XLSX.utils.sheet_add_aoa(wsSummary, [
        ['SUMMARY OF ACCOUNTS'],
        [''],
        ['Approved Budget', approvedBudget],
        ['Total Collections (YTD)', totalCollections],
        ['Total Disbursements (YTD)', totalDisbursements],
        ['Current Cash Balance', currentBalance],
    ], { origin: 'A16' });
    
    // Apply currency format
    ['B17', 'B18', 'B19', 'B20'].forEach(cell => {
        if (wsSummary[cell]) {
            wsSummary[cell].z = '₱#,##0.00';
            wsSummary[cell].s = { font: { bold: true } };
        }
    });
    
    // Signatory Section
    XLSX.utils.sheet_add_aoa(wsSummary, [
        [''],
        [('─'.repeat(30))],
        [''],
        ['CERTIFIED CORRECT:'],
        [''],
        ['__________________________'],
        ['Barangay Treasurer'],
        [''],
        ['APPROVED:'],
        [''],
        ['__________________________'],
        ['Punong Barangay'],
    ], { origin: 'A23' });
    
    wsSummary['!cols'] = [{ wch: 25 }, { wch: 18 }, { wch: 15 }];
    XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');
    
    // ═══════════════════════════════════════════════════════════════════════
    // SHEET 2: CASHBOOK
    // ═══════════════════════════════════════════════════════════════════════
    const cashbookHeaders = [
        ['Date', 'Description', 'Category', 'Doc Reference', 'Type', 'Amount', 'Running Balance', 'Status']
    ];
    
    const cashbookData = [...cashbookHeaders];
    formattedTransactions.forEach(t => {
        cashbookData.push([
            t.date,
            t.description,
            t.category,
            t.docNumber,
            t.type,
            t.amount,
            t.runningBalance,
            t.status
        ]);
    });
    
    const wsCashbook = XLSX.utils.aoa_to_sheet(cashbookData);
    wsCashbook['!cols'] = [
        { wch: 12 }, { wch: 35 }, { wch: 20 }, { wch: 18 },
        { wch: 12 }, { wch: 15 }, { wch: 15 }, { wch: 12 }
    ];
    
    // Header styling
    const headerRange = XLSX.utils.decode_range(wsCashbook['!ref']);
    for (let C = headerRange.s.c; C <= headerRange.e.c; ++C) {
        const cellRef = XLSX.utils.encode_cell({ r: headerRange.s.r, c: C });
        if (wsCashbook[cellRef]) {
            wsCashbook[cellRef].s = {
                fill: { fgColor: { rgb: '1F4E79' } },
                font: { color: { rgb: 'FFFFFF' }, bold: true },
                alignment: { horizontal: 'center' }
            };
        }
    }
    
    // Currency formatting & borders
    for (let R = headerRange.s.r + 1; R <= headerRange.e.r; ++R) {
        // Amount column (E)
        const amountCell = XLSX.utils.encode_cell({ r: R, c: 5 });
        if (wsCashbook[amountCell]) {
            wsCashbook[amountCell].z = '₱#,##0.00';
            wsCashbook[amountCell].s = { 
                numFmt: '#,##0.00',
                alignment: { horizontal: 'right' }
            };
        }
        
        // Balance column (F)
        const balanceCell = XLSX.utils.encode_cell({ r: R, c: 6 });
        if (wsCashbook[balanceCell]) {
            wsCashbook[balanceCell].z = '₱#,##0.00';
            wsCashbook[balanceCell].s = { 
                numFmt: '#,##0.00',
                alignment: { horizontal: 'right' },
                font: { bold: true }
            };
        }
        
        // Alternating row colors
        if (R % 2 === 0) {
            for (let C = headerRange.s.c; C <= headerRange.e.c; ++C) {
                const cellRef = XLSX.utils.encode_cell({ r: R, c: C });
                if (wsCashbook[cellRef] && !wsCashbook[cellRef].s) {
                    wsCashbook[cellRef].s = { fill: { fgColor: { rgb: 'F2F2F2' } } };
                }
            }
        }
        
        // Type-specific coloring
        const typeCell = XLSX.utils.encode_cell({ r: R, c: 4 });
        if (wsCashbook[typeCell]?.v === 'Collection') {
            const amountCell = XLSX.utils.encode_cell({ r: R, c: 5 });
            if (wsCashbook[amountCell]) {
                wsCashbook[amountCell].s = { 
                    font: { color: { rgb: '198754' } },
                    numFmt: '#,##0.00'
                };
            }
        } else if (wsCashbook[typeCell]?.v === 'Disbursement') {
            const amountCell = XLSX.utils.encode_cell({ r: R, c: 5 });
            if (wsCashbook[amountCell]) {
                wsCashbook[amountCell].s = { 
                    font: { color: { rgb: 'DC3545' } },
                    numFmt: '#,##0.00'
                };
            }
        }
    }
    
    XLSX.utils.book_append_sheet(wb, wsCashbook, 'Cashbook');
    
    // ═══════════════════════════════════════════════════════════════════════
    // SHEET 3: BUDGET ALLOCATIONS
    // ═══════════════════════════════════════════════════════════════════════
    const budgetHeaders = [
        ['Category', 'Type', 'Mandatory %', 'Allocated Amount']
    ];
    
    const budgetSheetData = [...budgetHeaders];
    budgetData.forEach(b => {
        budgetSheetData.push([
            b.category_type?.category_type || '',
            b.category_type?.type_nature || '',
            b.budget_mandatory_percent || '',
            parseFloat(b.budget_amount) || 0
        ]);
    });
    
    const wsBudget = XLSX.utils.aoa_to_sheet(budgetSheetData);
    wsBudget['!cols'] = [{ wch: 30 }, { wch: 12 }, { wch: 14 }, { wch: 20 }];
    
    // Header styling
    const budgetHeaderRange = XLSX.utils.decode_range(wsBudget['!ref']);
    for (let C = budgetHeaderRange.s.c; C <= budgetHeaderRange.e.c; ++C) {
        const cellRef = XLSX.utils.encode_cell({ r: budgetHeaderRange.s.r, c: C });
        if (wsBudget[cellRef]) {
            wsBudget[cellRef].s = {
                fill: { fgColor: { rgb: '1F4E79' } },
                font: { color: { rgb: 'FFFFFF' }, bold: true },
                alignment: { horizontal: 'center' }
            };
        }
    }
    
    // Currency formatting for amounts
    for (let R = budgetHeaderRange.s.r + 1; R <= budgetHeaderRange.e.r; ++R) {
        const amountCell = XLSX.utils.encode_cell({ r: R, c: 3 });
        if (wsBudget[amountCell]) {
            wsBudget[amountCell].z = '₱#,##0.00';
            wsBudget[amountCell].s = { 
                numFmt: '#,##0.00',
                alignment: { horizontal: 'right' }
            };
        }
    }
    
    // Add totals row
    const totalRow = budgetSheetData.length + 1;
    XLSX.utils.sheet_add_aoa(wsBudget, [
        ['TOTAL', '', '', budgetData.reduce((sum, b) => sum + parseFloat(b.budget_amount || 0), 0)]
    ], { origin: `A${totalRow}` });
    
    // Style totals row
    for (let C = 0; C <= 3; ++C) {
        const cellRef = XLSX.utils.encode_cell({ r: totalRow - 1, c: C });
        if (wsBudget[cellRef]) {
            wsBudget[cellRef].s = { 
                font: { bold: true },
                fill: { fgColor: { rgb: 'E7E6E6' } }
            };
        }
    }
    
    XLSX.utils.book_append_sheet(wb, wsBudget, 'Budget Allocations');
    
    // ═══════════════════════════════════════════════════════════════════════
    // SHEET 4: MONTHLY SUMMARY (Bonus)
    // ═══════════════════════════════════════════════════════════════════════
    const months = ['January', 'February', 'March', 'April', 'May', 'June',
                    'July', 'August', 'September', 'October', 'November', 'December'];
    
    const monthlyHeaders = [['Month', 'Collections', 'Disbursements', 'Net Balance']];
    const monthlySheetData = [...monthlyHeaders];
    
    // Group by month
    const monthlyGroups = {};
    formattedTransactions.forEach(t => {
        const month = t.date ? t.date.substring(0, 7) : '';
        if (!monthlyGroups[month]) {
            monthlyGroups[month] = { collections: 0, disbursements: 0 };
        }
        if (t.type === 'Collection') {
            monthlyGroups[month].collections += t.amount;
        } else {
            monthlyGroups[month].disbursements += t.amount;
        }
    });
    
    let runningTotal = 0;
    months.forEach((month, idx) => {
        const monthKey = `${fiscalYearData}-${String(idx + 1).padStart(2, '0')}`;
        const data = monthlyGroups[monthKey] || { collections: 0, disbursements: 0 };
        runningTotal += data.collections - data.disbursements;
        monthlySheetData.push([
            month,
            data.collections,
            data.disbursements,
            runningTotal
        ]);
    });
    
    const wsMonthly = XLSX.utils.aoa_to_sheet(monthlySheetData);
    wsMonthly['!cols'] = [{ wch: 15 }, { wch: 18 }, { wch: 18 }, { wch: 18 }];
    
    // Header styling
    const monthlyHeaderRange = XLSX.utils.decode_range(wsMonthly['!ref']);
    for (let C = monthlyHeaderRange.s.c; C <= monthlyHeaderRange.e.c; ++C) {
        const cellRef = XLSX.utils.encode_cell({ r: monthlyHeaderRange.s.r, c: C });
        if (wsMonthly[cellRef]) {
            wsMonthly[cellRef].s = {
                fill: { fgColor: { rgb: '1F4E79' } },
                font: { color: { rgb: 'FFFFFF' }, bold: true }
            };
        }
    }
    
    // Currency formatting
    for (let R = monthlyHeaderRange.s.r + 1; R <= monthlyHeaderRange.e.r; ++R) {
        [1, 2, 3].forEach(c => {
            const cellRef = XLSX.utils.encode_cell({ r: R, c: c });
            if (wsMonthly[cellRef]) {
                wsMonthly[cellRef].z = '₱#,##0.00';
                wsMonthly[cellRef].s = { alignment: { horizontal: 'right' } };
            }
        });
    }
    
    XLSX.utils.book_append_sheet(wb, wsMonthly, 'Monthly Summary');
    
    // ═══════════════════════════════════════════════════════════════════════
    // DOWNLOAD
    // ═══════════════════════════════════════════════════════════════════════
    const date = new Date().toISOString().slice(0, 10);
    XLSX.writeFile(wb, `Financial_Report_FY${fiscalYearData}_${date}.xlsx`);
}


function exportCashbook() {
    const wb = XLSX.utils.book_new();
    
    // Header info
    const ws = XLSX.utils.aoa_to_sheet([]);
    
    XLSX.utils.sheet_add_aoa(ws, [
        ['BARANGAY CASHBOOK'],
        [`Fiscal Year: ${fiscalYearData}`],
        [`Generated: ${new Date().toLocaleDateString('en-PH')}`],
        [''],
    ], { origin: 'A1' });
    
    ws['!merges'] = [
        { s: { r: 0, c: 0 }, e: { r: 0, c: 6 } },
        { s: { r: 1, c: 0 }, e: { r: 1, c: 6 } },
        { s: { r: 2, c: 0 }, e: { r: 2, c: 6 } },
    ];
    
    // Title style
    for (let r = 0; r <= 3; r++) {
        const cellRef = XLSX.utils.encode_cell({ r: r, c: 0 });
        if (ws[cellRef]) {
            ws[cellRef].s = { 
                font: { bold: true, size: 14 },
                alignment: { horizontal: 'center' }
            };
        }
    }
    
    // Table data
    const cashbookHeaders = [
        ['Date', 'Description', 'Category', 'Doc Reference', 'Type', 'Amount', 'Running Balance', 'Status']
    ];
    
    const cashbookData = [...cashbookHeaders];
    formattedTransactions.forEach(t => {
        cashbookData.push([
            t.date,
            t.description,
            t.category,
            t.docNumber,
            t.type,
            t.amount,
            t.runningBalance,
            t.status
        ]);
    });
    
    XLSX.utils.sheet_add_aoa(ws, cashbookData, { origin: 'A6' });
    
    ws['!cols'] = [
        { wch: 12 }, { wch: 35 }, { wch: 20 }, { wch: 18 },
        { wch: 12 }, { wch: 15 }, { wch: 15 }, { wch: 12 }
    ];
    
    // Header row styling (row 6 in the sheet, index 0 in data)
    const startRow = 6;
    [0, 1, 2, 3, 4, 5, 6, 7].forEach(c => {
        const cellRef = XLSX.utils.encode_cell({ r: startRow, c: c });
        if (ws[cellRef]) {
            ws[cellRef].s = {
                fill: { fgColor: { rgb: '1F4E79' } },
                font: { color: { rgb: 'FFFFFF' }, bold: true },
                alignment: { horizontal: 'center' }
            };
        }
    });
    
    // Data formatting
    const dataStartRow = startRow + 1;
    const dataEndRow = startRow + formattedTransactions.length;
    
    for (let R = dataStartRow; R <= dataEndRow; ++R) {
        // Amount column (E)
        const amountCell = XLSX.utils.encode_cell({ r: R, c: 5 });
        if (ws[amountCell]) {
            ws[amountCell].z = '₱#,##0.00';
            ws[amountCell].s = {
                numFmt: '#,##0.00',
                alignment: { horizontal: 'right' }
            };
        } else {
            ws[amountCell] = { t: 'n', v: 0, z: '₱#,##0.00' };
        }
    } }