import sys
import os

def make_crc32_table(poly):
    table = [0] * 256
    for i in range(256):
        c = i
        for j in range(8):
            if c & 1:
                c = poly ^ (c >> 1)
            else:
                c >>= 1
        table[i] = c
    return table

def crc32_standard(data, table, crc=0):
    crc ^= 0xffffffff
    for byte in data:
        crc = table[(crc ^ byte) & 0xff] ^ (crc >> 8)
    return crc ^ 0xffffffff

def next_internal(crc, table):
    return table[crc & 0xff] ^ (crc >> 8)

def find_patch_bytes(internal_current, internal_target, table, N):
    num_bits = 8 * N
    zero_appended = internal_current
    for _ in range(N):
        zero_appended = next_internal(zero_appended, table)
    delta = zero_appended ^ internal_target

    matrix = [0] * 32
    for pos in range(num_bits):
        remaining = pos // 8
        bitpos = pos % 8
        val = 1 << bitpos
        contrib = table[val]
        for _ in range(remaining):
            contrib = next_internal(contrib, table)
        for r in range(32):
            if contrib & (1 << r):
                matrix[r] |= (1 << pos)

    b_bits = [(delta >> i) & 1 for i in range(32)]
    augmented = [matrix[i] | (b_bits[i] << num_bits) for i in range(32)]
    current_row = 0
    pivots = [-1] * 32

    for col in range(num_bits):
        pivot = -1
        for r in range(current_row, 32):
            if augmented[r] & (1 << col):
                pivot = r
                break
        if pivot == -1:
            continue
        augmented[current_row], augmented[pivot] = augmented[pivot], augmented[current_row]
        for r in range(32):
            if r != current_row and (augmented[r] & (1 << col)):
                augmented[r] ^= augmented[current_row]
        pivots[current_row] = col
        current_row += 1
        if current_row == 32:
            break

    for r in range(current_row, 32):
        if (augmented[r] >> num_bits) & 1:
            return None

    solution_bits = [0] * num_bits
    for row in range(current_row - 1, -1, -1):
        col = pivots[row]
        s = (augmented[row] >> num_bits) & 1
        for c in range(col + 1, num_bits):
            if augmented[row] & (1 << c):
                s ^= solution_bits[c]
        solution_bits[col] = s

    patch_int = 0
    for pos in range(num_bits):
        if solution_bits[pos]:
            patch_int |= 1 << pos
    return patch_int

def main():
    if len(sys.argv) != 3:
        print("ex: python crc.py filename crc")
        sys.exit(1)

    filename = sys.argv[1]
    target_str = sys.argv[2]

    if not os.path.isfile(filename):
        print(f"'{filename}' not found")
        sys.exit(1)

    with open(filename, 'rb') as f:
        data = f.read()

    poly = 0xedb88320
    table = make_crc32_table(poly)

    current_crc = crc32_standard(data, table) & 0xffffffff

    target_str_lower = target_str.lower()
    if target_str_lower.startswith('0x'):
        target_str_lower = target_str_lower[2:]
    try:
        target = int(target_str_lower, 16) & 0xffffffff
    except ValueError:
        try:
            target = int(target_str_lower, 10) & 0xffffffff
        except ValueError:
            print("Invalid value")
            sys.exit(1)

    if current_crc == target:
        print("already matches")
        sys.exit(0)

    internal_current = current_crc ^ 0xffffffff
    internal_target = target ^ 0xffffffff

    N = 4
    patch_int = None
    while N <= 16:
        patch_int = find_patch_bytes(internal_current, internal_target, table, N)
        if patch_int is not None:
            break
        N += 1

    if patch_int is None:
        print("not find solution with N <= 16")
        sys.exit(1)

    patch_bytes = []
    for i in range(N):
        shift = 8 * (N - 1 - i)
        byte = (patch_int >> shift) & 0xff
        patch_bytes.append(byte)
        
    base_name = os.path.splitext(filename)[0]
    patched_filename = f"{base_name}_patched{os.path.splitext(filename)[1]}"
    with open(patched_filename, 'wb') as f:
        f.write(data + bytes(patch_bytes))

    with open(patched_filename, 'rb') as f:
        new_data = f.read()

    new_crc = crc32_standard(new_data, table) & 0xffffffff

    if new_crc == target:
        print(f"Patched with {N} bytes: {bytes(patch_bytes).hex()}. New file: {patched_filename}")
    else:
        print("failed")
        sys.exit(1)

if __name__ == '__main__':
    main()