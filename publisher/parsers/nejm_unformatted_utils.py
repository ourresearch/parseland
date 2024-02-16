import copy
import re
from nameparser import HumanName

from publisher.parsers.utils import strip_seqs


def parse_affs_by_unformatted_text(authors, affs_text):
    affs = re.findall(r'(?:;|\)|and|—)?(.*?(?:\(.*?\)|;|, and the |\Z))',
                      affs_text)
    affs = [aff for aff in affs if not aff.startswith('—') and len(aff) > 3]
    nested_affs = [aff for aff in affs if not re.search(r'\(.*?\)', aff)]
    if not affs:
        for author in authors:
            author['affiliations'].append(affs_text)
        return authors
    aff_initials_dict = affs_initials_dict(affs)
    if len(aff_initials_dict) == 1:
        for author in authors:
            author['affiliations'].append(tuple(aff_initials_dict.keys())[0])
        return authors
    aff_initials_dict = modify_nested_affs(aff_initials_dict, nested_affs)
    for author in authors:
        name = author['name']
        split = name.split(', ')
        if len(split) == 2:
            name = ' '.join(split[::-1])
        name = HumanName(name)
        patterns = _make_initials_patterns(name)
        for aff, initials in aff_initials_dict.items():
            for pattern in patterns:
                if pattern.search(initials):
                    author['affiliations'].append(aff)
    return authors


def affs_initials_dict(affs):
    d = {}
    for aff in affs:
        initials_matches = re.findall(r'\([\- .,A-Za-z]+\)', aff)
        initials = initials_matches[0] if initials_matches else None
        cleaned = clean_aff(aff)
        d[cleaned] = initials
    return d


def modify_nested_affs(affs_initials_dict, nested_affs):
    if not nested_affs:
        return affs_initials_dict
    affs_initials = [list(item) for item in affs_initials_dict.items()]
    last_nested_index = 0
    nested_count = 0
    for i, aff in enumerate(affs_initials):
        if not affs_initials[i][1]:
            for j in range(last_nested_index, i):
                affs_initials[j][
                    0] = f'{affs_initials[j][0]}, {nested_affs[nested_count].strip(" ;,").split("—")[0].strip(" ;,")}'
            last_nested_index = i
            nested_count += 1
    return dict(
        [(clean_aff(item[0]), item[1]) for item in affs_initials if item[1]])


def clean_aff(aff):
    cleaned = re.sub(r'\([\- .,A-Za-z]+\)', '', aff).strip(';, ')
    cleaned = strip_seqs(['From', ' the', ' and', 'the ', 'and '], cleaned,
                         recursive=True).strip(';, ')
    return cleaned


def _make_initials_patterns(name):
    initial_matches = {re.sub(r'\.\W*\.+', '.', name.initials().replace(' ', '')),
                       f'{name.first[0]}. *{name.last}',
                       '.'.join(re.findall(r'([A-Z])', name.full_name)) + '.'}
    if name.middle:
        initial_matches.add(f'{name.first[0]}. *{name.middle[0]}. {name.last}',)
    parts = [name.first, name.middle, name.last]
    parts = [part for part in parts if part]
    for i, part in enumerate(parts):
        new_parts = parts.copy()
        split = part.split('-')
        if len(split) > 1:
            for j, _part in enumerate(split):
                if j == 0:
                    new_parts[i] = _part
                else:
                    new_parts.insert(i + j, '-' + _part)
            initials = '.'.join([name[:2] if name.startswith('-') else name[0] for name in new_parts])
            initials += '.'
            initial_matches.add(initials)
    patterns = []
    for match in initial_matches:
        safe_match = match.replace(".", "\.")
        patterns.append(re.compile(f'[(,] *{safe_match}[),]'))
    return patterns

