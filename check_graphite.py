#!/usr/bin/python2
import json
import requests
import getopt
import sys

def main():
  #parse options
  vars = {}
  try:
    opts, args = getopt.getopt(sys.argv[1:], "g:w:c:u:h", ["help"])
  except getopt.GetoptError as err:
    print str(err)
    usage()
    return 3
  for o, a in opts:
    if o == "-h":
      usage()
      break
    if o == "--help":
      showVerboseHelp()
      return 3
    vars[o[1]] = a
  
  mustBeOptions = ['g','c','w','u']
  for op in mustBeOptions:
    if op not in vars:
      usage()
      return 3
  
  data = getGraph(vars['g'], vars['u'])
  if data[2] == 0:
    print "Error on handeling the request"
    return 3

  result = handleThreshold(data[0], vars['w'], vars['c'])

  if result == 'ERROR':
    print "Invalid Thresholds"
    return 3

  output = result+'|'+str(data[0])+';'+str(data[1])
  print output
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

  -u [URL]          URL to the page Graphite is running on,
                    in the form of "http://url.top/"

  -w [u]Wthreshold  Define warning threshold, only int or float
                    use 'u' to warn if value goes below threshold

  -c [u]Cthreshold  Define critical threshold, only int or float
                    use 'u' to warn if value goes below thrshold

  -h                Print usage

  --help            Display this site

  Example usage:
  '''+sys.argv[0]+''' -g carbon.agents.localhost_localdomain-a.cpuUsage -u http://example.com/ -w 85.4 -c u0
  Poll the graph carbon.agents.localhost_localdomain-a.cpuUsage on example.com warning if it is over 85.4
  and sending a critical if it is below 0.
  '''

#get latest changed data, return (x,y,0) on error
def getGraph(name, url):
  try:
    r = requests.get(url+'render?target='+name+'&format=json')
  except:#requests.exceptions.RequestException as e:
    return (0,0,0)

  js = json.loads(r.text)
  #Find latest entry
  #entry = (data, time)
  entry = ()
  if js == []:
    return (0,0,0)

  for p in js[0]["datapoints"]:
    if p[0] != None:
      entry = (p[0], p[1], 1)

  if entry != ():
    return entry
 
  return (0,js[0]["datapoints"][-1],1)

def handleThreshold(data, w, c):
  #test on critical first
    if c[0] == 'u':
      try: 
        float(c[1:])
        if data < int(c[1:]):
          return 'CRITICAL'
      except ValueError:
        return 'ERROR'
    else:
      try:
        float(c)
        if data > float(c):
          return 'CRITICAL'
      except ValueError:
        return 'ERROR'
    
    if w[0] == 'u':
      try:
        float(w[1:])
        if data < int(w[1:]):
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
  print 'Usage: \n'+sys.argv[0] + ' -g [Graph] -u [url] -w [u][Wthreshold] -c [u][Cthreshold] [-h, --help]'

if __name__ == "__main__":
  main()
