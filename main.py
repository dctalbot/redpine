import re
import os
import json

import ntpath

# nodes: [
# 	{data: {id: 'a'}},
# 	{data: {id: 'b'}}
# ],
# edges: [
# 	{ data: { id: 'ab', source: 'a', target: 'b' } }
# ]
BIG_BLOB = {}
BIG_LIST = []
SRC_TO_TGT = {}


def strip_emptylines_from(text):
    return os.linesep.join([s for s in text.splitlines() if s])


def get_first_word_from(str):
    word = str.split(maxsplit=1)[0]
    if word[-1] == ';':
        word = word[:-1]
    return word


def strip_ext(path):
    return os.path.splitext(path)[0]

def re_get_comments():
    return re.compile(r'\/\*[\s\S]*?\*\/|([^\\:]|^)\/\/.*$', re.MULTILINE | re.IGNORECASE)


def re_not_beginning_with(str):
    return re.compile('^(?!' + str + ').*', re.MULTILINE | re.IGNORECASE)


def get_exports(txt):
    result = set()
    txt = re_not_beginning_with('export ').sub('', txt)
    txt = re_get_comments().sub('', txt)

    # Exporting individual features
    for keyword in ['let', 'const', 'var']:
        matches = re_exclusively_between(
            'export ' + keyword + ' ', '[\n;]').findall(txt)
        for line in matches:
            if '{' in line or '}' in line:
                continue
            for expression in line.split(','):
                name = get_first_word_from(expression)
                result.add(name)

    # export function functionName(){...}
    matches = re_exclusively_between(
        'export function ', '\(').findall(txt)
    for match in matches:
        result.add(match)

    # export class ClassName {...}
    matches = re_exclusively_between(
        'export class ', ' \{').findall(txt)
    for match in matches:
        result.add(match)

    # export default App
    # default => single match
    match = re.findall(r'export default [A-Z]\w+', txt)[0].split()[-1]
    result.add(match)


def re_exclusively_between(start, end):
    """
    e.g.
    imports_re = re.compile(r'(?<=import ).*[\'\"\)](?=[;\n])')
    """
    return re.compile('(?<=' + start + ').*(?=' + end + ')')


def get_imports(text, default_name):
    result = list()
    text = re_not_beginning_with('import ').sub('', text)
    text = re_get_comments().sub('', text)
    text = strip_emptylines_from(text)
    text = text.replace(';', '')
    text = text.replace('import ', '')
    for line in text.splitlines():
        node = dict()
        splat = line.split(' from ')
        node['names'] = re.compile(r'\w+').findall(splat[0])
        node['source'] = re_exclusively_between(
            '[\'\"]', '[\'\"]').findall(splat[1])[0]
        result.append(node)

    return result


for root, subdirs, files in os.walk('../../goalert/goalert/web/src/app/'):
# for root, subdirs, files in os.walk('./input/todos'):
    for filename in files:
        ext = filename[-3:]
        if ext not in ['.js', '.jsx']:
            continue

        # create a node
        # {data: {id: 'a'}}
        abs_path = os.path.abspath(os.path.join(root, filename))

        # node = {'data': {'id': filename, 'label': filename}}
        # BIG_BLOB['nodes'].append(node)
        # BIG_LIST.append(node)
        with open(abs_path, 'r') as js_file:
            try:
                file_text = js_file.read()
                imports = get_imports(file_text, filename)
                for imp in imports:
                    src = imp['source']
                    # if src == 'react':
                    #     continue
                    # if src[0] not in ['.', '/']:
                    #     continue
                    # if relative import, resolve path
                    if src[0] in ['.', '/']:
                        src = os.path.abspath(os.path.join(root, src))
                    target = strip_ext(abs_path)

                    # print(abs_path)

                    # TODO get labels from imp['names']

                    if src in SRC_TO_TGT:
                        SRC_TO_TGT[src].append(target)
                    else:
                        SRC_TO_TGT[src] = [target]
            except:
                pass

                # node = {'data': {'source': src, 'label': label}}
                # BIG_LIST.append(node)

            # print(SRC_TO_TGT)
            # quit()
            # print(os.path.abspath(f))

# print(SRC_TO_TGT)

RESULT = []
unique_targets = []
for src in SRC_TO_TGT:
    for tgt in SRC_TO_TGT[src]:
        if tgt not in unique_targets:
            unique_targets.append(tgt)

for src in SRC_TO_TGT:
    RESULT.append(
        {"data": {"id": src, "label": os.path.basename(src)}})

for tgt in unique_targets:
    RESULT.append(
        {"data": {"id": tgt, "label": os.path.basename(tgt)}})

for src in SRC_TO_TGT:
    for tgt in SRC_TO_TGT[src]:
        RESULT.append({
            "data": {"source": src, "target": tgt}
        })

f = open("./output.json", "w")
json.dump(RESULT, f)
f.close()
