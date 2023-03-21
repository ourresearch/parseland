from dataclasses import asdict, is_dataclass


def has_corresponding(message):
    authors = message['authors']
    return bool([author for author in authors if author['is_corresponding']])


def has_affiliations(message):
    authors = message['authors']
    return bool([author for author in authors if author['affiliations']])


def strip_message_strs(message):
    if isinstance(message, list):
        for i in range(len(message)):
            message[i] = strip_message_strs(message[i])
    if isinstance(message, dict):
        for k in message.keys():
            message[k] = strip_message_strs(message[k])
    if isinstance(message, str):
        return message.strip('\n ')
    return message


def prep_message(message, parser):
    if isinstance(message, list):
        message = {'authors': message, 'abstract': None}

    message['authors'] = [asdict(author) if is_dataclass(author) else author for
                          author in message['authors']]

    if not message['authors']:
        message = parser.no_authors_output()

    if not has_corresponding(message):
        message['authors'] = parser.fallback_mark_corresponding_authors(
            message['authors'])

    if not message['abstract']:
        message['abstract'] = parser.fallback_parse_abstract()

    if 'abstract' in message and message['abstract']:
        message['abstract'] = message['abstract'].strip(' \n')

    message = alter_is_corresponding(message)
    message = sanitize_affiliations(message)
    message = strip_message_strs(message)
    return message


def alter_is_corresponding(message):
    """If all is_corresponding are False, change them to None."""
    authors = message['authors']

    is_corresponding_list = [
        author["is_corresponding"]
        for author in authors
        if "is_corresponding" in author
    ]
    if True not in is_corresponding_list:
        for i, val in enumerate(authors):
            authors[i]["is_corresponding"] = None

    # we have at least one corresponding author, but the non-corresponding authors have is_corresponding = None (need to be set to False)
    elif None in is_corresponding_list:
        for i, val in enumerate(authors):
            if val['is_corresponding'] is None:
                authors[i]["is_corresponding"] = False
    if 'authors' in message:
        message['authors'] = authors
    else:
        message = authors

    return message


def sanitize_affiliations(message):
    authors = message['authors']

    for author in authors:
        author['affiliations'] = [aff for aff in author['affiliations'] if
                                  'corresponding' not in aff.lower()]

    if 'authors' in message:
        message['authors'] = authors
    else:
        message = authors

    return message


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


def merge_messages(publisher_msg, generic_msg):
    publisher_has_cor = has_corresponding(publisher_msg)
    generic_has_cor = has_corresponding(generic_msg)

    publisher_has_aff = has_affiliations(publisher_msg)
    generic_has_aff = has_affiliations(generic_msg)

    publisher_has_abs = bool(publisher_msg.get('abstract'))
    generic_has_abs = bool(publisher_msg.get('abstract'))

    if len(generic_msg['authors']) >= len(publisher_msg['authors']) and (
            (not publisher_has_cor and generic_has_cor) or (
            not publisher_has_aff and generic_has_aff)):
        publisher_msg['authors'] = generic_msg['authors']

    if not publisher_msg['authors'] and generic_msg['authors']:
        publisher_msg['authors'] = generic_msg['authors']

    if not publisher_has_abs and generic_has_abs:
        publisher_msg['abstract'] = generic_msg['abstract']

    return publisher_msg


def check_bad_landing_page(soup):
    s = str(soup)
    if not soup.title:
        return True
    return any(['Redirecting' in soup.title.text,
                ])
