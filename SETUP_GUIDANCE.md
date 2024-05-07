# LOKAL for Kafka (setup guidance)
This file contains rough setup and usage instructions for LOKAL for Kafka (LfK).

Please note that the guidance is intended for developers who understand both Kafka and Python and is meant only as illustrative rough guidance.

LfK is being open-sourced in a generic alpha version to allow integration into broader ecosystems. Actual setup requires considering the specific needs of the broader ecosystem. This may call for significant changes to anything and everything covered in this guidance.

For the same reason, please also note the software is not nor tries to be a production-ready solution. While basic testing has been done to ensure a degree of operability and robustness, LfK as not been tested in its final intended setting – this is only logically possible upon integrating it into a broader ecosystem.

Linting pending.

## Prerequisites
This section covers the steps needed to set up the basic Kafka and Python infrastructure needed to run LfK.

### Kafka
LfK was developed and tested using Confluent's Cloud. If you are also using Confluent Cloud, you will need:
* A working enviromnent,
* A working cluster,
* The address for your bootstrap servers,
* API keys and secret,
* Schema Registry keys and secret.

If you are not using Confluent Cloud, LfK might probably still work, but I have not tested it. So, good luck and let me know how it goes!

### Python set up:
This repository contains the entire LfK distribution. It is eventually necessary to split the repository into admin-, producer-, and consumer-specific distributions. Having said that, you can start by cloning or otherwise downloading the whole thing:

* Cloning the entire repository. 
  * For guidance, see https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository and https://stackoverflow.com/questions/1778088/how-do-i-clone-a-single-branch-in-git.
  * The main branch has the latest released version.
  * The dev branch has latest commits.
* Creating an environment around it.
  * For guidance, see https://docs.python.org/3/library/venv.html.
* Installing required libraries using pip install -r requirements.txt.
  * For guidance, see https://pip.pypa.io/en/stable/user_guide/.

After, delete *dummy.md* files used to force the folder structure to show on the repository. LfK will work even if you leave them there, but these files are not needed for regular operations and are completely annoying (do NOT delete folders, though – the folder structure is needed in future steps):
* *./models*: check subfolders recursively for any file named *dummy.md*,
* *./sources*: check subfolders recursively for any file named *dummy.md*,
* *./transcriptions*: check subfolders recursively for any file named *dummy.md*,
* *./utils/temp/dummy.md.*


### AI models
OpenAI's Whisper models download by themselves to the folder *./models/whisper* on first use. This is the best way to ensure the models are to the latest standard available.

However, you will need to download some of the models needed to run other aspects of LfK (you will need a Hugging Face account to ask access to the models):
* Pyannote's speaker segmentation 3.0: https://huggingface.co/pyannote/segmentation-3.0.
  * Files needed: *config.yaml*, *pytorch_model.bin*.
  * Place in folder: *models\segmentation*. Be sure to also include a copy of the LICENSE and provide appropriate credits.
* Pyannote's wespeaker-voxceleb-resnet34-LM wrapper: https://huggingface.co/pyannote/wespeaker-voxceleb-resnet34-LM.
  * Files needed: *config.yaml*, *pytorch_model.bin*.
  * Place in folder: *models\embedding*. Be sure to also include a copy of the LICENSE and provide appropriate credits.
* Pyannote's speaker diarization 3.1: https://huggingface.co/pyannote/speaker-diarization-3.1.
  * Files needed: *config.yaml*, *handler.py*, *requirements.txt*.
  * Place in folder: *models\diarization*. Be sure to also include a copy of the LICENSE and provide appropriate credits.

Alternatively, you can adjust the functions in the file *./utils/lokal_transcribe.py* to enable automatic downloads via the HF hub. This is a relatively quick modification that you can do yourself by following the instructions in each of the pages linked above.

