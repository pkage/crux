##
# crux web api data routes
# this is kinda tricky b/c we need a stateful web server
# @author Patrick Kage

import zmq
from aiohttp import web
from crux.backend.daemon_api import DaemonAPI

class CruxAPIServer:
    # zmq stuff
    __context = None

    # daemon api
    dapi = None

    # currently editing pipeline
    pline = None
    agent = None

    def __init__(self):
        self.__context = zmq.Context()

    def attach_routes(self, app):
        app.router.add_get('/api/daemon/connect', self.connect_daemon)

    # --- daemon methods ---
    async def connect_daemon(self, req):
        """Connect daemon (POST)

        :param req: request
        """
        if self.dapi is None:
            self.dapi = DaemonAPI(req.query['daemon'], context=self.__context)
        else:
            self.dapi.disconnect()
            self.dapi.connect(req.query['daemon'])
        return web.Response(text='OK')

