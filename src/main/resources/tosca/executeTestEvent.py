#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

import sys

from java.lang import Exception
from java.io import PrintWriter
from java.io import StringWriter

from com.xebialabs.overthere import CmdLine, ConnectionOptions, OperatingSystemFamily, Overthere
from com.xebialabs.overthere.local import LocalConnection
from com.xebialabs.overthere.util import CapturingOverthereExecutionOutputHandler, OverthereUtils

if toscaServer is None:
    print "No server provided."
    sys.exit(1)

execServiceEndpoint = toscaServer['url']
toscaCiClientHome = openShiftServer['toscaCiClientHome']
toscaCmd = "java -jar %s/ToscaCIJavaClient.jar" % (toscaCiClientHome)
execResultFormat = 'junit'
configFile = "%s/config.xml" % (toscaCiClientHome)

script = """
%s -e %s -c %s -t %s
""" % (toscaCmd, execServiceEndpoint, configFile, execResultFormat)

stdout = CapturingOverthereExecutionOutputHandler.capturingHandler()
stderr = CapturingOverthereExecutionOutputHandler.capturingHandler()

scriptExtension = '.sh'
try:
    connection = LocalConnection.getLocalConnection()
    targetScript = connection.getTempFile('runtoscaciclient', scriptExtension)
    OverthereUtils.write( String(script).getBytes(), targetScript)
    targetScript.setExecutable(True)
    cmd = CmdLine.build( targetScript.getPath() )
    connection.execute( stdout, stderr, cmd )
except Exception, e:
    stacktrace = StringWriter()
    writer = PrintWriter( stacktrace, True )
    e.printStackTrace(writer)
    stderr.hadleLine(stacktrace.toString())

# set variables
output = stdout.getOutput()
error = stderr.getOutput()

if len(output) > 0:
    print "```"
    print output
    print "```"
else:
    print "----"
    print "#### Output:"
    print "```"
    print output
    print "```"

    print "----"
    print "#### Error stream:"
    print "```"
    print error
    print "```"
    print

    sys.exit(response.rc)
    
    
params = {'url': toscaServer['url'], 'username': username, 'password': password, 'proxyHost': toscaServer['proxyHost'],
          'proxyPort': toscaServer['proxyPort']}

tosca_event_url = '/tcrest/toscacommander/' + task.getPythonScript().getProperty(
    "workspace") + '/object/' + task.getPythonScript().getProperty("testEventId") + '/task/ExecuteNow'

response = HttpRequest(params).get(tosca_event_url, contentType='application/json')

if response.status == 200:
    print "Test event with Id %s has been executed in TOSCA." % (task.getPythonScript().getProperty("testEventId"))
else:
    print "Something went wrong, please make sure workspace %s is not locked by any other user." % (
    task.getPythonScript().getProperty("workspace"))
    sys.exit(1)
