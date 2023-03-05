from dataclasses import asdict, is_dataclass


def alter_is_corresponding(message):
    """If all is_corresponding are False, change them to None."""
    authors = []
    if "authors" in message:
        for author in message["authors"]:
            if is_dataclass(author):
                authors.append(asdict(author))
            else:
                authors.append(author)
        is_corresponding_list = [
            author["is_corresponding"]
            for author in authors
            if "is_corresponding" in author
        ]
        message["authors"] = authors
        if True not in is_corresponding_list:
            for i, val in enumerate(message["authors"]):
                message["authors"][i]["is_corresponding"] = None
    else:
        for author in message:
            if is_dataclass(author):
                authors.append(asdict(author))
            else:
                authors.append(author)
        is_corresponding_list = [
            author["is_corresponding"]
            for author in authors
            if "is_corresponding" in author
        ]
        message = authors
        if True not in is_corresponding_list:
            for i, val in enumerate(message):
                message[i]["is_corresponding"] = None

    return message