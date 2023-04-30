const chatForm = document.getElementById("chat-form")
const leaveChatButton = document.getElementsByClassName("leave")[0]
const userBanner = document.getElementById('user')
let role = null
let socket = io.connect('http://' + document.domain + ':' + location.port + '/chat');

chatForm.addEventListener("submit", e => {
    e.preventDefault()
    const formData = new FormData(e.target)
    console.log(formData)
    const data = Object.fromEntries(formData.entries())
    socket.emit('send_message', data)
    chatForm.reset()
})

leaveChatButton.addEventListener('click', e => {
    socket.emit('leave');
    window.location.href = "/home"
})


$(document).ready(function(){
    
    
    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    
    socket.on('status', (data) => createMessage(data)); 

});

const createMessage = (data) => {  
    console.log(data)   
    let tag  = document.createElement("p");
    tag.classList.add(`${data.role}Msg`)
    role = data.role
    let text = document.createTextNode(data.message);
    let element = document.getElementById("chat");
    tag.appendChild(text);
    element.appendChild(tag);
    $('#chat').scrollTop($('#chat')[0].scrollHeight);

}



