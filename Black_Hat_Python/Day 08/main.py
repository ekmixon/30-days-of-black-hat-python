import argparse
from threading import Thread
from turtle import tilt, title
from termcolor import colored
from os import path
from sys import exit
from queue import Queue
import requests
from bs4 import BeautifulSoup
def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('domain',help="target to scan")
    
    parser.add_argument('-t','-threads',dest="threads",help="Specify the threads, (Default => 10)",type=int,default=10)
    
    parser.add_argument('-w','--wordlist',dest='wordlist',required=False,default='wordlist.txt',help="Specify the wordlist to use !")
    
    parser.add_argument('--ignore-code',dest='ignore_codes',type=int,help="Codes to ignore",nargs='*')
    parser.add_argument('-mc',dest="match_codes",type=int,help="Status Codes to ignore",nargs='*')
    parser.add_argument('-fl',dest='Filter_response_length',type=int,help="Filter the response length")
    
    parser.add_argument('-header',dest='headers',help="Additional headers")
    parser.add_argument('-o',dest='output',help="File to output into ")
    parser.add_argument('-disable-redirect',action='store_true',dest='dis_redirect',help="Disable redirection,Default : Redirection True")
    
    return parser.parse_args()
def print_output_and_save_in_file(status_code,response_length,url,title):
    global subdomains
    if status_code>=200 and status_code<300:
        color='green'
    elif status_code>=300 and status_code<400:
        color='yellow'
    elif status_code>=400 and status_code<500:
        color='red'
    elif status_code>500 and status_code<600:
        color='magenta'
    print("Found ",end="")
    print(colored(f"{[status_code]}".ljust(9," "),color),end="")
    print(f"{response_length}".ljust(9),end="")
    print(f"{url}        [{title}]")   
    
    if outputfile:
        subdomains[url]=[status_code,response_length,title]
        
def sub_brute(subdomain):
    """Function to handle subdomains"""
    try:
        url=f"https://{subdomain}.{domain}"
        if headers:
            response=requests.get(url,allow_redirects=redirection,timeout=1)
        else:
            response=requests.get(url,allow_redirects=redirection,timeout=1,headers=headers)
    except requests.exceptions.Timeout:
        pass
    except:
        pass
    else:
        response_length=len(response.text)
        status_code=response.status_code
        soup=BeautifulSoup(response.text,'html.parser')
        title=soup.title.string
        if ignore_codes:
            if (status_code not in ignore_codes):
                if not Filter_response_length:
                    print_output_and_save_in_file(status_code,response_length,url,title)
                else:
                    if response_length not in Filter_response_length:
                        print_output_and_save_in_file(status_code,response_length,url,title)
        elif match_codes:   
            if (status_code in match_codes):
                if not Filter_response_length:
                    print_output_and_save_in_file(status_code,response_length,url,title)
                else:
                    if response_length not in Filter_response_length:
                        print_output_and_save_in_file(status_code,response_length,url,title)
        else:
            if not Filter_response_length:
                print_output_and_save_in_file(status_code,response_length,url,title)
            else:
                if response_length !=Filter_response_length:
                    print_output_and_save_in_file(status_code,response_length,url,title)
def get_subdomain():
    global q 
    while True:
        subdomain=q.get()
        sub_brute(subdomain)
        q.task_done()
        
def handle_threads(threads):
    global q
    
    for thread in range(threads):
        thread=Thread(target=get_subdomain)
        thread.daemon=True
        thread.start()
            
    subdomains=[]    
    
    
    with open (wordlist,'r') as f:
        for subdomain in f.readlines():
            subdomains.append(subdomain.strip())
    
    for subdomain in subdomains:
        q.put(subdomain)
    q.join()    
        

def print_banner(domain,threads,ignore_codes,headers,wordlist,outputfile,Filter_response_length,match_codes):
    from datetime import datetime
    print()
    print("-"*80)
    print(colored(f"Subdomain Bruteforcer starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",'yellow',attrs=['bold']))
    print("-"*80)
    print("[*] Domain".ljust(20," "),":",f"{domain}")
    print("[*] Threads".ljust(20," "),":",f"{threads}")
    print("[*] Wordlist".ljust(20," "),":",f"{wordlist}")
    if headers:
        print("[*] Headers".ljust(20," "),":",f"{headers}")
    if ignore_codes:
        print("[*] Ignore Codes".ljust(20," "),":",f"{ignore_codes}")
    if outputfile:
        print("[*] Output File".ljust(20," "),":",f"{outputfile}")
    if Filter_response_length:
        print("[*] Filter Length".ljust(20," "),":",f"{Filter_response_length}")
    if match_codes:
        print("[*] Match Codes".ljust(20," "),":",f"{match_codes}")
        
    
    print("-"*80)
    
if __name__=="__main__":
    arguments=get_args()
    q=Queue()
    if not path.exists(arguments.wordlist):
        print(colored("[-] Please Specify a valid wordlist ",'red'))
        exit()

    domain=arguments.domain
    wordlist=arguments.wordlist
    threads=arguments.threads
    headers=arguments.headers
    outputfile=arguments.output
    ignore_codes=arguments.ignore_codes
    match_codes=arguments.match_codes
    Filter_response_length=arguments.Filter_response_length
    
    if arguments.dis_redirect:
        redirection=False
    else:
        redirection=True
    if arguments.headers:
        headers={headers.split(':')[0].strip():headers.split(':')[1].strip()}
    print_banner(domain,threads,ignore_codes,headers,wordlist,outputfile,Filter_response_length,match_codes)
    
    subdomains={}
    handle_threads(threads=threads)
    if outputfile:
        with open(outputfile,'w') as f:
            for subdomain in subdomains:
                f.write(f"Found {subdomains[subdomain][0]}     [{subdomains[subdomain][1]}]\t{subdomain}{subdomains[subdomain][2]}         {subdomains[subdomain][3]}\n")