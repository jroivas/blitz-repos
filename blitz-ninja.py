#!/usr/bin/env python

import os
import sys
import utils

c_compile = {
    ".c":
            {
            "input": ".c",
            "output": ".o",
            "depfile": ".d",
            "deps": "gcc",
            "command": "gcc -c -o $out $in $cflags -MMD -MT $out -MF $depfile $includes"
        },
    ".cpp":
        {
            "input": ".cpp",
            "output": ".o",
            "depfile": ".d",
            "deps": "gcc",
            "command": "g++ -c -o $out $in $cxxflags -MMD -MT $out -MF $depfile $includes"
        }
    }

c_link = {
    "objects": {
        "input": "objects",
        "command": "g++ -o $out $in $libs"
    }
}

c_skip = ['.h']

def parse_compile(data):
    res = c_compile.copy()
    compiles = data.get('compile', None)
    if compiles is None:
        return res

    for c in compiles:
        if 'input' not in c:
            continue
        inp = c['input']
        res[inp] = c

    return res

def parse_link(data):
    res = c_link.copy()
    links = data.get('link', None)
    if links is None:
        return res

    for c in links:
        if 'name' not in c:
            continue
        inp = c['name']
        c['input'] = inp
        res[inp] = c

    return res

def parse_target(data):
    return data.get('target', [])

def parse_files(data):
    return data.get('sources', [])

def parse_skip(data):
    return c_skip + data.get('skip', [])

def parse_dir(data):
    return os.path.dirname(os.path.abspath(data))

def parse_variables(data):
    res = []
    for item in data:
        if item == 'compile':
            continue
        if item == 'link':
            continue
        if item == 'skip':
            continue
        if item == 'sources':
            continue
        if item == 'target':
            continue
        res.append('%s = %s' % (item, data[item]))

    return res

def alphastring(s):
    """
    >>> alphastring('abc')
    'abc'
    >>> alphastring('.h')
    '_h'
    >>> alphastring('&/')
    ''
    >>> alphastring('test.txt')
    'test_txt'
    """
    return ''.join([x for x in s if x.isalnum() or x == '.' or x == '_']).replace('.', '_')

def format_rule_name(item, prefix):
    return prefix + alphastring(item)

def gen_rules(items, prefix):
    res = ''
    for item in items:
        if 'command' not in items[item]:
            continue
        if 'input' not in items[item]:
            continue
        name = format_rule_name(items[item]['input'], prefix)
        items[item]['rule'] = name
        res += 'rule %s\n' % (name)
        res += '    command = %s\n' % (items[item]['command'])

        res += '\n'


    return res

def gen_builds(rules, files, folder, skips):
    res = ''
    for f in files:
        ok = True
        for s in skips:
            if f.endswith(s):
                ok = False
                break
        if not ok:
            continue

        base, ext = os.path.splitext(f)
        base = os.path.basename(base)

        if ext not in rules:
            raise ValueError('No rule to build: %s' % (f))

        res += 'build %s%s: %s %s\n' % (
            base,
            rules[ext]['output'],
            rules[ext]['rule'],
            os.path.join(folder, f)
            )
        if 'deps' in rules[ext]:
            res += '    deps  = %s\n' % (rules[ext]['deps'])
        if 'depfile' in rules[ext]:
            res += '    depfile = %s%s\n' % (
                base,
                rules[ext]['depfile']
                )
        res += '\n'

    return res

def gen_targets(links, targets):
    res = ''
    for t in targets:
        if 'name' not in t:
            raise ValueError('Invalid target: %s, missing name' % (t))
        if 'input' not in t:
            raise ValueError('Invalid target: %s, missing input' % (t))
        if 'link' not in t:
            t['link'] = 'objects'
            #raise ValueError('Invalid target: %s, missing link' % (t))

        items = ' '.join(t['input'])
        linkrule = 'link' + t['link']
        res += 'build %s: %s %s\n' % (t['name'], linkrule, items)

    return res

def gen_ninja(data):
    folder = parse_dir(buildfile)
    skips = parse_skip(data)
    rules = parse_compile(data)
    links = parse_link(data)

    ninja = ''
    ninja += 'includes = -I%s\n' % (folder)
    ninja += '\n'.join(parse_variables(data))
    ninja += '\n\n'

    ninja += gen_rules(rules, 'compile')
    ninja += gen_rules(links, 'link')

    ninja += gen_builds(rules, parse_files(data), folder, skips)

    ninja += gen_targets(links, parse_target(data))

    return ninja

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print ('Usage: %s build.json' % (sys.argv[0]))
        sys.exit(1)


    buildfile = sys.argv[1]
    p = utils.parse(buildfile)

    parse_variables(p)

    print gen_ninja(p)
