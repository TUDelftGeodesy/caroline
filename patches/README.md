# The Patches Directory
This directory will be copied onto the plugins directory. It should only be used as a last resort. 
To use it, recreate the exact folder structure leading to the file needing modification under this folder, then paste the modified file in the last folder.

E.g., to modify `depsi_post_v2.1.4.0/main/ps_post_create_final_dataset.m` from the DePSI_post plugin, create the folder `depsi_post_v2.1.4.0` in this directory, then create the folder `main` in `depsi_post_v2.1.4.0`, and then create the file `ps_post_create_final_dataset.m` in `main`. 
The file will be used to overwrite the one coming from GitHub or the tarball, so it should be usage-ready.