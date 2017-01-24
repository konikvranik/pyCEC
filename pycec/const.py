VENDORS = {0x0020C7: 'Akai',
           0x0010FA: 'Apple',
           0x002467: 'AOC',
           0x8065E9: 'Benq',
           0x18C086: 'Broadcom',
           0x009053: 'Daewoo',
           0x0005CD: 'Denon',
           0x001A11: 'Google',
           0x00D0D5: 'Grundig',
           0x001950: 'Harman Kardon',
           0x9C645E: 'Harman Kardon',
           0x00E091: 'LG',
           0x000982: 'Loewe',
           0x000678: 'Marantz',
           0x000CB8: 'Medion',
           0x0009B0: 'Onkyo',
           0x008045: 'Panasonic',
           0x00903E: 'Philips',
           0x00E036: 'Pioneer',
           0x001582: 'Pulse Eight',
           0x8AC72E: 'Roku',
           0x0000F0: 'Samsung',
           0x08001F: 'Sharp',
           0x534850: 'Sharp',
           0x080046: 'Sony',
           0x000039: 'Toshiba',
           0x000CE7: 'Toshiba',
           0x6B746D: 'Vizio',
           0x00A0DE: 'Yamaha',
           0: 'Unknown'}

CEC_LOGICAL_TO_TYPE = [0,  # TV0
                       1,  # Recorder 1
                       1,  # Recorder 2
                       3,  # Tuner 1
                       4,  # Playback 1
                       5,  # Audio
                       3,  # Tuner 2
                       3,  # Tuner 3
                       4,  # Playback 2
                       1,  # Recorder 3
                       3,  # Tuner 4
                       4,  # Playback 3
                       2,  # Reserved 1
                       2,  # Reserved 2
                       2,  # Free use
                       2]  # Broadcast

DEVICE_TYPE_NAMES = ["TV", "Recorder", "UNKNOWN", "Tuner", "Playback", "Audio"]

TYPE_TV = 0
TYPE_RECORDER = 1
TYPE_UNKNOWN = 2
TYPE_TUNER = 3
TYPE_PLAYBACK = 4
TYPE_AUDIO = 5

CMD_PHYSICAL_ADDRESS = (0x83, 0x84)
CMD_POWER_STATUS = (0x8f, 0x90)
CMD_AUDIO_STATUS = (0x71, 0x7a)
CMD_VENDOR = (0x8c, 0x87)
CMD_MENU_LANGUAGE = (0x91, 0x32)
CMD_OSD_NAME = (0x46, 0x47)
CMD_AUDIO_MODE_STATUS = (0x7d, 0x7e)
CMD_DECK_STATUS = (0x1a, 0x1b)
CMD_TUNER_STATUS = (0x07, 0x08)
CMD_MENU_STATUS = (0x8d, 0x8e)

CMD_ACTIVE_SOURCE = 0x82
CMD_STREAM_PATH = 0x86
CMD_KEY_PRESS = 0x44
CMD_KEY_RELEASE = 0x45
CMD_PLAY = 0x41
CMD_STANDBY = 0x36
CMD_POLL = None

STATUS_PLAY = 0x11
STATUS_RECORD = 0x12
STATUS_STILL = 0x14
STATUS_STOP = 0x1a
STATUS_OTHER = 0x1f

POWER_ON = 0x00
POWER_OFF = 0x01

PLAY_FORWARD = 0x24
PLAY_STILL = 0x25
PLAY_FAST_FORWARD_MEDIUM = 0x06
PLAY_FAST_REVERSE_MEDIUM = 0x0a

KEY_VOLUME_DOWN = 0x42
KEY_VOLUME_UP = 0x41
KEY_MUTE_TOGGLE = 0x43
KEY_MUTE_ON = 0x65
KEY_MUTE_OFF = 0x66
KEY_PLAY = 0x44
KEY_MUTE_FUNCTION = 0x65
KEY_STOP = 0x45
KEY_PAUSE = 0x46
KEY_RECORD = 0x47
KEY_REWIND = 0x48
KEY_FAST_FORWARD = 0x49
KEY_EJECT = 0x4a
KEY_FORWARD = 0x4b
KEY_BACKWARD = 0x4c
KEY_STOP_RECORD = 0x4d
KEY_PAUSE_RECORD = 0x4e
KEY_INPUT_SELECT = 0x34
KEY_POWER = 0x40
KEY_POWER_ON = 0x6d
KEY_POWER_OFF = 0x6c
KEY_POWER_TOGGLE = 0x6b

ADDR_UNKNOWN = -1
ADDR_TV = 0
ADDR_RECORDINGDEVICE1 = 1
ADDR_RECORDINGDEVICE2 = 2
ADDR_TUNER1 = 3
ADDR_PLAYBACKDEVICE1 = 4
ADDR_AUDIOSYSTEM = 5
ADDR_TUNER2 = 6
ADDR_TUNER3 = 7
ADDR_PLAYBACKDEVICE2 = 8
ADDR_RECORDINGDEVICE3 = 9
ADDR_TUNER4 = 10
ADDR_PLAYBACKDEVICE3 = 11
ADDR_RESERVED1 = 12
ADDR_RESERVED2 = 13
ADDR_FREEUSE = 14
ADDR_UNREGISTERED = 15
ADDR_BROADCAST = 15
