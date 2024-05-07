# LOKAL for Kafka
LOKAL for Kafka (LfK) (Alpha) is a Python-Kafka event-driven micro-services solution for distributed audio transcriptions.

When an audio is saved or recorded to a local computer/device LfK folder (which can be done manually or programmatically), LfK detects it and transfers it to a computing node/hub, where a transcription is created. When the transcription is ready, LfK makes it available to anyone subscribed to the service. If the transcription hub can handle transcriptions as fast as audios arrive, all happens in real-time. Else, messages queue.

![Diagram of how LOKAL for Kafka works](./assets/lfk-diagram.png)

> *Please note. LfK is **NOT** for sporadic personal usage. If you need transcriptions for yourself, use the original LOKAL instead: https://github.com/jbolns/LOKAL_transcriptions.*

## A component for broader ecosystems
LfK is for situations where the information contained in audio interactions (calls, meetings, conferences, etc.) is valuable, but audios are either created by many users/devices at different times and in different locations *or* the information contained in them is needed by many users/devices at different times and in different locations.

There are many potential use cases, including – but not limited to – customer service, organisational analytics, multi-location human-machine interactions, and healthcare.

Having said that, LfK is being open-sourced in a generic alpha version to allow integration into broader ecosystems, rather than as a final production-ready plug-and-play solution.

## Flexible
Instead of enforcing a particular style/quality for the entire organisation, LfK has options to pick between three different transcription approaches ([simple](./assets/example_simple_tiny.txt), [segmented](./assets/example_segmentation_tiny.txt), [diarised](./assets/example_diarisation_tiny.txt)) and all five OpenAI Whisper model sizes/qualities available([tiny](./assets/example_simple_tiny.txt), [base](./assets/example_simple_base.txt), [small](./assets/example_simple_small.txt), [medium](./assets/example_simple_medium.txt), [large](./assets/example_simple_large.txt)). There is also a setting to turn timestamps on and off by default, and a way to opt out from the default.

All options above are available on a transcription-by-transcription basis and can be accessed in one of three manners: 
* Dragging/dropping audios into the corresponding section of LfK's source folder (not recommended),
* Giving users an interface/App with straightforward dropdown options (recommended – the original LOKAL can be easily repurposed for this),
* Programatically placing audios in the appropriate folder (also recommended).

## Setup guidance
Setup guidance is available separately. Click [here](./SETUP_GUIDANCE.md) to access it.

Please note guidance is currently intended for developers with knowledge of both Kafka and Python.

## Known limitations
AI is not a magic pill. It has limitations. LfK's limitations include but are not limited to:

**Performance.** All models might incurr signficant errors, especially when overlapping speakers are present and/or speech involves names, places, acronyms, accents, industry-specific terms, or multiple languages. These limitations are considered reasonable. Where humans currently spend too much time on transcriptions at the expense of other more critical tasks, LfK can act as a preliminary tool that reduces the time needed to undertake transcriptions (provided human oversight and edition are present to ensure accuracy and precision). Where perfect accuracy and precision are not needed, LfK can help increase the amount of information available for analysis (provided analysis acknowledges and manages for the fact that the data corpus LfK or any AI tool can help to generate might contain significant errors). In any case, LfK needs to be implemented responsibly and users must remain in and be given sufficient control of and insight into the process.

**Cyber-security.** LfK is not designed to automatically consider cyber-security risks.

**Context-awareness.** In its generic form, LfK is not designed to consider the specific needs of any given industry. 

## License
LfK is released under an Apache 2.0 license. The code is available via GitHub: https://github.com/jbolns/LOKAL_for_Kafka.

## Support the development of LfK
If you find LfK useful and want it to be maintained, please consider [making a voluntary payment](https://www.polyzentrik.com/help-us-help/).

Or get in touch for implementation assistance and continued support: hello@polyzentrik.com.