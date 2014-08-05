#############################################################################
#
# Copyright (C) 2014 by NETWAYS GmbH
#                  <support@netways.de>
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
#!/usr/bin/env python

try: 
  import urllib2
except:
  import urllib as urllib2
import getopt
import sys


def main():
  #parse options
  cars = {'w':None,'c':None}
  
  try:
    opts, args = getopt.getopt(sys.argv[1:], "g:w:c:H:h", ["help"])
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
  
  mustBeOptions = ['g','H']
  for op in mustBeOptions:
    if op not in cars:
      usage()
      return 3

  data = getGraph(cars['g'], cars['H'])
  if data[2] == 0:
    print "Error on handeling the request"
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
  
  print output.rstrip('\n')
  if result == 'CRITICAL':
    return 2
  if result == 'WARNING':
    return 1
  else:
    return 0

def showVerboseHelp():
  print sys.argv[0]+' - Help'
  usage()
  print '''\
  -g [graph name]   Name of the graph as given by Graphite

  -H [URL]          URL to the page Graphite is running on,
                    in the form of "http://url.top/"

  -w [u]Wthreshold  Define warning threshold, only int or float
                    use 'u' to warn if value goes below threshold

  -c [u]Cthreshold  Define critical threshold, only int or float
                    use 'u' to warn if value goes below thrshold

  -h                Print usage

  --help            Display this site

  Example usage:
  '''+sys.argv[0]+''' -g carbon.agents.cpuUsage -H http://example.com/ -w 85.4 -c u0
  Poll the graph carbon.agents.cpuUsage on example.com, warning if it is over 85.4
  and sending a critical if it is below 0.
  '''

#get latest changed data, return (x,y,0) on error
def getGraph(name, url):
  try:
    r = urllib2.urlopen(url+'render?target='+name+'&format=raw')
  except:#requests.exceptions.RequestException as e:
    return (0,0,0)

  text  = r.read()
  #Find latest entry
  #entry = (data, time,sucess)
  entry = ()
  if text == None:
    return (0,0,0)
  
  text = text.split(',')
  text[-1] = text[-1][:-1] #last entry has a newline
  ctime = int(text[1]) #Starting time
  step = int(text[3][0])
  t = text[3].split('|')
  text[3] = t[-1] #first entry has a '|'

  #traverse and keep latest entry
  for word in text:
    if word != 'None':
      entry = (word, ctime, 1)
    ctime += step

  if entry != ():
    return entry

  #if no entry is found return 0 as value und time of latest actualisiation
  return (0,ctime,1)

def handleThreshold(data, w, c):
  #test on critical first, in case critical <= warning
  #nobody will see those, so casting to flaot instead
  #of int should be fine
  if c != None:
    if c[0] == 'u':
      try: 
        float(c[1:])
        if data < float(c[1:]):
          return 'CRITICAL'
      except ValueError:
        return'ERROR'
    else:
      try:
        float(c)
        if data > float(c):
          return 'CRITICAL'
      except ValueError:
        return 'ERROR'
  if w != None:  
    if w[0] == 'u':
      try:
        float(w[1:])
        if data < float(w[1:]):
          return 'WARNING'
      except ValueError:
        return 'ERROR'
    else:
      try: 
        float(w)
        if data > float(w):
          return 'WARNING'
      except ValueError:
        return 'ERROR'
    
  return 'OK'
      
def usage():
  print 'Usage: \n'+sys.argv[0] + ' -g [Graph] -H [url] -w [u][Wthreshold] -c [u][Cthreshold] [-h, --help]'

if __name__ == "__main__":
  sys.exit(main())
