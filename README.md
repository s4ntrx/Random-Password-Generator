# Random Password Generator

A desktop password generator built with Python and Tkinter. No third-party dependencies.

## Features

- Cryptographically secure randomness via `secrets` (not `random`)
- Length from 4 to 128 characters
- Lowercase, uppercase, digits, symbols, and an option to exclude look-alike characters
- Guarantees at least one character from every enabled set
- Live strength meter based on an entropy estimate
- Copy to clipboard, auto-cleared after 30 seconds
- Show/hide toggle

## Run

Requires Python 3.9+ with Tkinter (bundled on Windows and macOS; on Debian/Ubuntu: `sudo apt install python3-tk`).

```bash
git clone https://github.com/s4ntrx/Random-Password-Generator.git
cd Random-Password-Generator
python -m passgen
```

## Use as a library

```python
from passgen import Options, generate_password

print(generate_password(Options(length=24, symbols=False)))
```

## Test

```bash
python -m unittest discover -s tests -v
```

## Why `secrets` and not `random`

`random` uses a Mersenne Twister, which is predictable once enough output is observed. `secrets` draws from the operating system's cryptographic random source.

## Notes

The entropy figure is an upper-bound estimate (length x log2 of pool size). Forcing one character per set slightly reduces true entropy; at 12+ characters the difference is negligible.
