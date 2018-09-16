from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import json
import logging
import uuid
from collections import deque, defaultdict

import typing
from typing import \
    List, Text, Dict, Optional, Tuple, Any, Set, ValuesView

from rasa_core import utils
from rasa_core.actions.action import ACTION_LISTEN_NAME
from rasa_core.conversation import Dialogue
from rasa_core.events import UserUttered, ActionExecuted, Event

if typing.TYPE_CHECKING:
    from rasa_core.domain import Domain

logger = logging.getLogger(__name__)

# Checkpoint id used to identify story starting blocks
STORY_START = "STORY_START"

# Checkpoint id used to identify story end blocks
STORY_END = None

# need abbreviations otherwise they are not visualized well
GENERATED_CHECKPOINT_PREFIX = "GENR_"
CHECKPOINT_CYCLE_PREFIX = "CYCL_"

GENERATED_HASH_LENGTH = 5


class Checkpoint(object):
    def __init__(self, name, conditions=None):
        # type: (Optional[Text], Optional[Dict[Text, Any]]) -> None

        self.name = name
        self.conditions = conditions if conditions else {}

    def as_story_string(self):
        dumped_conds = json.dumps(self.conditions) if self.conditions else ""
        return "{}{}".format(self.name, dumped_conds)

    def filter_trackers(self, trackers):
        """Filters out all trackers that do not satisfy the conditions."""

        if not self.conditions:
            return trackers

        for slot_name, slot_value in self.conditions.items():
            trackers = [t
                        for t in trackers
                        if t.get_slot(slot_name) == slot_value]
        return trackers

    def __repr__(self):
        return "Checkpoint(name={!r}, conditions={})".format(
                self.name, json.dumps(self.conditions))


class StoryStep(object):
    def __init__(self,
                 block_name=None,  # type: Optional[Text]
                 start_checkpoints=None,  # type: Optional[List[Checkpoint]]
                 end_checkpoints=None,  # type: Optional[List[Checkpoint]]
                 events=None  # type: Optional[List[Event]]
                 ):
        # type: (...) -> None

        self.end_checkpoints = end_checkpoints if end_checkpoints else []
        self.start_checkpoints = start_checkpoints if start_checkpoints else []
        self.events = events if events else []
        self.block_name = block_name
        self.id = uuid.uuid4().hex  # type: Text

    def create_copy(self, use_new_id):
        copied = StoryStep(self.block_name, self.start_checkpoints,
                           self.end_checkpoints,
                           self.events[:])
        if not use_new_id:
            copied.id = self.id
        return copied

    def add_user_message(self, user_message):
        self.add_event(user_message)

    @staticmethod
    def _is_action_listen(event):
        return (isinstance(event, ActionExecuted) and
                event.action_name == ACTION_LISTEN_NAME)

    def add_event(self, event):
        # stories never contain the action listen events they are implicit
        # and added after a story is read and converted to a dialogue
        if not self._is_action_listen(event):
            self.events.append(event)

    def as_story_string(self, flat=False):
        # if the result should be flattened, we
        # will exclude the caption and any checkpoints.
        if flat:
            result = ""
        else:
            result = "\n## {}\n".format(self.block_name)
            for s in self.start_checkpoints:
                if s.name != STORY_START:
                    result += "> {}\n".format(s.as_story_string())
        for s in self.events:
            if isinstance(s, UserUttered):
                result += "* {}\n".format(s.as_story_string())
            elif isinstance(s, Event):
                converted = s.as_story_string()
                if converted:
                    result += "    - {}\n".format(s.as_story_string())
            else:
                raise Exception("Unexpected element in story step: "
                                "{}".format(s))

        if not flat:
            for e in self.end_checkpoints:
                result += "> {}\n".format(e.as_story_string())
        return result

    def explicit_events(self, domain, should_append_final_listen=True):
        # type: (Domain, bool) -> List[Event]
        """Returns events contained in the story step including implicit events.

        Not all events are always listed in the story dsl. This
        includes listen actions as well as implicitly
        set slots. This functions makes these events explicit and
        returns them with the rest of the steps events."""

        events = []

        for e in self.events:
            if isinstance(e, UserUttered):
                events.append(ActionExecuted(ACTION_LISTEN_NAME))
                events.append(e)
                events.extend(domain.slots_for_entities(e.entities))
            else:
                events.append(e)

        if not self.end_checkpoints and should_append_final_listen:
            events.append(ActionExecuted(ACTION_LISTEN_NAME))
        return events

    def __repr__(self):
        return "StoryStep(block_name={!r}, start_checkpoints={!r}, end_checkpoints={!r}, events={!r})".format(
                self.block_name,
                self.start_checkpoints,
                self.end_checkpoints,
                self.events)


