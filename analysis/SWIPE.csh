#!/bin/tcsh
#===============================================================================
#+
# NAME:
#   SWIPE
#
# PURPOSE:
#   Unpack a new SW database, and restore it ready for interrogation. 
#
# COMMENTS:
#
# INPUTS:
#   dbfile            Gzipped tarball from Adler.
#
# OPTIONAL INPUTS:
#   -h --help         Print this header
#
# OUTPUTS:
#
# EXAMPLES:
#
#   SWIPE.csh spacewarp_2013-05-07.tar.gz
#
# BUGS:
#
# REVISION HISTORY:
#   2013-05-07  started: Marshall (Oxford)
#-
# ==============================================================================

set help = 0
set survey = 'CFHTLS'

while ( $#argv > 0 )
   switch ($argv[1])
   case -h:        
      shift argv
      set help = 1
      breaksw
   case --{help}:        
      shift argv
      set help = 1
      breaksw
   case *:        
      set dbfile = $argv[1]
      shift argv
      breaksw
   endsw
end

if ($help) then
  more $0
  goto FINISH
endif

# ----------------------------------------------------------------------

echo '================================================================================'
echo '                   SWIPE: Space Warps Database Preparation                      '
echo '================================================================================'

echo "SWIPE: restoring database from $dbfile"

# Assume we are in a sensible directory, and just unpack here:
tar xvfz $dbfile

set db = $dbfile:r:r
echo "SWIPE: database json and bson files stored in $db"


# First need to kill any old servers:
echo "SWIPE: killing any mongo server already running"
set pid = `ps -e | grep 'mongod --dbpath' | \
                   grep -v 'grep' | head -1 | awk '{print $1}'`
if ($#pid > 0) then 
    kill $pid
    \rm -rf mongo
endif

# Start new mongo server in its own directory, out of the way:
echo "SWIPE: starting new server in directory mongo..."
set logfile = .${db}_mongostartup.log
mkdir -p mongo
chdir mongo
mongod --dbpath . >& ../$logfile &
# mongod --dbpath . &
chdir ..
sleep 10
echo "SWIPE: mongo startup log written to $logfile"

# Did it work?
set fail = `grep "couldn't connect to server" $logfile | head -1 | wc -l`
if ($fail) then
  echo "SWIPE: ERROR: failed to start server, exiting"
  goto FINISH
endif


# Now restore the new database:
echo "SWIPE: mongorestoring into database 'ouroboros_staging'"

set logfile = .${db}_mongorestore.log
mongorestore --drop --db ouroboros_staging $db >& $logfile
echo "SWIPE: mongorestore log stored in $logfile"

# Did it work?
set fail = `grep "couldn't connect to server" $logfile | head -1 | wc -l`
if ($fail) then
  echo "SWIPE: ERROR: failed to restore database, exiting"
  goto FINISH
endif

echo "SWIPE: new database all ready to be read by SWAP."

echo '================================================================================'

# ==============================================================================
FINISH:
