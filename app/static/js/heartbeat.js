var element = document.getElementById('heartbeat');
var heartbeatUrl = '/get_heartbeat';
var timeoutUrl = '/authenticate-user/check-token/timeout/';

const channel = new BroadcastChannel("sess_channel");
// Listen for messages from the channel
channel.onmessage = function (event) {
    switch (event.data) {
        case 'session timeout':
            setTimeout(function () { window.location.href = timeoutUrl; }, 10000);
            alert('Session has expired, please log in again')
            window.location.href = timeoutUrl;
            break;
        case 'session expired':
            window.location.href = timeoutUrl;
            break;
        case 'offline alert':
            alert("The network connection has been lost.");
            break;
    }
};

function sendHeartbeat() {
    var username = element.className;

    fetch('/get_heartbeat/' + username)
        .then(response => response.json())
        .then(data => {
            if (data.session_Inactive) {
                channel.postMessage('session timeout');
                window.location.href = timeoutUrl;
                channel.postMessage('session expired');
            }
            else {
                channel.postMessage('session online');
            }
        })
        .catch(error => {
            channel.postMessage('session expired');
            window.location.href = timeoutUrl;
        });
}

window.onoffline = (event) => {
    alert("The network connection has been lost.");
    channel.postMessage('offline alert');
};

document.getElementById('logout_currentUser').addEventListener('click', function () {
    channel.postMessage('session timeout');
});

setInterval(() => sendHeartbeat(), 600000);
setTimeout(sendHeartbeat, 1000);
