#!/bin/bash

echo "==============================================================="
echo "del_run_data.sh"
echo "==============================================================="

for arg in "$@"
do
  if [ "$fprog" ]  # if program flag has already been found
  then
    prog="$arg" # save prog name
    fprog=""
  fi

  if [ "$fl" ] # if deletion level has been found
  then
    l=$arg
    fl=""
  fi

  if [ "$arg" = "-p" ] # flag to state program name
  then
    fprog="true"
  elif [ "$arg" = "-l" ]
  then
    fl="true"
  fi
done

if [ -z "$prog" ] # no args in commandline
then
  echo "Usage":
  echo "del_run_data.sh -p PROGRAM -l LEVEL_OF_DELETION"
  echo
  echo "PROGRAM can be full name or just first letter."
  echo "Accepted PROGRAM options: nmesh, bam, sgrid."
  echo "Specifications for LEVEL_OF_DELETION by PROGRAM:"
  echo
  echo "-p     -l          files deleted"
  echo "-----------------------------------------------------------------------"
  echo "nmesh   0  ADM* (! ADM_alpha*), *_previous, trK*, mom*, normmom*,"
  echo "           C3GH_H[yz]*, C3GH_Phi*, C3GH_th*, C3GH_cP*, C3GH_gnD*, "
  echo "           C3GH_PinD*, C3GH*[yz].*, GHG_err_C3*, GHG_P*, GHG_gt[xyz]*, "
  echo "           GHG_gyz*, *mean*, *.*Y*, *.*Z*, *.*[XYZ][XYZ]*, "
  echo "           *.xz.*, *.yz.*, x.??.*, y.??.*, z.??.*, timer*, *Wv*,"
  echo "           GRHD_Sy*, GRHD_Sz*, checkpoint-* *vtk*"
  echo
  echo "        1  level 0 + checkpoint*, stdo*, *maxAbs*, GHG_H*"
  echo
  echo "        2  level 0 + 1 + *.*X* (! *.00X*,*.0X*,*.04X*,*.4X*,*.10X*)"
  echo "           *.xyz.*, *.xy.*, *.*t (! *.00t,*.0t,*.04t,*.4t,*.10t,*.t,*.txt)"
  echo
  echo "bam     0  AHmod*, ah*, ADM_mass, ejecta_spheres. Mbar_spheres,"
  echo "           moving_puncture_integrate*, output_r, puncture_properties"
  echo "           rho_mode, stdout.*, timer.* checkpoint.*-*"
  echo
  echo "        1  level 0 + checkpoint.*, *.dat, *.?z*_vtk, alpha*vtk, beta*vtk,"
  echo "           *[012]_vtk, *_v2.*vtk, output_1d"
  echo
  echo "        2  level 0 + 1 + output_[23]d"

elif [ -z "$prog" ] && [ -n "$l" ]
then
  echo "PROGRAM missing."
elif [ -n "$prog" ] && [ -z "$l" ]
then
  echo "LEVEL_OF_DELETION missing."
