'''
LOKAL for Kafka (LfK), v1. May 2024.
@author: Dr J.

Except for absolutely necessary classes, LfK tries to stick to a functional programming paradigm.
Any classes must be justified exceptionally well.

Copyright (c) 2024 Jose A Bolanos / Polyzentrik Tmi.
SPDX-License-Identifier: Apache-2.0.

'''

# ---------------------
# OVERALL TRANSCRIPTION FLOW
# ...
def run_transcription(path_to_temp_audio, transcription_approach, filename, model_size='tiny'):
    ''' F(x)
        (1) identifyies transcription_approach
        (2) calls the corresponding transcription f(x)
    '''
    
    # Import necessary libraries
    import os
    from dotenv import load_dotenv
    load_dotenv()

    # Update user
    print(f'\nStarting transcription of filename: {filename}')

    # Turn off timestamps if keyword present in filename
    try:
        timestamps = (os.getenv('TIMESTAMPS', 'False') == 'True')
        if path_to_temp_audio.find('-lfkn0t1m3') > 0:
            timestamps = not timestamps
    except Exception as e:
        print(f'Could not detect timestamps preference: {e}.\nSetting timestamps to ON.')
        timestamps = True

    
    # Calling transcription
    try:
        approach, model_size = transcription_approach.split('.')
        
        if approach == 'simple':
            transcribe_simple(path_to_temp_audio, filename, model_size, timestamps)
        elif approach == 'segmentation' or approach == 'diarisation':
                transcribe_complex(path_to_temp_audio, filename, model_size, timestamps, approach)
        else:
            transcribe_simple(path_to_temp_audio, filename, 'tiny', timestamps)
    except Exception as e:
        print(f'Transcription failed. Error is:\n, {e}')
    
    # Clear temp folder to ensure clean slate in next run
    try:
        central_backups = (os.getenv('CENTRAL_BACKUPS', 'False') == 'True')
        if central_backups == False:
            temp_folder = '\\'.join(path_to_temp_audio.rsplit('\\')[:-1])
            for file in os.listdir(temp_folder):
                try:
                    os.remove(f'{temp_folder}\\{file}')
                except:
                    print('Temporary file "{file}" could not be deleted. Check {temp_folder} and delete manually if needed.')
        
    except Exception as e:
        print(f'Error clearing temp files in {temp_folder}. Error is: {e}. Check manually if needed.')
    
    print('Transcription completed and stored to output folder.')


# ---------------------
# TWO TRANSCRIPTION APPROACHES
# Simple: Verbatim transcription line after line
# Complex: Segmented or diarised transcription
# ...
def transcribe_simple(path_to_temp_audio, filename, model_size, timestamps):
    ''' F(x) 
        (1) calls transcription model
        (2) writes result to TXT file
    '''
    
    # Import necessary libraries
    import os
    import datetime
    import whisper

    from dotenv import load_dotenv
    load_dotenv()

    # Define path for output file
    output_folder_in_server = os.getenv('MAIN_NODE_TRANSCRIPTIONS_FOLDER')
    path_to_output_file = f'{output_folder_in_server}\\simple\\{model_size}\\{filename}.txt'

    # Load model
    model = whisper.load_model(model_size, download_root='.\\models\\whisper')

    # Transcribe
    result = model.transcribe(path_to_temp_audio, verbose=True)
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


def transcribe_complex(path_to_temp_audio, filename, model_size, timestamps, approach_to_transcription):
    ''' F(x) 
        (1) call a segmentation or diarisation f(x) on a given audio,
        (2) splits audio according to segmentation,
        (3) performs transcription on each audio chunk,
        (4) merges transcriptions of chunks,
        (5) and writes joint result to TXT file.
    '''
    
    # Function specific imporst
    # Import necessary libraries
    from utils.assist import split_audio, run_whisper_on_loop, better_together, write_out
    
    import os
    from dotenv import load_dotenv
    load_dotenv()


    # Define path for temp and output files
    path_to_temp_folder = '.\\utils\\temp'

    output_folder_in_server = os.getenv('MAIN_NODE_TRANSCRIPTIONS_FOLDER')
    path_to_output_file = f'{output_folder_in_server}\\{approach_to_transcription}\\{model_size}\\{filename}.txt'

    # Run segmentation
    if approach_to_transcription == 'diarisation':
        diarisation(path_to_temp_audio)
    else:
        segmentation(path_to_temp_audio)
    
    # Re-organise diarisation into chunks and split audios accordingly
    CHUNKS = split_audio(path_to_temp_audio, path_to_temp_folder, approach_to_transcription)
    
    # Perform transcription on each temp audio file
    run_whisper_on_loop(path_to_temp_audio, model_size, path_to_temp_folder)
    
    # Join speaker chunks and transcribed content
    LINES = better_together(path_to_temp_folder, CHUNKS)
    
    # Write transcript into final TXT file
    write_out(path_to_output_file, filename, LINES, approach_to_transcription, timestamps)


# ---------------------
# SEGMENTATION
# ...
def segmentation(path_to_temp_audio):
    ''' F(x) segments given audio based on speech pauses (using Pyannote)
    '''

    # Import necessary libraries
    from pyannote.audio import Model
    from pyannote.audio.pipelines import VoiceActivityDetection
    from pyannote.audio.pipelines.utils.hook import ProgressHook

    # Load segmentation model
    model_location = './models/segmentation/pytorch_model.bin'
    model = Model.from_pretrained(model_location)
    pipeline = VoiceActivityDetection(segmentation=model)

    # Define hyper-parameters for model
    # 1: ignore short speech regions. 2: fill non-speech regions
    H_PARAMS = { 'min_duration_on': 1.5, 'min_duration_off': 0.5 }  

    # Run model
    pipeline.instantiate(H_PARAMS)
    with ProgressHook() as hook:
        segments = pipeline(path_to_temp_audio, hook=hook)

    # Save segments to temp TXT file
    L = []
    for turn, _ in segments.itertracks():
        L.append([turn.start-0.4, turn.end-0.4])

    # Write segments to temporary file
    with open('.\\utils\\temp\\temp-segments.txt', 'w') as f:
        for line in L:
            f.write(str(line[0]) + ', '  + str(line[1]) + '\n')
        f.close()


# ---------------------
# DIARISATION
# ...
def diarisation(path_to_temp_audio):
    ''' F(x) diarises a given audio (using Pyannote)
    '''

    # Import necessary libraries
    from pyannote.audio import Model
    from pyannote.audio.pipelines import SpeakerDiarization as Pipeline
    from pyannote.audio.pipelines.utils.hook import ProgressHook

    # Initialise models
    seg_model_loc = '.\\models\\segmentation\\pytorch_model.bin'
    emb_model_loc = '.\\models\\embedding\\pytorch_model.bin'
    segmentation_model = Model.from_pretrained(seg_model_loc)
    embedding_model = Model.from_pretrained(emb_model_loc)
    pipeline = Pipeline(segmentation=segmentation_model, embedding=embedding_model)

    # Set hyper-parameters
    PARAMS = {
        'segmentation': { 'min_duration_off': 0.5 },
        'clustering': {
            'method': 'centroid',
            'min_cluster_size': 12,
            'threshold': 0.7045654963945799,
        },
    }

    # Run model
    pipeline.instantiate(PARAMS)
    with ProgressHook() as hook:
        diarization = pipeline(path_to_temp_audio, hook=hook)

    # Write the diarisation result to temp file
    with open('.\\utils\\temp\\temp-diary.txt', 'a') as f:
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            f.writelines(f'{turn.start}, {turn.end}, {speaker}\n')
        f.close()