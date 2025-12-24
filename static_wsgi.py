def application(environ, start_response):
    with open("./static/test.html", "rb") as f:
        body = f.read()

    start_response("200 OK", [
        ("Content-Type", "text/html"),
        ("Content-Length", str(len(body))),
    ])
    return [body]
