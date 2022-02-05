import json
import os,sys,codecs
from datetime import datetime

def application(environ, start_response):
    status = '200 OK' 
    
    timestamp  = datetime.now().strftime('%Y  -  %m  -  %d   %H  :  %M  :  %S') 
    #output = 'Hello zc!--------' + timestamp
    
    with codecs.open("/usr/local/zc/httpd/first_edition/data_center.json", "r","utf-8") as f: 
    	    json_file = json.load(f)
            output =json.dumps(json_file)
            #output = 'str' 
#print(output)

    response_headers = [('Content-type', 'text/plain'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]

