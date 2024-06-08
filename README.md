# KRDict Converter

This is a simple script to convert [KRDict](https://krdict.korean.go.kr) from the Korean Language Institute into a simple term-definition JSON dictionary for all available languages.

```
usage: krdict_conv.py [-h] [--language {es,ar,id,en,ru,fr,ja,zh,th,mn,vi}] [--output OUTPUT] [--input INPUT] [--cache CACHE]

options:
  -h, --help            show this help message and exit
  --language {es,ar,id,en,ru,fr,ja,zh,th,mn,vi}, -l {es,ar,id,en,ru,fr,ja,zh,th,mn,vi}
                        Dictionary target language (default: en)
  --output OUTPUT, -o OUTPUT
                        Output file name (default: krdict_[LANGUAGE].zip)
  --input INPUT, -i INPUT
                        Input url/file name (default: KRDict download URL)
  --cache CACHE, -c CACHE
                        Cache file name, if input is a URL (default: None)
```

Note that download speeds from the KRDict website can be very slow. If you want to convert for multiple languages, make sure to use the cache option to avoid downloading the same file multiple times.
