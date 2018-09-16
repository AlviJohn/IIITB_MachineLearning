.. _docker:

Using Docker
============



We provide a Dockerfile which allows you to build an image of Rasa Core
with a simple command: ``docker build -t rasa_core .``

The default command of the resulting container starts the Rasa Core server
with the ``--core`` and ``--nlu`` options. At this stage the container does not
yet contain any models, so you have to mount them from a local folder into
the container's ``/app/model/dialogue`` and ``app/model/nlu`` directories.
The full run command looks like this:

.. code-block:: bash

   docker run \
      --mount type=bind,source=<PATH_TO_DIALOGUE_MODEL_DIR>,target=/app/dialogue \
      --mount type=bind,source=<PATH_TO_NLU_MODEL_DIR>,target=/app/nlu \
      rasa_core

You also have the option to use the container to train a model with

.. code-block:: bash

   docker run \
      --mount type=bind,source=<PATH_TO_STORIES_FILE>/stories.md,target=/app/stories.md \
      --mount type=bind,source=<PATH_TO_DOMAIN_FILE>/domain.yml,target=/app/domain.yml \
      --mount type=bind,source=<OUT_PATH>,target=/app/out \
      rasa_core train

You may in addition run any Rasa Core command inside the container with
``docker run rasa_core run [COMMAND]``.

