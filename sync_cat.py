import os
import time
from optparse import OptionParser

# Constants for clarity
SECTOR_SIZE = 512
BYTE_SIZE_MULTIPLIER = 100
CHUNK_SIZE = SECTOR_SIZE * BYTE_SIZE_MULTIPLIER

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=40, fill='='):
    """
    Standard terminal progress bar.
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} [{bar}] {percent}% {suffix}', end='')
    if iteration >= total:
        print()

def main(src, dest):
    src_size = os.path.getsize(src)
    dest_size = os.path.getsize(dest)

    if dest_size >= src_size:
        print("Destination is already the same size or larger than source.")
        return

    # Open both files: dest in r+b (read/update), src in rb (read)
    with open(dest, "r+b") as dest_f, open(src, "rb") as src_f:
        # 1. Validation: Compare the last 1% of the existing destination data
        # to the same section in the source to ensure they match.
        check_offset = int(dest_size * 0.99)
        dest_f.seek(check_offset)
        src_f.seek(check_offset)
        
        chunk_to_check = dest_f.read()
        if src_f.read(len(chunk_to_check)) != chunk_to_check:
            print("Error: Destination file content does not match source. Cannot resume.")
            return

        # 2. Preparation for Resume
        dest_f.seek(0, os.SEEK_END)
        current_pos = dest_f.tell()
        src_f.seek(current_pos)

        # 3. Transfer Loop
        last_time = time.time()
        bytes_since_last_update = 0
        speed = 0

        print_progress_bar(current_pos, src_size, prefix='Syncing:', suffix='0 MB/s')

        while current_pos < src_size:
            chunk = src_f.read(CHUNK_SIZE)
            if not chunk:
                break
            
            dest_f.write(chunk)
            current_pos += len(chunk)
            bytes_since_last_update += len(chunk)

            # Update speed calculation every 1 second
            now = time.time()
            elapsed = now - last_time
            if elapsed >= 1.0:
                speed = (bytes_since_last_update / (1024 * 1024)) / elapsed
                last_time = now
                bytes_since_last_update = 0
            
            print_progress_bar(
                current_pos, 
                src_size, 
                prefix='Syncing:', 
                suffix=f'{speed:.2f} MB/s'
            )

if __name__ == "__main__":
    parser = OptionParser(usage="usage: %prog [source] [destination]", version='1.1')
    (options, args) = parser.parse_args()

    if len(args) == 2:
        src_path, dest_path = args
        if os.path.isfile(src_path) and os.path.isfile(dest_path):
            main(src_path, dest_path)
        else:
            print("Error: One or both paths are invalid or do not exist.")
    else:
        parser.print_help()