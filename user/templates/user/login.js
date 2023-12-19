

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    // Add login logic here. For now, just log to console.
    console.log('Login attempt with username:', username, 'and password:', password);
});