else
  echo "PROGRAM : $prog"
  echo "LEVEL_OF_DELETION: $l"
  echo "===================================================="
  if [ "$l" -ge 0 ]
  then
    echo "Deleting level 0 files."
    echo "===================================================="
    if [[ "${prog,,}" == n* ]]
    then
      find . -name "ADM*" ! -name "ADM_alpha*" -exec rm -rfv {} +
      find . -name "*_previous" -exec rm -rfv {} +
      find . -name "trK*"  -exec rm -rfv {} +
      find . -name "momx*" -exec rm -rfv {} +
      find . -name "momy*" -exec rm -rfv {} +
      find . -name "momz*" -exec rm -rfv {} +
      find . -name "C3GH_tr*" -exec rm -rfv {} +
      find . -name "C3GH_err*" -exec rm -rfv {} +
      find . -name "normmomx*" -exec rm -rfv {} +
      find . -name "normmomy*" -exec rm -rfv {} +
      find . -name "normmomz*" -exec rm -rfv {} +
      find . -name "C3GH_Hy*" -exec rm -rfv {} +
      find . -name "C3GH_Hz*" -exec rm -rfv {} +
      find . -name "C3GH_Phi*" -exec rm -rfv {} +
      find . -name "C3GH_th*" -exec rm -rfv {} +
      find . -name "C3GH_cP*" -exec rm -rfv {} +
      find . -name "C3GH_gnD*" -exec rm -rfv {} +
      find . -name "C3GH_PinD*" -exec rm -rfv {} +
      find . -name "C3GH*y.*" -exec rm -rfv {} +
      find . -name "C3GH*z.*" -exec rm -rfv {} +
      find . -name "GHG_err_C3*" -exec rm -rfv {} +
      find . -name "GHG_P*" -exec rm -rfv {} +
      find . -name "GHG_gt[xyz]*" -exec rm -rfv {} +
      find . -name "GHG_gyz*" -exec rm -rfv {} +

      find . -name "*mean*" -exec rm -rfv {} +

      find . -name "*.*Y*" -exec rm -rfv {} +
      find . -name "*.*Z*" -exec rm -rfv {} +

      find . -name "*.*[XYZ][XYZ]*" -exec rm -rfv {} +

      find . -name "*.xz.*" -exec rm -rfv {} +
      find . -name "*.yz.*" -exec rm -rfv {} +
      find . -name "x.??.*" -exec rm -rfv {} +
      find . -name "y.??.*" -exec rm -rfv {} +
      find . -name "z.??.*" -exec rm -rfv {} +
      # find . -name "*.xyz.*" -exec rm -rfv {} +

      find . -name "timer*" -exec rm -rfv {} +

      find . -name "*Wv*" -exec rm -rfv {} +

      find . -name "GRHD_Sy*" -exec rm -rfv {} +
      find . -name "GRHD_Sz*" -exec rm -rfv {} +

      find . -name "checkpoint-?" -exec rm -rfv {} +
      find . -name "checkpoint-??" -exec rm -rfv {} +

      find . -name "*vtk*" -exec rm -rfv {} +

      # find . -name "ADM*" -exec rm -rfv {} +
      # find . -name "*_previous" -exec rm -rfv {} +
      # echo "Deleteing nmesh files."
    elif  [[ "${prog,,}" == b* ]]
    then
      find . -name "AHmod*" -exec rm -rfv {} +
      find . -name "ah*" -exec rm -rfv {} +
      find . -name "ADM_mass" -exec rm -rfv {} +
      find . -name "ejecta_spheres" -exec rm -rfv {} +
      find . -name "Mbar_spheres" -exec rm -rfv {} +
      find . -name "moving_puncture_integrate*" -exec rm -rfv {} +
      find . -name "output_r" -exec rm -rfv {} +
      find . -name "puncture_properties" -exec rm -rfv {} +
      find . -name "rho_mode" -exec rm -rfv {} +
      find . -name "stdout.*" -exec rm -rfv {} +
      find . -name "timer.*" -exec rm -rfv {} +
      find . -name "checkpoint.*-*" -exec rm -rfv {} +
    else
      echo "I don't know how to handle output from this program yet."
    fi
    echo "===================================================="
    echo "Done deleting level 0 files."
    if [ "$l" -ge 1 ]
    then
      echo "Deleting level 1 files."
      echo "===================================================="
      if [[ "${prog,,}" == n* ]]
      then
        # echo "Deleteing nmesh files."
        find . -name "checkpoint*" -exec rm -rfv {} +
        find . -name "stdo*" -exec rm -rfv {} +
        find . -name "*maxAbs*" -exec rm -rfv {} +
        find . -name "GHG_H*" -exec rm -rfv {} +
      elif  [[ "${prog,,}" == b* ]]
      then
        find . -name "checkpoint.*" -exec rm -rfv {} +
        find . -name "*.dat" -exec rm -rfv {} +
        find . -name "*.?z*_vtk" -exec rm -rfv {} +
        find . -name "alpha*vtk" -exec rm -rfv {} +
        find . -name "beta*vtk" -exec rm -rfv {} +
        find . -name "*[012]_vtk" -exec rm -rfv {} +
        find . -name "*_v2.*vtk" -exec rm -rfv {} +
        find . -name "output_1d" -exec rm -rfv {} +
      fi
      echo "===================================================="
      echo "Done deleting level 1 files."
    fi
    if [ "$l" -ge 2 ]
    then
      echo "Deleting level 2 files."
      echo "===================================================="
      if [[ "${prog,,}" == n* ]]
      then
        find . -name "*.*X*" \
                      ! -name "*.00X*" \
                      ! -name "*.0X*" \
                      ! -name "*.04X*" \
                      ! -name "*.4X*" \
                      ! -name "*.10X*" \
                    -exec rm -rfv {} +
        find . -name "*.xyz.*" -exec rm -rfv {} +
        find . -name "*.xy.*" -exec rm -rfv {} +
        find . -type f -name "*.*t" \
                      ! -name "*.00t" \
                      ! -name "*.0t" \
                      ! -name "*.04t" \
                      ! -name "*.4t" \
                      ! -name "*.10t" \
                      ! -name "*.t" \
                      ! -name "*.txt" \
                    -exec rm -rfv {} +
      elif  [[ "${prog,,}" == b* ]]
      then
        find . -name "output_[23]d" -exec rm -rfv {} +
      fi
      echo "===================================================="
      echo "Done deleting level 2 files."
    fi
  fi
fi

echo "==============================================================="
echo "Exiting script."
echo "==============================================================="
