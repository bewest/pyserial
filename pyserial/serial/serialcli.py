#! python
#Python Serial Port Extension for Win32, Linux, BSD, Jython and .NET/Mono
#serial driver for .NET/Mono (IronPython), .NET >= 2
#see __init__.py
#
#(C) 2008 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

import System.IO.Ports
from serialutil import *

def device(portnum):
    """Turn a port number into a device name"""
    return System.IO.Ports.SerialPort.GetPortNames()[portnum]

class Serial(SerialBase):
    """Serial port implemenation for .NET/Mono."""

    BAUDRATES = (50,75,110,134,150,200,300,600,1200,1800,2400,4800,9600,
                 19200,38400,57600,115200)

    def open(self):
        """Open port with current settings. This may throw a SerialException
           if the port cannot be opened."""
        if self._port is None:
            raise SerialException("Port must be configured before it can be used.")
        self._port_handle = None
        try:
            self._port_handle = System.IO.Ports.SerialPort(self.portstr)
        except Exception, msg:
            raise SerialException("could not open port %s: %s" % (self.portstr, msg))

        self._reconfigurePort()
        self._port_handle.Open()
        self._isOpen = True

    def _reconfigurePort(self):
        """Set commuication parameters on opened port."""
        if not self._port_handle:
            raise SerialException("Can only operate on a valid port handle")
        
        self.ReceivedBytesThreshold = 1
        
        if self._timeout is None:
            self._port_handle.ReadTimeout = System.IO.Ports.SerialPort.InfiniteTimeout
        else:
            self._port_handle.ReadTimeout = int(self._timeout*1000)
            
        # if self._timeout != 0 and self._interCharTimeout is not None:
            # timeouts = (int(self._interCharTimeout * 1000),) + timeouts[1:]
            
        if self._writeTimeout is None:
            pass
        else:
            self._port_handle.WriteTimeout = int(self._writeTimeout*1000)


        # Setup the connection info.
        self._port_handle.BaudRate = self._baudrate

        if self._bytesize == FIVEBITS:
            self._port_handle.DataBits     = 5
        elif self._bytesize == SIXBITS:
            self._port_handle.DataBits     = 6
        elif self._bytesize == SEVENBITS:
            self._port_handle.DataBits     = 7
        elif self._bytesize == EIGHTBITS:
            self._port_handle.DataBits     = 8
        else:
            raise ValueError("Unsupported number of data bits: %r" % self._bytesize)

        if self._parity == PARITY_NONE:
            self._port_handle.Parity       = System.IO.Ports.Parity.None
        elif self._parity == PARITY_EVEN:
            self._port_handle.Parity       = System.IO.Ports.Parity.Even
        elif self._parity == PARITY_ODD:
            self._port_handle.Parity       = System.IO.Ports.Parity.Odd
        elif self._parity == PARITY_MARK:
            self._port_handle.Parity       = System.IO.Ports.Parity.Mark
        elif self._parity == PARITY_SPACE:
            self._port_handle.Parity       = System.IO.Ports.Parity.Space
        else:
            raise ValueError("Unsupported parity mode: %r" % self._parity)

        if self._stopbits == STOPBITS_ONE:
            self._port_handle.StopBits     = System.IO.Ports.StopBits.One
        elif self._stopbits == STOPBITS_TWO:
            self._port_handle.StopBits     = System.IO.Ports.StopBits.Two
        else:
            raise ValueError("Unsupported number of stop bits: %r" % self._stopbits)
        
        if self._rtscts and self._xonxoff:
            self._port_handle.Handshake  = System.IO.Ports.Handshake.RequestToSendXOnXOff
        elif self._rtscts:
            self._port_handle.Handshake  = System.IO.Ports.Handshake.RequestToSend
        elif self._xonxoff:
            self._port_handle.Handshake  = System.IO.Ports.Handshake.XOnXOff
        else:
            self._port_handle.Handshake  = System.IO.Ports.Handshake.None

    #~ def __del__(self):
        #~ self.close()

    def close(self):
        """Close port"""
        if self._isOpen:
            if self._port_handle:
                try:
                    self.Close()
                except System.IO.Ports.InvalidOperationException:
                    # ignore errors. can happen for unplugged USB serial devices
                    pass
                self._port_handle = None
            self._isOpen = False

    def makeDeviceName(self, port):
        return device(port)

    #  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
    
    def inWaiting(self):
        """Return the number of characters currently in the input buffer."""
        if not self._port_handle: raise portNotOpenError
        return self._port_handle.BytesToRead

    def read(self, size=1):
        """Read size bytes from the serial port. If a timeout is set it may
           return less characters as requested. With no timeout it will block
           until the requested number of bytes is read."""
        if not self._port_handle: raise portNotOpenError
        data = []
        while size:
            data.append(self._port_handle.ReadByte())
            size -= 1
        return ''.join(data)

    def write(self, data):
        """Output the given string over the serial port."""
        if not self._port_handle: raise portNotOpenError
        if not isinstance(data, str):
            raise TypeError('expected str, got %s' % type(data))
        self._port_handle.Write(data)

    def flushInput(self):
        """Clear input buffer, discarding all that is in the buffer."""
        if not self._port_handle: raise portNotOpenError
        self._port_handle.DiscardInBuffer()

    def flushOutput(self):
        """Clear output buffer, aborting the current output and
        discarding all that is in the buffer."""
        if not self._port_handle: raise portNotOpenError
        self._port_handle.DiscardOutBuffer()

    def sendBreak(self, duration=0.25):
        """Send break condition. Timed, returns to idle state after given duration."""
        if not self._port_handle: raise portNotOpenError
        import time
        self._port_handle.BreakState = True
        time.sleep(duration)
        self._port_handle.BreakState = False

    def setBreak(self, level=1):
        """Set break: Controls TXD. When active, to transmitting is possible."""
        if not self._port_handle: raise portNotOpenError
        self._port_handle.BreakState = level

    def setRTS(self, level=1):
        """Set terminal status line: Request To Send"""
        if not self._port_handle: raise portNotOpenError
        self._port_handle.RtsEnable = level

    def setDTR(self, level=1):
        """Set terminal status line: Data Terminal Ready"""
        if not self._port_handle: raise portNotOpenError
        self._port_handle.DtrEnable = level

    def getCTS(self):
        """Read terminal status line: Clear To Send"""
        if not self._port_handle: raise portNotOpenError
        return self._port_handle.CtsHolding

    def getDSR(self):
        """Read terminal status line: Data Set Ready"""
        if not self._port_handle: raise portNotOpenError
        return self._port_handle.DsrHolding

    #~ def getRI(self):
        #~ """Read terminal status line: Ring Indicator"""
        #~ if not self._port_handle: raise portNotOpenError
        #~ return self._port_handle.XXX

    def getCD(self):
        """Read terminal status line: Carrier Detect"""
        if not self._port_handle: raise portNotOpenError
        return self._port_handle.CDHolding

    # - - platform specific - - - -

#Nur Testfunktion!!
if __name__ == '__main__':
    s = Serial(0)
    print s
    
    s = Serial()
    print s
    
    
    s.baudrate = 19200
    s.databits = 7
    s.close()
    s.port = 0
    s.open()
    print s

