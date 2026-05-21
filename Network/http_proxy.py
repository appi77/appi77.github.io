import socket
import threading

def handle(c):
    try:
        req = b""
        while b"\r\n\r\n" not in req:
            req += c.recv(4096)
        first_line = req.split(b"\r\n")[0].decode()
        method, url, _ = first_line.split(" ")
        if method == "CONNECT":
            host, port = url.split(":")
            port = int(port)
        else:
            from urllib.parse import urlparse
            p = urlparse(url)
            host = p.hostname
            port = p.port or 80
        r = socket.create_connection((host, port), timeout=10)
        if method == "CONNECT":
            c.send(b"HTTP/1.1 200 Connection established\r\n\r\n")
        else:
            r.send(req)
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
                try: a.close()
                except: pass
                try: b.close()
                except: pass
        threading.Thread(target=relay, args=(c, r), daemon=True).start()
        threading.Thread(target=relay, args=(r, c), daemon=True).start()
    except Exception as e:
        print("Error:", e)
        try: c.close()
        except: pass

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 9090))
s.listen(5)
print("HTTP Proxy ready on 9090")
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle, args=(conn,), daemon=True).start()
    
#python.exe http_proxy.py 
#ssh -R 1080:127.0.0.1:9090 ecmadmin@10.156.6.162 
#curl -x http://127.0.0.1:1080 https://ifconfig.me
