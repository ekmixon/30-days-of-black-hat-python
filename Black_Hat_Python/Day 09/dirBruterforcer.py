import argparse,requests
from threading import Thread
from bs4 import BeautifulSoup
from sys import exit
from queue import Queue
from termcolor import colored
from os import path


def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('target',help="The target to attack on provide it with http or https")
    parser.add_argument('-x',dest='extensions',nargs="*",help="Extension list separated by space and without dot (Example: php asp)")
    parser.add_argument('-r','--follow-redirect',dest="follow_redirect",action='store_true',help="Follow redirects")
    parser.add_argument('-H','--headers',dest="header",nargs='*',help="Specify HTTP headers, -H 'Header1: val1' -H 'Header2: val2'")
    parser.add_argument('-a','--useragent',metavar='string',dest="user_agent",help="Set the User-Agent string (default 'directorybuster/1.0')")
    parser.add_argument('-t','--threads',dest='threads',help="Number of threads",default=10,type=int)
    parser.add_argument('-ht','--hide-title',dest="hide_title",action='store_true',help="Specify for hiding response title in output")
    
    parser.add_argument('-mc',dest='match_codes',nargs='*',help="Include status codes, separated by space, example -mc 200 404")
    parser.add_argument('-ms',dest='match_size',nargs='*',help="Match amount of size in response")
    
    
    parser.add_argument('-fc',dest="filter_codes",nargs='*',help="Filter the status codes (provide space separated values")
    parser.add_argument('-fs',nargs='*',dest='filter_size',help="Filter the response size (provide space separated values")
    
    parser.add_argument('-w','--wordlist',dest='wordlist',help="Wordlist to use",required=True)
    parser.add_argument('-o','--output',dest='output',help="Output file to use!")
    
    return parser.parse_args()

def print_and_save_output(status_code,response_length,url,title):
    
    if status_code>=200 and status_code<300:
        color='green'
    elif status_code>=300 and status_code<400:
        color='yellow'
    elif status_code>=400 and status_code<500:
        color='red'
    elif status_code>500 and status_code<600:
        color='magenta'
    print(colored(f"{[status_code]}".ljust(9," "),color),end="")
    print(f"{response_length}".ljust(9),end="")
    print(f"{url}",end="    ")  
    if not hide_title:
        print(f"[{title.strip()}]")
    global Directories
    if output:
        if not hide_title:
            Directories[url]=[status_code,response_length,title]
        else:
            Directories[url]=[status_code,response_length]
            

def brute_dir(word):
    try:
        url=f"{target}{word}"
        if headers:
            response=requests.get(url,headers=headers,allow_redirects=redirection,timeout=1)
        else:
            response=requests.get(url,allow_redirects=redirection,timeout=1)
            
    except requests.exceptions.Timeout:
        pass
    except Exception as err:
        print("Error occured :",err)
    else:
        response_length=len(response.text)
        status_code=response.status_code
        url=url.split('://')[1]
        soup=BeautifulSoup(response.text,'lxml')
        if soup.title:
            title=soup.title.string
        else:
            tilte=[]
        
        if match_codes:
            if status_code in match_codes:
                if filter_size:
                    if response_length not in filter_size:
                        print_and_save_output(status_code,response_length,url,title)
                elif match_size:
                    if response_length in match_size:
                        print_and_save_output(status_code,response_length,url,title)
                else:
                    print_and_save_output(status_code,response_length,url,title)
                    
        elif filter_codes:
            if status_code not in filter_codes:
                if filter_size:
                    if response_length not in filter_size:
                        print_and_save_output(status_code,response_length,url,title)
                elif match_size:
                    if response_length in match_size:
                        print_and_save_output(status_code,response_length,url,title)
                else:
                    print_and_save_output(status_code,response_length,url,title)
                            
        else:
            if filter_size:
                if response_length not in filter_size:
                    print_and_save_output(status_code,response_length,url,title)
            elif match_size:
                if response_length in match_size:
                    print_and_save_output(status_code,response_length,url,title)
            else:
                print_and_save_output(status_code,response_length,url,title)
            
