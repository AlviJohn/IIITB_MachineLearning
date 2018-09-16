:desc: Fallback and default actions in Rasa
.. _section_fallback:

Confidence and Fallback Intents
===============================


Each of the pipelines will report a ``confidence`` score along with the predicted intent,
and the ``ner_crf`` component will do the same for the extracted entities. 

You can use the confidence score to choose when to ignore Rasa NLU's prediction and trigger
fallback behaviour, for example asking the user to rephrase. If you are using Rasa Core,
you can do this using a `Fallback Policy </core/fallbacks/>`_. 

Choosing a Confidence Cutoff
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A good way to choose a confidence cutoff is to calculate the model's confidence on a test set,
and compare the confidence values on the correctly and incorrectly predicted examples.

A Note about Confidence Scores
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Always keep in mind that the confidence score is not a true probability that the prediction 
is correct, it's just a metric defined by the model that approximately describes how similar
your input was to the training data. 

The intent classifier in the ``spacy_sklearn`` pipeline, for example, usually reports very low
confidence numbers, whereas the ``tensorflow_embedding`` pipeline usually provides very high confidences.
One common misconception is that if your model reports high confidence on your training examples,
it is a "better" model. In fact, this usually means that your model is overfitting.


