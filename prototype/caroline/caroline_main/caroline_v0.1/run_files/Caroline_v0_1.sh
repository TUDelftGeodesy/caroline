#!/bin/bash

param_file='param_file_Caroline_v0_1.txt'
step_file_version='0.1'

echo "Starting full DePSI run..."

cpath=`pwd`

if [ ! -d auxiliary_files ]
then
mkdir auxiliary_files
fi

echo "Creating auxiliary files..."

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${step_file_version}/main/fr_create_step_files.py ${param_file} ${cpath}

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

if [ ! -d ${shape_dir} ]
then
mkdir -p ${shape_dir}
fi


if [ ! -f ${shape_dir}/${AoI_name}_shape.shp ]
then
echo "Generating shapefile..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_convert_coord_to_shp.py ${param_file} ${cpath} ${AoI_name}
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

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_setup_doris_directories.py ${param_file} ${cpath} ${AoI_name}

echo "Copying directories..."
cd ${doris_dir}
for dir in `ls`
do
cd ${dir}
cp -r /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/files/doris_v5/dem .
cp -r /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/files/doris_v5/input_files .
cd good_images
link=`cat link_directory.txt`
ln -s ${link}/* .
ls -l 20*/*.zip > zip_files.txt
cd ${doris_dir}
done
cd ${cpath}

echo "Filtering bad images..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_filter_bad_images.py ${param_file} ${cpath} ${AoI_name}
cd ${doris_dir}
for dir in `ls`
do  
cd ${dir}/good_images
for d in `cat bad_zips.txt`
do
mv ${d} ../bad_images/${d}
done
cd ${doris_dir}
done
cd ${cpath}



echo "Finding available nodes..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_set_nodes_available.py ${cpath}
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
while [ ${allocated_nodes} -eq 0 ]
do
LOCALnodeload.pl > auxiliary_files/nodeload.txt
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_find_empty_nodes.py ${param_file} ${cpath} ${AoI_name} 8
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
done


echo "Generating doris files..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_doris_stack_sh.py ${param_file} ${cpath} ${AoI_name} ${version}
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_doris_input_xml.py ${param_file} ${cpath} ${AoI_name} ${version}


echo "Starting doris..."
cd ${doris_dir}
for dir in `ls`
do
cd ${dir}
ls > dir_contents.txt
qsub doris_stack.sh
cd ${doris_dir}
done
cd ${cpath}

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_wait_for_doris.py ${param_file} ${cpath} ${AoI_name}
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

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_setup_stitch_directories.py ${param_file} ${cpath} ${AoI_name}

