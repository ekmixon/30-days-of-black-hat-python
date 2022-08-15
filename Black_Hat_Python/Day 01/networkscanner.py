
# for unconditionally terminating the program ! 
from sys import exit

# argparse => For creating command-line arguments
# re => for regex
# socket=> for creating connections 
# struct -> For binary stuff!
import argparse,struct,re,random,socket

# Queue is datastrcture which follows fifo
from queue import Queue

# with scapy you can create a full fledged packet and you can create malicous packets with it 
import scapy.all as scapy

# For threading and locking those thread to avoid race condition
from threading import Thread,Lock


def get_args():
    # creating Command-line arguments
    parser=argparse.ArgumentParser()
    parser.add_argument('target',help="Target url or IP address")
    parser.add_argument('-arp',dest='arp',help="Use this for arp ping!",required=False,action='store_true')
    parser.add_argument('-pT',dest="tcpPortScan",help="Tcp Port Scan",required=False,action='store_true')
    parser.add_argument('-pU',dest="udpPortScan",help="Udp Port Scan",required=False,action='store_true')
    parser.add_argument('-p','--ports',dest="ports",help="Port range to scan, default is 1-65535 (all ports)",required=False,action='store',default='1-65535')
    parser.add_argument('-t','--threads',dest="threads",help="Threads for speed , default is 100",required=False,action='store',default=100,type=int)
    
    arguments=parser.parse_args()
              
   # Returning the arguments ! 
    return arguments
def arp_ping(ip):
        # code for validating the ip address range syntax 
        if not re.match(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}/[0-9]*$',ip):
            print("[-] Please provide a valid Ip address range for arp ping !")
            exit(1)
            
            
        try:
            arp_request_frame=scapy.ARP(pdst=ip) # creating a arp request frame with ip destination to our range provided !
            
            ether_broadcast_frame=scapy.Ether(dst="ff:ff:ff:ff:ff:ff") # setting the broadcast mac address to broadcast address ! 
            
            broadcast_arp_packet=ether_broadcast_frame/arp_request_frame # combining layer 2 and layer3 packets together ! means we have combined ethernet and arp frame togther ! 
            
            active_clients=scapy.srp(broadcast_arp_packet,timeout=3,verbose=False)[0] 
            #.srp function takes the whole packet and transmits and also we are storing the response in the active_clients variable !
            # In response we are returned a tuple  of length 2 in which clients who replied are in index 0 and who didn't replied are index 1 so we are only gathering active clients 
            print("""----------------------------------\nIPaddress\tMac address\n----------------------------------""")
            # Printing the result 
            

            # .psrc => Source Ip address
            # .hwsrc=>destination mac address
            # In reply of active replied clients we are replied with a list in which the first index '0' consists the data about 2nd layer The Data Link layer and in index 1 it consists the data about Network layer so are parsing data from the layer 3 
            # The index 1 has a object inside it which has data , we are only taking psrc and hwsrc ! 
            for i in range(0,len(active_clients)):
                print(f"{active_clients[i][1].psrc}\t{active_clients[i][1].hwsrc}")
            print("\n\n")
        except Exception as err:
            # Capturing the error !
            print(f"[-] Error occured !, Reason => {err}")
    
    
# Threaded Port scanner Code ! 

# 
def udp_packet_build(target):
    # "This code has been taken from the resources provided in the project"
    # "It creates a dns packet as UDP port does reply on UDP PORT"
    randint = random.randint(0, 65535)
    packet = struct.pack(">H", randint)  # Query Ids (Just 1 for now)
    packet += struct.pack(">H", 0x0100)  # Flags
    packet += struct.pack(">H", 1)  # Questions
    packet += struct.pack(">H", 0)  # Answers
    packet += struct.pack(">H", 0)  # Authorities
    packet += struct.pack(">H", 0)  # Additional
    split_url = target.split(".")
    for part in split_url:
        packet += struct.pack("B", len(part))
    for s in part:
        packet += struct.pack('c',s.encode())
    packet += struct.pack("B", 0)  # End of String
    packet += struct.pack(">H", 1)  # Query Type
    packet += struct.pack(">H", 1)  # Query Class
    return packet

def port_scan(port,host,scan_type):
    
    if scan_type=='T':
        try:
        # creating the socket object with AF_INET=> ipv4 address and sock_stream means use tcp protocol to create connection!
            client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            
            # Setting the timeout to 1 s
            client.settimeout(1)
            # Connecting to host at a specific port ! 
            client.connect((host,port))
            
        except KeyboardInterrupt:
            print ('You pressed Ctrl+C')
            exit(1)
        except:
            with lock:
                pass
        else:
            # Locking the thread to avoid race condition
            with lock: 
                print(f"{port}\tOpen")
        finally:
            client.close()    
            
    if scan_type=='U':
        # In case of udp there is a problem as on open port udp doesn't replies back
        for _ in range(5): # doing it 5 times to avoid packey failure 
            try:
                # getting the dns packet
                packet=udp_packet_build(host)
                # Sock_Dgram => means using protocol as UDP
                sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
                sock.timeout(1)
                # Sending the crafted packet
                sock.sendto(bytes(packet),(host,port))
                data,addr=sock.recvfrom(1024)
                sock.close()
            except Exception as err:
                pass
                with lock:
                    pass
            else:
                with lock:
                    print(f"{port}\tOpen")
    

def scan_thread(host,scan_type):
    global q
    while True:
        
        # getting the port number from queue, this will also remove the portno. from queue
        worker=q.get()
        
        # executing the main function 
        port_scan(worker,host,scan_type)
        
        # it ensures that the task is done ! 
        q.task_done()
    
def main(scan_type,host,start_port,end_port,threads):
    global q
    
    # creating a list of ports because we will put it the all the ports in queue
    ports=[i for i in range(start_port,end_port)]   
    
    
    for thread in range(threads):
        # Creating threads 
        thread=Thread(target=scan_thread,args=(host,scan_type))
        # We are making  the threads deaemon threads so they can run in background and help the other threads in executing ! 
        thread.daemon=True
        # we are also starting the thread 
        thread.start()
        
        
    for worker in ports:
        # We are putting the each port in queue
        q.put(worker)    
    # Used to wait until all the other threads don't finish
    q.join()

if __name__=="__main__":
    # parsing the arguments
    arguments=get_args()
    
    # Creating a global Queue data structure and Lock object 
    q=Queue()
    
    # this lock will be used to lock threads | To avoid Racecondition
    lock=Lock()
    
    # parsing the ports !
    start_port,end_port=arguments.ports.split('-')

    # For arp Scan ! 
    if arguments.arp:
        print("\n----------------------------------------\n\tArp Ping Scan Results \n-----------------------------------------")
        arp_ping(arguments.target)
        
   # For port Scans ! 
    if arguments.tcpPortScan:
        print("\n----------------------------------------\n\tTCP Port Scan Results \n-----------------------------------------")
        print("---------------------------\nPort\tState\n---------------------------")
        scan_type='T'
        main(scan_type,arguments.target,int(start_port),int(end_port),arguments.threads)
        
        
    if arguments.udpPortScan:
        print("\n----------------------------------------\n\tUDP Port Scan Results \n-----------------------------------------")
        print("---------------------------\nPort\tState\n---------------------------")
        scan_type='U'
        main(scan_type,arguments.target,int(start_port),int(end_port),arguments.threads)