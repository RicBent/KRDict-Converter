# KRDict Converter

### Generated dictionary files can be downloaded from the [releases](./releases/latest) page.

This is a simple script to convert [KRDict](https://krdict.korean.go.kr) from the Korean Language Institute into a simple term-definition JSON dictionary for all available languages.

```
usage: krdict_conv.py [-h] [--language LANGUAGE [LANGUAGE ...]] [--output OUTPUT] [--input INPUT] [--bilingual] [--cache CACHE] [--noprogress]

options:
  -h, --help            show this help message and exit
  --language LANGUAGE [LANGUAGE ...], -l LANGUAGE [LANGUAGE ...]
                        Dictionary target language (default: en, available: all, ko, es, ar, id, en, ru, fr, ja, zh, th, mn, vi)
  --output OUTPUT, -o OUTPUT
                        Output file name (default: krdict_%LANGUAGE%.zip)
  --input INPUT, -i INPUT
                        Input url/file name (default: KRDict download URL)
  --bilingual, -b       Add Korean definitions to other languages
  --cache CACHE, -c CACHE
                        Cache file name, if input is a URL (default: None)
  --noprogress, -np     Disable progress bars
```

Note that download speeds from the KRDict website can be very slow. You can use the `--cache`/`-c` option to save the downloaded file for later use.
