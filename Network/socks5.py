import socket
import threading

def relay(a, b):
    try:
        while True:
            x = a.recv(4096)
            if not x:
                break
            b.send(x)
    except:
        pass
    finally:
        try:
            a.close()
        except:
            pass
        try:
            b.close()
        except:
            pass

def handle(c):
    try:
        d = c.recv(262)
        if not d:
            return
        c.send(bytes([5, 0]))
        d = c.recv(262)
        if not d or len(d) < 4:
            return
        atype = d[3]
        if atype == 1:
            host = socket.inet_ntoa(d[4:8])
            port = (d[8] << 8) | d[9]
        elif atype == 3:
            dlen = d[4]
            host = d[5:5+dlen].decode()
            port = (d[5+dlen] << 8) | d[6+dlen]
        else:
            c.close()
            return
        r = socket.create_connection((host, port), timeout=10)
        c.send(bytes([5, 0, 0, 1, 0, 0, 0, 0, 0, 0]))
        threading.Thread(target=relay, args=(c, r), daemon=True).start()
        threading.Thread(target=relay, args=(r, c), daemon=True).start()
    except Exception as e:
        print("Error:", e)
        try:
            c.close()
        except:
            pass

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 9090))
s.listen(5)
print("SOCKS5 ready on 9090")
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()

## ssh -R 1080:127.0.0.1:9090 ecmadmin@10.156.6.162
