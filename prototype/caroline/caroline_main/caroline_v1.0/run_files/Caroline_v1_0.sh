#!/bin/bash

# Defaults
param_file='param_file_Caroline_v1_0.txt'
step_file_version='1.0'

if [ -z "${CAROLINE}" ]; then
	caroline_dir="/project/caroline/Software/caroline-prototype"
else
	caroline_dir="${CAROLINE}"
fi

TRACK_NUMBERS=()
TRACK_DIRECTIONS=()

print_usage () {
	cat <<-EOF
	usage: Caroline_v1_0.sh [-h | --help] [ -c configfile | --config-file=configfile ]

        This script runs Doris, stack stitch, depsy and depsy post

	options:
	  -h, --help         show this help message and exit
          -c, --config-file  specify which config file to use
          -t, --tracks       specify tracks to process

        configfile
          Full path to the configfile for this script. For an example, see:
	  ${caroline_dir}/${param_file}

        tracks
	  Comma separated list of tracks with orbit direction, e.g.:
          s1_dsc_t037,s1_asc_t161

	EOF
}

# Parse commandline arguments with getopt
OPTIONS=$(getopt -o hc:t: --long help,config-file:,tracks: -- "$@")
[ $? -eq 0 ] || {
	print_usage
	exit 1
}
eval set -- "${OPTIONS}"
while true
do
	case "$1" in
		-h|--help)
			print_usage
			exit
			;;
		-c|--config-file)
			shift;
			param_file="${1}"
			;;
		-t|--tracks)
			shift;
			TRACKS="${1}"
			;;
		--)
			shift
			break
	esac
	shift
done

