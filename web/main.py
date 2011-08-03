'''
Created on Jul 23, 2011

@author: federico
'''

from flask import Flask 

from configuration.apikeys import api_check, ApikeyException, CODES
from configuration.gates import Gates
from configuration.alarm import Alarm
from communication.backend import BackendCommunicator
from configuration.zonecontrol import BackendException
import time

def cb(data):
    print "callback", data
    
backend = BackendCommunicator(cb)
backend.start()

gates_control = Gates(backend)
alarm_control = Alarm(backend)
app = Flask(__name__)

@app.route('/backend/<apikey>/gate/<gate>/<command>')
def gate(apikey, gate, command):
    try:
        assert gate in ["top_gate", "our_gate", "garage"]
        assert command in ["open", "close", "trigger", "pedestrian", "stop_keep_open", "start_keep_open"]
    except AssertionError:
        return "invalid command"
    
    try:
        api_check(apikey)
    except ApikeyException:
        return "invalid apikey"
    
    try:
        getattr(getattr(gates_control, gate), command)()
        return "done"
    except BackendException as e:
        return str(e)
    
    #if apikey in API_KEYS:
    #    pass
    #else:
    #    return "invalid api key."

@app.route('/backend/<apikey>/keypad/<code>/<command>')
def keypad(apikey, code, command):
    try:
        api_check(apikey)
    except ApikeyException:
        return "invalid apikey"
    
    if code not in CODES:
        return "invalid code"
    
    if CODES[code] == "mountain men":
        if gates_control.top_gate.keep_open_enabled == True and gates_control.our_gate.keep_open_enabled == True:
            gates_control.top_gate.stop_keep_open()
            gates_control.our_gate.stop_keep_open()
        else:
            gates_control.top_gate.start_keep_open()
            gates_control.our_gate.start_keep_open()
        return "done"
    
    if "1" in command:
        gates_control.top_gate.open()
    if "2" in command:
        gates_control.our_gate.open()
    if "3" in command:
        gates_control.garage.open()
    if "5" in command:
        alarm_control.everything.toggle()
    
    

@app.route('/backend/<apikey>/gates/<command>')
def gates(apikey, command):
    try:
        api_check(apikey)
    except ApikeyException:
        return "invalid apikey"

    assert command in ["secure_open"]
    
    gates_control.top_gate.open()
    
    while gates_control.top_gate.status != "fully closed":
        time.sleep(3)
        
    gates_control.our_gate.open()
    return "done"
    
    
    
if __name__ == "__main__":
    app.run(threaded=True,port=5007)