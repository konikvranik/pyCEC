VENDORS = {0x000039: 'Toshiba',
           0x0000F0: 'Samsung',
           0x0005CD: 'Denon',
           0x000678: 'Marantz',
           0x000982: 'Loewe',
           0x0009B0: 'Onkyo',
           0x000CB8: 'Medion',
           0x000CE7: 'Toshiba',
           0x001582: 'PulseEight',
           0x001950: 'HarmanKardon',
           0x001A11: 'Google',
           0x0020C7: 'Akai',
           0x002467: 'AOC',
           0x008045: 'Panasonic',
           0x00903E: 'Philips',
           0x009053: 'Daewoo',
           0x00A0DE: 'Yamaha',
           0x00D0D5: 'Grundig',
           0x00E036: 'Pioneer',
           0x00E091: 'LG',
           0x08001F: 'Sharp',
           0x080046: 'Sony',
           0x18C086: 'Broadcom',
           0x534850: 'Sharp',
           0x6B746D: 'Vizio',
           0x8065E9: 'Benq',
           0x9C645E: 'HarmanKardon',
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

CMD_KEY_PRESS = 0x44
CMD_KEY_RELEASE = 0x45

KEY_VOLUME_DOWN = 0x42
KEY_VOLUME_UP = 0x41
KEY_MUTE = 0x43

TYPE_RECORDER_1 = 1

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
