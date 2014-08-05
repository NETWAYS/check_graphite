check_grapite.py
================
A nagios plugin to check on graphite graphs

###Installation Instructions:
-Run it

###Usage Instructions:
  -g [graph name]   Name of the graph as given by Graphite  
  -H [URL]          URL to the page Graphite is running on,
                    in the form of "http://url.top/"  
  -w [u]Wthreshold  Define warning threshold, only int or float  
                    use 'u' to warn if value goes below threshold  
  -c [u]Cthreshold  Define critical threshold, only int or float  
                    use 'u' to warn if value goes below thrshold  
  -h                Print usage  
  --help            Display this site  
  **Example usage**:  
  `./check_graphite.py -g carbon.agents.cpuUsage -H http://example.com/ -w 85.4 -c u0`  
Poll the graph carbon.agents.cpuUsage on example.com, warning if it is over 85.4
  and sending a critical if it is below 0.
