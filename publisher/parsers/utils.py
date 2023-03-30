import re


def strip_prefix(prefix, string, flags=0):
    return re.sub(f'^{prefix}', '', string, flags=flags)


def strip_suffix(suffix, string, flags=0):
    return re.sub(f'{suffix}$', '', string, flags=flags)


def strip_seq(seq, string, flags=0):
    return strip_prefix(seq, strip_suffix(seq, string, flags=flags), flags=flags)


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
