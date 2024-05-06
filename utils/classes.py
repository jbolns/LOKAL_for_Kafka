# ..................
# SECTION: KAFKA OBJECTS
# ..................
class KafkaAudio(object):
    ''' Takes an audio and makes an audio instance that can travel as message'''
    
    def __init__(self, path_to_audio, transcription_approach, final, params, frames, timestamp):
        
        self.path_to_audio = path_to_audio
        self.transcription_approach = transcription_approach
        self.final = final
        self.params = params
        self.frames = frames
        self.timestamp = timestamp


class KafkaTranscription(object):
    ''' Takes an audio and makes an audio instance that can travel as message'''
    
    def __init__(self, path_to_transcription, transcription_approach, content, timestamp):
        
        self.path_to_transcription = path_to_transcription
        self.transcription_approach = transcription_approach
        self.content = content
        self.timestamp = timestamp

