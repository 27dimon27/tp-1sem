def application(environ, start_response):
    path = environ.get('PATH_INFO', '/')

    if path == '/sample.html':
        with open('static/sample.html', 'rb') as f:
            data = f.read()

        start_response('200 OK', [
            ('Content-Type', 'text/html'),
            ('Content-Length', str(len(data)))
        ])
        return [data]

    response = b'Dynamic response'
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return [response]
