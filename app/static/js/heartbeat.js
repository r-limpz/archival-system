var node = document.getElementById('account_username');
var timeoutUrl = '/authenticate-user/check-token/timeout/';

const channel = new BroadcastChannel("sess_channel");
// Listen for messages from the channel
channel.onmessage = function (event) {
    switch (event.data) {
        case 'session timeout':
            setTimeout(function () { window.location.href = timeoutUrl; }, 10000);
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
    var username = node.textContent || node.innerText;

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

setTimeout(sendHeartbeat, 1000);
setInterval(() => sendHeartbeat(), 600000);

window.onoffline = (event) => {
    alert("The network connection has been lost.");
    channel.postMessage('offline alert');
};

document.getElementById('logout_currentUser').addEventListener('click', function () {
    channel.postMessage('session expired');
});


