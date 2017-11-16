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

execServiceEndpoint = toscaServer['endpoint']
toscaCiClientHome = toscaServer['toscaCiClientHome']
toscaCmd = "java -jar %s/ToscaCIJavaClient.jar" % (toscaCiClientHome)
execResultFormat = 'junit'
#configFile = "%s/config.xml" % (toscaCiClientHome)

stdout = CapturingOverthereExecutionOutputHandler.capturingHandler()
stderr = CapturingOverthereExecutionOutputHandler.capturingHandler()

scriptExtension = '.sh'

try:
    connection = LocalConnection.getLocalConnection()

    ciTestExecutionConfig="""
    <?xml version="1.0" encoding="utf-16" ?>
    <testConfiguration>
        <TestEvents>
            <TestEvent>%s</TestEvent>
        </TestEvents>
    </testConfiguration>
    """ % (testEvent)

    ciTestConfig = connection.getTempFile('TestConfig', ".xml")
    OverthereUtils.write( String(ciTestExecutionConfig).getBytes(), ciTestConfig)
    
    script = """
    %s -e %s -c %s -t %s
    """ % (toscaCmd, execServiceEndpoint, ciTestConfig.getPath(), execResultFormat)

    print script

    targetScript = connection.getTempFile('runtoscaciclient', scriptExtension)
    OverthereUtils.write( String(script).getBytes(), targetScript)
    targetScript.setExecutable(True)

    cmd = CmdLine.build( targetScript.getPath() )
    connection.execute( stdout, stderr, cmd )

except Exception, e:
    stacktrace = StringWriter()
    writer = PrintWriter( stacktrace, True )
    e.printStackTrace(writer)
    stderr.handleLine(stacktrace.toString())

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