# Sliding Window Compressor

This program compresses the input on a byte by byte basis.

The compressed data is array of bytes, pointers are represented with multiple bytes, led by escape character b"\xCC". 

> If encountered byte value b"\xCC" during compression and it's been outputted without compression, put a b"\xCC" in front of it to distinguish it from pointer identifier.

## How to run

### In terminal
```bash
# [C]ompress file and output to given file
python compressor.py -c path/to/file -o output.txt

# [D]ecompress file and output to given file
python compressor.py -d path/to/file -o output.txt
```

### In other Python files

```python
from Compressor.compressor import Compressor

c = Compressor()
c.compress_to_file(in_file, out_file)
c.decompress(out_file, out_file_decompressed)
```

## TODO

2. Fix pointer format
1. Add CLI utility
3. Remove hard-coded codes
4. Allow parameters