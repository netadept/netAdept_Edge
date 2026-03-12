from ipwhois import IPWhois
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('ip_address', help='ip address of host to connect to single device')

args = parser.parse_args()
ip = (args.ip_address)

def get_ip_ownership(ip):
    try:
        obj = IPWhois(ip)
        # Use lookup_rdap() for the recommended method (provides richer data)
        results = obj.lookup_rdap(asn_methods=["whois"])
        
        print(f"IP: {results['query']}")
        print(f"ASN: {results['asn']}")
        print(f"ASN Description: {results['asn_description']}")
        print(f"Country: {results['asn_country_code']}")
        
        print("\nNetwork Details:")
        for net in results['network']['links']:
            print(f"  - {net}")
            
        print("\nContact Info:")
        for entity, data in results['objects'].items():
            print(f"  - Entity: {entity}")
            print(f"    Name: {data['contact']['name']}")
            print(f"    Address: {data['contact']['address'][0]['value']}")
            print(f"    Email: {data['contact']['email']}")
            
    except Exception as e:
        print(f"Error: {e}")

# Example usage
get_ip_ownership(f"{ip}")  # Google DNS