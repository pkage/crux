##
# crux web dashboard
# powered by asyncio/aiohttp
# @author Patrick Kage

import pkg_resources
from aiohttp import web
import aiohttp_cors
from . import api

@web.middleware
async def cors_middleware(req, handler):
    resp = await handler(req)
    if req.method == 'GET':
        resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

def run_app(port):
    app = web.Application(middlewares=[cors_middleware])

    # set up cors
    cors = aiohttp_cors.setup(app, defaults={
        '*': aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers='*',
            allow_headers='*'
        )
    })

    # really quick hack: redirect '/' to '/index.html'
    async def redirect_base(req):
        return web.HTTPFound('/index.html')
    app.router.add_get('/', redirect_base)

    # create and attach the API server
    capi = api.CruxAPIServer()
    capi.attach_routes(app)

    # configure cors on all routes.
    for route in list(app.router.routes()):
        try:
            cors.add(route)
        except RuntimeError as re:
            pass

    # resolve static file path & serve
    static_files = pkg_resources.resource_filename('crux.wizards.web', 'static/')
    app.router.add_static('/', static_files)

    # if we've installed the webdebug extra, attach the debugger
    try:
        import aiohttp_debugtoolbar
        aiohttp_debugtoolbar.setup(app)
    except:
        raise

    # launch the app
    web.run_app(app, port=port)

