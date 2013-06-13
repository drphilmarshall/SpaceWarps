#!/bin/tcsh
#===============================================================================
#+
# NAME:
#   SWAPSHOP
#
# PURPOSE:
#   Run SWAP.py multiple times on a database, until all classifications
#   are in - and then collate outputs for use by SWITCH etc.
#
# COMMENTS:
#
# INPUTS:
#
# OPTIONAL INPUTS:
#   -h --help         Print this header
#   -f --startup      Start afresh. Def = continue from update.config
#   -s --survey name  Survey name (used in prefix of everything)
#   -t --test N       Only run SWAP.py N times
#   -a --animate      Make animated plot of subject trajectories
#   -d --download     Download images of candidates, false +ves etc
#
# OUTPUTS:
#
# EXAMPLES:
#
#   SWAPSHOP.csh
#
# BUGS:
#
# REVISION HISTORY:
#   2013-05-09  started: Marshall (Oxford)
#-
# ==============================================================================

set help = 0
set survey = 'CFHTLS'
set N = 'infinity'
set startup = 0
set animate = 0
set download = 0
set fast = 0

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
   case -f:        
      shift argv
      set startup = 1
      breaksw
   case --{startup}:        
      shift argv
      set startup = 1
      breaksw
   case -a:        
      shift argv
      set animate = 1
      breaksw
   case --{animate}:        
      shift argv
      set animate = 1
      breaksw
   case -d:        
      shift argv
      set download = 1
      breaksw
   case --{download}:        
      shift argv
      set download = 1
      breaksw
   case -s:        
      shift argv
      set survey = $argv[1]
      shift argv
      breaksw
   case --{survey}:        
      shift argv
      set survey = $argv[1]
      shift argv
      breaksw
   case -t:        
      shift argv
      set N = $argv[1]
      shift argv
      breaksw
   case --{test}:        
      shift argv
      set N = $argv[1]
      shift argv
      breaksw
   case --{fast}:        
      set fast = 1
      shift argv
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
echo '                    SWAPSHOP: Space Warps Analysis Blitz                        '
echo '================================================================================'

date

echo "SWAPSHOP: running SWAP.py over and over again until all"
echo "SWAPSHOP: classifications in survey '$survey' are analysed"

# ----------------------------------------------------------------------

# First write a startup.config file based on the standard one in swap:

if ($startup) then
    set configfile = startup.config
    cat $SWAP_DIR/swap/$configfile | sed s/SURVEY/$survey/g > $configfile
    echo "SWAPSHOP: start-up configuration stored in $configfile"
else
    set configfile = 'update.config'
    if (! -e $configfile) then
        echo "SWAPSHOP: ERROR: no update.config file to start from."
        goto FINISH
    endif
    echo "SWAPSHOP: continuing using configuration stored in $configfile"
endif

# Save time by only reporting at the end:
if ($fast) then
    sed s/'report: True'/'report: False'/g $configfile > junk
    mv junk $configfile
endif

# ----------------------------------------------------------------------
# Where did we get to? Save the previous batch of retirees for 
# comparison:

set here = $cwd:t

set retirees = ${survey}_${here}_retire_these.txt
set previousretirees = ${survey}_previously_retired.txt

# First time out there aren't any previous retirees:
if (! -e $previousretirees) then
    touch $previousretirees
endif
# Usual state of directory is that $retirees shows what was just 
# retired, while $previousretirees is the total retired so far, not
# including the latest batch.
# -> Now we have to concatenate them before we overwrite $retirees.
if (-e $retirees) then
    cat $retirees >> $previousretirees
    # Protect against idiocy:
    cat $previousretirees | sort | uniq >! junk
    mv junk $previousretirees
endif

set NPR = `cat $previousretirees | wc -l`

echo "SWAPSHOP: so far we have retired $NPR subjects. Let's do some more!" 

# ----------------------------------------------------------------------

# Get going on the new db:

set more_to_do = 1
set k = 0

