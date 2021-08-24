import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from eventy.trace_id import correlation_id_var
from eventy.integration.sanic import Sanic
from sanic.response import text

app = Sanic("My Hello, world app")


@app.route('/hello')
async def hello(request):
    return text(correlation_id_var.get())


@app.route('/health')
async def health(request):
    return text('ok')


if __name__ == '__main__':
    app.run()
