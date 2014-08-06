#!/usr/bin/env python
#############################################################################
#
# Copyright (C) 2014 NETWAYS GmbH
#                <support@netways.de>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# Or visit their web page on the internet at http://www.fsf.org.
#
#############################################################################

import urllib2
import getopt
import sys
from decimal import *

def main():
  #parse options
  cars = {'w':None,'c':None}
  
  try:
    opts, args = getopt.getopt(sys.argv[1:], "g:w:c:H:ht:", ["help"])
  except getopt.GetoptError:
    usage()
    return 3
  for o, a in opts:
    if o == "-h":
      usage()
      break
    if o == "--help":
      showVerboseHelp()
      return 3
    cars[o[1]] = a
  
  mustBeOptions = ['H']
  for op in mustBeOptions:
    if op not in cars:
      usage()
      return 3

  #asign defaults
  if 't' not in cars:
    cars['t'] = '24h'
  if 'H' not in cars:
    cars['H'] = 'http://localhost:80/'      

  data = getGraph(cars['g'], cars['H'], cars['t'])
  if data[2] == 1:
    print "Connection error"
    return 3
  elif data[2] == 2:
    print "Faulty data"
    return 3
  elif data[2] == 3:
    print 'Unknown time format'
    return 3
    
  result = handleThreshold(data[0], cars['w'], cars['c'])
  
  if result == 'ERROR':
    print "Invalid Thresholds"
    return 3
  
  output = result+'|time='+str(data[1])+';value='+str(data[0])
  
  if cars['w'] != None:
    output += ';w='+cars['w']
  if cars['c'] != None:
    output +=';c='+cars['c']
  output += ';max='+str(data[2][0])+';min='+str(data[2][1])+';avg='+str(data[2][2])+';sum='+str(data[2][3])+';from='+cars['t']
  
  print output

  if result == 'CRITICAL':
    return 2
  if result == 'WARNING':
    return 1
  else:
    return 0

#get latest changed data, return (x,y,z,0) on success
def getGraph(name, url, time):
  #graphite wants full names
  try:
    int(time[:-1])
  except ValueError:
    return (0,0,3)
  #no negatives please
  if time[0] == '-':
    time = time[1:]
  if time[-1] == 'd':
    time += 'ays'
  elif time[-1] == 'h':
    time += 'ours'
  elif time[-1] == 'm':
    time += 'inutes'
  else:
    return (0,0,3)
  
  url = url+'render?target='+name+'&format=raw&from=-'+time
  try:
    r = urllib2.urlopen(url)
  except urllib2.HTTPError, e: #2.4 can't into as
    #I have no idea what I'm doing
    if e.code != 401:
      return (0,0,1)
    print 'The server asks for authentication'
    user = raw_input('Username: ')
    passwd = getpass.getpass('Password: ')
    passMgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passMgr.add_password(None, url, user, passwd)
    authhandler = urllib2.HTTPBasicAuthHandler(passMgr)
    opener = urllib2.build_opener(authhandler)
    urllib2.install_opener
    r = urllib2.urlopen(url)
  except:
    return (0,0,1)

  text  = r.read()
  #Find latest entry
  #entry = (data,time,MaxMinAvgSum,status)
  entry = ()
  if text == None:
    return (0,0,1)
  
  text = text.split(',')
  try:
    ctime = int(text[1]) #Starting time
    step = int(text[3][0])
    t = text[3].split('|')
    text[3] = t[-1] #first entry has a '|'
    text[-1] = text[-1][:-1] #last entry has a newline
  except ValueError:
    return (0,0,2)

  #traverse, collect values and keep latest entry
  vals = []
  for word in text[3:]:
    if word != 'None':
      vals.append(word)
      entry = (word, ctime)
    ctime += step
  
  if entry != ():
    return (entry[0],entry[1],getMaxMinAvgSum(vals),0)

  #if no entry is found return 0 as value und time of latest actualisiation
  return (0,ctime,(0,0,0,0),0)

def handleThreshold(data, w, c):
  #test on critical first, in case critical <= warning
  #float just yields wrong compare values sometimes
  
  if c != None:
    if c[0] == 'u':
      try: 
        v = Decimal(c[1:])
        d = Decimal(data)
        if d < v:
          return 'CRITICAL'
      except ValueError:
        return'ERROR'
    else:
      try:
        v = Decimal(c)
        d = Decimal(data)
        if d > c:
          return 'CRITICAL'
      except ValueError:
        return 'ERROR'
  if w != None:  
    if w[0] == 'u':
      try:
        v = Decimal(w[1:])
        d = Decimal(data)
        if d < v:
          return 'WARNING'
      except ValueError:
        return 'ERROR'
    else:
      try: 
        t = Decimal(w)
        d = Decimal(data)
        if d > t:
          return 'WARNING'
      except ValueError:
        return 'ERROR'
    
  return 'OK'
      
def getMaxMinAvgSum(data):
  #(max,min,avg,sum)
  a = [Decimal(i) for i in data]
  return (max(a),min(a),sum(a)/len(a),sum(a))
 

def usage():
  print 'Usage: \n'+sys.argv[0] + ' -g [Graph] -H [url] [-w [u][Wthreshold]] [-c [u][Cthreshold]] [-t [time frame]] [-h, --help]'

def showVerboseHelp():
  print '  '+sys.argv[0]+' - Help\n'
  print '''\
  -g [graph name]      Name of the graph as given by Graphite

  -H [URL]             URL to the page Graphite is running on,
                       in the form of "http://url.top/"

  -w [[u][Wthreshold]  Define warning threshold, only int or float
                       use 'u' to warn if value goes below threshold

  -c [[u]Cthreshold]   Define critical threshold, only int or float
                       use 'u' to warn if value goes below thrshold
  
  -t [time frame]      Get data for the last X [d]ays/[h]ours/[m]inutes
                       Default is 24 hours
  
  -h                   Print usage

  --help               Display this site

  Example usage:
  '''+sys.argv[0]+''' -g carbon.agents.cpuUsage -H http://example.com/ -w 85.4 -c u0 -t 3d
  Poll the graph carbon.agents.cpuUsage on example.com for the last three days, 
  warning if it is over 85.4 and sending a critical if it is below 0.
  '''

if __name__ == "__main__":
  sys.exit(main())
