import json
import os
import sys
import urllib.error
import urllib.request

# Executed inside the supplied client Pod; never prints its credential.
method, url = sys.argv[1:3]
body = json.dumps({'text': sys.argv[3]}).encode() if method == 'POST' else None
request = urllib.request.Request(url, data=body, method=method, headers={
    'Authorization': 'Bearer ' + os.environ['API_TOKEN'],
    'Content-Type': 'application/json',
})
try:
    with urllib.request.urlopen(request, timeout=5) as response:
        print('HTTP', response.status)
        print(response.read().decode())
except (urllib.error.URLError, TimeoutError) as error:
    print('Request failed:', error)
    sys.exit(1)