class Story(object):
    def __init__(self, story_steps=None):
        # type: (List[StoryStep]) -> None
        self.story_steps = story_steps if story_steps else []

    @staticmethod
    def from_events(events):
        """Create a story from a list of events."""

        story_step = StoryStep()
        for event in events:
            story_step.add_event(event)
        return Story([story_step])

    def as_dialogue(self, sender_id, domain):
        events = []
        for step in self.story_steps:
            events.extend(
                    step.explicit_events(domain,
                                         should_append_final_listen=False))

        events.append(ActionExecuted(ACTION_LISTEN_NAME))
        return Dialogue(sender_id, events)

    def as_story_string(self, flat=False):
        story_content = ""
        for step in self.story_steps:
            story_content += step.as_story_string(flat)

        if flat:
            return "## Generated Story {}\n{}".format(
                    hash(story_content), story_content)
        else:
            return story_content

    def dump_to_file(self, filename, flat=False):
        with io.open(filename, "a") as f:
            f.write(self.as_story_string(flat))


class StoryGraph(object):
    def __init__(self, story_steps, story_end_checkpoints=None):
        # type: (List[StoryStep], Optional[Dict[Text, Text]]) -> None
        self.story_steps = story_steps
        self.step_lookup = {s.id: s for s in self.story_steps}
        ordered_ids, cyclic_edges = StoryGraph.order_steps(story_steps)
        self.ordered_ids = ordered_ids
        self.cyclic_edge_ids = cyclic_edges
        if story_end_checkpoints:
            self.story_end_checkpoints = story_end_checkpoints
        else:
            self.story_end_checkpoints = {}

    def ordered_steps(self):
        # type: () -> List[StoryStep]
        """Returns the story steps ordered by topological order of the DAG."""

        return [self.get(step_id) for step_id in self.ordered_ids]

    def cyclic_edges(self):
        # type: () -> List[Tuple[Optional[StoryStep], Optional[StoryStep]]]
        """Returns the story steps ordered by topological order of the DAG."""

        return [(self.get(source), self.get(target))
                for source, target in self.cyclic_edge_ids]

    @staticmethod
    def overlapping_checkpoint_names(cps, other_cps):
        # type: (List[Checkpoint], List[Checkpoint]) -> Set[Text]
        """Find overlapping checkpoints names"""

        return {cp.name for cp in cps} & {cp.name for cp in other_cps}

    def with_cycles_removed(self):
        # type: () -> StoryGraph
        """Create a graph with the cyclic edges removed from this graph."""

        story_end_checkpoints = self.story_end_checkpoints.copy()
        cyclic_edge_ids = self.cyclic_edge_ids
        # we need to remove the start steps and replace them with steps ending
        # in a special end checkpoint
        story_steps = {s.id: s for s in self.story_steps}

        # collect all overlapping checkpoints
        # we will remove unused start ones
        all_overlapping_cps = set()

        if self.cyclic_edge_ids:
            # we are going to do this in a recursive way. we are going to remove
            # one cycle and then we are going to let the cycle detection run again
            # this is not inherently necessary so if this becomes a performance
            # issue, we can change it. It is actually enough to run the cycle
            # detection only once and then remove one cycle after another, but
            # since removing the cycle is done by adding / removing edges and nodes
            # the logic is a lot easier if we only need to make sure the change is
            # consistent if we only change one compared to changing all of them.

            for s, e in cyclic_edge_ids:
                cid = utils.generate_id(max_chars=GENERATED_HASH_LENGTH)
                prefix = GENERATED_CHECKPOINT_PREFIX + CHECKPOINT_CYCLE_PREFIX
                # need abbreviations otherwise they are not visualized well
                sink_cp_name = prefix + "SINK_" + cid
                connector_cp_name = prefix + "CONN_" + cid
                source_cp_name = prefix + "SRC_" + cid
                story_end_checkpoints[sink_cp_name] = source_cp_name

                overlapping_cps = self.overlapping_checkpoint_names(
                        story_steps[s].end_checkpoints,
                        story_steps[e].start_checkpoints)

                all_overlapping_cps.update(overlapping_cps)

                # change end checkpoints of starts
                start = story_steps[s].create_copy(use_new_id=False)
                start.end_checkpoints = [cp
                                         for cp in start.end_checkpoints
                                         if cp.name not in overlapping_cps]
                start.end_checkpoints.append(Checkpoint(sink_cp_name))
                story_steps[s] = start

                needs_connector = False

                for k, step in list(story_steps.items()):
                    additional_ends = []
                    for original_cp in overlapping_cps:
                        for cp in step.start_checkpoints:
                            if cp.name == original_cp:
                                if k == e:
                                    cp_name = source_cp_name
                                else:
                                    cp_name = connector_cp_name
                                    needs_connector = True

                                if not self._is_checkpoint_in_list(
                                        cp_name, cp.conditions,
                                        step.start_checkpoints):
                                    # add checkpoint only if it was not added
                                    additional_ends.append(
                                            Checkpoint(cp_name, cp.conditions))

                    if additional_ends:
                        updated = step.create_copy(use_new_id=False)
                        updated.start_checkpoints.extend(additional_ends)
                        story_steps[k] = updated

                if needs_connector:
                    start.end_checkpoints.append(Checkpoint(connector_cp_name))

        # the process above may generate unused checkpoints
        # we need to find them and remove them
        self._remove_unused_generated_cps(story_steps,
                                          all_overlapping_cps,
                                          story_end_checkpoints)

        return StoryGraph(list(story_steps.values()),
                          story_end_checkpoints)

    @staticmethod
    def _checkpoint_difference(cps, cp_name_to_ignore):
        # type: (List[Checkpoint], Set[Text]) -> List[Checkpoint]
        """Finds checkpoints which names are
            different form names of checkpoints to ignore"""

        return [cp for cp in cps if cp.name not in cp_name_to_ignore]

    def _remove_unused_generated_cps(self, story_steps, overlapping_cps,
                                     story_end_checkpoints):
        # type: (Dict[Text, StoryStep], Set[Text], Dict[Text, Text]) -> None
        """Finds unused generated checkpoints
            and remove them from story steps."""

        unused_cps = self._find_unused_checkpoints(story_steps.values(),
                                                   story_end_checkpoints)

        unused_overlapping_cps = unused_cps.intersection(overlapping_cps)

        unused_genr_cps = {cp_name
                           for cp_name in unused_cps
                           if cp_name.startswith(GENERATED_CHECKPOINT_PREFIX)}

        k_to_remove = set()
        for k, step in story_steps.items():
            # changed all ends
            updated = step.create_copy(use_new_id=False)
            updated.start_checkpoints = self._checkpoint_difference(
                    updated.start_checkpoints, unused_overlapping_cps)

            # remove generated unused end checkpoints
            updated.end_checkpoints = self._checkpoint_difference(
                    updated.end_checkpoints, unused_genr_cps)

            if (step.start_checkpoints and not updated.start_checkpoints or
                    step.end_checkpoints and not updated.end_checkpoints):
                # remove story step if the generated checkpoints
                # were the only ones
                k_to_remove.add(k)

            story_steps[k] = updated

        # remove unwanted story steps
        for k in k_to_remove:
            del story_steps[k]

    @staticmethod
    def _is_checkpoint_in_list(checkpoint_name, conditions, cps):
        # type: (Text, Dict[Text, Any], List[Checkpoint]) -> bool
        """Checks if checkpoint with name and conditions is
            already in the list of checkpoints."""

        for cp in cps:
            if checkpoint_name == cp.name and conditions == cp.conditions:
                return True
        return False

    @staticmethod
    def _find_unused_checkpoints(story_steps, story_end_checkpoints):
        # type: (ValuesView[StoryStep], Dict[Text, Text]) -> Set[Text]
        """Finds all unused checkpoints."""

        collected_start = {STORY_END, STORY_START}
        collected_end = {STORY_END, STORY_START}

        for step in story_steps:
            for start in step.start_checkpoints:
                collected_start.add(start.name)
            for end in step.end_checkpoints:
                start_name = story_end_checkpoints.get(end.name, end.name)
                collected_end.add(start_name)

        return collected_end.symmetric_difference(collected_start)

    def get(self, step_id):
        # type: (Text) -> Optional[StoryStep]
        """Looks a story step up by its id."""

        return self.step_lookup.get(step_id)

    def as_story_string(self):
        # type: () -> Text
        """Convert the graph into the story file format."""

        story_content = ""
        for step in self.story_steps:
            story_content += step.as_story_string(flat=False)
        return story_content

    @staticmethod
    def order_steps(story_steps):
        # type: (List[StoryStep]) -> Tuple[deque, Set[Tuple[Text, Text]]]
        """Topological sort of the steps returning the ids of the steps."""

        checkpoints = StoryGraph._group_by_start_checkpoint(story_steps)
        graph = {s.id: {other.id
                        for end in s.end_checkpoints
                        for other in checkpoints[end.name]}
                 for s in story_steps}
        return StoryGraph.topological_sort(graph)

    @staticmethod
    def _group_by_start_checkpoint(story_steps):
        # type: (List[StoryStep]) -> Dict[Text, List[StoryStep]]
        """Returns all the start checkpoint of the steps"""

        checkpoints = defaultdict(list)
        for step in story_steps:
            for start in step.start_checkpoints:
                checkpoints[start.name].append(step)
        return checkpoints

    @staticmethod
    def topological_sort(
            graph  # type: Dict[Text, Set[Text]]
    ):
        # type: (...) -> Tuple[deque, Set[Tuple[Text, Text]]]
        """Creates a top sort of a directed graph. This is an unstable sorting!

        The function returns the sorted nodes as well as the edges that need
        to be removed from the graph to make it acyclic (and hence, sortable).

        The graph should be represented as a dictionary, e.g.:

        >>> example_graph = {
        ...         "a": set("b", "c", "d"),
        ...         "b": set(),
        ...         "c": set("d"),
        ...         "d": set(),
        ...         "e": set("f"),
        ...         "f": set()}
        >>> StoryGraph.topological_sort(example_graph)
        (deque([u'e', u'f', u'a', u'c', u'd', u'b']), [])
        """

        GRAY, BLACK = 0, 1
        ordered = deque()
        unprocessed = set(graph)
        visited_nodes = {}

        removed_edges = set()

        def dfs(node):
            visited_nodes[node] = GRAY
            for k in graph.get(node, set()):
                sk = visited_nodes.get(k, None)
                if sk == GRAY:
                    removed_edges.add((node, k))
                    continue
                if sk == BLACK:
                    continue
                unprocessed.discard(k)
                dfs(k)
            ordered.appendleft(node)
            visited_nodes[node] = BLACK

        while unprocessed:
            dfs(unprocessed.pop())
        return ordered, removed_edges

    def visualize(self, output_file=None):
        import networkx as nx
        from rasa_core.training import visualization
        from colorhash import ColorHash

        G = nx.MultiDiGraph()
        next_node_idx = [0]
        nodes = {"STORY_START": 0, "STORY_END": -1}

        def ensure_checkpoint_is_drawn(c):
            if c.name not in nodes:
                next_node_idx[0] += 1
                nodes[c.name] = next_node_idx[0]

                if c.name.startswith(GENERATED_CHECKPOINT_PREFIX):
                    # colors generated checkpoints based on their hash
                    color = ColorHash(c.name[-GENERATED_HASH_LENGTH:]).hex
                    G.add_node(next_node_idx[0],
                               label=utils.cap_length(c.name),
                               style="filled",
                               fillcolor=color)
                else:
                    G.add_node(next_node_idx[0], label=utils.cap_length(c.name))

        G.add_node(nodes["STORY_START"],
                   label="START", fillcolor="green", style="filled")
        G.add_node(nodes["STORY_END"],
                   label="END", fillcolor="red", style="filled")

        for step in self.story_steps:
            next_node_idx[0] += 1
            step_idx = next_node_idx[0]

            G.add_node(next_node_idx[0],
                       label=utils.cap_length(step.block_name),
                       style="filled",
                       fillcolor="lightblue",
                       shape="box")

            for c in step.start_checkpoints:
                ensure_checkpoint_is_drawn(c)
                G.add_edge(nodes[c.name], step_idx)
            for c in step.end_checkpoints:
                ensure_checkpoint_is_drawn(c)
                G.add_edge(step_idx, nodes[c.name])

            if not step.end_checkpoints:
                G.add_edge(step_idx, nodes["STORY_END"])

        if output_file:
            visualization.persist_graph(G, output_file)

        return G
