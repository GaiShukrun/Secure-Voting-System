class AES:
    def __init__(self):
        # Initialize AES S-box (substitution box)
        self.sbox = [
            0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
            0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
            0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
            0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
            0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
            0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
            0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
            0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
            0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
            0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
            0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
            0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
            0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
            0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
            0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
            0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
        ]

        self.inv_sbox = [
            0x52, 0x09, 0x6a, 0xd5, 0x30, 0x36, 0xa5, 0x38, 0xbf, 0x40, 0xa3, 0x9e, 0x81, 0xf3, 0xd7, 0xfb,
            0x7c, 0xe3, 0x39, 0x82, 0x9b, 0x2f, 0xff, 0x87, 0x34, 0x8e, 0x43, 0x44, 0xc4, 0xde, 0xe9, 0xcb,
            0x54, 0x7b, 0x94, 0x32, 0xa6, 0xc2, 0x23, 0x3d, 0xee, 0x4c, 0x95, 0x0b, 0x42, 0xfa, 0xc3, 0x4e,
            0x08, 0x2e, 0xa1, 0x66, 0x28, 0xd9, 0x24, 0xb2, 0x76, 0x5b, 0xa2, 0x49, 0x6d, 0x8b, 0xd1, 0x25,
            0x72, 0xf8, 0xf6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xd4, 0xa4, 0x5c, 0xcc, 0x5d, 0x65, 0xb6, 0x92,
            0x6c, 0x70, 0x48, 0x50, 0xfd, 0xed, 0xb9, 0xda, 0x5e, 0x15, 0x46, 0x57, 0xa7, 0x8d, 0x9d, 0x84,
            0x90, 0xd8, 0xab, 0x00, 0x8c, 0xbc, 0xd3, 0x0a, 0xf7, 0xe4, 0x58, 0x05, 0xb8, 0xb3, 0x45, 0x06,
            0xd0, 0x2c, 0x1e, 0x8f, 0xca, 0x3f, 0x0f, 0x02, 0xc1, 0xaf, 0xbd, 0x03, 0x01, 0x13, 0x8a, 0x6b,
            0x3a, 0x91, 0x11, 0x41, 0x4f, 0x67, 0xdc, 0xea, 0x97, 0xf2, 0xcf, 0xce, 0xf0, 0xb4, 0xe6, 0x73,
            0x96, 0xac, 0x74, 0x22, 0xe7, 0xad, 0x35, 0x85, 0xe2, 0xf9, 0x37, 0xe8, 0x1c, 0x75, 0xdf, 0x6e,
            0x47, 0xf1, 0x1a, 0x71, 0x1d, 0x29, 0xc5, 0x89, 0x6f, 0xb7, 0x62, 0x0e, 0xaa, 0x18, 0xbe, 0x1b,
            0xfc, 0x56, 0x3e, 0x4b, 0xc6, 0xd2, 0x79, 0x20, 0x9a, 0xdb, 0xc0, 0xfe, 0x78, 0xcd, 0x5a, 0xf4,
            0x1f, 0xdd, 0xa8, 0x33, 0x88, 0x07, 0xc7, 0x31, 0xb1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xec, 0x5f,
            0x60, 0x51, 0x7f, 0xa9, 0x19, 0xb5, 0x4a, 0x0d, 0x2d, 0xe5, 0x7a, 0x9f, 0x93, 0xc9, 0x9c, 0xef,
            0xa0, 0xe0, 0x3b, 0x4d, 0xae, 0x2a, 0xf5, 0xb0, 0xc8, 0xeb, 0xbb, 0x3c, 0x83, 0x53, 0x99, 0x61,
            0x17, 0x2b, 0x04, 0x7e, 0xba, 0x77, 0xd6, 0x26, 0xe1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0c, 0x7d
        ]

        self.Rcon = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36]

    def sub_bytes(self, state):
        """Apply S-box substitution to each byte of the state"""
        # print("\nSubBytes:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        
        for i in range(4):
            for j in range(4):
                state[i][j] = self.sbox[state[i][j]]
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def inv_sub_bytes(self, state):
        """Apply inverse S-box substitution"""
        # print("\nInverse SubBytes:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        
        for i in range(4):
            for j in range(4):
                state[i][j] = self.inv_sbox[state[i][j]]
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def shift_rows(self, state):
        """Shift rows of state to the left by their row number"""
        # print("\nShiftRows:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        
        # Row 1: shift left by 1
        state[1] = state[1][1:] + state[1][:1]
        # Row 2: shift left by 2
        state[2] = state[2][2:] + state[2][:2]
        # Row 3: shift left by 3
        state[3] = state[3][3:] + state[3][:3]
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def inv_shift_rows(self, state):
        """Inverse shift rows of state to the right by their row number"""
        # print("\nInverse ShiftRows:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        
        # Row 1: shift right by 1
        state[1] = state[1][-1:] + state[1][:-1]
        # Row 2: shift right by 2
        state[2] = state[2][-2:] + state[2][:-2]
        # Row 3: shift right by 3
        state[3] = state[3][-3:] + state[3][:-3]
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def mix_columns(self, state):
        """Mix columns using Galois field multiplication"""
        # print("\nMixColumns:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        
        for i in range(4):
            column = state[i]
            state[i] = self.mix_single_column(column)
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def mix_single_column(self, column):
        """Mix one column for MixColumns operation"""
        temp = column.copy()
        column[0] = self.gmul(temp[0], 2) ^ self.gmul(temp[1], 3) ^ temp[2] ^ temp[3]
        column[1] = temp[0] ^ self.gmul(temp[1], 2) ^ self.gmul(temp[2], 3) ^ temp[3]
        column[2] = temp[0] ^ temp[1] ^ self.gmul(temp[2], 2) ^ self.gmul(temp[3], 3)
        column[3] = self.gmul(temp[0], 3) ^ temp[1] ^ temp[2] ^ self.gmul(temp[3], 2)
        return column

    def inv_mix_columns(self, state):
        """Inverse mix columns using Galois field multiplication"""
        # print("\nInverse MixColumns:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        
        for i in range(4):
            column = state[i]
            state[i] = self.inv_mix_single_column(column)
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def inv_mix_single_column(self, column):
        """Mix one column for Inverse MixColumns operation"""
        temp = column.copy()
        column[0] = self.gmul(temp[0], 0x0e) ^ self.gmul(temp[1], 0x0b) ^ self.gmul(temp[2], 0x0d) ^ self.gmul(temp[3], 0x09)
        column[1] = self.gmul(temp[0], 0x09) ^ self.gmul(temp[1], 0x0e) ^ self.gmul(temp[2], 0x0b) ^ self.gmul(temp[3], 0x0d)
        column[2] = self.gmul(temp[0], 0x0d) ^ self.gmul(temp[1], 0x09) ^ self.gmul(temp[2], 0x0e) ^ self.gmul(temp[3], 0x0b)
        column[3] = self.gmul(temp[0], 0x0b) ^ self.gmul(temp[1], 0x0d) ^ self.gmul(temp[2], 0x09) ^ self.gmul(temp[3], 0x0e)
        return column

    def gmul(self, a, b):
        """Galois field multiplication of a and b"""
        p = 0
        for _ in range(8):
            if b & 1:
                p ^= a
            carry = a & 0x80
            a = (a << 1) & 0xff
            if carry:
                a ^= 0x1b
            b >>= 1
        return p

    def add_round_key(self, state, round_key):
        """XOR the state with the round key"""
        # print("\nAddRoundKey:")
        # print(f"Before: {[[hex(x) for x in row] for row in state]}")
        # print(f"Key: {[[hex(x) for x in row] for row in round_key]}")
        
        for i in range(4):
            for j in range(4):
                state[i][j] ^= round_key[i][j]
        
        # print(f"After: {[[hex(x) for x in row] for row in state]}")
        return state

    def sub_word(self, word):
        """Substitute each byte in a word using the S-box"""
        return [self.sbox[b] for b in word]

    def rot_word(self, word):
        """Rotate the word one byte to the left"""
        return word[1:] + word[:1]

    def key_expansion(self, key):
        """Expand the 16-byte key into 11 round keys"""
        # Convert key to state array if it's a list
        if isinstance(key, list):
            key_state = [[key[4*i + j] for j in range(4)] for i in range(4)]
        else:
            key_state = [[key[i*4 + j] for j in range(4)] for i in range(4)]
        
        # print("\nKey Expansion:")
        # print(f"Original Key: {[[hex(x) for x in row] for row in key_state]}")
        
        # Create 11 round keys (44 words)
        expanded_keys = [key_state]
        
        for i in range(10): # 10 main rounds, characteristic of AES-128
            last_key = expanded_keys[-1]
            new_key = [[0 for _ in range(4)] for _ in range(4)]
            
            # Get last column of previous key
            last_col = [last_key[j][3] for j in range(4)]
            
            # Apply transformations
            rotated = self.rot_word(last_col)
            subbed = self.sub_word(rotated)
            rcon = [self.Rcon[i], 0, 0, 0]
            
            # First column
            for j in range(4):
                new_key[j][0] = last_key[j][0] ^ subbed[j] ^ rcon[j]
            
            # Other columns
            for col in range(1, 4):
                for row in range(4):
                    new_key[row][col] = last_key[row][col] ^ new_key[row][col-1]
            
            # print(f"Round {i+1} Key: {[[hex(x) for x in row] for row in new_key]}")
            expanded_keys.append(new_key)
        
        return expanded_keys

    def encrypt(self, state, key):
        """Encrypt a state matrix using the given key"""
        round_keys = self.key_expansion(key)
        
        # print("\nEncryption:")
        # print(f"Initial State: {[[hex(x) for x in row] for row in state]}")
        
        # Initial round
        state = self.add_round_key(state, round_keys[0])
        
        # Main rounds
        for i in range(1, 10):
            state = self.sub_bytes(state)
            state = self.shift_rows(state)
            state = self.mix_columns(state)
            state = self.add_round_key(state, round_keys[i])
        
        # Final round
        state = self.sub_bytes(state)
        state = self.shift_rows(state)
        state = self.add_round_key(state, round_keys[10])
        
        return state

    def decrypt(self, state, key):
        """Decrypt a state matrix using the given key"""
        round_keys = self.key_expansion(key)
        
        # print("\nDecryption:")
        # print(f"Initial State: {[[hex(x) for x in row] for row in state]}")
        
        # Initial round
        state = self.add_round_key(state, round_keys[10])
        state = self.inv_shift_rows(state)
        state = self.inv_sub_bytes(state)
        
        # Main rounds
        for i in range(9, 0, -1):
            state = self.add_round_key(state, round_keys[i])
            state = self.inv_mix_columns(state)
            state = self.inv_shift_rows(state)
            state = self.inv_sub_bytes(state)
        
        state = self.add_round_key(state, round_keys[0])
        return state