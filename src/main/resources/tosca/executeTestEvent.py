#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
if toscaServer is None:
    print "No server provided."
    sys.exit(1)

if username is None:
    username = toscaServer['username']
if password is None:
    password = toscaServer['password']

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
