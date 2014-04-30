import os

try:
    from OSC import *
except ImportError:
    os.system("osascript -e 'display dialog \"Import Error: PyOSC does not exist.\nPlease first open Terminal and run the following command:\nsudo pip install PyOSC\n\nThen open the application again.\"'")
    os._exit(0)
   
try:
    import logging
    import socket
    import time, threading
    from subprocess import Popen, PIPE
    import telnetlib
except ImportError:
    os.system("osascript -e 'display dialog \"Import Error: Missing Python Library\"'")
    os._exit(0)

def OSCResponse(addr, source, message):
    clnt = OSCClient()
    clientAddress = ( source[0], 53000 )
    clnt.connect(clientAddress)
    clnt.send( OSCMessage(addr + " " + message ) )

def ScriptPath_Handler(addr, tags, data, source):
    print data[0]
    try:
        print "osascript " + data[0].replace(" ", "\\ ") + ""
        os.system("osascript " + data[0].replace(" ", "\\ ") + "")
        OSCResponse(addr + "/Sent", source, str(data[0].replace(" ", "\\ ")))
    except:
        OSCResponse(addr + "/Error", source, sys.exc_info()[0])

def ScriptCode_Handler(addr, tags, data, source):
    print data[0]
    try:
        message = data[0]
        message = message.replace("'", "\"")
        p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(message)
        OSCResponse(addr + "/Sent", source, str(message))
    except:
        OSCResponse(addr + "/Error", source, sys.exc_info()[0])
    
def UDP_Handler(addr, tags, data, source):
    if (len(data) == 3):
        OSCResponse(addr + "/IPAddress", source, str(data[0]))
        OSCResponse(addr + "/Port", source, str(data[1]))
        OSCResponse(addr + "/Command", source, str(data[2]))
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data[2].encode(encoding='UTF-8'), (str(data[0]), int(data[1])))
            OSCResponse(addr + "/Sent", source, str(data[2]))
        except:
            OSCResponse(addr + "/Error", source, sys.exc_info()[0])

def Telnet_Handler(addr, tags, data, source):
    OSCResponse(addr, source, "Attempting to send Telnet Command: " + data[1])
    if (data[0].count(" ") > 0):
        try:
            tn = telnetlib.Telnet(data[0].split(" ")[0], int(data[0].split(" ")[1]), 30)
            tn.write(str(data[1]) + "\r")
            time.sleep(.1)
            tn.close()
            OSCResponse(addr + "/Sent", source, str(data[1]))
        except:
           OSCResponse(addr + "/Error", source, sys.exc_info()[0])
    else:
        try:
            tn = telnetlib.Telnet(data[0], 23, 30)
            tn.write(str(data[1]) + "\r")
            time.sleep(.1)
            tn.close()
            OSCResponse(addr + "/Sent", source, str(data[1]))
        except:
           OSCResponse(addr + "/Error", source, sys.exc_info()[0])

TelnetUsername = ""                   
def TelnetUsername_Handler(addr, tags, data, source):
    OSCResponse(addr, source, "Set Telnet Username: " + data[0])
    global TelnetUsername
    TelnetUsername = data[0]

TelnetPassword = ""                   
def TelnetPassword_Handler(addr, tags, data, source):
    OSCResponse(addr, source, "Set Telnet Password: " + data[0])
    global TelnetPassword
    TelnetPassword = data[0]
                    
def Terminal_Handler(addr, tags, data, source):
    print data[0]
    try:
        os.system(data[0].replace("'", "\""))
        OSCResponse(addr + "/Sent", source, str(data[0]))
    except:
        OSCResponse(addr + "/Error", source, sys.exc_info()[0])
        
def Exit_Handler(addr, tags, data, source):
    print "\nClosing OSCServer."
    try:
        srvr.close()
    except:
        os._exit(0)
    os._exit(0)
    
    
try:
    srvr = OSCServer( ('0.0.0.0', 54000) )
    srvr.addDefaultHandlers()
    srvr.addMsgHandler("/runScript/path", ScriptPath_Handler)
    srvr.addMsgHandler("/runScript/code", ScriptCode_Handler)
    srvr.addMsgHandler("/runScript/UDP", UDP_Handler)
    srvr.addMsgHandler("/runScript/Telnet", Telnet_Handler)
    srvr.addMsgHandler("/runScript/Telnet/SetUsername", TelnetUsername_Handler)
    srvr.addMsgHandler("/runScript/Telnet/SetPassword", TelnetPassword_Handler)
    srvr.addMsgHandler("/runScript/Terminal", Terminal_Handler)
    srvr.addMsgHandler("/quit", Exit_Handler)
    srvr.addMsgHandler("/exit", Exit_Handler)
except:
    os.system("osascript -e 'display dialog \"There was an error opening the socket.\nThis may simply be because another app is using port 54000.\nIf the problem persists, please restart your computer and try again.\"'")
    os._exit(0)


# Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread( target = srvr.serve_forever )
st.start()

try :
    while 1 :
        time.sleep(5)
 
except KeyboardInterrupt :
    print "\nClosing OSCServer."
    srvr.close()
    print "Waiting for Server-thread to finish"
    st.join() ##!!!
    print "Done"
