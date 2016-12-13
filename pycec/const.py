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
