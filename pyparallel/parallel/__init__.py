#!/usr/bin/env python 
#portable parallel port access with python
#this is a wrapper module for different platform implementations
#
# (C)2001-2002 Chris Liechti <cliechti@gmx.net>
# this is distributed under a free software license, see license.txt

import sys, os, string
VERSION = string.split("$Revision: 1.2 $")[1]     #extract CVS version

#chose an implementation, depending on os
if os.name == 'nt':
    from parallelwin32 import *
elif os.name == 'posix':
    #from parallelposix import *
    from parallelppdev import *     #only ppdev for now
elif os.name == 'java':
    from paralleljava import *
else:
    raise "Sorry no implementation for your platform available."

#no "mac" implementation. someone want's to write it? i have no access to a mac.
