#!/bin/bash

param_file='param_file_Caroline_v0_2.txt'
step_file_version='0.2'
caroline_dir="/project/caroline/Share/software/caroline/prototype/caroline/caroline_main"

echo "Starting full Caroline run..."

cpath=`pwd`

if [ ! -d auxiliary_files ]
then
mkdir auxiliary_files
fi

echo "Creating auxiliary files..."

python3 ${caroline_dir}/caroline_v${step_file_version}/main/fr_create_step_files.py ${param_file} ${cpath}

do_doris=`cat auxiliary_files/do_doris.txt`
do_stitching=`cat auxiliary_files/do_stack_stitching.txt`
do_depsi=`cat auxiliary_files/do_depsi.txt`
do_depsi_post=`cat auxiliary_files/do_depsi_post.txt`
doris_dir=`cat auxiliary_files/doris_directory.txt`
stitch_dir=`cat auxiliary_files/stitch_directory.txt`
depsi_dir=`cat auxiliary_files/depsi_directory.txt`
shape_dir=`cat auxiliary_files/shape_directory.txt`
AoI_name=`cat auxiliary_files/AoI_name.txt`
version=`cat auxiliary_files/Caroline_version.txt`
dem_directory=`cat auxiliary_files/dem_directory.txt`
depsi_directory=`cat auxiliary_files/depsi_code_dir.txt`
geocoding_directory=`cat auxiliary_files/geocoding_dir.txt`
rdnaptrans_directory=`cat auxiliary_files/rdnaptrans_dir.txt`
depsi_post_directory=`cat auxiliary_files/depsi_post_dir.txt`
cpxfiddle_directory=`cat auxiliary_files/cpxfiddle_dir.txt`
if [ ! -d ${shape_dir} ]
then
mkdir -p ${shape_dir}
fi


if [ ! -f ${shape_dir}/${AoI_name}_shape.shp ]
then
echo "Generating shapefile..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_convert_coord_to_shp.py ${param_file} ${cpath} ${AoI_name}
else
echo "Shapefile already exists."
fi


if [ ${do_doris} -eq 1 ]
then

echo ""
echo ""
echo "Starting doris..."
echo "Creating directories..."

if [ ! -d ${doris_dir} ]
then
mkdir -p ${doris_dir}
fi

python3 ${caroline_dir}/caroline_v${version}/main/fr_setup_doris_directories.py ${param_file} ${cpath} ${AoI_name}

echo "Copying and linking directories..."
cd ${doris_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}
ln -s ${dem_directory} dem
cp -r ${caroline_dir}/caroline_v${version}/files/doris_v5/input_files .
cd good_images
link=`cat link_directory.txt`
ln -s ${link}/* .
ls -l 20*/*.zip > zip_files.txt
cd ${doris_dir}
done
cd ${cpath}

