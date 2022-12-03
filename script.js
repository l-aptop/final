var socket = null;
var input = null;
var map = {"Shift": false, "Enter": false};
onkeydown = onkeyup = function(e){
    e = e || event;
    map[e.key] = e.type == 'keydown';
    if(map.Enter === true && map.Shift === false){send()};
}
function join() {
    user = document.getElementById("username-input");
    if (user.value.trim() === "") {
        return alert("Please enter a username!")
    } else if (user.value.trim().length > 12) {
      user.value = "";
      return alert("Your username must be 1-12 characters in length.")
    } else {
        username = user.value.trim();
        if (location.protocol === "https:") {
            proto = "wss";
        } else {
            proto = "ws";
        }
        window.socket = new WebSocket(proto + "://" + location.host + "/socket?username=" + username);
        user.remove();
        document.getElementById("username-title").remove();
        document.getElementById("join").remove();
        messages = document.getElementById("messages");
        window.input = document.getElementById("text");
        window.input.focus();
        document.getElementById("send_container").style = "display:block;";
        messages.style = "display:block;";
        window.socket.onclose = function(data) {
            return location.reload();
        }
        window.socket.onmessage = function(data) {
            data = JSON.parse(data.data);
            if (data.code === 0) {
                alert(data.error);
                return location.reload();
            } else {
                if(data.username==="System"){
                    messages.innerHTML += "<div class='message'><p class='messagetext'>" + data.message + "</p></div>";
                } else {
                    messages.innerHTML += "<div class='message'><p class='messagetext'><b class='username'>" + data.username + ":</b> " + data.message + "</p></div>";
                }
            }
        }
    }
}
var lastsent = new Date();
function send() {
    if (window.input !== null && window.input.value.trim() !== "" && window.input.value.trim().length < 500 && new Date() - lastsent > 500) {
        window.socket.send(window.input.value.trim());
        window.input.value = "";

    };
    if (window.input.value.length >= 500) alert("Your message is too big! Make it less than 500 characters")
    window.input.focus();
    window.scrollTo(0, document.body.scrollHeight);
}
