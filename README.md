# IPv4_to_IPv6_address_generator
The IPv4_to_IPv6_address_generator helper tool allows you to convert an IPv4 address to an IPv6 Link Local one. To do so it first pings the provided IPv4 address to ensure that the corresponding MAC is cached in the ARP table. After that is extracts the MAC and converts it to the Link Local IPv6 address based on RFC2464. Finally you can select if you want to run nmap an the newly generated address.

# Usage
./IPv4_to_IPv6_address_generator.py <<IP address to convert>> [network portion (defaults to fe80)]

Example: ./IPv4_to_IPv6_address_generator.py 10.0.0.138

# Sample Output
./IPv4_to_IPv6_address_generator.py 10.0.0.138
Will ping IP 10.0.0.138 to ensure that MAC is in ARP table
Will search of MAC of IP 10.0.0.138 in ARP table
Found MAC: a4526f447e69
Original MAC: a4526f447e69
Original binary MAC: 101001000101001001101111010001000111111001101001
7th Bit flipped MAC: 101001100101001001101111010001000111111001101001
New MAC: a6526f447e69
EUI: a6526ffffe447e69
Will generate IPv6 address of EUI a6526ffffe447e69 in network fe80

==============================================
IPv6 Address: fe80::a652:6fff:fe44:7e69
==============================================
