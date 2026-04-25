// Toggle password visibility
document.getElementById('togglePassword').addEventListener('click', function () {
        const pwd = document.getElementById('password');
        const icon = document.getElementById('eyeIcon');
        if (pwd.type === 'password') {
            pwd.type = 'text';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            pwd.type = 'password';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
});

    // Password match validation
document.getElementById('submitBtn').addEventListener('click', function (e) {
        const pwd     = document.getElementById('password').value;
        const confirm = document.getElementById('confirmPassword').value;
        const msg     = document.getElementById('passwordMismatch');

        if (pwd !== confirm) {
            e.preventDefault();
            msg.classList.remove('d-none');
        } else {
            msg.classList.add('d-none');
        }
});

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('employeeSearch');
    const positionFilter = document.getElementById('positionFilter');
    const statusFilter = document.getElementById('statusFilter');
    const tableBody = document.getElementById('employeeTable');

    // Function to apply all filters
    function applyFilters() {
        const searchTerms = searchInput.value.toLowerCase().split(" ");
        
        // Get the TEXT of selected options, not the value
        const selectedPositionText = positionFilter.options[positionFilter.selectedIndex].text;
        const selectedStatusText = statusFilter.options[statusFilter.selectedIndex].text;
        
        const rows = tableBody.getElementsByTagName('tr');

        for (let i = 0; i < rows.length; i++) {
            const rowText = rows[i].textContent.toLowerCase();
            const positionCell = rows[i].cells[2]?.textContent.trim(); // Position column
            const statusCell = rows[i].cells[5]?.textContent.trim();   // Status column

            // Check search terms
            const matchesSearch = searchTerms.every(term => rowText.includes(term));
            
            // Check position filter (compare against option text)
            const matchesPosition = selectedPositionText === "Filter by Position" || positionCell === selectedPositionText;
            
            // Check status filter (compare against option text)
            const matchesStatus = selectedStatusText === "Filter by Status" || statusCell === selectedStatusText;

            // Show row only if all filters match
            rows[i].style.display = (matchesSearch && matchesPosition && matchesStatus) ? "" : "none";
        }
    }

    // Only run if all elements exist on the page
    if (searchInput && positionFilter && statusFilter && tableBody) {
        searchInput.addEventListener('keyup', applyFilters);
        positionFilter.addEventListener('change', applyFilters);
        statusFilter.addEventListener('change', applyFilters);
    }
});

 // Auto close flash messages
    const DURATION = 5000;
    document.querySelectorAll('.alert').forEach(function(alert) {
        const bar = alert.querySelector('.alert-timer-bar');
        if (bar) {
            bar.style.transition = `width ${DURATION}ms linear`;
            setTimeout(() => bar.style.width = '0%', 50);
        }
        setTimeout(function() {
            alert.classList.remove('show');
            setTimeout(function() { alert.remove(); }, 500);
        }, DURATION);
    });

// console.log("✅ JavaScript is connected and running!");
// alert("If you see this, JS is working!");