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