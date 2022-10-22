import subprocess
  
for ping in range(100, 200):
    address = "192.168.1." + str(ping)
    res = subprocess.call(['ping', '-c', '3', address])
    if res == 0:
        print( "ping to", address, "OK")
        print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++=")
    elif res == 2:
        print("no response from", address)
    else:
        print("ping to", address, "failed!")
