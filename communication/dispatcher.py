'''
Created on Sep 27, 2011

@author: federico
'''
from threading import Thread
from Queue import Queue
import os

#import pycurl

class Dispatcher(Thread):
    def __init__(self):
        self.queue = Queue()
        self.running = True
        self.targets = []
        
        Thread.__init__(self)
        
    def dispatch(self, event):
        if not self.is_alive():
            raise Exception("Dispatcher thread not running!")
        self.queue.put(event)
        
    def add_target(self, target):
        if target not in self.targets:
            self.targets.append(target)
    
    def run(self):
        while self.running:
            event = self.queue.get()
            for target in self.targets:
                self._request(target, event)
    
    def _request(self, target, event):
        print "sent request to", target, "saying", event
        os.system("wget http://" + target + ":8080/" + event)
        #curl = pycurl.Curl()
        #curl.setopt(pycurl.CAINFO, "myFineCA.crt")
        #curl.setopt(pycurl.SSL_VERIFYPEER, 1)
        #curl.setopt(pycurl.SSL_VERIFYHOST, 2)
        #curl.setopt(pycurl.URL, "https://" + target + "/" + event)
        
        #curl.perform()
