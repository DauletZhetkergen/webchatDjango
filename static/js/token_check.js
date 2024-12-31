



document.addEventListener('DOMContentLoaded', function () {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {

        window.location.href = '/login';
    } else {

        checkToken(accessToken);
    }
});

async function checkToken(token) {
    try {
        const response = await fetch('/api/check-token/', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });

        if (!response.ok) {
            localStorage.removeItem('access_token');
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Ошибка при проверке токена:', error);
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    }
}