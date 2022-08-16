from sys import argv
filename, cpath = argv

f = open("{}/auxiliary_files/nodes_available.txt".format(cpath),"w")
f.write("0")
f.close()