def get_words():
    try:
        global words
        while True:
            word=words.get()
            brute_dir(word)
            words.task_done()
    except:
        pass
def handle_threads(threads):
    for thread in range(threads):
        thread=Thread(target=get_words)
        thread.daemon=True
        thread.start()
    dirs=[]    
    with open (wordlist,'r') as f:
        for word  in f.readlines():
            word=word.strip()
            # if the word is admin.php , index.html,style.css
            if '.' in word:
                dirs.append(f'/{word}')
            else:
                dirs.append(f'/{word}')
            if extensions:
                for ext in extensions:
                    dirs.append(f'/{word}.{ext}')

    global words 
    
    for word in dirs:
        words.put(word)
    words.join()

def print_banner(target,extensions,headers,useragent,threads,match_codes,match_size,filter_codes,filter_size,wordlist,output):
    from datetime import datetime
    print("-"*80)
    print(colored(f"Directory and file bruteforcer starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",'yellow',attrs=['bold']))
    print("-"*80)
    print("[*] Url".ljust(20," "),":",f"{target}")
    print("[*] Threads".ljust(20," "),":",f"{threads}")
    print("[*] Wordlist".ljust(20," "),":",f"{wordlist}")
    if headers:
        print("[*] Headers".ljust(20," "),":",f"{headers}")
    if extensions:
        print("[*] Extensions".ljust(20," "),":",f"{extensions}")
    if output:
        print("[*] Output File".ljust(20," "),":",f"{output}")
    if useragent:
        print("[*] User Agent".ljust(20," "),":",f"{useragent}")
    if match_size:
        print("[*] Match Res size".ljust(20," "),":",f"{match_size}")
    if match_codes:
        print("[*] Match Codes".ljust(20," "),":",f"{match_codes}")
    if filter_codes:
        print("[*] Filter Codes".ljust(20," "),":",f"{filter_codes}")
    if filter_size:
        print("[*] Filter Res Size".ljust(20," "),":",f"{filter_size}")
    print("-"*80)

if __name__=="__main__":
    
    words=Queue()
    
    arguments=get_args()
    # getting all the command-line values 
    target=arguments.target
    extensions=arguments.extensions
    hide_title=arguments.hide_title
    redirection=arguments.follow_redirect
    if not redirection:
        redirection=False

    useragent=arguments.user_agent
    threads=arguments.threads
    
    match_codes=arguments.match_codes
    match_size=arguments.match_size
    
    filter_codes=arguments.filter_codes
    filter_size=arguments.filter_size
    
    if match_size and filter_size:
        print(colored("[+] For now Using Matching and Filtering Response Length together is not available !",'red'))
        exit()
    if match_codes and filter_codes:
        print(colored("[+] For now Using Matching and Filtering Response Status code together is not available !",'red'))
    output=arguments.output
    header=arguments.header
    
    wordlist=arguments.wordlist
    if not path.exists(wordlist):
        print(colored("[-] Provide a valid wordlist file !",'red'))
        exit()
    
    # Printing the banner 
    print_banner(target,extensions,header,useragent,threads,match_codes,match_size,filter_codes,filter_size,wordlist,output)
    
    # Converting header varible data into dictionary so that it could be used while sending headers 
    
    
    headers={}
    if header:
        for header in header:
            headers[header.split(':')[0]]=f"{header.split(':')[1]}"
    if useragent:
        header[useragent.split(':')[0]]=f"{useragent.split(':')[1]}"
        
    Directories={}
    if output:
        with open(output,'w') as f:
            for directory in Directories:
                if not hide_title:
                    f.write(f"{Directories[directory][0]}     [{Directories[directory][1]}]\t{directory}{Directories[directory][2]}\n")
                else:   
                    f.write(f"{Directories[directory][0]}     [{Directories[directory][1]}]\t{directory}\t")
    handle_threads(threads=threads)
    