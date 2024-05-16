var element = document.getElementById('heartbeat');
var heartbeatUrl = element.className;
var timeoutUrl = '/authenticate-user/check-token/timeout/';

const channel = new BroadcastChannel("sess_channel");

// Listen for messages from the channel
channel.onmessage = function (event) {
    switch (event.data) {
        case 'session timeout':
            alert("Session Timeout");
            window.location.href = timeoutUrl;
            break;
        case 'offline alert':
            alert("The network connection has been lost.");
            break;
    }
};

function sendHeartbeat() {
    fetch(heartbeatUrl)
        .then(response => response.json())
        .then(data => {
            if (data.session_Inactive) {
                channel.postMessage('session timeout');
                window.location.href = timeoutUrl;
            }
            else {
                channel.postMessage('session online');
            }
        })
        .catch(error => console.error('Error:', error));
}

setTimeout(sendHeartbeat, 3000);
setInterval(() => sendHeartbeat(), 600000);
window.onoffline = (event) => {
    alert("The network connection has been lost.");
    channel.postMessage('offline alert');
};

document.getElementById('logout_currentUser').addEventListener('click', function () {
    channel.postMessage('session timeout');
});
