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
# File contains helper functions used by the main transcription handlers.
# Kept separately from other utils and conversions to avoid clutter.


# ---------------------
# AUDIO SPLITTING
# ...
def split_audio(path_to_audio, path_to_temp_folder, approach):
    ''' Splits audio in as many chunks as speaker segments,
        saving each segment as a file of its own.

        Arguments:
        - path_to_audio: (str) path to source audio
        - path_to_temp_folder: (str) path to folder w. file
                containing a .txt file with segmentation or diarisation results
                (# of speaker segments is drawn from this file)
        - approach: (str) whether the input/output will be used in
                segmentation or diarisation-styled transcription
                (necessary because formats differ slightly)

        Outputs:
        - CHUNKS: (arr) array with the timings for the different segments
        - MANY audio files, one per segment
            (saved to "path_to_temp_folder")
    '''

    # Import necessary libraries
    from pydub import AudioSegment

    # Build array to organise splitting
    CHUNKS = []
    currentSpeaker = ''
    if approach == 'segmentation':
        with open(f'{path_to_temp_folder}/temp-segments.txt', 'r') as f:
            for line in f.readlines():
                newline = line.split(', ')
                CHUNKS.append([float(newline[0]), float(newline[1])])
            f.close()
    else:
        with open(f'{path_to_temp_folder}/temp-diary.txt', 'r') as f:
            for line in f.readlines():
                newline = line.split(', ')
                if newline[2] != currentSpeaker:
                    CHUNKS.append([newline[2], float(newline[0])])
                    currentSpeaker = newline[2]
            f.close()

    # Split audio into a file per speaker segment
    i = 0
    n = len(str(len(CHUNKS)))

    audio = AudioSegment.from_file(path_to_audio)
    for chunk in CHUNKS:
        if i < len(CHUNKS) - 1:
            if approach == 'segmentation':
                extract = audio[CHUNKS[i][0]*1000:CHUNKS[i + 1][0]*1000]
            else:
                extract = audio[CHUNKS[i][1]*1000:CHUNKS[i + 1][1]*1000]
            extract.export(f'{path_to_temp_folder}/lfkt3mpaud1o{str(i).zfill(n)}.wav', format='wav')
            i += 1
    if approach == 'segmentation':
        extract = audio[CHUNKS[i][0]*1000:]
    else:
        extract = audio[CHUNKS[i][1]*1000:]
    extract.export(f'{path_to_temp_folder}/lfkt3mpaud1o{str(i).zfill(n)}.wav', format='wav')

    # Return the speaker chunks for later usage
    return CHUNKS


# ---------------------
# LOOPED TRANSCRIPTIONS
# For transcriptions of many audio segments
# ...
def run_whisper_on_loop(filename, model_to_use, path_to_temp_folder):
    ''' Calls Whisper on all audios in a given temp folder,
        writing the result of each run to a corresponding temp TXT.

        Arguments:
        - filename: (str) name of the original source audio file
        - model_to_use: (str) size of model to use for transcription
        - path_to_temp_folder: (str) path to folder containing temp audios

        Outputs:
        - MANY .txt files with transcription contents for each temp audio
            (saved to "path_to_temp_folder").
    '''

    # Import necessary libraries
    import os
    import whisper

    # Load transcription model
    print('\nNow loading transcription model. Depending on your computer, this might take a bit..')
    model = whisper.load_model(model_to_use, download_root='./models/whisper')

    # Perform transcription on each temp audio file.
    current_track = 1
    files = [f for f in os.listdir(path_to_temp_folder) if f.endswith('wav')]
    for file in files:
        if file.startswith('lfkt3mpaud1o'):
            print(f'\nTranscribing chunk # {current_track} of {len(files)}')
            current_track += 1
            try:
                result = model.transcribe(f'{path_to_temp_folder}/{file}', verbose=True)
                # Write transcription into a temp TXT file
                with open(f'{path_to_temp_folder}/temp-transcript{file[:-4]}.txt', 'w') as f:
                    try:
                        f.write(result['text'])
                    except Exception:
                        pass
                    f.close()
            except Exception as e:
                print(f'Error transcribing segment of audio: {e}')


# ---------------------
# MISC OPERATIONS
# ...
def better_together(path_to_temp_folder, CHUNKS):
    ''' Joins temp files into a single array

        Arguments:
        - path_to_temp_folder: (str) path to folder w. temp audio transcripts
        - CHUNKS: (arr) array with segment timings

        Outputs:
        - LINES: (arr) with the joint transcripts for all temp audios,
            organised according to the timings in CHUNKS.
    '''

    # Import necessary libraries
    import os

    # Join the diarisation array and contents of temporary TXT files
    i = 0
    LINES = []
    for file in os.listdir(path_to_temp_folder):
        if file.startswith('temp-transcript'):
            with open(f'{path_to_temp_folder}/{file}') as f:
                LINES.append([CHUNKS[i][0], CHUNKS[i][1], f.read()])
                i += 1

    # Return the joint array
    return LINES


def write_out(path_to_output_file, filename, LINES, approach, timestamps):
    ''' writes joint results to TXT file

        Arguments:
        - path_to_output_file: (str) desired path for final .txt. file
        - filename: (str) name of file (without extension of path)
        - LINES: (arr) array with joint results of all segment transcripts
        - approach: (str) approach used for transcription
        - timestamps: (str) whether transcript needs timestamps or not

        Outputs:
        - ONE .txt file with ordered contents of transcription for source audio
    '''

    # Function imports
    import datetime

    # Write to the final transcription file
    with open(path_to_output_file, 'w') as f:
        f.write(f'TRANSCRIPT OF file {filename} \n\n')
        for line in LINES:
            try:
                if approach == 'segmentation':
                    if timestamps is True:
                        start_timestamp = f'[{datetime.timedelta(seconds=int(line[0]))}]'
                    else:
                        start_timestamp = ''
                    line_content = line[2]
                    f.write(f'{start_timestamp}\n{line_content}\n\n')
                else:
                    if timestamps is True:
                        start_timestamp = f'[{datetime.timedelta(seconds=int(line[1]))}]'
                        spacer = ' '
                    else:
                        start_timestamp = ''
                        spacer = ''
                    speaker = line[0]
                    line_content = line[2]
                    f.write(f'{start_timestamp}{spacer}{speaker}\n{line_content}\n\n')
            except Exception:
                pass
        f.close()
