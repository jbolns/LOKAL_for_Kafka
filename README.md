# LfK > Location-based audio messaging (JSON)
LOKAL for Kafka (LfK) is a micro-services solution for distributed audio transcriptions meant as a component for broader Kafka ecosystems rather than a standalone solution in itself.

This branch is a flavoured distro for systems using JSON schemas and location-based audio messaging (audio locations messaged, rather than audios as such).

Additional tailored branches possible. Get in touch for inquiries: hello@polyzentrik.com. 

## A component for broader ecosystems
LfK is a component of a broader one-day-will-be Kafka ecosystem. It can also be integrated as an add-on in existing Kafka ecosystems.

LfK is NOT a production-ready standalone solution.

## Implementation guidance

### General logic

This LfK distro is meant to plug into a system-wide event broadcasting topic. When the primary LfK consumer detects an applicable event in said broadcasting topic, a retrieve-transcribe-produce sequence is ignited:
* Audio is retrieved from its original location and placed into an async folder (see *./audio_consumer.py* and *./utils/retrieve.py*)
* When audio has applicable metadata, transcription is kickstarted (see *./audio_watch.py* and *./utils/lokal_transcribe.py*)
* When transcription is ready, the service sens the result to a final transcriptions topic (see *./transcriptions_producer.py*)
* **Optional.** One or many final devices can consume the final transcriptions and save transcriptions locally (see *./transcriptions_consumer.py*).

### Prerequisites
#### Kafka
As noted, this LfK distro is meant to be a part of a system with a central Kafka topic that updates the network of relevant events.
* Enter the name of this central topic into the corresponding *.env* variable.
* The schema for this central topic must have the following fields (more fields possible – but you might need to adjust schemas):
  * event_type: (str) describes the type of event,
  * path: (str) path to resource,
  * operation_metadata: (obj) metadata w. transcription settings:
    * filename: (str) target name for OUTPUT file (only name - no extension),
    * transcription_approach: (str) 'simple' | 'segmentation' | 'diarisation' (preferred transcription approach),
    * model_size: (str) 'tiny' | 'base' | 'small' | 'medium' | 'large' (size of model to use),
    * final: (str) 'yes' | 'no' (trigger – no transcription produced if not present or negated),
    * timestamps: (str) 'yes | 'no' (whether to add timestamps to transcriptions).

#### AI models
LfK uses OpenAI's Whisper models and pyannote's models for segmentation and diarisation.
* **Whisper.** You can either download and put the Whisper models in *./models/whisper* or wait for them to download on first usage.
* **pyannote.** You will need to download the following models from HF (you need to ask access to the models):
  * Pyannote's speaker segmentation 3.0: https://huggingface.co/pyannote/segmentation-3.0.
    * Files needed: *config.yaml*, *pytorch_model.bin*.
    * Save to: *models\segmentation* (be sure to also include a copy of the LICENSE and provide appropriate credits).
  * Pyannote's wespeaker-voxceleb-resnet34-LM wrapper: https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM.
    * Files needed: *config.yaml*, *pytorch_model.bin*.
    * Save to: *models\embedding* (be sure to also include a copy of the LICENSE and provide appropriate credits).
  * Pyannote's speaker diarization 3.1: https://huggingface.co/pyannote/speaker-diarization-3.1.
    * Files needed: *config.yaml*, *handler.py*, *requirements.txt*.
    * Save to: *models\diarization* (be sure to also include a copy of the LICENSE and provide appropriate credits).

#### Other
1. [FFmpeg](https://www.ffmpeg.org/) is absolutely required (if running in pure Python) (loads automatically when run as a docker container).
2. You may also want to erase *dummy.md* files from the following folders: *./models* (check recursively), *./sources*, *./async*, *./transcriptions*, *./utils/temp* – there only to force folder structure onto repository.
3. Finally, you will need to define an approach to partitions and adjust line #96 of *./audio_transcriptions_producer* to match. Since this is a decision that can only be made once real-world factors are considered, keys are currently simply tied to the type of transcription performed, which is doubtedly optimal.

### Configure LfK

#### Environment variables
Rename *.env.example* as *.env* and fill the information there to determine key behaviours and enable connectivity with cluster, schema registry, and any external storage service.

Make special note of the variable called "KAFKA_PLATFORM". Your configs will vary depending on the variable you enter in this field (details below).
* If value is 'confluent', configs will match the requirements for connectivity with a Confluent setup.
* If value is 'other', configs will be reduced to only bootstrap servers for main connectivity and url for schema registry:
* If value is different than 'confluent' or 'other', configs will default to a blank variable, which you can adjust by modifying *./config.py*.

### Run LfK
You can run LfK as a standalone Docker container or as a pure Python service.

#### Docker
If your system meets the settings used in this LfK distro, you might be able to run LfK as a standalone containerised microservice that communicates with your existing cluster. 

> Note 1. This service contains the core service only, i.e., transcribing audios and producing results to a final_transcriptions topic. if you wish to download final transcriptions to local devices, you need to run *./transcriptions_consumer.py* independently.

> Note 2. To stick with the principle of one process per container, LfK runs as two containers with a shared mounted volume. The first container reads Kafka messages and retrieves audio. The second container performs the transcription and messages it to the final_transcriptions topic.

To start the service:

```
# From the root directory.
docker compose up -d
```

To stop the service

```
# From the root directory.
docker compose down
```


#### Python
Alternatively, this branch contains all the Python files needed to run LfK directly with Python.

* Clone this branch and this branch only.
  * For guidance, see https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository and https://stackoverflow.com/questions/1778088/how-do-i-clone-a-single-branch-in-git.
* Create an environment around it.
  * For guidance, see https://docs.python.org/3/library/venv.html.
* Install required libraries: *pip install -r requirements.txt*.
  * For guidance, see https://pip.pypa.io/en/stable/user_guide/.
* Run all necessary scripts.
    * On the transcriptions hub: *python run_hub.py*.
      * Or run *python audio_consumer.py* and *python audio_watch.py* on separate terminals (clearer logs).
    * **Optional.** On any device acting as a consumer: *python transcriptions_consumer.py*.

## This guide is incomplete
I did my best to include all major considerations, but I have a feeling that I totally forgot something.

Feel free to contact: hello@polyzentrik.com.

## License
LfK is released under an Apache 2.0 license. See details at the main branch of this repository: https://github.com/jbolns/LOKAL_for_Kafka.

## Contribute or support the development of LfK
If you find LfK useful and want it to be maintained, please consider [making a voluntary payment](https://www.polyzentrik.com/help-us-help/).