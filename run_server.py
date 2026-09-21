import http.server
import socketserver
import os
import urllib.parse

PORT = 3000
DIRECTORY_SRC = os.path.join(os.path.dirname(__file__), 'src', 'dashboard')
DIRECTORY_PUBLIC = os.path.join(os.path.dirname(__file__), 'public')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Remove query parameters
        path = urllib.parse.urlparse(path).path
        
        # If the request matches a folder in public, serve from public
        if path.startswith('/public/'):
            path = path[len('/public/'):]
            return os.path.join(DIRECTORY_PUBLIC, path.lstrip('/'))
            
        if path.startswith('/data/') or path.startswith('/overlays/') or path.startswith('/geojson/') or path.startswith('/assets/'):
            return os.path.join(DIRECTORY_PUBLIC, path.lstrip('/'))
            
        # Otherwise serve from src/dashboard
        if path == '/':
            path = '/index.html'
            
        return os.path.join(DIRECTORY_SRC, path.lstrip('/'))

print(f"Serving at http://localhost:{PORT}")
with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
