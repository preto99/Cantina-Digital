document.getElementById('openCamera').addEventListener('click', function() {
    let video = document.getElementById('camera');
    video.style.display = 'block';
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(function(stream) {
            video.srcObject = stream;
            video.play();
        })
        .catch(function(err) {
            console.log("An error occurred: " + err);
        });
});

document.getElementById('camera').addEventListener('click', function() {
    let code = prompt("Digite o código QR lido:");
    if (code) {
        fetch('/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => response.json())
        .then(data => {
            let message = document.getElementById('message');
            if (data.count === 1) {
                message.textContent = "Primeira leitura do dia!";
                message.className = "blue";
            } else {
                message.textContent = `Lido ${data.count} vezes hoje.`;
                message.className = "red";
            }
        })
        .catch(error => console.error('Error:', error));
    }
});
