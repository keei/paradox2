'''
Created on Jul 23, 2011

@author: federico
'''
import serial, logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from threading import Lock, Thread
from Queue import Queue, Empty

from constants import paradox
import time

PORT = "/dev/ttyS0"

class BackendCommunicator:
    def __init__(self, event_callback):
        self.serial = serial.Serial(PORT, 57600, timeout=1)
        self.serial.flushInput()
        
        self.in_queue = Queue()
        self.out_queue = Queue()
        self.read_queue = Queue()
        
        self.event_callback = event_callback
        
        self.lock = Lock()
        self.running = True
                
    def start(self):
        # Read all pending data
        Thread(target=self._read_and_process_data).start()
        Thread(target=self._trigger_requests).start()
            
    def _read_and_process_data(self):
        while True:
            with self.lock:
                try:
                    line = self.serial.readline(eol='\r').strip().upper()
                except:
                    line = ""
            
            if line != "":
                logging.debug("READ IN:" + line)
                if not line.startswith("G"):
                    logging.debug("put line on read queue")
                    self.read_queue.put(line)
                else:
                    logging.debug("sent line for processing")
                    try:
                        self._process(line)
                    except:
                        logging.warning("unexpected error processing")
            else:
                time.sleep(0.5)
            
                                    
    def _trigger_requests(self):
        while True:
            request = self.in_queue.get()
            logging.debug("---- got request from in_queue, waiting for lock")
            with self.lock:
                logging.debug("---- have lock, sending data")
                self.serial.write(request + "\r")
                logging.debug("---- data sent")
                time.sleep(0.1)
                            
            try:
                data = self.read_queue.get(5)
            except Empty:
                logging.debug("---- waiting on read queue-list-bastard timed out")
                self.out_queue.put("timeout")      
                continue
                
            logging.debug("---- data recieved from read queue:" + data)
            
            result = self._verify(request, data)
            
            if result == "ok":
                self.out_queue.put(data)
            else:
                self.out_queue.put(result)

    def request(self, request):
        self.in_queue.put(request)
        return self.out_queue.get(True)
    
    def _process(self, line):
        interpreted = paradox.interprete(line)
        if interpreted: self.event_callback(interpreted)
        
    def _verify(self, request, result):
        """
        timeout - no response received in time
        failed - response received with &fail
        ok - no problem
        error - something weird
        """
        logging.debug("verify called with request of '%s' and result of '%s'" %(request, result))

        if not result:
            return "timeout"
        elif result.endswith(paradox.FAIL):
            return "failed"
        else:
            if request[:5] == result[:5]:
                return "ok"
            else:
                return "error"
    
def cb(data):
    print data
    
if __name__ == "__main__":
    x = BackendCommunicator(cb)
    x.start()
    print x.request("RA001")
    print "blocking (:"
