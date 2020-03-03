#!/usr/local/bin/python
import configparser
from urllib.parse import parse_qs
from dorado_gather import collect_data, prometheus_output

try:
    from http.server import BaseHTTPRequestHandler, HTTPServer
except Exception as e:
    e
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = config['DEFAULT']['port']
    if int(port) < 65535 and int(port) > 0:
        port = int(port)
except Exception as e:
    e
    port = 9720


class myHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # try:
        query = parse_qs(self.path)
        mpath = self.path
        ans = ''
        if '/?address' in str(mpath) and '/favicon.ico' not in str(mpath):
            address = query['/?address'][0].replace('%3A', ':').replace('%2F', '/')
            res = prometheus_output(collect_data(address))
        else:
            res = ''
        if mpath == '/metrics':
            ans += '<html><body><pre>'
        ans += res
        if mpath == '/metrics':
            ans += '</pre></body></html>'
        self.wfile.write(ans.encode())
        return


try:
    # Create a web server and define the handler to manage the
    # incoming request
    server = HTTPServer(('', port), myHandler)
    print('Started httpserver on port ', port)

    # Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
