document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const form = e.target;
    const formData = new URLSearchParams(new FormData(form));
    const button = document.getElementById('login-button');
    const spinner = document.getElementById('spinner');
    const btnText = document.getElementById('button-text');
    const messageBox = document.getElementById('message');

    messageBox.style.display = 'none';
    button.disabled = true;
    spinner.style.display = 'inline-block';
    btnText.textContent = 'Logging in...';

    try {
        const res = await fetch('http://localhost:8000/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: formData,
            credentials: 'include',
            mode: 'cors'
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || 'Login failed');
        }

        localStorage.setItem('auth_token', data.access_token);
        messageBox.textContent = 'Login successful! Redirecting...';
        messageBox.className = 'message success';
        messageBox.style.display = 'block';

        setTimeout(() => {
            window.location.href = '/frontend/dashboard.html';
        }, 1500);
    } catch (err) {
        messageBox.textContent = err.message;
        messageBox.className = 'message error';
        messageBox.style.display = 'block';
    } finally {
        button.disabled = false;
        spinner.style.display = 'none';
        btnText.textContent = 'Login';
    }
});
