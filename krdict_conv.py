#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import json
import zipfile
import requests
import argparse
import io


LANG_MAP = {
    '스페인어': 'es',
    '아랍어': 'ar',
    '인도네시아어': 'id',
    '영어': 'en',
    '러시아어': 'ru',
    '프랑스어': 'fr',
    '일본어': 'ja',
    '중국어': 'zh',
    '타이어': 'th',
    '몽골어': 'mn',
    '베트남어': 'vi',
}

XML_ZIP_URL = 'https://krdict.korean.go.kr/dicBatchDownload?seq=87'

parser = argparse.ArgumentParser()

available_langs = ['ko'] + list(LANG_MAP.values())
available_langs_txt = ', '.join(available_langs)

parser.add_argument('--language', '-l', default=['en'], help=f'Dictionary target language (default: en, available: all, {available_langs_txt})', nargs='+')
parser.add_argument('--output', '-o', default='krdict_%LANGUAGE%.zip', help='Output file name (default: krdict_%%LANGUAGE%%.zip)')
parser.add_argument('--input', '-i', default=XML_ZIP_URL, help='Input url/file name (default: KRDict download URL)')
parser.add_argument('--bilingual', '-b', dest='bilingual', action='store_true', help='Add Korean definitions to other languages')
parser.add_argument('--cache', '-c', default=None, help='Cache file name, if input is a URL (default: None)')
parser.add_argument('--noprogress', '-np', dest='no_progress', action='store_true', help='Disable progress bars')

args = parser.parse_args()

if args.output is None:
    args.output = f'krdict_%LANGUAGE%.zip'

langs = args.language
if langs == ['all']:
    langs = available_langs

for lang in langs:
    if not lang in available_langs:
        parser.error(f'Unknown language: {lang}')

if len(langs) > 1 and not '%LANGUAGE%' in args.output:
    parser.error('Multiple languages selected, but output file name does not contain %LANGUAGE%')

print_progress_max_len = None

def print_progress(progress, text=None, done=False):
    if args.no_progress:
        return

    global print_progress_max_len

    out = f'\r{progress * 100:4.0f}% '

    width = 40
    progress_width = int(progress * width)
    head_char = '>' if progress < 1 else '='
    out += '[' + '=' * progress_width + head_char + ' ' * (width - progress_width) + ']'

    if text:
        out += f' {text}'

    if not print_progress_max_len is None and len(out) < print_progress_max_len:
        out = out + ' ' * (print_progress_max_len - len(out))
    print_progress_max_len = len(out)

    print(out, end='', flush=True)

    if done:
        print()
        print_progress_max_len = None



if args.input.startswith('http'):
    print(f'Downloading {args.input}...')

    resp = requests.get(args.input, stream=True)
    total = int(resp.headers.get('content-length', 0))
    total_kb = total / 1024

    data = b''

    for new_data in resp.iter_content(chunk_size=1024):
        data += new_data

        dl_kb = len(data) / 1024

        print_progress(len(data) / total, f'{dl_kb:.0f} / {total_kb:.0f} KB')

    print_progress(1, f'{total_kb:.0f} / {total_kb:.0f} KB', done=True)

    if args.cache:
        with open(args.cache, 'wb') as f:
            f.write(data)

    input_zip = zipfile.ZipFile(io.BytesIO(data))

else:
    input_zip = zipfile.ZipFile(args.input)



fnames = input_zip.namelist()

fnames_sorted = [
    (fname, int(fname.split('_')[0]))
    for fname in fnames
]
fnames_sorted.sort(key=lambda x: x[1])


def node_get_feat(node, ignore=False):
    feat = {}
    for sub in node:
        if sub.tag == 'feat':
            feat[sub.attrib['att']] = sub.attrib.get('val') # Some have "None" for some reason
        else:
            if type(ignore) == list:
                if sub.tag in ignore:
                    continue
            if ignore is False:
                raise Exception(f'Unknown tag: {sub.tag}')
            elif ignore is True:
                pass

    return feat


lang_data = {}
for lang in langs:
    lang_data[lang] = []

fname_count = len(fnames_sorted)


print('Converting...')

for i, (fname, _) in enumerate(fnames_sorted):
    print_progress(i / fname_count, fname)

    parts = fname.split('.')[0].split('_')
    index = int(parts[0])
    assert index == i + 1

    tree = ET.parse(input_zip.open(fname))
    root = tree.getroot()

    for lexicon in root:
        if lexicon.tag != 'Lexicon':
            continue

        for entry in lexicon:
            if entry.tag != 'LexicalEntry':
                continue

            assert entry.attrib['att'] == 'id'
            id = int(entry.attrib['val'])

            feat = {}
            lemma = {}          # writtenForm, variant (optional)
            word_form = []      # ?
            senses = []

            for sub in entry:
                if sub.tag == 'feat':
                    feat[sub.attrib['att']] = sub.attrib['val']

                elif sub.tag == 'Lemma':
                    lemma.update(node_get_feat(sub))

                elif sub.tag == 'WordForm':
                    word_form.append(node_get_feat(sub, ['FormRepresentation']))

                elif sub.tag == 'RelatedForm':
                    pass

                elif sub.tag == 'Sense':
                    assert sub.attrib['att'] == 'id'
                    sense = {
                        'id': int(sub.attrib['val']),
                        'syntacticPattern': [],
                        'equivalents': {},
                    }
                    for sub2 in sub:
                        if sub2.tag == 'feat':
                            att = sub2.attrib['att']
                            val = sub2.attrib['val']
                            if att in sense:
                                sense[att].append(val)
                            else:
                                sense[att] = val
                        elif sub2.tag == 'Equivalent':
                            feat = node_get_feat(sub2)
                            lang = feat['language']
                            if lang not in LANG_MAP:
                                raise Exception(f'Unknown language: {lang}')
                            lang = LANG_MAP[lang]
                            sense['equivalents'][lang] = {
                                'lemma': feat['lemma'],
                                'definition': feat['definition'],
                            }
                        elif sub2.tag == 'Multimedia':
                            pass
                        elif sub2.tag == 'SenseRelation':
                            pass
                        elif sub2.tag == 'SenseExample':
                            pass
                        else:
                            raise Exception(f'Unknown tag: {sub2.tag}')
                    senses.append(sense)

                else:
                    raise Exception(f'Unknown tag: {sub.tag}')

            written_form = lemma['writtenForm']

            if written_form.startswith('-'):
                written_form = written_form[1:]
            if written_form.endswith('-'):
                written_form = written_form[:-1]

            senses.sort(key=lambda x: x['id'])

            for s in senses:
                eq = s['equivalents']
                definition = s['definition']

                for lang in langs:
                    if lang == 'ko':
                        lang_data[lang].append({
                            't': written_form,
                            'd': definition,
                        })
                        continue

                    try:
                        lang_eq = eq[lang]
                    except KeyError:
                        continue

                    parts = [
                        lang_eq['lemma'],
                        lang_eq["definition"],
                    ]

                    if args.bilingual:
                        parts.append(definition)
                    
                    lang_data[lang].append({
                        't': written_form,
                        'd': '\n'.join(parts),
                    })

print_progress(1, 'All done.', done=True)

for lang, lang_data in lang_data.items():
    fname = args.output.replace('%LANGUAGE%', lang)
    z = zipfile.ZipFile(fname, 'w')
    z.writestr('data.json', json.dumps(lang_data, ensure_ascii=False))
    z.close()
    print(f'Output for {lang} written to: {fname}')
