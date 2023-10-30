#!/usr/bin/python

from datetime import datetime
import sys, cgi, os

# get form data from JavaScript
formdata = cgi.FieldStorage()

# get workerId and dataString (JSON stringified array)
ID = formdata.getvalue('ID', 'ID_NULL')
dataString = formdata.getvalue('dataString', 'dataString_NULL')

# get string of current date and time
now = str(datetime.now())[:19].replace(":","-")

# write file in /data/
outputFilename = './data/' + ID + '_' + now + '.txt'
with open(outputFilename, 'w') as outputFile:
    outputFile.write(dataString)

# print header and 'Done.' message
sys.stdout.write('Content-type: text/plain; charset=UTF-8\n\n')
sys.stdout.write('Done.')