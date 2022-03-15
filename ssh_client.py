from http import client
import paramiko

# client = paramiko.SSHClient()


# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# client.connect("spider.surfsara.nl", username="caroline-mgarcia", key_filename='/home/manuel/.ssh/caroline_spider.pub')

# stdin, stdout, stderr = client.exec_command('uptime')

# print (stdout.readlines())
# client.close()

command = """"bash /some/dir/script.sh"""
sleep_time = '20s'

prefix ="""
JID=$(""" + command + """)
echo  $JID
sleep 10s 
""" 
    
loop = """
ST="PENDING"
while [ "$ST" != "COMPLETED" ] ; do 
    ST=$(sacct -j ${JID##* } -o State | awk 'FNR == 3 {print $1}')
    sleep """ + sleep_time + """
    if [ "$ST" == "FAILED" ]; then
        echo 'Job final status:' $ST, exiting...
        exit 122
    fi; done    
echo $ST
""" 
            
_command = prefix + loop
print(_command)