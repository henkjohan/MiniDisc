# MiniDisc interface module for the Sony MDS-E12
The MDS-E12 has a build in RS232 port, like several other studio line MiniDisc players. This interface can be used to control the player from a computer.
This interface module enables the user to interact with the player in such a way that fully automated recording on the MiniDisc is possible.

# Modules used and interaction
```mermaid
graph TD
  A[user_script] --> B[RS232]
  B --> C[SONY_MDS_E12]

  A --> D[audio_handler]
  D --> E[miniaudio]
  E --> J[PC audio out]
  J --> C

  F[mutagen] --> E
  G[ID3] --> F
  H[MP3] --> F
  I[FlAC] --> F

```
## mutagen
ID3, MP3 and FLAC are used from mutagen to extract metadata information from MP3 or FLAC files.
This is the title and artist to form later the track title for the MiniDisc.
Also the track length as we need that for our timer as the player we are using is not blocking.

## miniaudio
The miniaudio module is used to playback the track that we want to record on the MiniDisc.


# Connections
The following connections need to be made between the computer and the MDS-E12.
The audio connection can either be analog or digital.

```mermaid
graph TD
  A[computer] --> B[RS232]
  A --> C[audio_connection]
  B --> D[MDS-E12]
  C --> D
```
