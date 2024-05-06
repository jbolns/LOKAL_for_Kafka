# ---------------------
# AUDIO SPLITTING
# ...
def split_audio(path_to_audio, path_to_temp_folder, approach):
    ''' F(x) splits audio in as many chunks as speaker segments.
        Each segment is saved to temp folder.
    '''

    # Import necessary libraries
    from pydub import AudioSegment

    # Build array to organise splitting
    print('Breaking audio into transcription segments...')
    CHUNKS = []
    currentSpeaker = ''
    if approach == 'segmentation':
        with open(f'{path_to_temp_folder}\\temp-segments.txt', 'r') as f:
            for line in f.readlines():
                newline = line.split(', ')
                CHUNKS.append([float(newline[0]), float(newline[1])])
            f.close()
    else:
        with open(f'{path_to_temp_folder}\\temp-diary.txt', 'r') as f:
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
            extract.export(f'{path_to_temp_folder}\\lfkt3mpaud1o{str(i).zfill(n)}.wav', format='wav')
            i += 1
    if approach == 'segmentation':
        extract = audio[CHUNKS[i][0]*1000:]
    else:
        extract = audio[CHUNKS[i][1]*1000:]
    extract.export(f'{path_to_temp_folder}\\lfkt3mpaud1o{str(i).zfill(n)}.wav', format='wav')

    # Return the speaker chunks for later usage
    return CHUNKS


# ---------------------
# LOOPED TRANSCRIPTIONS
# For transcriptions of many audio segments
# ...
def run_whisper_on_loop(filename, model_to_use, path_to_temp_folder):
    ''' F(x) calls Whisper on each temp audio.
        It writes result of each run to a corresponding temp TXT
    '''

    # Import necessary libraries
    import os
    import whisper

    # Load transcription model
    print(f'Transcription of segments of "{filename}" about to begin. Loading model...')
    model = whisper.load_model(model_to_use, download_root='./models/whisper')

    # Perform transcription on each temp audio file.
    current_track = 1
    file_list = [f for f in os.listdir(path_to_temp_folder) if f.endswith('wav')]
    for file in file_list:
        if file.startswith('lfkt3mpaud1o'):
            print(f'\nSegment {current_track} of {len(file_list)-1}')
            current_track += 1
            try:
                result = model.transcribe(f'{path_to_temp_folder}\\{file}', verbose=True)
                # Write transcription into a temp TXT file
                with open(f'{path_to_temp_folder}\\temp-transcript{file[:-4]}.txt', 'w') as f:
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
    ''' F(x) joins temp files into a single array
    '''

    # Import necessary libraries
    import os
       
    # Join the diarisation array and contents of temporary TXT files
    i = 0
    LINES = []
    for file in os.listdir(path_to_temp_folder):
        if file.startswith('temp-transcript'):
            with open(f'{path_to_temp_folder}\\{file}') as f:
                LINES.append([CHUNKS[i][0], CHUNKS[i][1], f.read()])
                i += 1
    
    # Return the joint array
    return LINES


def write_out(path_to_output_file, filename, LINES, approach, timestamps):
    ''' F(x) writes joint results to TXT file
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