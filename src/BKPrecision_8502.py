'''
Created on Feb 5, 2016


Open Source Initiative OSI - The MIT License:Licensing
Tue, 2006-10-31 04:56 nelson

The MIT License

Copyright (c) 2009 BK Precision

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

@Revision: 1.0 
@Date: 2008/05/17 15:57:15 
@Author:  Don Peterson 



@author: tgack
@Revision: 1.1

    This module is based on the original dcload.py from BK Precision

    Removed windows dependencies and COM interface.
    Removed most of the magic numbers, i.e. hard coded commands
    Fixed a bug in SetTriggerSource command, was sending set address command
    
@Description:

    This module contains a class that implements an easy to use interface
    for remote control of the BK Precision 8502 Electronic Load.
    
     
    
@Dependenices:
    PySerial

@Defaults:
    Baud rate: 4800
    
'''

import sys
import serial
import time
from string import join

# Debugging information is set to stdout by default.  You can change
# the out variable to another method to e.g. write to a different
# stream.
out = sys.stdout.write
nl = "\n"


class BKPrecision_8502:
    '''
    classdocs
    '''
    debug = 0               # SEt to 1 to see dumps of commands and responses
    length_packet = 26      # Number of bytes in a packet
    convert_current = 1e4   # Convert current in A to 0.1mA
    convert_voltage = 1e3   # Convert voltage in V to mV
    convert_power = 1e3     # Convert power in W to mW
    convert_resistance = 1e3 # Convert resistance in ohm to mohm
    to_ms = 1000            # Convert seconds to ms
    
    # Number of settings in storage registers
    lowest_register = 1
    highest_register = 25
    
    # Values for setting modes of CC, CV, CW, or CR
    modes = {"cc":0, "cv": 1, "cw": 2, "cr":3 }
    
    COMMANDS = {
        "RETURN_DATA" : 0x12,
        "SET_REMOTE_OPERATION" : 0x20,
        "ON_OFF" : 0x21,
        "SET_MAX_VOLT" : 0x22,
        "READ_MAX_VOLT" : 0x23,
        "SET_MAX_CURRENT" : 0x24,
        "READ_MAX_CURRENT" : 0x25,
        "SET_MAX_POWER" : 0x26,
        "READ_MAX_POWER" : 0x27,
        "SET_MODE" : 0x28,
        "READ_MODE" : 0x29,
        "SET_CC_MODE_VALUE" : 0x2A,
        "READ_CC_MODE_VALUE" : 0x2B,
        "SET_CV_MODE_VALUE" : 0x2C,
        "READ_CV_MODE_VALUE" : 0x2D,
        "SET_CW_MODE_VALUE" : 0x2E,
        "READ_CW_MODE_VALUE" : 0x2F,
        "SET_CR_MODE_VALUE" : 0x30, 
        "READ_CR_MODE_VALUE" : 0x31,
        "SET_CC_MODE_TRNS_C_AND_T" : 0x32,
        "READ_CC_MODE_TRNS_C_AND_T" : 0x33,
        "SET_CV_MODE_TRANS_V_AND_T" : 0x34,
        "READ_CV_MODE_TRANS_V_AND_T" : 0x35,
        "SET_CW_MODE_TRANS_P_AND_T" : 0x36,
        "READ_CW_MODE_TRANS_P_AND_T" : 0x37,
        "SET_CR_MODE_TRANS_R_AND_T" : 0x38,
        "READ_CR_MODE_TRANS_R_AND_T" : 0x39,
        "SEL_LIST_OPERATION" : 0x3A,
        "READ_LIST_OPERATION" : 0x3B,
        "SET_LIST_REPEAT" : 0x3C,
        "READ_LIST_REPEAT" : 0x3D,
        "SET_LIST_NUMBER_STEPS" : 0x3E,
        "READ_LIST_NUMBER_STEPS" : 0x3F,
        "SET_STEP_C_AND_T_VALUE" : 0x40,
        "READ_STEP_C_AND_T_VALUE" : 0x41,
        "SET_STEP_V_AND_T_VALUE" : 0x42,
        "READ_STEP_V_AND_T_VALUE" : 0x43,
        "SET_STEP_P_AND_T_VALUE" : 0x44,
        "READ_STEP_P_AND_T_VALUE" : 0x45,
        "SET_STEP_R_AND_T_VALUE" : 0x46,
        "READ_STEP_R_AND_T_VALUE" : 0x47,
        "SET_LIST_FILENAME" : 0x48,
        "READ_LIST_FILENAME" : 0x49,
        "SET_MEM_LIST_PART" : 0x4A,
        "READ_MEM_LIST_PART" : 0x4B,
        "STORE_LIST_FILE" : 0x4C,
        "RECALL_LIST_FILE" : 0x4D,
        "SET_MIN_BATT_TEST_VOLT" : 0x4E,
        "READ_MIN_BATT_TEST_VOLT" : 0x4F,
        "SET_TIMER_LOAD_ON" : 0x50,
        "READ_TIMER_LOAD_ON" : 0x51,
        "SET_TIMER_LOAD_ON_ENABLE" : 0x52,
        "READ_TIMER_STATE_LOAD_ON" : 0x53,
        "SET_COMM_ADDRESS" : 0x54,
        "SET_LOCAL_CONTROL_ENABLE" : 0x55,
        "SET_REMOTE_SENSE_ENABLE" : 0x56,
        "READ_REMOTE_SENSE_ENABLE" : 0x57,
        "SEL_TRIGGER_SOURCE" : 0x58,
        "READ_TRIGGER_SOURCE" : 0x59,
        "TRIGGER_LOAD" : 0x5A,
        "STORE_LOAD_SETTINGS" : 0x5B,
        "RECALL_LOAD_SETTINGS" : 0x5C,
        "SELECT_FUNCTION_TYPE" : 0x5D,
        "READ_FUNCTION_TYPE" : 0x5E,
        "READ_INPUT_VALUE" : 0x5F,
        "ENTER_CAL_STATE" : 0x60,
        "READ_CAL_STATE" : 0x61,
        "SET_VOLT_CAL_P_INDEX" : 0x62,
        "SET_VOLT_TO_CAL_PROG" : 0x63,
        "SET_CUR_CAL_P_INDEX" : 0x64,
        "SET_CUR_TO_P_INDEX" : 0x65,
        "STORE_CAL_DATA_EE" : 0x66,
        "SET_CAL_INFO" : 0x67,
        "READ_CAL_INFO" : 0x68,
        "RESTORE_FACTOR_CAL" : 0x69,
        "READ_DEVICE_INFO" : 0x6A,
        "READ_BARCODE_INFO" : 0x6B
        
    }
    

    def __init__(self, port, baudrate, address):
        '''
        Constructor
        '''
        self.sp = serial.Serial(port, baudrate, timeout=1, parity=serial.PARITY_NONE)
        self.address = address
        
    def DumpCommand(self, byte_list):
        '''Print out the contents of a 26 byte command.  Example:
            aa .. 20 01 ..   .. .. .. .. ..
            .. .. .. .. ..   .. .. .. .. ..
            .. .. .. .. ..   cb
        '''
        assert(len(byte_list) == self.length_packet)
        header = " "*3
        out(header)
        for i in xrange(self.length_packet):
            if i % 10 == 0 and i != 0:
                out(nl + header)
            if i % 5 == 0:
                out(" ")
            s = "%02x" % ord(byte_list[i])
            if s == "00":
                # Use the decimal point character if you see an
                # unattractive printout on your machine.
                #s = "."*2
                # The following alternate character looks nicer
                # in a console window on Windows.
                s = chr(250)*2
            out(s)
        out(nl)
                
    def CommandProperlyFormed(self, cmd):
        '''Return 1 if a command is properly formed; otherwise, return 0.
        '''
        commands = (
            0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29,
            0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33,
            0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B, 0x3C, 0x3D,
            0x3E, 0x3F, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47,
            0x48, 0x49, 0x4A, 0x4B, 0x4C, 0x4D, 0x4E, 0x4F, 0x50, 0x51,
            0x52, 0x53, 0x54, 0x55, 0x56, 0x57, 0x58, 0x59, 0x5A, 0x5B,
            0x5C, 0x5D, 0x5E, 0x5F, 0x60, 0x61, 0x62, 0x63, 0x64, 0x65,
            0x66, 0x67, 0x68, 0x69, 0x6A, 0x6B, 0x6C, 0x12
        )
        # Must be proper length
        if len(cmd) != self.length_packet:
            out("Command length = " + str(len(cmd)) + "-- should be " + \
                str(self.length_packet) + nl)
            return 0
        # First character must be 0xaa
        if ord(cmd[0]) != 0xaa:
            out("First byte should be 0xaa" + nl)
            return 0
        # Second character (address) must not be 0xff
        if ord(cmd[1]) == 0xff:
            out("Second byte cannot be 0xff" + nl)
            return 0
        # Third character must be valid command
        byte3 = "%02X" % ord(cmd[2])
        if ord(cmd[2]) not in commands:
            out("Third byte not a valid command:  %s\n" % byte3)
            return 0
        # Calculate checksum and validate it
        checksum = self.CalculateChecksum(cmd)
        if checksum != ord(cmd[-1]):
            out("Incorrect checksum" + nl)
            return 0
        return 1
    
    def CalculateChecksum(self, cmd):
        '''Return the sum of the bytes in cmd modulo 256.
        '''
        assert((len(cmd) == self.length_packet - 1) or (len(cmd) == self.length_packet))
        checksum = 0
        for i in xrange(self.length_packet - 1):
            checksum += ord(cmd[i])
        checksum %= 256
        return checksum
    
    def StartCommand(self, byte):
        return chr(0xaa) + chr(self.address) + chr(byte)
                    
    def SendCommand(self, command):
        '''Sends the command to the serial stream and returns the 26 byte
        response.
        '''
        assert(len(command) == self.length_packet)
        self.sp.write(command)
        response = self.sp.read(self.length_packet)
        assert(len(response) == self.length_packet)
        return response                    

    def ResponseStatus(self, response):
        '''Return a message string about what the response meant.  The
        empty string means the response was OK.
        '''
        responses = {
            0x90 : "Wrong checksum",
            0xA0 : "Incorrect parameter value",
            0xB0 : "Command cannot be carried out",
            0xC0 : "Invalid command",
            0x80 : "",
        }
        assert(len(response) == self.length_packet)
        assert(ord(response[2]) == 0x12)
        return responses[ord(response[3])]

    def CodeInteger(self, value, num_bytes=4):
        '''Construct a little endian string for the indicated value.  Two
        and 4 byte integers are the only ones allowed.
        '''
        assert(num_bytes == 1 or num_bytes == 2 or num_bytes == 4)
        value = int(value)  # Make sure it's an integer
        s  = chr(value & 0xff)
        if num_bytes >= 2:
            s += chr((value & (0xff << 8)) >> 8)
            if num_bytes == 4:
                s += chr((value & (0xff << 16)) >> 16)
                s += chr((value & (0xff << 24)) >> 24)
                assert(len(s) == 4)
        return s
    
    def DecodeInteger(self, value):
        '''Construct an integer from the little endian string. 1, 2, and 4 byte 
        strings are the only ones allowed.
        '''
        assert(len(value) == 1 or len(value) == 2 or len(value) == 4)
        n  = ord(value[0])
        if len(value) >= 2:
            n += (ord(value[1]) << 8)
            if len(value) == 4:
                n += (ord(value[2]) << 16)
                n += (ord(value[3]) << 24)
        return n
    
    def GetReserved(self, num_used):
        '''Construct a string of nul characters of such length to pad a
        command to one less than the packet size (leaves room for the 
        checksum byte.
        '''
        num = self.length_packet - num_used - 1
        assert(num > 0)
        return chr(0)*num
                           
    def PrintCommandAndResponse(self, cmd, response, cmd_name):
        '''Print the command and its response if debugging is on.
        '''
        assert(cmd_name)
        if self.debug:
            out(cmd_name + " command:" + nl)
            self.DumpCommand(cmd)
            out(cmd_name + " response:" + nl)
            self.DumpCommand(response)
              
              
    def GetCommand(self, command, value, num_bytes=4):
        '''Construct the command with an integer value of 0, 1, 2, or 
        4 bytes.
        '''
        cmd = self.StartCommand(command)
        if num_bytes > 0:
            r = num_bytes + 3
            cmd += self.CodeInteger(value)[:num_bytes] + self.Reserved(r)
        else:
            cmd += self.Reserved(0)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        return cmd
              
    def GetData(self, data, num_bytes=4):
        '''Extract the little endian integer from the data and return it.
        '''
        assert(len(data) == self.length_packet)
        if num_bytes == 1:
            return ord(data[3])
        elif num_bytes == 2:
            return self.DecodeInteger(data[3:5])
        elif num_bytes == 4:
            return self.DecodeInteger(data[3:7])
        else:
            raise Exception("Bad number of bytes:  %d" % num_bytes)
                
    def Reserved(self, num_used):
        assert(num_used >= 3 and num_used < self.length_packet - 1)
        return chr(0)*(self.length_packet - num_used - 1)
                
    def SendIntegerToLoad(self, byte, value, msg, num_bytes=4):
        '''Send the indicated command along with value encoded as an integer
        of the specified size.  Return the instrument's response status.
        '''
        cmd = self.GetCommand(byte, value, num_bytes)
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, msg)
        return self.ResponseStatus(response)
                                    
    def GetIntegerFromLoad(self, cmd_byte, msg, num_bytes=4):
        '''Construct a command from the byte in cmd_byte, send it, get
        the response, then decode the response into an integer with the
        number of bytes in num_bytes.  msg is the debugging string for
        the printout.  Return the integer.
        '''
        assert(num_bytes == 1 or num_bytes == 2 or num_bytes == 4)
        cmd = self.StartCommand(cmd_byte)
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, msg)
        return self.DecodeInteger(response[3:3 + num_bytes])
                                    
                                 
    def GetCommandFromKey(self, S):
        "Returns the integer value of the command"
        if S.upper() not in self.COMMANDS:
            raise Exception("Unknown command")
            
        return self.COMMANDS[S]
                                        
    def TimeNow(self):
        "Returns a string containing the current time"
        return time.asctime()
    
    def TurnLoadOn(self):
        "Turns the load on"
        msg = "Turn load on"
        on = 1
        return self.SendIntegerToLoad(self.GetCommandFromKey("ON_OFF"), on, msg, num_bytes=1)
    def TurnLoadOff(self):
        "Turns the load off"
        msg = "Turn load off"
        off = 0
        return self.SendIntegerToLoad(self.GetCommandFromKey("ON_OFF"), off, msg, num_bytes=1)
    
    def SetRemoteControl(self):
        "Sets the load to remote control"
        msg = "Set remote control"
        remote = 1
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_REMOTE_OPERATION"), remote, msg, num_bytes=1)
    
    def SetLocalControl(self):
        "Sets the load to local control"
        msg = "Set local control"
        local = 0
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_REMOTE_OPERATION"), local, msg, num_bytes=1)
    
    def SetmaxCurrent(self, current):
        "Sets the maximum current the load will sink"
        msg = "Set max current"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_MAX_CURRENT"), current*self.convert_current, msg, num_bytes=4)
    
    def GetMaxCurrent(self):
        "Returns the maximum current the load will sink"
        msg = "Set max current"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_MAX_CURRENT"), msg, num_bytes=4)/self.convert_current
    
    def SetMaxVoltage(self, voltage):
        "Sets the maximum voltage the load will allow"
        msg = "Set max voltage"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_MAX_VOLT"), voltage*self.convert_voltage, msg, num_bytes=4)
    
    def GetMaxVoltage(self):
        "Gets the maximum voltage the load will allow"
        msg = "Get max voltage"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_MAX_VOLT"), msg, num_bytes=4)/self.convert_voltage
    
    def SetMaxPower(self, power):
        "Sets the maximum power the load will allow"
        msg = "Set max power"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_MAX_POWER"), power*self.convert_power, msg, num_bytes=4)
    
    def GetMaxPower(self):
        "Gets the maximum power the load will allow"
        msg = "Get max power"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_MAX_POWER"), msg, num_bytes=4)/self.convert_power
    
    def SetMode(self, mode):
        "Sets the mode (constant current, constant voltage, etc."
        if mode.lower() not in self.modes:
            raise Exception("Unknown mode")
        msg = "Set mode"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_MODE"), self.modes[mode.lower()], msg, num_bytes=1)
    
    def GetMode(self):
        "Gets the mode (constant current, constant voltage, etc."
        msg = "Get mode"
        mode = self.GetIntegerFromLoad(self.GetCommandFromKey("READ_MODE"), msg, num_bytes=1)
        modes_inv = {0:"cc", 1:"cv", 2:"cw", 3:"cr"}
        return modes_inv[mode]
    
    def SetCCCurrent(self, current_in_A):
        "Sets the constant current mode's current level"
        msg = "Set CC current"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_CC_MODE_VALUE"), current_in_A*self.convert_current, msg, num_bytes=4)
    
    def GetCCCurrent(self):
        "Gets the constant current mode's current level"
        msg = "Get CC current"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_CC_MODE_VALUE"), msg, num_bytes=4)/self.convert_current
    
    def SetCVVoltage(self, voltage_in_V):
        "Sets the constant voltage mode's voltage level"
        msg = "Set CV voltage"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_CV_MODE_VALUE"), voltage_in_V*self.convert_voltage, msg, num_bytes=4)
    
    def GetCVVoltage(self):
        "Gets the constant voltage mode's voltage level"
        msg = "Get CV voltage"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_CV_MODE_VALUE"), msg, num_bytes=4)/self.convert_voltage
    
    def SetCWPower(self, power_in_W):
        "Sets the constant power mode's power level"
        msg = "Set CW power"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_CW_MODE_VALUE"), power_in_W*self.convert_power, msg, num_bytes=4)
    def GetCWPower(self):
        "Gets the constant power mode's power level"
        msg = "Get CW power"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_CW_MODE_VALUE"), msg, num_bytes=4)/self.convert_power
    
    def SetCRResistance(self, resistance):
        "Sets the constant resistance mode's resistance level"
        msg = "Set CR resistance"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_CR_MODE_VALUE"), resistance*self.convert_resistance, msg, num_bytes=4)
    
    def GetCRResistance(self):
        "Gets the constant resistance mode's resistance level"
        msg = "Get CR resistance"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_CR_MODE_VALUE"), msg, num_bytes=4)/self.convert_resistance
    
    def SetTransient(self, mode, A, A_time_s, B, B_time_s, operation="continuous"):
        '''Sets up the transient operation mode.  mode is one of 
        "CC", "CV", "CW", or "CR".
        '''
        if mode.lower() not in self.modes:
            raise Exception("Unknown mode")
        opcodes = {"cc":0x32, "cv":0x34, "cw":0x36, "cr":0x38}
        if mode.lower() == "cc":
            const = self.convert_current
        elif mode.lower() == "cv":
            const = self.convert_voltage
        elif mode.lower() == "cw":
            const = self.convert_power
        else:
            const = self.convert_resistance
        cmd = self.StartCommand(opcodes[mode.lower()])
        cmd += self.CodeInteger(A*const, num_bytes=4)
        cmd += self.CodeInteger(A_time_s*self.to_ms, num_bytes=2)
        cmd += self.CodeInteger(B*const, num_bytes=4)
        cmd += self.CodeInteger(B_time_s*self.to_ms, num_bytes=2)
        transient_operations = {"continuous":0, "pulse":1, "toggled":2}
        cmd += self.CodeInteger(transient_operations[operation], num_bytes=1)
        cmd += self.Reserved(16)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Set %s transient" % mode)
        return self.ResponseStatus(response)
    
    def GetTransient(self, mode):
        "Gets the transient mode settings"
        if mode.lower() not in self.modes:
            raise Exception("Unknown mode")
        opcodes = {"cc":0x33, "cv":0x35, "cw":0x37, "cr":0x39}
        cmd = self.StartCommand(opcodes[mode.lower()])
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get %s transient" % mode)
        A = self.DecodeInteger(response[3:7])
        A_timer_ms = self.DecodeInteger(response[7:9])
        B = self.DecodeInteger(response[9:13])
        B_timer_ms = self.DecodeInteger(response[13:15])
        operation = self.DecodeInteger(response[15])
        time_const = 1e3
        transient_operations_inv = {0:"continuous", 1:"pulse", 2:"toggled"}
        if mode.lower() == "cc":
            return str((A/self.convert_current, A_timer_ms/time_const,
                    B/self.convert_current, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
        elif mode.lower() == "cv":
            return str((A/self.convert_voltage, A_timer_ms/time_const,
                    B/self.convert_voltage, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
        elif mode.lower() == "cw":
            return str((A/self.convert_power, A_timer_ms/time_const,
                    B/self.convert_power, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
        else:
            return str((A/self.convert_resistance, A_timer_ms/time_const, 
                    B/self.convert_resistance, B_timer_ms/time_const,
                    transient_operations_inv[operation]))
    
    def SetBatteryTestVoltage(self, min_voltage_in_V):
        "Sets the battery test voltage"
        msg = "Set battery test voltage"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_MIN_BATT_TEST_VOLT"), min_voltage_in_V*self.convert_voltage, msg, num_bytes=4)
    
    def GetBatteryTestVoltage(self):
        "Gets the battery test voltage"
        msg = "Get battery test voltage"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_MIN_BATT_TEST_VOLT"), msg, num_bytes=4)/self.convert_voltage
    
    def SetLoadOnTimer(self, time_in_s):
        "Sets the time in seconds that the load will be on"
        msg = "Set load on timer"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_TIMER_LOAD_ON"), time_in_s, msg, num_bytes=2)
    
    def GetLoadOnTimer(self):
        "Gets the time in seconds that the load will be on"
        msg = "Get load on timer"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("SET_TIMER_LOAD_ON"), msg, num_bytes=2)
    
    def SetLoadOnTimerState(self, enabled=0):
        "Enables or disables the load on timer state"
        msg = "Set load on timer state"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_TIMER_LOAD_ON"), enabled, msg, num_bytes=1)
    
    def GetLoadOnTimerState(self):
        "Gets the load on timer state"
        msg = "Get load on timer"
        state = self.GetIntegerFromLoad(self.GetCommandFromKey("READ_TIMER_STATE_LOAD_ON"), msg, num_bytes=1)
        if state == 0:
            return "disabled"
        else:
            return "enabled"
    
    def SetCommunicationAddress(self, address=0):
        '''Sets the communication address.  Note:  this feature is
        not currently supported.  The communication address should always
        be set to 0.
        '''
        msg = "Set communication address"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_COMM_ADDRESS"), address, msg, num_bytes=1)
    
    def EnableLocalControl(self):
        "Enable local control (i.e., key presses work) of the load"
        msg = "Enable local control"
        enabled = 1
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_LOCAL_CONTROL_ENABLE"), enabled, msg, num_bytes=1)
    
    def DisableLocalControl(self):
        "Disable local control of the load"
        msg = "Disable local control"
        disabled = 0
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_LOCAL_CONTROL_ENABLE"), disabled, msg, num_bytes=1)
    
    def SetRemoteSense(self, enabled=0):
        "Enable or disable remote sensing"
        msg = "Set remote sense"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SET_REMOTE_SENSE_ENABLE"), enabled, msg, num_bytes=1)
    
    def GetRemoteSense(self):
        "Get the state of remote sensing"
        msg = "Get remote sense"
        return self.GetIntegerFromLoad(self.GetCommandFromKey("READ_REMOTE_SENSE_ENABLE"), msg, num_bytes=1)
    
    def SetTriggerSource(self, source="immediate"):
        '''Set how the instrument will be triggered.
        "immediate" means triggered from the front panel.
        "external" means triggered by a TTL signal on the rear panel.
        "bus" means a software trigger (see TriggerLoad()).
        '''
        trigger = {"immediate":0, "external":1, "bus":2}
        if source not in trigger:
            raise Exception("Trigger type %s not recognized" % source)
        msg = "Set trigger type"
        return self.SendIntegerToLoad(self.GetCommandFromKey("SEL_TRIGGER_SOURCE"), trigger[source], msg, num_bytes=1)
    
    def GetTriggerSource(self):
        "Get how the instrument will be triggered"
        msg = "Get trigger source"
        t = self.GetIntegerFromLoad(self.GetCommandFromKey("READ_TRIGGER_SOURCE"), msg, num_bytes=1)
        trigger_inv = {0:"immediate", 1:"external", 2:"bus"}
        return trigger_inv[t]
    
    def TriggerLoad(self):
        '''Provide a software trigger.  This is only of use when the trigger
        mode is set to "bus".
        '''
        cmd = self.StartCommand(self.GetCommandFromKey("TRIGGER_LOAD"))
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Trigger load (trigger = bus)")
        return self.ResponseStatus(response)
    
    def SaveSettings(self, register=0):
        "Save instrument settings to a register"
        assert(self.lowest_register <= register <= self.highest_register)
        msg = "Save to register %d" % register
        return self.SendIntegerToLoad(self.GetCommandFromKey("STORE_LOAD_SETTINGS"), register, msg, num_bytes=1)
    
    def RecallSettings(self, register=0):
        "Restore instrument settings from a register"
        assert(self.lowest_register <= register <= self.highest_register)
        cmd = self.GetCommand(self.GetCommandFromKey("RECALL_LOAD_SETTINGS"), register, num_bytes=1)
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Recall register %d" % register)
        return self.ResponseStatus(response)
    
    def SetFunction(self, function="fixed"):
        '''Set the function (type of operation) of the load.
        function is one of "fixed", "short", "transient", or "battery".
        Note "list" is intentionally left out for now.
        '''
        msg = "Set function to %s" % function
        functions = {"fixed":0, "short":1, "transient":2, "battery":4}
        return self.SendIntegerToLoad(self.GetCommandFromKey("SELECT_FUNCTION_TYPE"), functions[function], msg, num_bytes=1)
    
    def GetFunction(self):
        "Get the function (type of operation) of the load"
        msg = "Get function"
        fn = self.GetIntegerFromLoad(self.GetCommandFromKey("READ_FUNCTION_TYPE"), msg, num_bytes=1)
        functions_inv = {0:"fixed", 1:"short", 2:"transient", 4:"battery"}
        return functions_inv[fn]
    
    def GetInputValues(self):
        '''Returns voltage in V, current in A, and power in W, op_state byte,
        and demand_state byte.
        '''
        cmd = self.StartCommand(self.GetCommandFromKey("READ_INPUT_VALUE"))
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get input values")
        voltage = self.DecodeInteger(response[3:7])/self.convert_voltage
        current = self.DecodeInteger(response[7:11])/self.convert_current
        power   = self.DecodeInteger(response[11:15])/self.convert_power
        op_state = hex(self.DecodeInteger(response[15]))
        demand_state = hex(self.DecodeInteger(response[16:18]))
        s = [str(voltage) + " V", str(current) + " A", str(power) + " W", str(op_state), str(demand_state)]
        return join(s, "\t")
    
    def GetProductInformation(self):
        "Returns model number, serial number, and firmware version"
        cmd = self.StartCommand(self.GetCommandFromKey("READ_DEVICE_INFO"))
        cmd += self.Reserved(3)
        cmd += chr(self.CalculateChecksum(cmd))
        assert(self.CommandProperlyFormed(cmd))
        response = self.SendCommand(cmd)
        self.PrintCommandAndResponse(cmd, response, "Get product info")
        model = response[3:8]
        fw = hex(ord(response[9]))[2:] + "."
        fw += hex(ord(response[8]))[2:] 
        serial_number = response[10:20]
        return join((str(model), str(serial_number), str(fw)), "\t")    

