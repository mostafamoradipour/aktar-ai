import websocket
import threading
import socket
import ssl


HOST = 'wss://api.kachrobotics.com/user/?uuid=0c2431ed-7d45-4c91-8db4-37b9b51fd359'
ws_isconnected = False
sleep_reconnection_time = 5


def is_internet_available():
    for timeout in [1, 5, 10, 15]:
        try:
            socket.setdefaulttimeout(timeout)
            host = socket.gethostbyname("www.google.com")
            s = socket.create_connection((host, 80), 2)
            s.close()
            return True
        except Exception as e:
            return False


def run_for_ever(sslopt, ws):
    ws.run_forever(sslopt=sslopt)


def on_message(ws, message):
    pass


def on_open(ws):
    global ws_isconnected
    ws_isconnected = True


def on_close(ws):
    global ws_isconnected
    ws_isconnected = False


def on_error(ws, error):
    print(error)


# MONGO
if is_internet_available():
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(HOST, on_message=on_message, on_open=on_open, on_close=on_close, on_error=on_error)
    ws_th = threading.Thread(target=run_for_ever, args=({"cert_reqs": ssl.CERT_NONE}, ws))
    ws_th.daemon = True
    ws_th.start()
    while not ws_isconnected:
        continue
    if ws_isconnected:
        print('Websocket connection has been stablished ...')
    else:
        print('Websocket connection did not stablished!')
    # ws_th.join()
