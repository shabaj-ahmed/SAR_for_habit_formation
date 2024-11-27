var socket = io();

// Handle new messages
socket.on('new_message', function(message) {
    // Update conversation history
    var historyDiv = document.getElementById('conversation-history');
    var messageDiv = document.createElement('div');
    messageDiv.innerText = message.sender.toUpperCase() + ": " + message.content;
    historyDiv.appendChild(messageDiv);
    // Auto-scroll to the bottom
    historyDiv.scrollTop = historyDiv.scrollHeight;
});

// Handle mic status updates
socket.on('mic_status', function(is_active) {
    var micStatusImg = document.getElementById('mic-status');
    micStatusImg.src = is_active ? '/static/microphone-black-shape.png' : '/static/microphone-off_Dave_Gandy.png';
});

// Handle cam status updates
socket.on('cam_status', function(is_active) {
    var camStatusImg = document.getElementById('cam-status');
    camStatusImg.src = is_active ? '/static/videocam_icon_small.png' : '/static/videocam_off_icon_small.png';
});

var socket = io();

// Start check-in button
var startButton = document.getElementById('start-check-in-button');
if (startButton) {
    startButton.addEventListener('click', function() {
        fetch('/start_check_in', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function(response) {
            return response.json();
        }).then(function(data) {
            console.log('Check-in started:', data);
        });
    });
}

// Contact and Help buttons
document.getElementById('contact-button').addEventListener('click', function() {
    alert('Contact us at: [Email/Phone]');
});

document.getElementById('help-button').addEventListener('click', function() {
    alert('Help content goes here.');
});
