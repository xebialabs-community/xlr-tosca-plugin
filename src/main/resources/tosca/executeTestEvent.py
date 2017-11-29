#
# Copyright 2017 XEBIALABS
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#


from  java.util import UUID
from org.apache.commons.mail import EmailException, SimpleEmail, DefaultAuthenticator, HtmlEmail
import time, sys
import xml.etree.ElementTree as ET

from java.util import Date
from java.util import GregorianCalendar
from javax.xml.datatype import DatatypeConfigurationException
from javax.xml.datatype import DatatypeFactory
from javax.xml.datatype import XMLGregorianCalendar


if toscaServer is None:
    print "No server provided."
    sys.exit(1)

if emailTestResults == True :
    if smtpServer is None :
        print "No SMTP server provided"
        sys.exit(1)

SOCKET_TIMEOUT = 30000 # 30s

def sendEmail (message):
    email = HtmlEmail()
    email.setHostName(smtpServer['host'])
    email.setSmtpPort(smtpServer['port'])
    if smtpServer['useTLS'] == True :
        email.setSSLOnConnect(True)
    if smtpServer['username']:
       email.setAuthentication(smtpServer['username'], smtpServer['password'])
       email.setSocketConnectionTimeout(SOCKET_TIMEOUT)
       email.setSocketTimeout(SOCKET_TIMEOUT)

    try:
        email.setFrom(smtpServer['fromAddress'])
        for toAddress in toAddresses.split(','):
            email.addTo(toAddress)
        if ccAddresses:
            for ccAddress in ccAddresses.split(','):
                email.addCc(ccAddress)
        #if bccAddresses:
        #    for bccAddress in bccAddresses.split(','):
        #        email.addBcc(bccAddress)
        email.setSubject(subject)
        email.setHtmlMsg(message)
        email.send()
    except EmailException, e:
        print 'ERROR: Unable to send notification due to:', e
        sys.exit(1)  

clientId = UUID.randomUUID()
dt           = Date()
gregCalendar = GregorianCalendar()
gregCalendar.setTime(dt)
startTime    = DatatypeFactory.newInstance().newXMLGregorianCalendar(gregCalendar)

execTestEventContent= """
  <s:Envelope xmlns:s='http://schemas.xmlsoap.org/soap/envelope/'>
  <s:Body>
  <DistributeCiTestEvents xmlns='Tricentis.DistributionServer.ServiceInterface.Services'>
   <distributeCiTestEventsRequest xmlns:a='http://schemas.datacontract.org/2004/07/Tricentis.DistributionServer.ServiceInterface.Data.Manager' 
     xmlns:i='http://www.w3.org/2001/XMLSchema-instance'><a:AgentConfiguration i:nil='true' xmlns:b='http://schemas.microsoft.com/2003/10/Serialization/Arrays'/>
    <a:CiClientId>%s</a:CiClientId>
    <a:CiClientTimeout>10800000</a:CiClientTimeout>
    <a:EventNames xmlns:b='http://schemas.microsoft.com/2003/10/Serialization/Arrays'>
      <b:string>%s</b:string>
    </a:EventNames>
    <a:PollingInterval>300000</a:PollingInterval>
    <a:StartTime>%s</a:StartTime>
   </distributeCiTestEventsRequest>
  </DistributeCiTestEvents>
</s:Body>
</s:Envelope>
""" % (clientId, testEvent, startTime)

pollResultsContent = """
<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' 
xmlns:tric='Tricentis.DistributionServer.ServiceInterface.Services'
 xmlns:tric1='http://schemas.datacontract.org/2004/07/Tricentis.DistributionServer.ServiceInterface.Data.Manager'>
   <soapenv:Header/>
   <soapenv:Body>
      <tric:PollCiTestEventsResults>
         <tric:pollCiTestEventsResultsRequest>
            <tric1:CiClientId>%s</tric1:CiClientId>
         </tric:pollCiTestEventsResultsRequest>
      </tric:PollCiTestEventsResults>
   </soapenv:Body>
</soapenv:Envelope>
""" % (clientId)


ns={'t':'Tricentis.DistributionServer.ServiceInterface.Services', 'a':'http://schemas.datacontract.org/2004/07/Tricentis.DistributionServer.ServiceInterface.Data.Manager','b':'http://schemas.datacontract.org/2004/07/Tricentis.DistributionServer.ServiceInterface.Data.Monitor'}

