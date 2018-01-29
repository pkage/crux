##
# Crux data pipeline manager
# @author Patrick Kage

from copy import deepcopy
from crux.common.logging import Logger
from crux.common.exception import CruxException
from crux.common.messaging import Message
from crux.pipeline.component import Component

class PipelineError(CruxException):
    pass

# Pipeline manager class
class Pipeline:
    """Pipeline manager class

    This class is intended to provide a programmatic way to manipulate pipeline definitions, not as a direct execution agent
    """
    # housekeeping
    __log = None

    # pipeline information
    pipeline = []
    components = {}

    def __init__(self, context=None):
        """Initialize the pipeline

        :param context: the zmq context to use. one will be created if one is not provided.
        """
        # logger name 'pipeline'
        self.__log = Logger(logging=True, name='pipeline')

        # init context
        if context is None:
            self.__log.warn('pipeline is making its own zmq context, something is probably wrong')
            self.__context = zmq.Context()

    def get_order(self):
        return range(len(self.pipeline))

    def set_order(self, order):
        """Set the order of components to execute
        This is a set 0-len(pipeline), with the swaps out of order

        :param order: an array of integers
        """

        # make sure every element of the order set is unique
        if len(set(order)) != len(order) or set(range(len(self.pipeline))) != set(order):
            raise PipelineError('invalid order array!')

        # rebuild the pipeline with the new order (illuminati?)
        pipeline = []
        for idx in order:
            pipeline.append(self.pipeline[idx])
        self.pipeline = pipeline

        self.__log('re-ordered pipeline to {}'.format(order))

    def step_add(self, component, idx=None):
        """Add a step to this pipeline

        :param component: name of the component to load
        :param idx: (optional) index to insert into
        :raises PipelineError: on unloaded component
        """

        self.__log('adding {} to pipeline position {}'.format(component, idx if idx is not None else 'end'))

        # throw if we don't have that component
        if not component in self.components:
            raise PipelineError('component "{}" is not loaded!'.format(component))

        # insert at the end
        if idx is None:
            idx = len(self.pipeline)

        self.pipeline.insert(idx, {
            "component": component,
            "parameters": {}
        })

    def step_remove(self, idx):
        """Remove a step from the pipeline

        :param idx: index to remove
        """
        del self.pipeline[idx]

    def step_config(self, idx, cfg):
        """Configure a step of the pipeline

        :param idx: index to target
        :param cfg: values to replace with
        """
        self.pipeline[idx] = cfg

    def component_load(self, name, src, version):
        """Load a component into this pipeline

        :param name: name of the component
        :param src: src (URI, filepath, git)
        :param version: semver version constraint string
        :raises PipelineError: if component is already loaded
        """
        if name in self.components:
            raise PipelineError('component "{}" already loaded!'.format(name))

        self.components[name] = {
            'src': src,
            'version': version
        }

    def component_unload(self, name):
        """Unload a component from the pipeline

        This takes into account if any steps in the pipeline depend on the component
        If so, the component will not be unloaded and the step must be removed.

        :param name: name of the component
        :raises Pipe
        """
        if not name in self.components:
            raise PipelineError('component "{}" not loaded, cannot remove!'.format(name))

        for i in range(len(self.pipeline)):
            step = self.pipeline[i]
            if step['component'] == name:
                raise PipelineError('component "{}" in use by step {}!'.format(name, i))

        del self.components[name]

    def load(self, data):
        """Import a pipeline configuration for editing

        :param data: data to import from (json string or dict)
        """

        # coerce from json string if it's not a dict
        if type(data) is not dict:
            data = json.loads(data)

        self.components = data['components']
        self.pipeline = data['pipeline']

    def save(self):
        """Export the pipeline configuration for this machine

        :returns: pipeline config (deepcopy)
        """
        return deepcopy(self.components)

