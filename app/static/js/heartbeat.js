var element = document.getElementById('heartbeat');
var heartbeatUrl = element.className;
var logoutUrl = element.getAttribute('data-logout-url');

const channel = new BroadcastChannel("sess_channel");

// Listen for messages from the channel
channel.onmessage = function (event) {
    switch (event.data) {
        case 'session timeout':
            alert("Session timeout");
            window.location.href = logoutUrl;
            channel.close()
            break;
        case 'offline alert':
            alert("The network connection has been lost.");
            break;
        default:
            console.log( 'channel data ', event.data)
    }
};
function sendHeartbeat() {
    fetch(heartbeatUrl)
        .then(response => response.json())
        .then(data => {
            if (data.session_Inactive) {
                channel.postMessage('session timeout');
                window.location.href = logoutUrl;
            }
        })
        .catch(error => console.error('Error:', error));
}

sendHeartbeat();
setInterval(() => sendHeartbeat(), 600000);

window.onoffline = (event) => {
    alert("The network connection has been lost.");
    channel.postMessage('offline alert');
};

document.getElementById('logout_currentUser').addEventListener('click', function () {
    channel.postMessage('session timeout');
});

