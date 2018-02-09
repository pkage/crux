##
# crux web dashboard
# powered by asyncio/aiohttp
# @author Patrick Kage

import pkg_resources
from aiohttp import web
from . import api


def run_app(port):
    app = web.Application()
    # really quick hack: redirect '/' to '/index.html'
    async def redirect_base(req):
        return web.HTTPFound('/index.html')
    app.router.add_get('/', redirect_base)

    # create and attach the API server
    capi = api.CruxAPIServer()
    capi.attach_routes(app)

    # resolve static file path & serve
    static_files = pkg_resources.resource_filename('crux.wizards.web', 'static/')
    app.router.add_static('/', static_files)

    # launch the app
    web.run_app(app, port=port)