echo "Filtering bad images..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_filter_bad_images.py ${param_file} ${cpath} ${AoI_name}
cd ${doris_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do  
cd ${dir}/good_images
for d in `cat bad_zips.txt`
do
mv ${d} ../bad_images/${d}
done
cd ${doris_dir}
done
cd ${cpath}


echo "Generating doris files..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_doris_stack_sh.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_doris_input_xml.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}


echo "Starting doris..."
cd ${doris_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}
ls > dir_contents.txt
sbatch doris_stack.sh > job_id.txt
cd ${doris_dir}
done
cd ${cpath}

python3 ${caroline_dir}/caroline_v${version}/main/fr_wait_for_doris.py ${param_file} ${cpath} ${AoI_name}
fi



if [ ${do_stitching} -eq 1 ]
then

echo ""
echo ""
echo "Starting stack stitching..."
echo "Creating directory..."
if [ ! -d ${stitch_dir} ]
then
mkdir -p ${stitch_dir}
fi

python3 ${caroline_dir}/caroline_v${version}/main/fr_setup_stitch_directories.py ${param_file} ${cpath} ${AoI_name}

echo "Linking directories..."
cd ${stitch_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}
linkdir=`cat link_directory.txt`
ln -s ${linkdir}/* .
cd ${stitch_dir}
done
cd ${cpath}

echo "Generating matlab and bash file..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_stitch_MAIN_m.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_stitch_MAIN_sh.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}

echo "Starting stack stitching..."
cd ${stitch_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}
ls > dir_contents.txt
sbatch MAIN.sh > job_id.txt
cd ${stitch_dir}
done
cd ${cpath}

python3 ${caroline_dir}/caroline_v${version}/main/fr_wait_for_stitch.py ${param_file} ${cpath} ${AoI_name}

fi


if [ ${do_depsi} -eq 1 ]
then

echo ""
echo ""
echo "Starting DePSI..."
echo "Creating directory..."
if [ ! -d ${depsi_dir} ]
then
mkdir -p ${depsi_dir}
fi

python3 ${caroline_dir}/caroline_v${version}/main/fr_setup_depsi_directories.py ${param_file} ${cpath} ${AoI_name}

echo "Linking master files..."
cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}/psi
link=`cat master_directory.txt`
ln -s ${link}/master.res slave.res
ln -s ${link}/dem_radar*.raw dem_radar.raw
cd ${depsi_dir}
done
cd ${cpath}

echo "Copying boxes..."
cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}/boxes
#ln -s ${caroline_dir}/caroline_v${version}/files/depsi/boxes/* .
ln -s ${rdnaptrans_directory} .
ln -s ${geocoding_directory} .
ln -s ${depsi_directory} .
cd ${depsi_dir}
done
cd ${cpath}

echo "Generating matlab and bash files..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_param_file_txt.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_depsi_m.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_depsi_sh.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}

echo "Starting depsi..."
cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/psi
ls > dir_contents.txt
sbatch depsi.sh > job_id.txt
cd ${depsi_dir}
done
cd ${cpath}

python3 ${caroline_dir}/caroline_v${version}/main/fr_wait_for_depsi.py ${param_file} ${cpath} ${AoI_name}

fi


if [ ${do_depsi_post} -eq 1 ]
then
echo "Starting DePSI_post..."

echo "Copying boxes..."
cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}/boxes
ln -s ${depsi_post_directory} .
cd ${depsi_dir}
done
cd ${cpath}


echo "Creating mrm raster..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_setup_create_mrm.py ${param_file} ${cpath} ${AoI_name}

cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}/psi
nlines=`cat nlines_crop.txt`
project_id=`cat project_id.txt`
${caroline_dir}/caroline_v${version}/files/depsi_post/create_mrm_ras_rxaz_header.sh ${project_id} ${nlines} 1 1 ${cpxfiddle_directory}
cd ${depsi_dir}
done
cd ${cpath}


echo "Generating mrm matlab and bash file..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_post_read_mrm_m.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_post_read_mrm_sh.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}


echo "Correcting mrm raster..."
cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}/psi
ls > dir_contents_read_mrm.txt
sbatch read_mrm.sh > job_id.txt
cd ${depsi_dir}
done
cd ${cpath}

python3 ${caroline_dir}/caroline_v${version}/main/fr_wait_for_read_mrm.py ${param_file} ${cpath} ${AoI_name}


echo "Generating depsi_post matlab and bash file..."
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_post_depsi_post_m.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}
python3 ${caroline_dir}/caroline_v${version}/main/fr_generate_depsi_post_depsi_post_sh.py ${param_file} ${cpath} ${AoI_name} ${version} ${caroline_dir}


echo "Starting DePSI_post..."
cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
cd ${dir}/psi
ls > dir_contents_depsi_post.txt
sbatch depsi_post.sh > job_id.txt
cd ${depsi_dir}
done
cd ${cpath}
  
python3 ${caroline_dir}/caroline_v${version}/main/fr_wait_for_depsi_post.py ${param_file} ${cpath} ${AoI_name}


echo "Creating tarball..."
cd ${depsi_dir}
for dir in `cat ${cpath}/auxiliary_files/loop_directories.txt`
do
echo ${dir}
cd ${dir}/psi
project_id=`cat project_id.txt`
${caroline_dir}/caroline_v${version}/files/depsi_post/create_post_project_tar.sh ${project_id}
cd ${depsi_dir}
done
cd ${cpath}

fi
