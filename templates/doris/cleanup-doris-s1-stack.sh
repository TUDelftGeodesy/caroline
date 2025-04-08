#!/bin/bash

folder_to_clean=**coregistration_directory**

echo 'Cleaning '$folder_to_clean

echo 'Removing...'
echo 'log files'
rm -rf $folder_to_clean/stack/job_*.log
echo 'cint.raw'
rm -rf $folder_to_clean/stack/2*/cint.raw
echo 'coherence.raw'
rm -rf $folder_to_clean/stack/2*/coherence.raw
burst=0
while [ $burst -le 9 ]
do
echo 's*/b*'$burst'/cint.raw'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/cint.raw
echo 's*/b*'$burst'/cint_srp.raw'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/cint_srp.raw
echo 's*/b*'$burst'/coherence.raw'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/coherence.raw
echo 's*/b*'$burst'/dac*'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/dac*
echo 's*/b*'$burst'/demcrop.raw'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/demcrop.raw
echo 's*/b*'$burst'/*.ras'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/inter*.ras
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/*.ras
#echo 's*/b*'$burst'/rsmp_orig*'
#rm -rf $folder_to_clean/stack/2*/s*/b*$burst/rsmp_orig*
#echo 's*/b*'$burst'/slave_rsmp_reramped.raw'
#rm -rf $folder_to_clean/stack/2*/s*/b*$burst/slave_rsmp_reramped.raw
echo 's*/b*'$burst'/slave_iw_*deramped.raw'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/slave_iw_*deramped.raw
echo 's*/b*'$burst'/master_slave.crd'
rm -rf $folder_to_clean/stack/2*/s*/b*$burst/master_slave.crd
burst=$(( $burst + 1))
done

echo 'Finished'
