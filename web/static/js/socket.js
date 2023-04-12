class MySocket{
    constructor(){
        this.mysocket =  null;
        this.vMsgContainer = document.getElementById("msgcontainer");
        this.vMsgIpt = document.getElementById("ipt");
    }

    showMessage(text, myself){
        var div = document.createElement("div");
        div.innerHTML = text;
        var cself = (myself)? "self" : "";
        div.className="msg " + cself;
        this.vMsgContainer.appendChild(div);
    }

    send(){
        var txt = this.vMsgIpt.value;
        this.showMessage("<b>Me</b> " + txt,true);
        this.mysocket.send(txt);
        this.vMsgIpt.value = ""
    }

    keypress(e){
        if (e.keyCode == 13) {
            this.send();
        }
    }

    connectSocket(){
        console.log("memulai socket");
        var socket = new WebSocket(socketAPI);
        this.mysocket = socket;

        socket.addEventListener("message", (event) => {
            // this.showMessage(event.data,false);
            var mess = JSON.parse(event.data)
            if (mess.source === "process") {
                if (mess.status === "success") {
                    processFinish(mess)
                } else {
                    showProcessStop()
                }
            }
            // alert(event.data)
        });

        socket.onopen = ()=> {
            console.log("socket opend")
        };
        socket.onclose = ()=>{
            console.log("socket close")
        }
    }
}

var mysocket = new MySocket()
mysocket.connectSocket();