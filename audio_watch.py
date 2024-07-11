'''
LOKAL for Kafka (LfK), v1. May 2024.
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
# File keeps an eye on the async folder.
# When a file hits this folder, checks ensure file is audio
# and metadata is present, calling transcription if so.


# ..................
# TOP-LEVEL IMPORTS
# ...
# Top level
import time
import mimetypes
from dotenv import load_dotenv

# Watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pydub.utils import mediainfo

# Other scripts
from config_folders import HUB_ASYNC_FOLDER
from utils.lokal_transcribe import run_transcription


# ..................
# WATCHDOG
# ...
class Watch(FileSystemEventHandler):
    ''' Watches for changes in the async transcriptions folder
    '''

    def __init__(self, path):
        self.observer = Observer()
        self.event_handler = ActionHandler()
        self.path = path

    def run(self):

        try:
            print(f'Watching "{self.path}" for file changes...')
            self.observer.schedule(self.event_handler, self.path, recursive=True)
            self.observer.start()

            while True:
                time.sleep(100)  # Thread sleep time

        except KeyboardInterrupt:
            self.observer.stop()

        self.observer.join()


class ActionHandler(FileSystemEventHandler):
    ''' Triggers producer when called by Watcher
    '''

    @staticmethod
    def on_any_event(event):
        ''' Handles events in folder being watched

            Arguments:
            - event: (obj) information of file changes

            Outputs:
            - If audio and meets checks, a call to a transription service
                (per event)
        '''

        # Record timestamp for action
        timestamp = round(time.time()*1000)

        try:
            # Handle actions
            # Triggers a message only if audio is created or modified
            if event.is_directory:  # No need to track folder actions
                return None
            elif event.event_type == 'deleted':  # Not a transcribable event
                return None
            elif event.event_type == 'created':  # Not a transcribable event
                return None
            else:
                if '-lfkT3MP' not in event.src_path:  # Exempt temporary files

                    print(f'\nFile {event.event_type}. Location: {event.src_path}. Timestamp: {timestamp}.')

                    # Run checks on audio to see if transcription applies
                    OK = True

                    # Check if file is audio
                    try:
                        file_type = mimetypes.guess_type(event.src_path)[0].split('/')[0]
                        OK = False if file_type != 'audio' else True
                    except Exception as e:
                        print(f'Check failed: {e}')
                        OK = False

                    # Check if audio has applicable operation_metadata
                    try:
                        operation_metadata = mediainfo(event.src_path)['TAG']['comment'].split(',')
                        OK = False if len(operation_metadata) != 5 else True
                    except Exception as e:
                        print(f'Check failed: {e}')
                        OK = False

                    # Check if operation metadata includes "final" flag
                    try:
                        filename, transcription_approach, model_size, final, timestamps = operation_metadata
                        OK = True if final == 'yes' else True if final == 1 else True if final is True else False
                    except Exception as e:
                        print(f'Check failed: {e}')
                        OK = False

                    # Call transcription if all checks are met
                    if OK is True:
                        run_transcription(event.src_path, filename, transcription_approach, model_size, timestamps)
                    else:
                        print('No go. Misc. event.')

        except Exception as e:
            print(f'Error processing event in async: {e}.')


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':

    # Load environment
    load_dotenv()

    # Run producer
    Watch(HUB_ASYNC_FOLDER).run()
