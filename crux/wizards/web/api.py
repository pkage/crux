##
# crux web api data routes
# this is kinda tricky b/c we need a stateful web server
# @author Patrick Kage

import zmq
from aiohttp import web
from crux.common.socket import RequestTimeoutException
from crux.common.logging import Logger
from crux.common.messaging import Message
from crux.common.validation import validate_uri
from crux.pipeline.component import Component
from crux.backend.daemon_api import DaemonAPI
from crux.backend.pipelineagent import PipelineAgent

class CruxAPIServer:
    # housekeeping
    log = None

    # zmq stuff
    __context = None
    REQ_TIMEOUT = 2500 # milliseconds

    # daemon api
    dapi = None

    # currently editing pipeline
    pline = None
    agent = None

    def __init__(self):
        self.log = Logger(name='webapi', logging=True)
        self.__context = zmq.Context()

    def attach_routes(self, app):
        """Attach webapi routes

        :param app: aiohttp web app
        """
        app.router.add_get( '/api/daemon/connect',  self.connect_daemon)
        app.router.add_get( '/api/daemon/get',      self.get_daemons)
        app.router.add_get( '/api/components/list', self.get_all_components)
        app.router.add_get( '/api/components/get',  self.get_component)
        app.router.add_get( '/api/components/load', self.load_component)
        app.router.add_post('/api/components/send', self.send_to_component)

    # --- helper methods ---
    def create_error(self, msg=None):
        resp = {'success': False}
        if msg is not None:
            resp['message'] = msg
            self.log.warn('failing request with "{}"!'.format(msg))
        else:
            self.log.warn('failing request!')
        return web.json_response(resp)

    # --- daemon methods ---
    async def connect_daemon(self, req):
        """Connect daemon (POST)

        HTTP method: GET
        Query params: daemon

        :param req: request from webserver
        """
        if not 'daemon' in req.query:
            return self.create_error('"daemon" is a required parameter!')

        if not validate_uri(req.query['daemon']):
            return self.create_error('"{}" is not a valid address!'.format(req.query['daemon']))

        self.log.info('connecting daemon {}'.format(req.query['daemon']))
        if self.dapi is None:
            self.dapi = DaemonAPI(req.query['daemon'], context=self.__context)
        else:
            self.dapi.disconnect()
            self.dapi.connect(req.query['daemon'])

        return web.json_response({'success': True})

    async def get_daemons(self, req):

        if self.dapi is None:
            return web.json_response({
                'address': None,
                'success': True
            })
        else:
            return web.json_response({
                'address': self.dapi.get_addr(),
                'success': True
            })

    # --- component methods ---

    def resolve_component(self, addr, timeout=None):
        return Component(addr, context=self.__context, timeout=timeout if timeout is not None else self.REQ_TIMEOUT)

    async def get_all_components(self, req):
        """get_all_components

        HTTP method: GET

        :param req: request from webserver
        """
        self.log.info('getting all components')

        if self.dapi is None:
            return self.create_error('no daemon connected')

        # enumerate all component addresses
        processes = self.dapi.process_list()

        # fail if enumeration fails
        if not processes.success:
            self.log.warn('failed to get processes')
            return self.create_error('failed to get processes')
        else:
            processes = processes.payload

        # extract cruxfile from all components
        out = {}
        for address in processes:
            try:
                out[address] = self.resolve_component(address, timeout=self.REQ_TIMEOUT).cruxfile
            except RequestTimeoutException as rte:
                pass

        # pass back
        return web.json_response({
            'components': out,
            'success': True
        })

    async def get_component(self, req):
        """Get a running component

        HTTP method: GET
        Query params: address

        :param req: request from webserver
        """
        if not 'address' in req.query:
            return self.create_error('"address" is a required parameter!')

        self.log.info('getting component {}'.format(req.query['address']))

        try:
            component = self.resolve_component(req.query['address']).cruxfile
        except RequestTimeoutException as rte:
            return self.create_error('Request to {} timed out!'.format(req.query['address']))

        return web.json_response({
            'component': component,
            'success': True
        })

    async def load_component(self, req):
        """Load component onto the daemon

        HTTP method: GET
        Query params: path

        :param req: request from webserver
        """
        if not 'path' in req.query:
            return self.create_error('"address" is a required parameter!')

        if self.dapi is None:
            return self.create_error('no daemon connected')

        self.log.info('loading {} onto daemon'.format(req.query['path']))

        resp = self.dapi.process_start(req.query['path'])

        if not resp.success:
            return self.create_error('process loading failed: {}'.format(resp.payload))

        return web.json_response({
            'component': resp.payload,
            'success': True
        })

    async def send_to_component(self, req):
        """Send a query to a component

        HTTP method: POST
        Query params: address

        :param req: request from webserver
        """

        if not 'address' in req.query:
            return self.create_error('"address" is a required parameter!')

        msg = await req.json()

        print(msg)

        if not 'name' in msg:
            return self.create_error('name not in message!')

        try:
            component = self.resolve_component(req.query['address'])
        except RequestTimeoutException as rte:
            return self.create_error('request to {} timed out!'.format(req.query['address']))

        self.log('component resolved!')

        # craft the request
        request = Message(name=msg['name'])
        if 'payload' in msg:
            request.payload = msg['payload']

        # make the request
        try:
            response = component.request(request, timeout=self.REQ_TIMEOUT)
        except RequestTimeoutException as rte:
            return self.create_error('request to {} timed out!'.format(req.query['address']))

        # prepare the JSON response
        resp = {
            'name': response.name,
            'success': response.success,
            'payload': response.payload
        }

        # respond
        return web.json_response({
            'response': resp,
            'success': True
        })

