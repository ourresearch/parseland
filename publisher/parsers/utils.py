import re
import unicodedata

EMAIL_RE = re.compile(r'\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b',
                      flags=re.IGNORECASE)


def strip_prefix(prefix, string, flags=0):
    return re.sub(f'^{prefix}', '', string, flags=flags)


def strip_suffix(suffix, string, flags=0):
    return re.sub(f'{suffix}$', '', string, flags=flags)


def strip_seq(seq, string, flags=0):
    return strip_prefix(seq, strip_suffix(seq, string, flags=flags),
                        flags=flags)


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


def email_matches_name(email, name):
    _email = strip_prefix('mailto:', email)

    normalized_name = unicodedata.normalize('NFD', name.lower()).encode('ascii',
                                                                        'ignore').decode()
    split = [part for part in re.split('[ ,]', normalized_name.strip()) if
             len(part) > 1]
    return any([part in _email.split('@')[0] for part in split])
