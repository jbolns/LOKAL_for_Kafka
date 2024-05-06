# ---------------------
# PRODUCER OPERATIONS
# The following functions are used by the audio producer to 
# read and manipulate incoming Kafka messages
# ...
def any_format_to_wav(path_to_audio):
    ''' F(x) converts audio in any format to .wav
        Relies on FFmpeg being installed on system.
    '''

    import io
    from pydub import AudioSegment
    
    try:
        buffer = io.BytesIO()
        audio = AudioSegment.from_file(path_to_audio)
        audio.export(buffer, format='wav')
    except Exception as e:
        print(f'Error converting audio file to .wav format: {e}')
    
    return buffer


def audio_to_chunks(path_to_audio, max_duration):
    ''' F(x) converts long audio into smaller audio_chunks
        Used by producer to split long audios into manageable sizes
    '''

    import io
    from pydub import AudioSegment
    from pydub.utils import make_chunks

    if path_to_audio.endswith('.wav'):
        audio = AudioSegment.from_file(path_to_audio, format='wav')
    else:
        converted_audio = any_format_to_wav(path_to_audio)
        audio = AudioSegment.from_file(converted_audio, format='wav')
    
    chunks = make_chunks(audio, max_duration)

    buffer_array = []
    for chunk in chunks:
        buffer = io.BytesIO()
        chunk.export(buffer, format='wav')
        buffer_array.append(buffer)
    
    return buffer_array


def audio_to_dict(audio, ctx):
    ''' F(x) converts audio object to dictionary
        Used by Kafka producer
    '''
    
    return {
        'path_to_audio' : audio.path_to_audio,
        'transcription_approach' : audio.transcription_approach,
        'final' : audio.final,
        'params' : audio.params,
        'frames' : audio.frames,
        'timestamp' : audio.timestamp
        }


# ---------------------
# CONSUMER OPERATIONS
# The following functions are used by the consumer to 
# read and manipulate incoming Kafka messages
# ...
def dict_to_audio(dict, ctx):
    ''' F(x) converts dictionary to audio object
        Used by Kafka consumer
    '''

    from utils.classes import KafkaAudio
    
    return KafkaAudio(
        dict['path_to_audio'],
        dict['transcription_approach'],
        dict['final'],
        dict['params'],
        dict['frames'],
        dict['timestamp']
        )


def audio_to_data(audio_bytes):
    ''' F(x) converts an audio object into a
        string with headers params
        and a sequence of bytes
    '''

    import wave

    with wave.open(audio_bytes) as f:
        params = f.getparams()
        frames = f.readframes(-1)
    params = ','.join([str(p) for p in params])
    return params, frames


def data_to_audio(params, frames, filename):
    ''' F(x) converts params and frames into temp audio file
    '''

    # Imports specific to function
    import os
    import wave
    from dotenv import load_dotenv
    load_dotenv()

    # Define a path to temporary audio file
    temp_folder = os.getenv('MAIN_NODE_TEMP_FOLDER')
    path_to_temp_audio = f'{temp_folder}\\{filename}.wav'

    # Extract params into string
    params = params.split(',')
    params = tuple([int(i) if i.isnumeric() else i for i in params])

    # Write to temp file
    with wave.open(path_to_temp_audio, 'wb') as f:
        f.setparams(params)
        f.writeframes(frames)
    
    # Return path to temp file just created
    return path_to_temp_audio


def data_to_audio_buffer(params, frames, filename):
    ''' F(x) converts params and frames into temp audio file
        It uses a buffer instead of a temp file.
        Buffers are not great with Whisper,
        but might work w. other models like faster whisper.
        UNTESTED
    '''

    import io
    import wave

    params = params.split(',')
    params = tuple([int(i) if i.isnumeric() else i for i in params])
    
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as f:
        f.setparams(params)
        f.writeframes(frames)
    
    return buffer

# ---------------------
# TRANSCRIPTIONS PRODUCER OPERATIONS
# The following functions are used by the producer to 
# read and manipulate incoming Kafka messages
# ...

def txt_to_dict(transcription, ctx):
    ''' F(x) converts audio object to dictionary
        Used by Kafka producer
    '''
    
    return {
        'path_to_transcription' : transcription.path_to_transcription,
        'transcription_approach' : transcription.transcription_approach,
        'content' : transcription.content,
        'timestamp' : transcription.timestamp
        }


def dict_to_txt(dict, ctx):
    ''' F(x) converts dictionary to string object
        Used by Kafka consumer
    '''

    from utils.classes import KafkaTranscription
    
    return KafkaTranscription(
        dict['path_to_transcription'],
        dict['transcription_approach'],
        dict['content'],
        dict['timestamp']
        )