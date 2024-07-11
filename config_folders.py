'''
LOKAL for Kafka (LfK), v1. June 2024.
@author: Dr J.

Except for absolutely necessary classes,
LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

# ..................
# FILE SUMMARY
# ...
# File holds the locations for key folders needed to run LfK.

# ..................
# TOP-LEVEL IMPORTS
# ...
# Python
import os


# ..................
# HUB OPERATIONS
# ...

# The following folders are absolutely necessary for the
# functioning of the main transcriptions hub.

# The "async" folder holds audios pending transcription.
# When an applicable event is detected,
# LfK retrieves the relevant audio and places it here.
# If metadata checks, transcription is triggered.
HUB_ASYNC_FOLDER = './async'

# The "temp" folder is used for intermediate steps.
# Some models are not particularly friendly with io buffers.
# Having a temp folder widens compatibility.
HUB_TEMP_FOLDER = './utils/temp'

# Finalised transcriptions are saved to the transcriptions folder,
# from where they are sent to the final_transcriptions topic.
HUB_TRANSCRIPTIONS_FOLDER = './transcriptions'


# ..................
# CLIENT OPERATIONS
# ...

# LfK includes an optional script to run on any device wishing to
# consume final_transcriptions from final_transcriptions topic.

# The "output" folder is the local folder to save
# final transcriptions on any such device.

OUTPUT_FOLDER = os.path.expanduser('~/Desktop')

# ..................
# TEST OPERATIONS
# ...

# LfK includes a mock event broadcaster to send faux events to
# a faux central topic for testing and development purposes.

# The "source" folder tells this broadcaster where to get audios from.
SOURCE_FOLDER = './sources'
