import re
import unicodedata
from nameparser import HumanName

EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
                      flags=re.IGNORECASE)


def strip_prefix(prefix, string, flags=0):
    return re.sub(f'^{prefix}', '', string, flags=flags)


def strip_suffix(suffix, string, flags=0):
    return re.sub(f'{suffix}$', '', string, flags=flags)


def strip_seq(seq, string, flags=0):
    return strip_prefix(seq, strip_suffix(seq, string, flags=flags),
                        flags=flags)


def _strip_seqs(seqs, string, flags=0):
    for seq in seqs:
        string = strip_seq(seq, string, flags)
    return string


def strip_seqs(seqs, string, flags=0, recursive=False):
    if not recursive:
        return _strip_seqs(seqs, string, flags)
    new_string = string
    prev_string = string
    while True:
        new_string = _strip_seqs(seqs, new_string, flags)
        if new_string == prev_string:
            break
        prev_string = new_string
    return new_string


def cleanup_raw_name(raw_name):
    return strip_prefix('and', raw_name.strip(' .,')).strip(' .,')


def is_h_tag(tag):
    return re.match('^h[1-6]$', tag.name)


def remove_parents(tags):
    final_tags = []
    for tag1 in tags:
        is_parent = False
        for tag2 in tags:
            if tag1 == tag2:
                continue
            tag1_children = list(tag1.children)
            if tag2 in tag1_children:
                is_parent = True
        if not is_parent:
            final_tags.append(tag1)
    return final_tags


def split_name(name):
    return [part for part in re.split('[ ,]', name.strip()) if
            len(part) > 1]


def name_in_text(name, text):
    name_split = split_name(name)
    if len(name_split) == 3:
        # only care about middle initial
        name_split[1] = name_split[1][0]
    return all([part in text for part in name_split])


def email_matches_name(email, name):
    _email = strip_prefix('mailto:', email)

    normalized_name = unicodedata.normalize('NFD', name.lower()).encode('ascii',
                                                                        'ignore').decode()
    split = split_name(normalized_name)
    return any([part in _email.split('@')[0] for part in split])


def names_match(name1: HumanName, name2: HumanName):
    if not isinstance(name1, HumanName):
        name1 = HumanName(name1)
    if not isinstance(name2, HumanName):
        name2 = HumanName(name2)
    return name1.last.lower() == name2.last.lower() and name1.first.lower() == name2.first.lower()
