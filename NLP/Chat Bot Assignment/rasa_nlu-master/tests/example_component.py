from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_nlu.components import Component


class MyComponent(Component):
    """A new component"""

    # Name of the component to be used when integrating it in a
    # pipeline. E.g. ``[ComponentA, ComponentB]``
    # will be a proper pipeline definition where ``ComponentA``
    # is the name of the first component of the pipeline.
    name = ""

    # Defines what attributes the pipeline component will
    # provide when called. The listed attributes
    # should be set by the component on the message object
    # during test and train, e.g.
    # ```message.set("entities", [...])```
    provides = []

    # Which attributes on a message are required by this
    # component. e.g. if requires contains "tokens", than a
    # previous component in the pipeline needs to have "tokens"
    # within the above described `provides` property.
    requires = []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {}

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None which means it can handle all languages.
    # This is an important feature for backwards compatibility of components.
    language_list = None

    def __init__(self, component_config=None):
        super(MyComponent, self).__init__(component_config)

    def train(self, training_data, cfg, **kwargs):
        """Train this component.

        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.train`
        of components previous to this one."""
        pass

    def process(self, message, **kwargs):
        """Process an incoming message.

        This is the components chance to process an incoming
        message. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`components.Component.pipeline_init`
        of ANY component and
        on any context attributes created by a call to
        :meth:`components.Component.process`
        of components previous to this one."""
        pass

    def persist(self, model_dir):
        """Persist this component to disk for future loading."""

        pass

    @classmethod
    def load(cls, model_dir=None, model_metadata=None, cached_component=None,
             **kwargs):
        """Load this component from file."""

        if cached_component:
            return cached_component
        else:
            component_config = model_metadata.for_component(cls.name)
            return cls(component_config)
