package websocket

import (
	"github.com/gorilla/websocket"
	"log"
	"net/http"
)

var upgrader = websocket.Upgrader{
	ReadBufferSize:  1024,
	WriteBufferSize: 1024,
}

var savedsockets map[string]*websocket.Conn

func InitStorage() {
	savedsockets = map[string]*websocket.Conn{}
}

func SocketReaderCreate(w http.ResponseWriter, r *http.Request) {
	log.Println("socket request")

	defer func() {
		err := recover()
		if err != nil {
			log.Println(err)
		}
		r.Body.Close()
	}()

	con, _ := upgrader.Upgrade(w, r, nil)
	session, err := r.Cookie("session")
	if err != nil {
		log.Printf("fail to get session: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
	}

	savedsockets[session.Value] = con
}

func SendMessage(session string, message string) error {
	con, ok := savedsockets[session]
	if !ok {
		log.Printf("websocket: no such session in ws storage")
		return nil
	}
	if err := con.WriteMessage(1, []byte(message)); err != nil {
		log.Printf("websocket: fail to write message: %v", err)
	}
	return nil
}

//
//
//func (i *socketReader) read() {
//	_, b, er := i.con.ReadMessage()
//	if er != nil {
//		panic(er)
//	}
//	log.Println(i.name + " " + string(b))
//	log.Println(i.mode)
//
//	if i.mode == 1 {
//		i.name = string(b)
//		i.writeMsg("System", "Welcome "+i.name+", please write a message and we will broadcast it to other users.")
//		i.mode = 2 // real msg mode
//
//		return
//	}
//
//	i.broadcast(string(b))
//
//	log.Println(i.name + " " + string(b))
//}
//
//func (i *socketReader) writeMsg(name string, str string) {
//	i.con.WriteMessage(websocket.TextMessage, []byte("<b>"+name+": </b>"+str))
//}
//
//func (i *socketReader) startThread() {
//	i.writeMsg("System", "Please write your name")
//	i.mode = 1 //mode 1 get user name
//
//	go func() {
//		defer func() {
//			err := recover()
//			if err != nil {
//				log.Println(err)
//			}
//			log.Println("thread socketreader finish")
//		}()
//
//		for {
//			i.read()
//		}
//
//	}()
//}
