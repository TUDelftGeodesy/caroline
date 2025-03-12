from sys import argv

filename, cpath = argv

f = open(f"{cpath}/auxiliary_files/nodes_available.txt", "w")
f.write("0")
f.close()