### FFmpeg
[FFmpeg](https://www.ffmpeg.org/) is required on any system running audio producers or audio consumers. FFmpeg is used for conversions between audio types and LfK's native audio format (*.wav*) and by the transcription models. Without it, LfK will quite simply not work. Installation guidance for FFmpeg is available [here](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/).

It is also a good idea to check FFmpeg's to ensure you use it in accordance with their license terms.

## Set up
The following steps cover the steps needed to set LfK up and run it in its generic form.

### Environment variables (.env)
All commonly used config variables go into an *.env* file at the root of the repository. For security reasons, this repository does not contain a fully working *.env* file with active loging details for a working Kafka cluster. However, you can copy *.env.example* as *.env* and then fill out all information there. 

**Confluent Cloud.** Settings needed to connect to Confluent Cloud.
* BOOTSTRAP_SERVERS: You get this from Confluent.
* API_KEY: You get this from Confluent.
* API_SECRET: You get this from Confluent.

**Schema Registry.** Settings needed to connect to Confluent's Schema Registry.
* SCHEMA_REGISTRY_URL: You get this from Confluent.
* SCHEMA_REGISTRY_KEY: You get this from Confluent.
* SCHEMA_REGISTRY_SECRET: You get this from Confluent.

**Schema type.** This will tell the rest of files what kind of schema you are using.
* SCHEMA_TYPE: 'Avro' or 'JSON' (LfK is compatible with either, but not with protobuf).

**Topic configurations.** Configurations applicable to topics and messages.
* MAX_MESSAGE_SIZE: Max size for any one message, in bytes. Confluent's default is 2097164, which is OK for most audio content.
* AUDIO_SIZE_RATIO: Messages carry some meta-data and overhead, so this sets the max % of message size audio itself can use. LfK was tested using a value of 0.4.
* JSON_RATIO: JSON instead of Avro, this reduces the max size of the audio field (JSON messages seem to have larger overhead). LfK was tested using a value of 0.3.

**LfK settings.** Paths and settings commonly used by LfK.
* SOURCE_FOLDER: The local (PRODUCER) folder to watch for any audios (the default is '.\\sources')
* MAIN_NODE_TEMP_FOLDER: The main hub folder to perform temporary operations (the default is '.\\utils\\temp').
* MAIN_NODE_TRANSCRIPTIONS_FOLDER: The main hub folder to save completed transcriptions (the default is '.\\transcriptions').
* LOCAL_NODE_OUTPUT_FOLDER: The local (CONSUMER) folder to save any received transcriptions (the default is the user's Desktop).
* TIMESTAMPS: Whether to use timestamps or not.
* CENTRAL_BACKUPS: Whether to keep a central backup of audios and transcriptions in main hub or not.

### Schemas
To facilitate integration with Kafka ecosystems, LfK is compatible with both Avro and JSON schemas (schema strings are located in *./schemas*). Whenever the choice of either schema type calls for different code, LfK checks *.env* and uses the corresponding code.

To understand LfK's approach to schemas, it is important to have in mind that audio files are typically too large in size to send in a single Kafka message. 

There are two ways to manage this challenge. In the 'location-driven' solution you send a small message containing the location of the audio and have the consumers request the audio over the Internet. In the 'audio-driven' solution, you break the audio into small pieces to send as separate messages and have the consumer reconstruct audios once it receives all segments.

LfK packs with a schema that can be used to support either the 'location-driven' or 'audio-driven' solution. 

Irrespective of which schema type you choose, the message will contain:
* path_to_audio: a path to the audio location,
* transcription_approach: a lfk string containing information about transcription style and model size,
* final: if audios is too long for a single message, LfK chunk it into segments and uses this field to flag the last segment,
* params: a short strong with the headers needed to reconstruct the audio,
* frames: a very long string (bytes in avro, base64 in JSON) with the actual audio content,
* timestamp: the timestamp at which the message was created.

Do NOT under any circumstance delete the *path_to_audio* field. As explained in due course, LfK uses the path's structure to transfer information about the approach and model size to be used during transcription. Additionally, if you opt for the 'location-driven' solution you will need to recreate aspects of the path's structure for transcriptions to be possible. More details about this later in this guidance.

### Creating topics
The repository comes with a file named *admin.py*. You can use this file to create topics needed for a basic LfK configuration.

The file is not particularly original. It is basically [this approach](https://developer.confluent.io/courses/kafka-python/adminclient-class-hands-on/) with minor modifications to produce Avro or JSON topics as determined by the corresponding setting in .env.

In real world conditions, you probably need several topics with a carefully calculated number of partitions determined by your business specifics. You might be able to achieve this by modifying *'admin.py* slightly.

Having said that, the *'admin.py* file can help you rapidly set up topics to run LfK in its generic form.

## Operational logic
The following sections explain the overall production-consumption-production-consumption logic by which audios created in a specific local device are transcribed and made available to many other devices (which may or may not include the audio originator).

> Note. Please keep in mind that LfK is compatible with both Avro and JSON schemas, which is handled via strategically placed IFs across files. 

### Producing audios (in local devices)
Audio detection and production of audio messages is handled from the file called *producer_audios.py*.

This file is logically divided into two sections.

#### Watchdog
LfK uses Python Watchdog to keep an eye on the source folder (set in .env) for any audio files saved to it. Once an audio file is saved to the source folder, Watchdog sends the audio location to the second part of the producer.

The structure of LfK's source folder is important. The folder has two levels of subfolders, which determine the type of transcription you will get. You can in theory drop audio files to this folder, but it might make more sense to think about it as a destination to programatically drop audios created by a different application (which allows you to easily manage the subfolder the audio goes to by, e.g., giving user choices via dropdowns):
* Simple: line to line transcription of words only.
  * Tiny: transcription using model of size *tiny*,
  * Base: transcription using model of size *base*,
  * Small: transcription using model of size *small*,
  * Medium: transcription using model of size *medium*,
  * Large: transcription using model of size *large*.
* Segmentation: transcription split into small paragraphs roughly corresponding to pauses in speech (helpful for, e.g., transcribing conversations in multiple languages).
  * Tiny/Base/Small/Medium/Large. 
* Diarisation: transcription split into paragraphs roughly corresponding to speaker changes.
  * Tiny/Base/Small/Medium/Large.

If you opt to use a different source folder, you will need to figure out how to include the subfolder structure in the message's *path_to_audio* field because the transcription consumer gets styling information from this path. 

#### Message
The Kafka producer section of *producer_audios.py* is essentially an audio splitter and messaging loop. 
* Ideal audio segment size is calculated after considering the size and duration of the audio, the max_message size of topic, and the ratios set in *.env*.
* The main audio is segmented into as many chunks as needed.
  * LfK will print out a notice to inform the duration of segments to produce.
* Each segment is sent in a separate message.
* When the loop hits the last segment, it flags it as final using the *final* field in the schema.

Since Kafka cannot handle audios natively, the audio is also split into two components: *params* and *frames*. 
* Params: a very short string containing the headers needed to reconstruct the audio,
* Frames: a very long string containing the actual content of the audio.
  * This string is a bytes string if you are using Avro and base64 string if you are using JSON.
  * The need to convert bytes to base64 is the main reason why JSON schemas tend to require more messages per audio than Avro.
  * If you get errors saying some messages are too large to send via Kafka, play around with *AUDIO_SIZE_RATIO* and *JSON_RATIO* (in .env).
  * If you get size-related errors with 1 second long segments, adjust the topic's max_message_size.
  * Audios are not typically so high-quality for a second-long segment to be so massive that it cannot be sent over Kafka. Having said that, if you are using such ridiculously high-quality audios that 1 second long segments error out even after increasing the topic's max_message_size, consider reducing audio quality. LfK is a transcriptions solution. Audios need to be clear enough for conversations to come through. More is an overkill.

### Consuming audios & producing transcriptions (in the transcription hub)
The files needed for the transcription hub to consume audio messages and produce transcriptions are *consumer_audios.py* and *producer_transcriptions.py*.

Both create temporary files (wiped out automatically) and thus need writing privileges. Additionally, *consumer_audios.py* recreates the original audio file and writes the transcription to a .txt file (audios and transcriptions can be deleted automatically by using the *CENTRAL_BACKUPS* setting in *.env*).

#### Audio consumer
The consumption of audios *consumer_audios.py* is a relatively straightforward process that can, nonetheless, be lengthy due to the need to call a few AI models to transcribed the audios.
* LfK checks if a message is the last in a series of messages.
  * If it is not, it accumulates the message.
  * If it is, it joins accumulated messages, reconstructs the audio, and triggers transcription.
* The rest of the process varies depending on the approach requested.
  * If approach is 'simple': the chosen transcription model is called on the entire audio.
  * If approach is 'segmentation': a segmentation function breaks the audio into segments determined by pauses in speech, calls the transcription model on each segment, and joins results.
  * If approach is 'diarisation': a diarisation function breaks the audio into segments corresponding to speakers, calls the transcription model on each segment, and joins results.
* Timestamps can be enabled/disabled globally via *.env' or specifically for a given audio by adding the keyword "-lfkn0t1m3" to the original audio filename.

At the end of the transcription process, *consumer_audios.py* writes a finalised transcription to the *./transcriptions* folder.

> Note. Kafka can timeout if transcription takes too long. There are settings to manage this and one could even consider completely detaching the audio consumer from the transcription service to avoid any potential timeouts. However, since the idea is to enable near real-time time outputs, the seemingly reasonable alternative is to ensure the transcription hub is powerful enough to avoid unreasonable waiting periods.

#### Transcriptions producer
Production of transcriptions is simpler than production of audios, but follows a similar two-step logic.
* Using Watchdog, *producer_transcriptions* detect when a transcription is written to the transcriptions folder.
* When a transcription is detected, *producer_transcriptions* opens it, reads it, and sends the contents as a Kafka message.

> Note. To avoid redundant messages due to duplicate file operations, the transcription producer creates a cache file with the contents of the very last message sent. If the contents of a potential new message are the exact same as the cache, the new message is flagged as redundant and not sent. This cache file survives deletion even if central backups are turned off.

### Transcriptions consumer (needed in devices receiving the final transcriptions)
Consumption of transcriptions is handled by *consumer_transcriptions.py*, which is a fairly straightforward.
* When a new message arrives, the consumer takes the contents of the transcriptions and writes them to a .txt file located in destination folder set in *.env*.

## Creating role-specific distributions
It makes no sense to pack the entire LfK code base into every single device in your organisation. That would not be smart.

At a minimum, once you have ensured things run appropriately, you will need to split this repository into role-specific distributions and install the corresponding distributions into the appropriate devices.
* Admins: perhaps just keep the repository as it is.
* Audio creators: delete all producers and consumers besides *producer_audios.py*.
* Main transcription hub: delete all producers and consumers besides *consumer_audios.py* and *producer_transcriptions.py*.
* Transcription consumers, delete all producers and consumers besides *consumer_transcriptions.py*.
  * If an audio creator is also a transcription consumer, leave both *producer_audios.py* and *consumer_transcriptions.py*.

This is a minimum. It would be ideal to also go over all the scripts in the *./utils* folder removing any functions not needed by the particular role.

## This guide is incomplete
This is the longest guidance document I have ever written. It was very boring, but I did my best to include all major considerations needed to get a sense of how LfK works.

Having said that, I have a feeling that I totally forgot something.

Sorry about that! 

## Having troubles?
LfK is a sophisticated solution for a complex problem. Challenges may arise. 

Do get in touch if you feel stuck: hello@polyzentrik.com.