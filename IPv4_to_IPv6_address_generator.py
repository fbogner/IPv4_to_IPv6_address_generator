import sys
import os
import re
from subprocess import check_call, check_output


DEVNULL = open(os.devnull, 'wb')

def isWin():
	return (sys.platform=="win32")

def isLinux():
	return (sys.platform=="linux2")

def add_mac_address_of_ip_to_arp_table(ip):
	
	global DEVNULL	# get the global dev null device to easily discard all command output
	
	print "Will ping IP "+ip+" to ensure that MAC is in ARP table"
	
	if isWin():
		
		try:
			# ping the adress and ignore the result as long as it's not an excaption
			check_call(['ping','-w','1','-n','1',ip], stdout=DEVNULL, stderr=DEVNULL)
			return True
		except:
			return False

	elif isLinux():	
		try:
			check_call(['ping','-W','1','-c','1',ip], stdout=DEVNULL, stderr=DEVNULL)
			return True
		except:
			return False
	else:
		raise EnvironmentError('Operating system ('+sys.platform+') not supported')

def get_mac_for_ip(ip):

	global DEVNULL	# get the global dev null device to easily discard all command output

	print "Will search of MAC of IP "+ip+" in ARP table"
	
	if isWin():
		
		try:
			# query the arp table and parse it line by line until we fine the one with the given ip address
			arp_table = check_output(['arp','-a'], stderr=DEVNULL)
			matcher = re.compile('([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})\s*([0-9a-f]{2}\-[0-9a-f]{2}\-[0-9a-f]{2}\-[0-9a-f]{2}\-[0-9a-f]{2}\-[0-9a-f]{2})')
			parsed_table = matcher.findall( arp_table )
			
			for current_ip,current_mac in parsed_table:
				
				if ip == current_ip:
					# TODO Convert to HEX
					pattern = re.compile('[\W_]+')
					current_mac=pattern.sub('', current_mac)
					
					print "Found MAC: "+current_mac
					
					return current_mac
						
			return False
		except:
			return False
	elif isLinux():
		
		try:
			# query the arp table and parse it line by line until we fine the one with the given ip address
			arp_table = check_output(['arp','-n'], stderr=DEVNULL)
			matcher = re.compile('([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})[\s\w]*([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})')
			parsed_table = matcher.findall( arp_table )
			#print parsed_table
			for current_ip,current_mac in parsed_table:
				#print current_ip
				#print current_mac
				if ip == current_ip:
					# TODO Convert to HEX
					pattern = re.compile('[\W_]+')
					current_mac=pattern.sub('', current_mac)
					
					print "Found MAC: "+current_mac
					
					return current_mac
						
			return False
		except:
			return False
	else:
		raise EnvironmentError('Operating system ('+sys.platform+') not supported')

def generate_EUI_64_of_mac(mac):
	print "Original MAC: "+mac
	
	# print MAC in binary 
	binary_mac="{0:048b}".format(int(mac,16))
	print "Original binary MAC: "+binary_mac
	
	# flip the 7th bit as defined by https://tools.ietf.org/html/rfc4291#section-2.5.1
	new_7th_bit=1
	if binary_mac[6]==1:
		new_7th_bit[6]=0
	
	new_binary_mac = binary_mac[:6] + str(new_7th_bit) + binary_mac[7:]
	
	print "7th Bit flipped MAC: "+new_binary_mac
	
	# prefix the mac with 0s if needed
	new_mac=format(int(new_binary_mac,2),'x').zfill(12)
	print "New MAC: "+ new_mac
	
	# add fffe in the center of the string also as defined by https://tools.ietf.org/html/rfc4291#section-2.5.1
	new_eui_mac = new_mac[:6]+"fffe"+new_mac[6:]
	print "EUI: "+new_eui_mac
	
	return new_eui_mac

def EUI_to_ipv6_address(eui,network="fe80"):

	print "Will generate IPv6 address of EUI "+eui+" in network "+network
	
	eui_list=list(eui)
	
	# build the full address based on the eui
	return 	network+"::"+ list_to_hex_string(eui_list[:4])+':'+	list_to_hex_string(eui_list[4:8])+':'+ list_to_hex_string(eui_list[8:12])+':'+list_to_hex_string(eui_list[12:16])
	
def list_to_hex_string(sublist):
	hex_with_leading_zeros = "".join(sublist)	# build a string from the list
	return "{0:x}".format(int(hex_with_leading_zeros,16)) # convert hex string to an int and back to hex. This removes leading zeros!

def call_nmap(ipv6):
	
	if isWin():
		print 'Will run: nmap.exe -6 '+ipv6
		os.system('nmap.exe -6 '+ ipv6)
		return
	if isLinux():
		print 'Will run: sudo nmap -6 ' + ipv6 + ' -Pn'
		os.system('sudo nmap -6 ' + ipv6 + ' -Pn')
		return	
	raise EnvironmentError('Operating system ('+sys.platform+') not supported')

	
def main():
	
	if len(sys.argv) != 2 and len(sys.argv) != 3:
		print("Wrong number of arguments! (On Windows start me using the python interpreter)")
		print("Usage: python "+sys.argv[0]+" <IP address to convert> [network portion (defaults to fe80)]")
		exit(1)
		
	ip=sys.argv[1]
	network = 'fe80'
	if len(sys.argv) == 3: 
		network = sys.argv[2]
	
	# ping the IPv4 address to ensure the MAC is in the ARP table
	if not add_mac_address_of_ip_to_arp_table(ip):
		print('Failed to ping '+ip)
		exit(1)
	
	# fetch the MAC from the ARP table
	mac = get_mac_for_ip(ip)
	if mac == False:
		print 'Failed to get MAC for IP '+ip
		exit(1)
	
	# build the EUI-64 based on the MAC
	eui = generate_EUI_64_of_mac(mac)
	
	# finally construct the ipv6 address
	ipv6=EUI_to_ipv6_address(eui,network)
	
	print 
	print "=============================================="
	print 'IPv6 Address: '+ipv6
	print "=============================================="
	print
	
		
	if raw_input("Type the letter n to directly launch nmap or anything else to quit: ") == 'n':
		call_nmap(ipv6)
	
	
if __name__ == "__main__":
	main()