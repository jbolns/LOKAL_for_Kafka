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
# File handles audio transcription. When done, a producer
# is called to send output to final transcriptions topic.


# ..................
# TOP-LEVEL IMPORTS
# ...
# System operations
import os
from dotenv import load_dotenv
from config_folders import HUB_TRANSCRIPTIONS_FOLDER, HUB_TEMP_FOLDER


# ..................
# OVERALL TRANSCRIPTION FLOW
# ...
def run_transcription(path_to_audio,
                      filename,
                      transcription_approach='simple',
                      model_size='tiny',
                      timestamps=True):

    ''' Manages the transcription process for a single audio
        1. identifyies transcription_approach
        2. calls the corresponding transcription f(x)
        3. calls transcriptions producer to message output via Kafka
        4. (if backups set to off) deletes files in transcription hub

        Arguments:
        - path_to_audio: (str) path to transcribable audio resource
        - filename: (str) name of file to be produced (same as audio)
        - transcription_approach: (str) approach transcription should follow
        - model_size: (str) size of model to use for transcription
        - timestamps: (boolean) whether to include timestamps or not

        Outputs:
        - ONE .txt file with contents of the transcription for the source audio
            (via other f(x)s called in the process)
    '''

    # Function imports
    from audio_transcriptions_producer import produce

    # Load the environment
    load_dotenv()

    # Update user
    print(f'\nStarting transcription of audio at: {path_to_audio}')

    # Calling transcription
    try:
        if transcription_approach == 'simple':
            transcribe_simple(path_to_audio, filename, model_size, timestamps)
        elif transcription_approach == 'segmentation':
            transcribe_complex(path_to_audio, filename, model_size, timestamps, transcription_approach)
        elif transcription_approach == 'diarisation':
            transcribe_complex(path_to_audio, filename, model_size, timestamps, transcription_approach)
        else:
            transcribe_simple(path_to_audio, filename, 'tiny', True)
    except Exception as e:
        print(f'Error with transcription:\n, {e}')

    # Define path for output file
    # Could be returned from transcriptions function,
    # but best to keep that function as close to original as possible
    path_to_output_file = f'{HUB_TRANSCRIPTIONS_FOLDER}/{filename}.txt'

    # Re-construct metadata and
    operation_metadata = {'filename': filename,
                          'transcription_approach': transcription_approach,
                          'model_size': model_size,
                          'final': 'yes',
                          'timestamps': timestamps}

    # Call transcriptions producer
    produce(path_to_output_file, operation_metadata)

    # Clear temp folder to ensure clean slate in next run
    try:
        central_backups = (os.getenv('CENTRAL_BACKUPS', 'False') == 'True')
        if central_backups is False:
            print('\nCentral backups NOT enabled. Clearing main hub.\
                \nTo keep files on main hub, change setting in .env.')
            # Delete the transcription in the hub
            os.remove(path_to_output_file)

            # Delete the audio in the hub's async folder
            os.remove(path_to_audio)

            # Delete temp files in temp folder
            for file in os.listdir(HUB_TEMP_FOLDER):
                if file != 'dummy.md':
                    try:
                        os.remove(f'{HUB_TEMP_FOLDER}/{file}')
                    except Exception as e:
                        print(f'Temporary file "{file}" could not be deleted.\
                            \nCheck {HUB_TEMP_FOLDER} if needed.\
                            \nError: {e}')
    except Exception as e:
        print(f'Error clearing temp files. Best check  {HUB_TEMP_FOLDER} manually.\
            \nError is: {e}.')

    # Announce transcription completion
    print('\nTranscription complete.')


# ..................
# TWO TRANSCRIPTION APPROACHES
# Simple: Verbatim line after line
# Complex: Segmented or diarised
# ...
def transcribe_simple(path_to_audio, filename, model_size, timestamps):
    ''' Undertakes actions needed to produce a simple verbatim transcription

        Arguments:
        - path_to_audio: (str) path to transcribable audio resource
        - filename: (str) name of file to be produced (same as audio)
        - model_size: (str) size of model to use for transcription
        - timestamps: (boolean) whether to include timestamps or not

        Outputs:
        - ONE .txt file with contents of the transcription for the source audio
            (via other f(x)s called in the process)
    '''

    # Import necessary libraries
    import datetime
    import whisper

    # Load the environment
    load_dotenv()

    # Define path for output file
    path_to_output_file = f'{HUB_TRANSCRIPTIONS_FOLDER}/{filename}.txt'

    # Load model
    model = whisper.load_model(model_size, download_root='./models/whisper')

    # Transcribe
    result = model.transcribe(path_to_audio, verbose=True)
    segments = result['segments']

    # Write transcription to file
    with open(path_to_output_file, 'w') as f:
        for segment in segments:
            if timestamps is True:
                start_timestamp = datetime.timedelta(seconds=int(segment['start']))
                line_content = segment['text']
                line = f'[{start_timestamp}]{line_content}'
            else:
                line = segment['text']
            try:
                f.write(f'{line.strip()}\n')
            except Exception:
                f.write('!------ LINE IS MISSING --------!')
        f.close()