headers		= {'SOAPAction':'Tricentis.DistributionServer.ServiceInterface.Services/IManagerService/DistributeCiTestEvents'}
request		= HttpRequest(toscaServer)
response	= request.post(toscaServer['apiUrl'], execTestEventContent, contentType = 'text/xml', headers = headers)

if response.status == 200:
   print "Requested test event distribution for Id: %s" % (clientId)
else:
    print 'Failed to trigger distribution for Id: %s' % (clientId)
    print response.headers, '\n'
    print response.status, '\n'
    print response.response, '\n'
    sys.exit(1)

headers = {'SOAPAction':'Tricentis.DistributionServer.ServiceInterface.Services/IManagerService/PollCiTestEventsResults'}
while (True):
    response = request.post(toscaServer['apiUrl'], pollResultsContent, contentType = 'text/xml', headers = headers)
    if response.status == 200 :
        respBody =  response.response
        tree =  ET.fromstring(respBody)
        execFinished = tree.find('.//t:PollCiTestEventsResultsResponse/t:PollCiTestEventsResultsResult/a:ExecutionFinished', ns).text
        if execFinished == "false":
            print "Execution still in progress for id: %s" % (clientId), '\n'
            time.sleep(300)
        elif execFinished == "true":
            result = response.response
            break 
        else:
            print response.headers, '\n'
            print response.status, '\n'
            print response.response, '\n'
            sys.exit(1)
    else:
        print response.headers, '\n'
        print response.status, '\n'
        print response.response, '\n'
        sys.exit(1)


# Parse the results

allPassed = True
passedCount = 0
failedCount = 0
resultTree = ET.fromstring(result)
distributionEntries = resultTree.find('.//t:PollCiTestEventsResultsResponse/t:PollCiTestEventsResultsResult/a:DistributionEvents/b:MonitorDistributionEvent/b:MonitorDistributionItems/b:MonitorDistributionItem/b:MonitorDistributionList/b:MonitorDistributionEntries', ns)

testCaseStatuses = {} 
for distributionEntry in distributionEntries:
    testCaseStatus = distributionEntry.find('./b:TestResult',ns).text
    testCaseName = distributionEntry.find('./b:Name',ns).text
    testCaseStatuses[testCaseName] = testCaseStatus
    if testCaseStatus == 'Passed':
       passedCount += 1
    else:
        failedCount += 1
        allPassed = False

passedTestCaseCount = passedCount
failedTestCaseCount = failedCount
totalTestCases = passedTestCaseCount + failedTestCaseCount
thresholdVal = round(float(passedTestCaseCount * 100)/float(totalTestCases),2)

statusString = ''
if emailTestResults == True :
    resultsBody = 'Test event: <b>%s</b> execution results in release %s<br><br>' % (testEvent,release.title)
    subject += ' - %s%s' % (thresholdVal, '%')
    failedResults ='<table>'
    passedResults ='<table>'
    for key in testCaseStatuses :
        if testCaseStatuses[key] == 'Passed' :
            passedResults += '<tr><td>%s</td><td><font color="green">%s</font><td></tr>' % (key, testCaseStatuses[key])
        else:
            failedResults += '<tr><td>%s</td><td><font color="red">%s</font><td></tr>' % (key, testCaseStatuses[key])

    if failedTestCaseCount == 0:
        failedResults = '<tr><td>None</td></tr>'
    if passedTestCaseCount == 0:
        passedResults = '<tr><td>None</td></tr>'

    failedResults +='</table>'
    passedResults +='</table>'

    resultsBody += '<b>Failed Test Cases</b>'
    resultsBody += failedResults 
    resultsBody += '<br>'
    resultsBody += '<b>Passed Test Cases</b>'
    resultsBody += passedResults

    sendEmail(resultsBody)


if not allPassed:
    if failTask == True : 
        print 'Not all test cases passed'
        sys.exit(1) 
    else:
        if thresholdVal < float(desiredThreshold) :
            print 'Success rate of %s is below desired value %s' % (thresholdVal, desiredThreshold)
            sys.exit(1) 
        else:
          print 'Passed with some failures'



