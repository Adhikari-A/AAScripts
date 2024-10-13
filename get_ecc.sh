#!/bin/bash
echo "=================================================================="
echo "'get_ecc.sh'"
echo "=================================================================="

bam_dir=$1
tskip=$2
dmin=$3
fb=$4

if [ -d "$bam_dir" ]
then
  if [ -n "$tskip" ] && [ -n "$dmin" ] && [ -n "$fb"  ]
  then
    #sgird_dir=$1
    if [[ "$bam_dir" =~ /$ ]]
    then
      bam_dir="${bam_dir%?}"
    fi
    echo "bam directory: $bam_dir"
    bam_par_file=$(ls "$bam_dir"/*.par)
    bam_mpd_file=$(ls "$bam_dir"/"moving_puncture_distance.lxyz"* \
                                                        | grep -E '[0-9]{1,2}$')
    if [ -f "$bam_par_file" ] && [ -f "$bam_mpd_file" ]
    then
      com=""
      if [ "$fb" = "-FB"  ]
      then
        echo "Using force balance."
        echo 
        com="EccRed.py"
      elif [ "$fb" = "-noFB"  ]
      then
        echo "Not using force balance."
        echo 
        com="EccRed_noForceBal.py"
      fi
        
      if [ -n "$com"  ]
      then
        echo "bam par file:"
        echo "$bam_par_file"
        echo "bam moving puncture distance file:"
        echo "$bam_mpd_file"
        remove_repeat.py "$bam_mpd_file" "-t" "8"
        bam_mpd_file="${bam_mpd_file}_rr.txt"
        if [ -f "$bam_mpd_file" ]
        then
          echo "Cleaned file:"
          echo  "$bam_mpd_file"
          com="$com $bam_mpd_file"
        
          echo
          sgrid_dir=$(grep "sgrid_datadir" "$bam_par_file" | awk '{print $NF}' \
                                                       | tr -d '\r\n') # delete stupid stuff
          sgrid_dir=$(echo "$sgrid_dir" | tr -d '\n')
          echo "sgrid dir:"
          echo "$sgrid_dir"
          if [ -d "$sgrid_dir"  ]
          then
            sgrid_bns_file=$(ls "$sgrid_dir"/"BNS"*.txt)
            if [ -f "$sgrid_bns_file" ]
            then
              echo "Sgrid BNS data properties file:"
              echo "$sgrid_bns_file"
              echo
   	  
              o=$(grep "Omega" "$sgrid_bns_file" | tail -1 | awk '{print $NF}'\
                                                 | tr -d '\r\n') # delete stupid stuff
              if [ -n "$o"  ]
              then
                echo "Omega = $o"
              
                m=$(grep "M_ADM" "$sgrid_bns_file" | tail -1 | awk '{print $NF}'\
                                                 | tr -d '\r\n') # delete stupid stuff
                if [ -n "$m" ]
                then
                  echo "M_ADM = $m"
                  echo "tskip = $tskip"
                  echo "dmin = $dmin"
                  echo 
                  com="$com --Mass $m --Omega $o --tskip $tskip --dmin $dmin"
                  echo "Eccentricity reduction command:"
                  echo "$com"
                  echo
                  ecc_out_file="${bam_dir}.ecc_d.ts${tskip}.dm${dmin}.txt"
                  echo "Redirecting output to file:"
                  echo "$ecc_out_file"
                  $com > "$ecc_out_file"  
                  echo
                  echo "Fitting result:"
                  echo "-------------------------------------------"
                  tail "$ecc_out_file" 
                  echo "-------------------------------------------"
                  echo 
                  echo "Plotting with tgraph.py:"
                  tgr="tgraph.py $ecc_out_file -c 1:3 $ecc_out_file"
                  echo "$tgr"
                  $tgr
                else
                  echo "Could not find Omega in BNS data properties file. :("
                fi
              else
                echo "Could not find Omega in BNS data properties file. :("
              fi

            else
              echo "Sgrid BNS data properties file not found."
            fi
          else
            echo "Data dir for sgrid not found."
          fi
        else
          echo "Cleaning moving puncture distance file went wrong. :("
        fi
      else
        echo "Force balance flag set wrong. :("
      fi
    else
      echo "Par file or moving puncture distance file missing in bam dir."
    fi
  else
    echo "Either tskip or dmin of force balance option missing missing. :("
  fi
else
  echo "Usage:"
  echo "get_ecc.sh bam_dir tskip dmin force_balance_option"
  echo
  echo "force_balance_option:"
  echo "  -FB   : use Force Balance"
  echo "  -noFB : don't use Force Balance"
  echo
  echo "Assumes exists of properly set following symbolic links:"
  echo "  EccRed_noForceBal.py"
  echo "  EccRed.py"
  echo "  remove_repeat.py"
  echo "  tgraph.py"
fi  

echo "=================================================================="
echo "Exiting program."
echo "=================================================================="
