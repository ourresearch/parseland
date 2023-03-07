from dataclasses import asdict, is_dataclass


def sanitize_message(message):
    message = alter_is_corresponding(message)
    message = sanitize_affiliations(message)
    return message


def alter_is_corresponding(message):
    """If all is_corresponding are False, change them to None."""
    authors = message['authors'] if 'authors' in message else message
    authors = [asdict(author) if is_dataclass(author) else author for author in authors]

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
    authors = message['authors'] if 'authors' in message else message
    authors = [asdict(author) if is_dataclass(author) else author for author in authors]

    for author in authors:
        author['affiliations'] = [aff for aff in author['affiliations'] if 'corresponding' not in aff.lower()]

    if 'authors' in message:
        message['authors'] = authors
    else:
        message = authors

    return message