if [ ! -z ${TRACKS} ]; then
	for TRACK in $(echo "${TRACKS}" | sed -e 's/,/ /g')
	do
		TRACK_NUMBER=$(echo ${TRACK} | cut -d_ -f3 | sed -e 's/^t//' | sed -e 's/^0//')
		TRACK_DIRECTION=$(echo ${TRACK} | cut -d_ -f2)
		TRACK_NUMBERS+=("${TRACK_NUMBER}")
		TRACK_DIRECTIONS+=("'${TRACK_DIRECTION}'")
	done

	TRACK_NUMBERS_STRING=${TRACK_NUMBERS[@]}
	TRACK_NUMBERS_STRING=${TRACK_NUMBERS_STRING// /,}
	TRACK_DIRECTIONS_STRING=${TRACK_DIRECTIONS[@]}
	TRACK_DIRECTIONS_STRING=${TRACK_DIRECTIONS_STRING// /,}
fi

echo "Starting full CAROLINE run..."

cpath=`pwd`

AUX=$(echo ${param_file} | cut -d. -f1)
RUN_TS=$(date +%Y%m%dT%H%M%S)
auxiliary_files="config_files_"${AUX}"_"${RUN_TS}

if [ ! -d ${auxiliary_files} ]; then
  mkdir ${auxiliary_files}
fi

echo "Creating auxiliary files..."

# Copy the config file to auxilary files
TMP_CONFIG=$(mktemp ${auxiliary_files}/caroline_config_XXX --suffix=.txt)
cp $param_file ${TMP_CONFIG}
param_file=${TMP_CONFIG}
echo "Running with config file ${param_file}"

# Overwrite track config if tracks are specified on commandline as argument
sed -i "s/^track =.*/track = [$TRACK_NUMBERS_STRING]/" $param_file
sed -i "s/^asc_dsc =.*/asc_dsc = [$TRACK_DIRECTIONS_STRING]/" $param_file

python3 ${caroline_dir}/caroline_v${step_file_version}/bin/setup/create_step_files.py ${param_file} ${cpath} ${auxiliary_files}

do_doris=`cat ${auxiliary_files}/do_doris.txt`
do_deinsar=`cat ${auxiliary_files}/do_deinsar.txt`
do_stitching=`cat ${auxiliary_files}/do_stack_stitching.txt`
do_depsi=`cat ${auxiliary_files}/do_depsi.txt`
do_depsi_post=`cat ${auxiliary_files}/do_depsi_post.txt`
doris_dir=`cat ${auxiliary_files}/doris_directory.txt`
deinsar_dir=`cat ${auxiliary_files}/deinsar_directory.txt`
stitch_dir=`cat ${auxiliary_files}/stitch_directory.txt`
depsi_dir=`cat ${auxiliary_files}/depsi_directory.txt`
shape_dir=`cat ${auxiliary_files}/shape_directory.txt`
doris_AoI_name=`cat ${auxiliary_files}/doris_AoI_name.txt`
deinsar_AoI_name=`cat ${auxiliary_files}/deinsar_AoI_name.txt`
stitch_AoI_name=`cat ${auxiliary_files}/stitch_AoI_name.txt`
depsi_AoI_name=`cat ${auxiliary_files}/depsi_AoI_name.txt`
shape_AoI_name=`cat ${auxiliary_files}/shape_AoI_name.txt`
version=`cat ${auxiliary_files}/Caroline_version.txt`
dem_directory=`cat ${auxiliary_files}/dem_directory.txt`
depsi_directory=`cat ${auxiliary_files}/depsi_code_dir.txt`
geocoding_directory=`cat ${auxiliary_files}/geocoding_dir.txt`
rdnaptrans_directory=`cat ${auxiliary_files}/rdnaptrans_dir.txt`
depsi_post_directory=`cat ${auxiliary_files}/depsi_post_dir.txt`
cpxfiddle_directory=`cat ${auxiliary_files}/cpxfiddle_dir.txt`
do_tarball=`cat ${auxiliary_files}/depsi_post_mode.txt`

if [ ! -d ${shape_dir} ]; then
  mkdir -p ${shape_dir}
fi


if [ ! -f ${shape_dir}/${shape_AoI_name}_shape.shp ]; then
  echo "Generating shapefile..."
  python3 ${caroline_dir}/caroline_v${version}/bin/utils/convert_coord_to_shp.py ${param_file} ${cpath} ${shape_AoI_name}
else
  echo "Shapefile already exists."
fi


if [ ${do_deinsar} -eq 1 ]; then

  echo ""
  echo ""
  echo "Starting DeInSAR..."
  echo "Creating directories..."

  if [ ! -d ${deinsar_dir} ]; then
    mkdir -p ${deinsar_dir}
  fi

  python3 ${caroline_dir}/caroline_v${version}/bin/setup/setup_deinsar_directories.py ${param_file} ${cpath} ${deinsar_AoI_name}

  echo "Generating input files..."

  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_deinsar_input_files.py ${param_file} ${cpath} ${version} ${caroline_dir}

  echo "Generating DeInSAR files..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_deinsar_deinsar_py.py ${param_file} ${cpath} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_deinsar_deinsar_sh.py ${param_file} ${cpath} ${version} ${caroline_dir}

  echo "Starting DeInSAR..."
  cd ${deinsar_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_deinsar.txt`
  do
    cd ${dir}
    ls > dir_contents.txt
    sbatch run_deinsar.sh > job_id.txt
    cd ${doris_dir}
  done
  cd ${cpath}

  python3 ${caroline_dir}/caroline_v${version}/bin/wait/wait_for_deinsar.py ${param_file} ${cpath} ${deinsar_AoI_name}

fi


if [ ${do_doris} -eq 1 ]; then

  echo ""
  echo ""
  echo "Starting doris..."
  echo "Creating directories..."

  if [ ! -d ${doris_dir} ]; then
    mkdir -p ${doris_dir}
  fi

  python3 ${caroline_dir}/caroline_v${version}/bin/setup/setup_doris_directories.py ${param_file} ${cpath} ${doris_AoI_name}

  echo "Copying and linking directories..."
  cd ${doris_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_doris.txt`
  do
    cd ${dir}
    ln -sfn ${dem_directory} dem
    cp -r ${caroline_dir}/caroline_v${version}/files/doris_v5/input_files .
    cd good_images
    link=`cat link_directory.txt`
    rm -rf 20*
    ln -s ${link}/* .
    ls -l 20*/*.zip > zip_files.txt
    cd ${doris_dir}
  done
  cd ${cpath}

  echo "Filling in DEM properties in input files..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_doris_input_files.py ${param_file} ${cpath} ${doris_AoI_name} ${version} ${caroline_dir}

  echo "Filtering bad images..."
  python3 ${caroline_dir}/caroline_v${version}/bin/utils/filter_bad_images.py ${param_file} ${cpath} ${doris_AoI_name}
  cd ${doris_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_doris.txt`
  do
    cd ${dir}/good_images
    for d in `cat bad_zips.txt`
    do
      rm -rf ../bad_images/${d}
      mv ${d} ../bad_images/${d}
    done
    cd ${doris_dir}
  done
  cd ${cpath}


  echo "Generating doris files..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_doris_stack_sh.py ${param_file} ${cpath} ${doris_AoI_name} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_doris_input_xml.py ${param_file} ${cpath} ${doris_AoI_name} ${shape_AoI_name} ${version} ${caroline_dir}


  echo "Starting doris..."
  cd ${doris_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_doris.txt`
  do
    cd ${dir}
    ls > dir_contents.txt
    sbatch doris_stack.sh > job_id.txt
    cd ${doris_dir}
  done
  cd ${cpath}

  python3 ${caroline_dir}/caroline_v${version}/bin/wait/wait_for_doris.py ${param_file} ${cpath} ${doris_AoI_name}
fi



if [ ${do_stitching} -eq 1 ]; then

  echo ""
  echo ""
  echo "Starting stack stitching..."
  echo "Creating directory..."
  if [ ! -d ${stitch_dir} ]; then
    mkdir -p ${stitch_dir}
  fi

  python3 ${caroline_dir}/caroline_v${version}/bin/setup/setup_stitch_directories.py ${param_file} ${cpath} ${stitch_AoI_name} ${doris_AoI_name}

  echo "Linking directories..."
  cd ${stitch_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_stitch.txt`
  do
    cd ${dir}
    linkdir=`cat link_directory.txt`
    ln -sfn ${linkdir}/* .
    cd ${stitch_dir}
  done
  cd ${cpath}

  echo "Generating matlab and bash file..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_stitch_MAIN_m.py ${param_file} ${cpath} ${stitch_AoI_name} ${shape_AoI_name} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_stitch_MAIN_sh.py ${param_file} ${cpath} ${stitch_AoI_name} ${version} ${caroline_dir}

  echo "Starting stack stitching..."
  cd ${stitch_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_stitch.txt`
  do
    cd ${dir}
    ls > dir_contents.txt
    sbatch MAIN.sh > job_id.txt
    cd ${stitch_dir}
  done
  cd ${cpath}

  python3 ${caroline_dir}/caroline_v${version}/bin/wait/wait_for_stitch.py ${param_file} ${cpath} ${stitch_AoI_name}

fi


if [ ${do_depsi} -eq 1 ]; then

  echo ""
  echo ""
  echo "Starting DePSI..."
  echo "Creating directory..."
  if [ -d "${depsi_dir}" ]; then
    cd ${depsi_dir}
    for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
    do
      mv "${dir}" "${dir}-$(date +%Y%m%dT%H%M%S)"
    done
  fi
  cd "${cpath}"
  mkdir -p ${depsi_dir}

  python3 ${caroline_dir}/caroline_v${version}/bin/setup/setup_depsi_directories.py ${param_file} ${cpath} ${depsi_AoI_name} ${stitch_AoI_name}

  echo "Linking master files..."
  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/psi
    mother_res=`cat mother_res.txt`
    mother_dem=`cat mother_dem.txt`
    ln -sf ${mother_res} slave.res
    ln -sf ${mother_dem} dem_radar.raw
    cd ${depsi_dir}
  done
  cd ${cpath}

  echo "Copying boxes..."
  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/boxes
    #ln -s ${caroline_dir}/caroline_v${version}/files/depsi/boxes/* .
    ln -sfn ${rdnaptrans_directory} .
    ln -sfn ${geocoding_directory} .
    ln -sfn ${depsi_directory} .
    cd ${depsi_dir}
  done
  cd ${cpath}

  echo "Generating matlab and bash files..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_param_file_txt.py ${param_file} ${cpath} ${depsi_AoI_name} ${stitch_AoI_name} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_depsi_m.py ${param_file} ${cpath} ${depsi_AoI_name} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_depsi_sh.py ${param_file} ${cpath} ${depsi_AoI_name} ${version} ${caroline_dir}

  echo "Starting depsi..."
  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/psi
    ls > dir_contents.txt
    sbatch depsi.sh > job_id.txt
    cd ${depsi_dir}
  done
  cd ${cpath}

  python3 ${caroline_dir}/caroline_v${version}/bin/wait/wait_for_depsi.py ${param_file} ${cpath} ${depsi_AoI_name}

fi


if [ ${do_depsi_post} -eq 1 ]; then
  echo "Starting DePSI_post..."

  echo "Copying boxes..."
  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/boxes
    ln -sfn ${depsi_post_directory} .
    cd ${depsi_dir}
  done
  cd ${cpath}


  echo "Creating mrm raster..."
  python3 ${caroline_dir}/caroline_v${version}/bin/setup/setup_create_mrm.py ${param_file} ${cpath} ${depsi_AoI_name}

  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/psi
    nlines=`cat nlines_crop.txt`
    project_id=`cat project_id.txt`
    ${caroline_dir}/caroline_v${version}/files/depsi_post/create_mrm_ras_rxaz_header.sh ${project_id} ${nlines} 1 1 ${cpxfiddle_directory}
    cd ${depsi_dir}
  done
  cd ${cpath}


  echo "Generating mrm matlab and bash file..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_post_read_mrm_m.py ${param_file} ${cpath} ${depsi_AoI_name} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_post_read_mrm_sh.py ${param_file} ${cpath} ${depsi_AoI_name} ${version} ${caroline_dir}


  echo "Correcting mrm raster..."
  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/psi
    ls > dir_contents_read_mrm.txt
    sbatch read_mrm.sh > job_id.txt
    cd ${depsi_dir}
  done
  cd ${cpath}

  python3 ${caroline_dir}/caroline_v${version}/bin/wait/wait_for_read_mrm.py ${param_file} ${cpath} ${depsi_AoI_name}


  echo "Generating depsi_post matlab and bash file..."
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_post_depsi_post_m.py ${param_file} ${cpath} ${depsi_AoI_name} ${version} ${caroline_dir}
  python3 ${caroline_dir}/caroline_v${version}/bin/generate/generate_depsi_post_depsi_post_sh.py ${param_file} ${cpath} ${depsi_AoI_name} ${version} ${caroline_dir}


  echo "Starting DePSI_post..."
  cd ${depsi_dir}
  for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
  do
    cd ${dir}/psi
    ls > dir_contents_depsi_post.txt
    sbatch depsi_post.sh > job_id.txt
    cd ${depsi_dir}
  done
  cd ${cpath}

  python3 ${caroline_dir}/caroline_v${version}/bin/wait/wait_for_depsi_post.py ${param_file} ${cpath} ${depsi_AoI_name}

  if [ ${do_tarball} -eq 1 ]; then

    echo "Creating tarball..."
    cd ${depsi_dir}
    for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`
    do
      echo ${dir}
      cd ${dir}/psi
      project_id=`cat project_id.txt`
      ${caroline_dir}/caroline_v${version}/files/depsi_post/create_post_project_tar.sh ${project_id}
      cd ${depsi_dir}
    done
    cd ${cpath}

  fi

  #
  # Upload csv to skygeo
  # THIS IS NOW DONE IN run-caroline.sh
  #
  #echo "Uploading csv to skygeo viewer"
  #cd ${depsi_dir}
  #for dir in `cat ${cpath}/${auxiliary_files}/loop_directories_depsi.txt`; do
  #  echo ${dir}
  #  cd ${dir}/psi
  #  upload-result-csv-to-skygeo.sh
  #  cd ${depsi_dir}
  #done
  #cd ${cpath}

fi

# always send completion email
send-success-mail.sh ${param_file} ${cpath} ${version} ${caroline_dir}