while ($more_to_do)
    
    # Stop early if we are just testing:
    if ($k == $N) then
        
        echo 'stopped' > .swap.cookie
    
    else
        # Run SWAP again:
        @ kk = $k + 1
        echo "SWAPSHOP: starting batch number $kk"
        
        SWAP.py  $configfile
    
        # Keep a record of the config we used in this run...
        # That means replacing the new start time in update.config
        # with the actual start time of the latest run:

        set latest = `\ls -dtr ${survey}_????-??-??_??:??:?? | tail -1`
        set now = `echo $latest | sed s/$survey//g | cut -c2-50`
        
        set tomorrow = `grep 'start:' $configfile | \
                        grep -v 'a_few' | cut -d':' -f2-20`
        sed s/$tomorrow/$now/g $configfile > $latest/update.config
        
    endif     
    
    @ k = $k + 1
    
    # See if we should keep going:
    set more_to_do = `grep 'running' .swap.cookie | wc -l`
    if ($more_to_do) set configfile = update.config
    
end

# OK, run SWAP one more time (on last classification again), and 
# write the report:

if ($fast) then
    sed s/'report: False'/'report: True'/g update.config > junk ; mv junk update.config
    echo "SWAPSHOP: starting plotting run"
    SWAP.py  update.config
endif

# Great: we should now have everything we need, in a whole bunch of 
# directories.

# ----------------------------------------------------------------------

# Collate outputs in various ways:

set latest = `\ls -dtr ${survey}_????-??-??_??:??:?? | tail -1`

# - - - - - - - - - - 
# 1) Retirement plan:

# Compare latest grand total with previous list, and take the difference
# to SWITCH:

cat $previousretirees         | sort > old
cat $latest/*retire_these.txt | sort > new
sdiff -s old new | grep -e '<' -e '>'  \
                 | sed s/'<'//g | sed s/'>'//g > $retirees
\rm old new
# Note that we should retire inclusively - if a subject is in the
# previously retired list but not in the latest list, that means it 
# was orginally scheduled for returement, the SWITCH failed, it stayed
# in play, and got voted up again - but that's not what we want. We want
# to be fair to all subjects! Once you cross the line, thats it.


set NR = `cat $retirees | wc -l`

if ($NR > 0) then
    echo "SWAPSHOP: if you want, you can go ahead and retire $NR subjects with"
    echo " "
    echo "          SWITCH.py $retirees > retirement.log &"
    echo " "
else
    echo "SWAPSHOP: no subjects to retire"
endif

# - - - - - - - - - -
# 2) Final report:

set report = ${survey}_${here}_report.pdf
cp $latest/*report.pdf  $report

echo "SWAPSHOP: final report: $report"

# - - - - - - - - - -
# 3) Animated plots:

if ($animate) then

    echo "SWAPSHOP: you can view an animated plot on your browser with (wait for it):"
    echo " "

    # foreach type ( trajectories histories probabilities )
    foreach type ( trajectories )

        set gif = $cwd/${survey}_${here}_${type}.gif

        convert -delay 50 -loop 0 ${survey}_*/*${type}.png $gif

        echo "          file://$gif"
        echo " "

    end

endif

# - - - - - - - - - -
# 4) Image download:

if ($download) then

    foreach type ( candidates \
                   training_false_negatives \
                   training_false_positives )
        mkdir -p $type
        chdir $type
        echo "SWAPSHOP: in folder '$type',"

        set catalog = `\ls ../${latest}/*${type}*txt`
        set N = `cat $catalog | wc -l`
        echo -n "SWAPSHOP: downloading $N images from $catalog..."

        foreach url ( `cat $catalog` )
            set png = $url:t
            set log = .$png:r.log
            wget -O $png "$url" >& $log
            echo -n "."
        end
        echo "SWAPSHOP: ...done."

        chdir ..

    end

endif
    
echo "SWAPSHOP: all done."

date
echo '================================================================================'

# ==============================================================================
FINISH:
