# Sliding Window Compressor

This program compresses the input on a byte by byte basis.

The compressed data is array of bytes, pointers are represented with multiple bytes, led by escape character b"\xCC". 

> If encountered byte value b"\xCC" during compression and it's been outputted without compression, put a b"\xCC" in front of it to distinguish it from pointer identifier.

## How to run

### In terminal
```bash
# Compress file and output to given file
python cli.py zip path/to/file output.file

# Decompress file and output to given file
python cli.py unzip path/to/file output.file
```

### In other Python files

```python
from Compressor.compressor import Compressor

c = Compressor()
c.compress_to_file(in_file, out_file)
c.decompress_to_file(in_file, out_file)
```

## TODO
3. Remove hard-coded length and Allow parameters