const chatbox = document.getElementById("chatbox");
const userInput = document.getElementById("user_input");
const sendButton = document.getElementById("send_btn");
console.log(window.location.host)


const token = localStorage.getItem('access_token')

const socket = new WebSocket(
    'ws://' + window.location.host + '/ws/chat/?token=' + token);

socket.onopen = function (e) {
    console.log('WebSocket connection established');
};

socket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    console.log(data)
    if (data.type === 'init_messages') {
        const messages = data.messages;
        messages.forEach(function(messageData) {
            chatbox.innerHTML += '<p><strong>'+messageData.user + '</strong>' + messageData.message + '</p>';
        });
    }
    const message = data.message;
    if (data.type === 'llm_answer') {
        // Обрабатываем новое сообщение
        chatbox.innerHTML += '<p><strong>AI:</strong> ' + message + '</p>';
    }
};


sendButton.onclick = function () {
    const message = user_input.value;
    chatbox.innerHTML += '<p><strong>You:</strong> ' + message + '</p>';
    socket.send(JSON.stringify({
        'message': message
    }));
    userInput.value = '';
};