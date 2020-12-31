import atexit
import inspect
import sys
from wsgiref.simple_server import make_server


class Routes:
    """Provides a registry for routing"""
    registry = {}

    @classmethod
    def add(cls, fn):
        cls.registry[f'/{fn.__name__}'] = fn


def app(environ, start_response):
    """Check the route registry and call the appropriate function on a match (coercing the return value to bytes"""
    headers = [('Content-type', 'text/plain; charset=utf-8')]

    path = environ['PATH_INFO']

    if path in Routes.registry:
        status = '200 OK'
        resp = bytes(Routes.registry[path](), 'utf-8')
    else:
        status = '404 Not Found'
        resp = b'Not Found'

    start_response(status, headers)
    return [resp + b'\n']


@atexit.register
def run():
    main = sys.modules['__main__']

    for dir_entry in dir(main):
        obj = getattr(main, dir_entry)
        if inspect.isfunction(obj) and not obj.__name__.startswith('_'):
            Routes.add(obj)

    with make_server('', 8000, app) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
