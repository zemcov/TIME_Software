import crcmod


def crc16_calc(lst_bytes):
    crc = 0
    init = 0xFFFF
    initial = True
    num_shifts = 0
    for byte in lst_bytes:
        if initial:
            crc = init ^ byte
            while (~( crc & 1)):
                crc = crc >> 1
                num_shifts += 1
            initial = False
        else:
            crc = 0xA001 ^ crc
            while num_shifts < 9:
                while ~( crc & 1):
                    crc = crc >> 1
                    num_shifts += 1
        num_shifts = 0
        
    return crc
crc = crc16_calc([0x0002, 0x0007])                     
print(crc)          
                     
        
        
    
