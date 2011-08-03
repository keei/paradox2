'''
Created on Jul 23, 2011

@author: federico
'''

import re

OK = "&OK"
FAIL = "&FAIL"
COMMUNICATION = "COMM"

###### COMMANDS SENT TO THE MODULE FROM US
VIRTUAL_INPUT_OPEN = "VO%03d"
VIRTUAL_INPUT_CLOSED = "VC%03d"

REQUEST_AREA_STATUS = "RA%03d"
REQUEST_AREA_STATUS_REPLY = re.compile(r"RA%03d(\w\w\w\w\w\w\w)")
REQUEST_AREA_STATUS_BYTE_6 = {"D": "disarmed", "A": "armed", "F": "force armed", "S": "stay armed", "I": "instant armed"}
REQUEST_AREA_STATUS_BYTE_7 = {"M": "zone in memory", "O": "OK"}
REQUEST_AREA_STATUS_BYTE_8 = {"T": "trouble", "O": "OK"}
REQUEST_AREA_STATUS_BYTE_9 = {"N": "not ready", "O": "OK"}
REQUEST_AREA_STATUS_BYTE_10 = {"P": "in programming", "O": "OK"}
REQUEST_AREA_STATUS_BYTE_11 = {"A": "in alarm", "O": "OK"}
REQUEST_AREA_STATUS_BYTE_12 = {"S": "strobe", "O": "OK"}

REQUEST_ZONE_STATUS = "RZ%03d"
REQUEST_ZONE_STATUS_REPLY = re.compile(r"RZ\d\d\d(\w\w\w\w\w)")
REQUEST_ZONE_STATUS_BYTE_6 = {"C": "closed", "O": "open", "T": "tampered", "F": "fire loop trouble"}
REQUEST_ZONE_STATUS_BYTE_7 = {"A": "in alarm", "O": "OK"}
REQUEST_ZONE_STATUS_BYTE_8 = {"F": "fire alarm", "O": "OK"}
REQUEST_ZONE_STATUS_BYTE_9 = {"S": "supervision lost", "O": "OK"}
REQUEST_ZONE_STATUS_BYTE_10 = {"L": "low battery", "O": "OK"}

# XXX: TODO
REQUEST_ZONE_LABEL = "ZL%03d"
REQUEST_AREA_LABEL = "AL%03d"
REQUEST_USER_LABEL = "UL%03d"

# If incorrect code - we get an &fail back.
AREA_ARM = "AA%03d%s%s"
ARAE_ARM_BYTE6 = {"regular arm": "A", "force arm": "F", "stay arm": "S", "instant arm": "I"}

AREA_DISARM = "AD%03d%s"

EMERGENCY_PANIC = "PE%03d"
MEDICAL_PANIC = "PM%03d"
FIRE_PANIC = "PF%03d"
SMOKE_RESET = "SR%03d"

###### COMMANDS SENT TO US FROM THE MODULE
VIRTUAL_PGM_ON = re.compile(r"PGM(\d\d)ON")
VIRTUAL_PGM_OFF = re.compile(r"PGM(\d\d)OFF")

SYSTEM_EVENT = re.compile(r"G(\d\d\d)N(\d\d\d)A(\d\d\d)")

# NB: Pad to 3
SYSTEM_EVENT_GROUP = {0: "zone ok", 1: "zone open", 2: "zone tampered", 3: "zone fire loop",
                      10: "armed with usercode",
                      14: "disarmed with usercode",
                      17: "disarmed after alarm with usercode",
                      20: "arming canceled with usercode",
                      23: "zone bypassed",
                      24: "zone in alarm",
                      25: "fire alarm",
                      26: "zone alarm restore",
                      27: "fire alarm restore",
                      30: "special alarm",
                      31: "duress alarm by user",
                      32: "zone shutdown",
                      33: "zone tamper",
                      34: "zone tamper restore",
                      36: "trouble event",
                      37: "trouble restore",
                      38: "module trouble",
                      39: "module trouble restore",
                      41: "low battery on zone",
                      42: "zone supervision trouble",
                      43: "low battery on zone restore",
                      44: "zone supervision trouble restore",
                      64: "status 1",
                      65: "status 2",
                      66: "status 3"                      
                      }

SYSTEM_EVENT_NUMBER_SIGNIFICANCE = {0: "zone in question", 1: "zone in question", 2: "zone in question", 3: "zone in question",
                      10: "usercode in question",
                      14: "usercode in question",
                      17: "usercode in question",
                      20: "usercode in question",
                      23: "zone in question",
                      24: "zone in question",
                      25: "zone in question",
                      26: "zone in question",
                      27: "zone in question",
                      30: {0: "emergency panic", 1: "medical panic", 2: "fire panic"},
                      31: "usercode in question",
                      32: "zone in question",
                      33: "zone in question",
                      34: "zone in question",
                      36: {1: "ac failure", 2: "battery failure", 5: "bell absent"},
                      37: {1: "ac failure", 2: "battery failure", 5: "bell absent"},
                      38: "dont care",
                      39: "dont care",
                      41: "zone in question",
                      42: "zone in question",
                      43: "zone in question",
                      44: "zone in question",
                      64: "area in question",
                      65: "area in question",
                      66: "area in question"                      
                      }

SYSTEM_AREA_NUMBER_SIGNIFICANCE = {64: {0: "armed", 1: "force armed", 2: "stay armed", 3: "instant armed", 4: "strobe alarm", 5: "silent alarm", 6: "audible alarm", 7: "fire alarm"},
                                 65: {0: "ready", 1: "exit delay", 2: "entry delay", 3: "system in trouble", 5: "zones bypassed"},
                                 66: {5: "zone low battery"}}

class Event(object):
    group = None
    number = None
    area = None
    
    def __str__(self):
        return "Group '%s' Number '%s' Area '%s'" % (self.group, self.number, self.area)
    
def interprete(line):
    event_to_return = Event()
    
    match = SYSTEM_EVENT.match(line)
    if not match: return None
    
    group, number, area = match.groups()
    group = int(group)
    number = int(number)
    area = int(area)
    
    if group not in SYSTEM_EVENT_GROUP:
        return None
    else:
        event_to_return.group = SYSTEM_EVENT_GROUP[group]
    
    if isinstance(SYSTEM_EVENT_NUMBER_SIGNIFICANCE[group], dict):
        event_to_return.number = SYSTEM_EVENT_NUMBER_SIGNIFICANCE[group][number]
    else:
        event_to_return.number = number
    
    if group in SYSTEM_AREA_NUMBER_SIGNIFICANCE:
        event_to_return.area = SYSTEM_AREA_NUMBER_SIGNIFICANCE[group][area]
    else:
        event_to_return.area = area
    
    return event_to_return
    