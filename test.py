import json
from socket import *
import sys

s = socket(AF_INET, SOCK_STREAM)
s.connect(('localhost', 10000))
s.send(json.dumps({'op': 'out', 'tup': ('1', '2', '3', '4')}))
ans = s.recv(512)
resp = json.loads(ans)
print "\n"
print resp["res"]
print resp["tup"]

s.close()
