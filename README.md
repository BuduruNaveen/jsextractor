# JS Extractor

A Python tool to extract all JavaScript URLs from web pages. Supports single URLs or bulk extraction from a file, with concurrent fetching and JSON output.

## Features

- Extracts JS from `<script src>`, `import`, `require()`, CSS `url()`, and inline scripts
- Separates same-origin vs external JS files
- Multi-threaded concurrent processing
- JSON output mode for piping into other tools
- Handles redirects, relative URLs, and various patterns

## Usage

Clone the repository : git clone https://github.com/BuduruNaveen/jsextractor.git

```bash
# Single URL
python js_extractor.py https://example.com

# Bulk from file (one URL per line)
python js_extractor.py urls.txt

# JSON output
python js_extractor.py https://example.com --json
```

## Requirements

- Python 3.6+
- `requests` (`pip install requests`)

Note : This tool is Made for educational purposes only.
I am not responsible to any kind of illigal activities by this tool 
About the Author : Nothing to say!
