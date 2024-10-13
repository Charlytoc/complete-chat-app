import { io, Socket } from "socket.io-client";

class SocketManager {
    private socket: Socket;

    constructor(url: string) {
        this.socket = io(url, {
            autoConnect: false,
            transports: ["websockets", "polling"],
        })
    }

    connect() {
        this.socket.connect();
    }

    disconnect() {
        this.socket.disconnect();
    }

    on(event: string, callback: (...args: any[]) => void) {
        this.socket.on(event, callback);
    }

    off(event: string) {
        this.socket.off(event);
    }

    emit(event: string, data: any) {
        const token = localStorage.getItem("token");
        this.socket.emit(event, {...data, token});
    }
}

const socketManager = new SocketManager("http://localhost:8001");
export default socketManager;