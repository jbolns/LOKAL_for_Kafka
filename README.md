# LOKAL for Kafka
LOKAL for Kafka (LfK). Python + Kafka micro-services solution for distributed audio transcriptions:

1. Audio is recorded/created and messaged to Kafka
2. LfK transfers it to a transcriptions hub
3. When transcription is ready, LfK messages result back to Kafka

![Diagram of how LOKAL for Kafka works](./assets/lfk-diagram.png)

## A component for broader ecosystems
LfK is for situations where MANY audios are created across MANY places and transcriptions are needed elsewhere or across MANY places.

Many use cases exist, including – but not limited to – customer service, organisational analytics, multi-location human-machine interactions, and healthcare.

That said, LfK is meant as a component for broader microservice ecosystems rather than as a standalone solution in itself. For a standalone transcriptions app, see the [original LOKAL](https://github.com/jbolns/LOKAL_transcriptions).

## Example outputs
LfK is fairly flexible. It allows user to pick between several approaches to transcription ([simple](./assets/example_simple_tiny.txt), [segmented](./assets/example_segmentation_tiny.txt), [diarised](./assets/example_diarisation_tiny.txt)) and five OpenAI Whisper model sizes/qualities available ([tiny](./assets/example_simple_tiny.txt), [base](./assets/example_simple_base.txt), [small](./assets/example_simple_small.txt), [medium](./assets/example_simple_medium.txt), [large](./assets/example_simple_large.txt)).

## Flavoured distribution approach

### Main branch is a non-deployable foundation
**Do NOT implement from main branch.** The main branch is a base to develop flavoured LfK distributions using **either** JSON or Avro schemas and messaging **either** full audios or audio locations. The branch, thus, contains redundant chunks not needed in any given approach (one opts between full audios or locations and between JSON and Avro), can be in a broken state, and is often out-of-sync with other branches. Use only if you want to help develop LfK further.

### Deployable "flavours" available at other branches
For slimmed down flavoured LfK distributions that are more easily deployable as a microservice, see tailored branches for:
* [JSON schemas + location-based messaging](https://github.com/jbolns/LOKAL_for_Kafka/tree/location-based-json). This branch contains a slimmed down LfK distribution that is more easily compatible with systems using JSON schemas and location-based audio messaging (Kafka messages contain the locations of audios rather than the audios themselves).

Or get in touch to request an additional tailored branch fully matching your system characteristics: hello@polyzentrik.com.

## Known limitations
AI is not a magic pill. It has limitations. LfK's limitations include:

**Performance.** All models might incurr signficant errors, especially when overlapping speakers are present and/or speech involves names, places, acronyms, accents, industry-specific terms, or multiple languages. These limitations are considered reasonable. Where humans currently spend too much time on transcriptions at the expense of other more critical tasks, LfK can act as a preliminary tool that reduces the time needed to undertake transcriptions. Where perfect accuracy and precision are not needed, LfK can help increase the amount of information available for analysis. In any case, LfK needs to be implemented responsibly and users must remain in and be given sufficient control of and insight into the process.

**Cyber-security.** LfK is not designed to automatically consider cyber-security risks.

**Context-awareness.** In its generic form, LfK is not designed to consider the specific needs of any given industry.

## License
LfK is released under an Apache 2.0 license. The code is available via GitHub: https://github.com/jbolns/LOKAL_for_Kafka.

## Contribute or support the development of LfK
If you find LfK useful and want it to be maintained, please consider [making a voluntary payment](https://www.polyzentrik.com/help-us-help/).

Alternatively, get in touch to contribute differently (perhaps with code or other kind of knowledge-based contributions).