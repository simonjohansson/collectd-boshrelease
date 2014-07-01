#!/usr/bin/python

# Quick script to query monit jobs and turn them into sensu alerts.
# Matt Johnson <matjohn2@cisco.com>

import subprocess
import json
import socket 
from pprint import pprint

#Dictionary for holding monit jobs
monit_jobs = {}

#Monit agent IP
monit_ip = '127.0.0.1'
#Monit agent Port
monit_port = 3030

#Monit status code when in a healthy state
ok_marker = 'running'

#Debug Counters
debug_count_good = 0
debug_count_bad = 0


#FUNC Check jobs for error
def check(values):
    for k in values:
        v = values[k]

        if v == ok_marker:
         #Job is fine
         formatgood(k)

        else:
         #Job is Baaaad
         formatbad(k) 

#Format a good job alert
def formatgood(k):
 global debug_count_good
 debug_count_good += 1
 response ={'output':'Monit Job '+ k +' is OK', 'name':k, 'handlers':["twitter"], 'subscribers': 'cfmonit', 'status':0, 'type':'monit'}
 sensujson = json.dumps(response)
 sendsensu(sensujson)

#Format a bad job alert 
def formatbad(k):
  global debug_count_bad
  debug_count_bad += 1 
  #input 'k' is the monit job name
  monit_single_process = subprocess.Popen("/var/vcap/bosh/bin/monit status | grep -A3 "+k, shell=True,stdout=subprocess.PIPE)
  output = monit_single_process.stdout.read().replace('\n',' ')
  response = {'output':output, 'name':k, 'handlers':["twitter"], 'subscribers': 'cfmonit', 'status':2, 'type':'monit'} 
  sensujson = json.dumps(response)
  sendsensu(sensujson)

#Send the alert to Sensu
def sendsensu(json):
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((monit_ip,monit_port))
  s.send(json)
  s.close()

####################################
#MAIN - Get monit summary and process
#####################################
monit = subprocess.Popen('/var/vcap/bosh/bin/monit summary', shell=True, stdout=subprocess.PIPE)
for line in monit.stdout:
      if "Process" in line:
          p,k,v = line.split("'",3)
          v = v.strip()
          k = k.strip()
          monit_jobs[k] = v

check(monit_jobs)
print('DEBUG: '+ str(debug_count_good) + ' Good Jobs and ' +str(debug_count_bad) + ' errored jobs sent to sensu client at ' + monit_ip + ':' + str(monit_port))
