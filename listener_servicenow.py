#!/usr/bin/python3.6

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import requests
import json

# ServiceNow configuration
# URL and authorization
serviceNowURL = "https://dev75809.service-now.com/api/now/table/incident"
authorization = "YWRtaW46UW5GSENwaDl0NUxl"

hostName = "172.23.193.87"
hostPort = 24001

# Create the ServiceNow ticket with the following information
# alert information from KPI alert
def createServiceNowTicket(ticket_short_description, ticket_description):
    url = "https://dev75809.service-now.com/api/now/table/incident"
    payload = '{"description": "ticket_description", \
                "short_description": "ticket_short_description"}'
    payload = payload.replace("ticket_short_description", str(ticket_short_description))
    payload = payload.replace("ticket_description", str(ticket_description))
    print("payload  :", payload)
    headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Basic YWRtaW46UW5GSENwaDl0NUxl',
    }
    response = requests.request("POST", url, headers=headers, data = payload)
    print(response.status_code)

#FILEHANDLE = open("/root/cw-logs/crossworkHiAlerts.txt", "w+")
class MyServer(BaseHTTPRequestHandler):


    #    GET is for clients geting the predi
    def do_GET(self):
        self.send_response(200)
        self.wfile.write(bytes("<p>You accessed path: %s</p>" % self.path, "utf-8"))

    #    POST is for submitting data.
    def do_POST(self):
        print( "incomming http: ", self.path )

        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print(post_data)
        print ("POST_DATA type   :  ", type(post_data))
        self.send_response(200)

        # HI Alert format
        # series [
        #           {
        #               'name' : 'alert'
        #               'tags' : { + }
        #               'columns' : [ + ]
        #               'values' : [ + ]
        #           }
        # pager_incident_data is create by mapping attributes in columns field to corresponding values in 'values' field
        data = json.loads(post_data)
        print("DATA type   :  ", type(data))
        print("DATA    :  ", (data))
        dl = list(data.values())
        dll = dl[0]
        dll_2 = dll[0]
        dll_2.pop('name')
        dll_2.pop('tags')
        column_list = dll_2.pop('columns')
        values_list = dll_2.pop('values')
        incident_details = dict(zip(column_list, values_list[0]))
        incident_title = incident_details.get('id')
        incident_description = incident_details.get('msg')

        # TODO
        #Filter the alarms to process only the required alarms

        # Create ServiceNow Ticket
        print(time.asctime(), "short description, description - %s:%s" % (incident_title, incident_description))
        createServiceNowTicket(incident_title, incident_description)

myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    #FILEHANDLE.close()
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
