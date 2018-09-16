from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from typing import Text, Any, Dict

from rasa_core.nlg.generator import NaturalLanguageGenerator
from rasa_core.trackers import DialogueStateTracker
from rasa_core.utils import EndpointConfig

logger = logging.getLogger(__name__)


def nlg_response_format_spec():
    """Expected response schema for an NLG endpoint.

    Used for validation of the response returned from the NLG endpoint."""
    return {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "buttons": {
                "type": "array",
                "items": {"type": "object"}
            },
            "elements": {
                "type": "array",
                "items": {"type": "object"}
            },
            "attachment": {"type": "object"}
        },
    }


def nlg_request_format_spec():
    """Expected request schema for requests sent to an NLG endpoint."""

    return {
        "type": "object",
        "properties": {
            "template": {"type": "string"},
            "arguments": {"type": "object"},
            "tracker": {
                "type": "object",
                "properties": {
                    "sender_id": {"type": "string"},
                    "slots": {"type": "object"},
                    "latest_message": {"type": "object"},
                    "latest_event_time": {"type": "number"},
                    "paused": {"type": "boolean"},
                    "events": {"type": "array"}
                }
            },
            "channel": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"}
                }
            }
        },
    }


def nlg_request_format(template_name, tracker, output_channel, **kwargs):
    # type: (Text, DialogueStateTracker, Text, **Any) -> Dict[Text, Any]
    """Create the json body for the NLG json body for the request."""

    tracker_state = tracker.current_state(
            should_include_events=True, only_events_after_latest_restart=True)

    return {
        "template": template_name,
        "arguments": kwargs,
        "tracker": tracker_state,
        "channel": {
            "name": output_channel
        }
    }


class CallbackNaturalLanguageGenerator(NaturalLanguageGenerator):
    """Generate bot utterances by using a remote endpoint for the generation.

    The generator will call the endpoint for each message it wants to
    generate. The endpoint needs to respond with a properly formatted
    json. The generator will use this message to create a response for
    the bot."""

    def __init__(self, endpoint_config):
        # type: (EndpointConfig) -> None

        self.nlg_endpoint = endpoint_config

    def generate(self, template_name, tracker, output_channel, **kwargs):
        # type: (Text, DialogueStateTracker, Text, **Any) -> Dict[Text, Any]
        """Retrieve a named template from the domain using an endpoint."""

        body = nlg_request_format(template_name,
                                  tracker,
                                  output_channel,
                                  **kwargs)

        response = self.nlg_endpoint.request(method="post", json=body)
        response.raise_for_status()

        content = response.json()
        if self.validate_response(content):
            return content
        else:
            raise Exception("NLG web endpoint returned an invalid response.")

    @staticmethod
    def validate_response(content):
        # type: (content) -> bool
        """Validate the NLG response. Raises exception on failure."""
        from jsonschema import validate
        from jsonschema import ValidationError

        try:
            validate(content, nlg_response_format_spec())
            return True
        except ValidationError as e:
            e.message += (
                ". Failed to validate NLG response from API, make sure your "
                "response from the NLG endpoint is valid. "
                "For more information about the format visit "
                "https://nlu.rasa.com/...")
            raise e
