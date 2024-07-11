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
# Runs LfK service.
# - Consume broadcasts from the central topic
# - Detect applicable events
# - Transcribe audios for applicable events
# - Produce the results to a final_transcriptions topic

# To consume final transcriptions to a local folder on any given device,
# run transcriptions_consumer.py separately. If said device is NOT also
# the main hub where transcriptions are produced, best practice is to trim
# this LfK distribution into a sub-distro containing only the files needed
# for consumption of final outputs.

# ..................
# TOP-LEVEL IMPORTS
# ...
import subprocess


# ..................
# Subprocesses
# ...

def run_lfk():
    ''' Undertakes all operations at the main hub and saves
        final into a folder in the said main hub.
    '''

    # Consumes event broadcasts & retrieve audio to async folder if applicable
    audio_consumer = subprocess.Popen(["python", "audio_consumer.py"], shell=True)

    # Watch async folder & transcribe if audio w. correct metadata hits it
    audio_watcher = subprocess.Popen(["python", "audio_watch.py"], shell=True)

    # Keep all processes alive
    audio_consumer.wait()
    audio_watcher.wait()


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':
    run_lfk()
