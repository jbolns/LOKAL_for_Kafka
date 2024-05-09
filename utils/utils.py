'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

Except for absolutely necessary classes, LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

def recommended_chunk_size(path_to_audio, schema_type):
        ''' Gets a path to a audio and figures out recommended audio chunk size
            based on audio duration, size of file, and parameters from .env.

            F(x) is a guesstimation based on audio attributes and .env file configs
            Adjust key parameters directly in .env.
        '''
        
        # Function imports
        import os
        from pydub import AudioSegment
        from dotenv import load_dotenv
        from utils.conversions import any_format_to_wav

        # Load the environment
        load_dotenv()

        # Calculate max audio chunk size from .env settings
        max_msg_size = int(os.getenv('MAX_MESSAGE_SIZE')) / (1024*1024)
        audio_ratio = float(os.getenv('AUDIO_SIZE_RATIO'))
        schema_adjustment = float(os.getenv('JSON_RATIO')) if schema_type == 'json' else 1
        rec_chunk_size = max_msg_size * audio_ratio * schema_adjustment
    
        # Convert audio to message format (.wav) if needed
        audio = AudioSegment.from_file(path_to_audio)
        duration = audio.duration_seconds
        
        if path_to_audio.endswith('.wav'):
            MB_p_second = os.path.getsize(path_to_audio) / (1024 * 1024) / duration
        else:
            buffer = any_format_to_wav(path_to_audio)
            MB_p_second = buffer.getbuffer().nbytes / (1024 * 1024) / duration

        # Calculate seconds of audio that fit in recommended chunk size
        secs_in_rec_size = int(rec_chunk_size / MB_p_second)
        ms_in_rec_size = secs_in_rec_size * 1000 if secs_in_rec_size >= 1 else 1
        
        return ms_in_rec_size