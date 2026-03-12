import whois
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('domain', help='domain name to check')
args = parser.parse_args()
domain = (args.domain)

def whatis():
	w = whois.whois(f"{domain}")
	print(w.text)

whatis()
