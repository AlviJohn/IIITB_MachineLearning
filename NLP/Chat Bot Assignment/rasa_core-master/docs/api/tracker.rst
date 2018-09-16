Dialogue State Tracker
======================

The tracker stores and maintains the state of the dialogue with a single user.
It is stored in a tracker store, retrieved when incoming messages for the
conversation are received and updated after actions have been executed


.. autoclass:: rasa_core.trackers.DialogueStateTracker

   .. automethod:: DialogueStateTracker.current_state
   .. automethod:: DialogueStateTracker.current_slot_values
   .. automethod:: DialogueStateTracker.get_slot    
   .. automethod:: DialogueStateTracker.get_latest_entity_values
   .. automethod:: DialogueStateTracker.copy