echo "Linking directories..."
cd ${stitch_dir}
for dir in `ls`
do
cd ${dir}
linkdir=`cat link_directory.txt`
ln -s ${linkdir}/* .
cd ${stitch_dir}
done
cd ${cpath}

echo "Finding available nodes..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_set_nodes_available.py ${cpath}
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
while [ ${allocated_nodes} -eq 0 ]
do
LOCALnodeload.pl > auxiliary_files/nodeload.txt
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_find_empty_nodes.py ${param_file} ${cpath} ${AoI_name} 1
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
done

echo "Generating matlab and bash file..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_stitch_MAIN_m.py ${param_file} ${cpath} ${AoI_name} ${version}
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_stitch_MAIN_sh.py ${param_file} ${cpath} ${AoI_name} ${version}

echo "Starting stack stitching..."
cd ${stitch_dir}
for dir in `ls`
do
cd ${dir}
ls > dir_contents.txt
qsub MAIN.sh
cd ${stitch_dir}
done
cd ${cpath}

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_wait_for_stitch.py ${param_file} ${cpath} ${AoI_name}

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

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_setup_depsi_directories.py ${param_file} ${cpath} ${AoI_name}

echo "Linking master files..."
cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/psi
link=`cat master_directory.txt`
ln -s ${link}/master.res slave.res
ln -s ${link}/dem_radar_${AoI_name}.raw dem_radar.raw
cd ${depsi_dir}
done
cd ${cpath}

echo "Copying boxes..."
cd ${depsi_dir}
for dir in `ls`
do  
cd ${dir}/boxes
cp -r /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/files/depsi/boxes/* .
cd ${depsi_dir}
done
cd ${cpath}

echo "Finding available nodes..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_set_nodes_available.py ${cpath}
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
while [ ${allocated_nodes} -eq 0 ]
do  
LOCALnodeload.pl > auxiliary_files/nodeload.txt
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_find_empty_nodes.py ${param_file} ${cpath} ${AoI_name} 1
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
done

echo "Generating matlab and bash files..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_param_file_txt.py ${param_file} ${cpath} ${AoI_name} ${version}
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_depsi_m.py ${param_file} ${cpath} ${AoI_name} ${version}
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_depsi_sh.py ${param_file} ${cpath} ${AoI_name} ${version}

echo "Starting depsi..."
cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/psi
ls > dir_contents.txt
qsub depsi.sh
cd ${depsi_dir}
done
cd ${cpath}

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_wait_for_depsi.py ${param_file} ${cpath} ${AoI_name}

fi


if [ ${do_depsi_post} -eq 1 ]
then
echo "Starting DePSI_post..."

echo "Copying boxes..."
cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/boxes
cp -r /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/files/depsi_post/depsi_post_v* .
cd ${depsi_dir}
done
cd ${cpath}


echo "Creating mrm raster..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_setup_create_mrm.py ${param_file} ${cpath} ${AoI_name}

cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/psi
nlines=`cat nlines_crop.txt`
project_id=`cat project_id.txt`
/home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/files/depsi_post/create_mrm_ras_rxaz_header.sh ${project_id} ${nlines} 1 1
cd ${depsi_dir}
done
cd ${cpath}


echo "Finding available nodes..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_set_nodes_available.py ${cpath}
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
while [ ${allocated_nodes} -eq 0 ]
do  
LOCALnodeload.pl > auxiliary_files/nodeload.txt
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_find_empty_nodes.py ${param_file} ${cpath} ${AoI_name} 1
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
done


echo "Generating mrm matlab and bash file..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_post_read_mrm_m.py ${param_file} ${cpath} ${AoI_name} ${version}
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_post_read_mrm_sh.py ${param_file} ${cpath} ${AoI_name} ${version}


echo "Correcting mrm raster..."
cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/psi
ls > dir_contents_read_mrm.txt
qsub read_mrm.sh
cd ${depsi_dir}
done
cd ${cpath}

python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_wait_for_read_mrm.py ${param_file} ${cpath} ${AoI_name}


echo "Finding available nodes..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_set_nodes_available.py ${cpath}
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
while [ ${allocated_nodes} -eq 0 ]
do  
LOCALnodeload.pl > auxiliary_files/nodeload.txt
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_find_empty_nodes.py ${param_file} ${cpath} ${AoI_name} 1
allocated_nodes=`cat auxiliary_files/nodes_available.txt`
done


echo "Generating depsi_post matlab and bash file..."
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_post_depsi_post_m.py ${param_file} ${cpath} ${AoI_name} ${version}
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_generate_depsi_post_depsi_post_sh.py ${param_file} ${cpath} ${AoI_name} ${version}


echo "Starting DePSI_post..."
cd ${depsi_dir}
for dir in `ls`
do
cd ${dir}/psi
ls > dir_contents_depsi_post.txt
qsub depsi_post.sh
cd ${depsi_dir}
done
cd ${cpath}
  
python /home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/main/fr_wait_for_depsi_post.py ${param_file} ${cpath} ${AoI_name}


echo "Creating tarball..."
cd ${depsi_dir}
for dir in `ls`
do
echo ${dir}
cd ${dir}/psi
project_id=`cat project_id.txt`
/home/sanvandiepen/code/Caroline/Caroline_main/Caroline_v${version}/files/depsi_post/create_post_project_tar.sh ${project_id}
cd ${depsi_dir}
done
cd ${cpath}

fi
