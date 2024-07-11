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
# File handles audio retrieval from internal or external locations,
# and drop any audio retrieved into async transcription folder.


# ..................
# OVERALL TRANSCRIPTION FLOW
# ...
def audio_retriever(path_to_source_audio, operation_metadata):
    ''' Retrieves a single audio & places it in async transcription folder
        1. retrieves audio from original location
        2. places audio in async folder (watched by a transcription service)
        3. if audio not originally in .wav format, converts local copy to .wav
        4. writes metadata to audio header

        Arguments
        - path_to__source_audio: (str) the path to the audio resource
        - operation_metadata: (obj) metadata w. transcription settings

        Outputs
        - ONE audio saved to transcriptions hub
            (for easier usage and manipulation during transcriptions)
            (deleted after transcription unless backups enabled in ".env")
    '''

    # Function imports
    import os
    import subprocess
    from dotenv import load_dotenv
    from pydub import AudioSegment
    from config_folders import HUB_ASYNC_FOLDER
    from utils.conversions import any_format_to_wav
    from utils.utils import internal_retrieve, external_retrieve

    # Load the environment
    load_dotenv()

    # Update user
    print('Retrieving...')

    # Get or calculate necessary variables
    client_name = os.getenv('CLIENT_NAME')
    file_extension = path_to_source_audio.rsplit('.', 1)[-1]
    filename = operation_metadata['filename']
    path_to_local_temp = f'{HUB_ASYNC_FOLDER}/{filename}-lfkT3MP.{file_extension}'

    # Retrieve audio and place in async folder
    try:
        if client_name == 'internal':
            internal_retrieve(path_to_source_audio, path_to_local_temp)
        else:
            credentials = [os.getenv('AWS_REGION'),
                           os.getenv('AWS_ACCESS_KEY_ID'),
                           os.getenv('AWS_SECRET_ACCESS_KEY')]
            external_retrieve(path_to_source_audio, path_to_local_temp, client_name.lower(), credentials)
    except Exception as e:
        print(f'Error retrieving audio from {path_to_source_audio}: {e}')

    # Convert to .wav if audio in any other format
    if file_extension == 'wav':
        print('Audio originally in .wav format. OK.')
        path_to_wav_temp = path_to_local_temp
    else:
        try:
            print('Source audio NOT in .wav. Converting local copy to .wav.')
            # Convert
            converted_audio = any_format_to_wav(path_to_local_temp)
            audio = AudioSegment.from_file(converted_audio, format='wav')
            # Save
            path_to_wav_temp = f'{HUB_ASYNC_FOLDER}/{filename}-lfkT3MP.wav'
            audio.export(path_to_wav_temp, format='wav')
        except Exception as e:
            print(f'Error converting {path_to_local_temp} to .wav: {e}')

    # Write metadata to final audio
    # Kept at the end to avoid premature transcriptions
    # (async folder watcher triggers transcription when it sees metadata)
    print('Writing metadata to local audio copy.')
    path_to_final_audio = f'{HUB_ASYNC_FOLDER}/{filename}.wav'
    try:

        # Push all metadata into a single string
        metadata_string = ','.join(operation_metadata.values())

        # Use FFmpeg to write string into audio's comment tag
        subprocess.call(['ffmpeg',
                         '-loglevel',
                         'quiet',
                         '-i',
                         path_to_wav_temp,
                         '-metadata',
                         f'comment={metadata_string}',
                         path_to_final_audio])

    except Exception as e:
        print(f'Error writing metadata to {path_to_wav_temp}: {e}')

    # Remove any temporary copies created in the process
    try:
        os.remove(path_to_wav_temp)
        if file_extension != 'wav':
            os.remove(path_to_local_temp)
    except Exception as e:
        print(f'Error deleting temp files in async folder: {e}.')
