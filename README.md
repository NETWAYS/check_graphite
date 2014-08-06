check_grapite.py
================
An icinga2 plugin to check on graphite graphs

###Installation Instructions:
-Run it

###Usage Instructions:  
  -g [graph name]      Name of the graph as given by Graphite

  -H [URL]             URL to the page Graphite is running on,
                       in the form of "http://url.top/"
                       Default is "http://localhost:80/"

  -w [[u]Wthreshold]  Define warning threshold, only int or float
                       use 'u' to warn if value goes below threshold

  -c [[u]Cthreshold]   Define critical threshold, only int or float
                       use 'u' to warn if value goes below thrshold
  
  -t [time frame]      Get data for the last X [d]ays/[h]ours/[m]inutes
                       Default is 24 hours
  
  -m [mode]            Declare mode
                       0: Default mode
                       1: Needs -T [threshold] option, counts the time the
                          graph is over your threshold. Can be combined
                          with all other options
   
  -h                   Print usage

  --help               Display this site

  Example usage:
  ./check_graphite -g carbon.agents.cpuUsage -H http://example.com/ -w 85.4 -c u0 -t 3d
  Poll the graph carbon.agents.cpuUsage on example.com for the last three days, 
  warning if it is over 85.4 and sending a critical if it is below 0.

###Output
The output will be formatted the following way:
mode dependant|most recent value;warning threshold;critical threshold;
max value;min value;average value;sum of all values;time frame

