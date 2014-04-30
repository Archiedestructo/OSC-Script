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

def WriteInfoConsole(addr, source, message):
    logging.info(message)
    
def WriteErrorConsole(addr, source, message):
    logging.error(message)

def ScriptPath_Handler(addr, tags, data, source):
    print data[0]
    try:
        print "osascript " + data[0].replace(" ", "\\ ") + ""
        os.system("osascript " + data[0].replace(" ", "\\ ") + "")
    except:
        print "ScriptPath_Hanlder error"

def ScriptCode_Handler(addr, tags, data, source):
    print data[0]
    try:
        message = data[0]
        message = message.replace("'", "\"")
        p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(message)
        print (p.returncode, stdout, stderr)
    except:
        print "ScriptCode_Hanlder error"
    
def UDP_Handler(addr, tags, data, source):
    if (len(data) == 3):
        print data[0]
        print data[1]
        print data[2]
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data[2].encode(encoding='UTF-8'), (str(data[0]), int(data[1])))
        except:
            print "UDP_Handler error"

def Telnet_Handler(addr, tags, data, source):
    OSCResponse(addr, source, "Attempting to send Telnet Command: " + data[1])
    if (data[0].count(" ") > 0):
        try:
            tn = telnetlib.Telnet(data[0].split(" ")[0], int(data[0].split(" ")[1]), 30)
            tn.write(str(data[1]) + "\r")
            time.sleep(.1)
            tn.close()
            print "Sent"
        except:
           print "Error connecting"
    else:
        try:
            tn = telnetlib.Telnet(data[0], 23, 30)
            tn.write(str(data[1]) + "\r")
            time.sleep(.1)
            tn.close()
            print "Sent"
        except:
           print "Error connecting"
        
def Terminal_Handler(addr, tags, data, source):
    print data[0]
    try:
        os.system(data[0].replace("'", "\""))
    except:
        print "Terminal_Hanlder error"
        
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