def transcribe_complex(path_to_audio, filename, model_size, timestamps, transcription_approach):
    ''' Undertakes actions to transcribe using segmentation or diarisation

        Arguments:
        - path_to_audio: (str) path to transcribable audio resource
        - filename: (str) name of file to be produced (same as audio)
        - model_size: (str) size of model to use for transcription
        - timestamps: (boolean) whether to include timestamps or not
        - transcription_approach: (str) approach transcription should follow

        Outputs:
        - ONE .txt file with contents of the transcription for the source audio
            (via other f(x)s called in the process)
    '''

    # Function imports
    from utils.assist import split_audio, run_whisper_on_loop, better_together, write_out

    # Path for temp and output files
    path_to_output_file = f'{HUB_TRANSCRIPTIONS_FOLDER}/{filename}.txt'

    # Run segmentation or diarisation
    if transcription_approach == 'diarisation':
        diarisation(path_to_audio)
    else:
        segmentation(path_to_audio)

    # Re-organise into chunks and split into temp audios accordingly
    CHUNKS = split_audio(path_to_audio, HUB_TEMP_FOLDER, transcription_approach)

    # Perform transcription on each temp audio
    run_whisper_on_loop(path_to_audio, model_size, HUB_TEMP_FOLDER)

    # Join speaker chunks timings and transcribed contents of each chunk
    LINES = better_together(HUB_TEMP_FOLDER, CHUNKS)

    # Write transcript to final .txt file
    write_out(path_to_output_file, filename, LINES, transcription_approach, timestamps)


# ..................
# SEGMENTATION
# ...
def segmentation(path_to_audio):
    ''' Segments an audio based on speech pauses (using Pyannote)

        Arguments:
        - path_to_audio: (str) path to transcribable audio resource

        Outputs:
        - ONE .txt file with the timings from the segmentation
            (saved to a folder containing temp files)
    '''

    # Function imports
    from pyannote.audio import Model
    from pyannote.audio.pipelines import VoiceActivityDetection
    from pyannote.audio.pipelines.utils.hook import ProgressHook

    # Update user
    print('\nSegmenting audio ahead of transcription.')

    # Segmentation model
    model_location = './models/segmentation/pytorch_model.bin'
    model = Model.from_pretrained(model_location)
    pipeline = VoiceActivityDetection(segmentation=model)

    # Hyper-parameters
    H_PARAMS = {
        'min_duration_on': 1.5,  # ignore short speech regions
        'min_duration_off': 0.5  # fill non-speech regions
        }

    # Run model
    pipeline.instantiate(H_PARAMS)
    with ProgressHook() as hook:
        segments = pipeline(path_to_audio, hook=hook)

    # Write segments to temporary .txt file
    L = []
    for turn, _ in segments.itertracks():
        L.append([turn.start-0.4, turn.end-0.4])

    with open('./utils/temp/temp-segments.txt', 'w') as f:
        for line in L:
            f.write(str(line[0]) + ', ' + str(line[1]) + '\n')
        f.close()


# ..................
# DIARISATION
# ...
def diarisation(path_to_audio):
    ''' Diarises an audio (using Pyannote)

        Arguments:
        - path_to_audio: (str) path to transcribable audio resource

        Outputs:
        - ONE .txt file with the timings from the diarisation
            (saved to a folder containing temp files)
    '''

    # Function imports
    from pyannote.audio import Model
    from pyannote.audio.pipelines import SpeakerDiarization as Pipeline
    from pyannote.audio.pipelines.utils.hook import ProgressHook

    # Update user
    print('\nDiarising audio ahead of transcription.')

    # Initialise models
    seg_model_loc = './models/segmentation/pytorch_model.bin'
    emb_model_loc = './models/embedding/pytorch_model.bin'
    segmentation_model = Model.from_pretrained(seg_model_loc)
    embedding_model = Model.from_pretrained(emb_model_loc)
    pipeline = Pipeline(segmentation=segmentation_model, embedding=embedding_model)

    # Hyper-parameters
    PARAMS = {
        'segmentation': {'min_duration_off': 0.5},
        'clustering': {
            'method': 'centroid',
            'min_cluster_size': 12,
            'threshold': 0.7045654963945799,
        },
    }

    # Run model
    pipeline.instantiate(PARAMS)
    with ProgressHook() as hook:
        diarization = pipeline(path_to_audio, hook=hook)

    # Write result to temp file
    with open('./utils/temp/temp-diary.txt', 'a') as f:
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            f.writelines(f'{turn.start}, {turn.end}, {speaker}\n')
        f.close()


# ..................
# NAME-MAIN
# ...
if __name__ == '__main__':
    pass
