from bs4 import NavigableString
from nameparser import HumanName

from publisher.elements import Affiliation, Author
from publisher.parsers.parser import PublisherParser


class Dove(PublisherParser):
    parser_name = "dove_press"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('dovepress.com')

    def authors_found(self):
        return bool(self.soup.select('div.article-inner_html > p'))

    def parse(self):
        tags = self.soup.select('div.article-inner_html > p')
        if len(tags) > 1:
            tags = [tag for l in tags for tag in l]
            children = tags
        else:
            children = list(tags[0].children)
        authors = []
        parsed_affs = False
        parse_affs = False
        parse_abs = False
        abstract = ''
        corresponding_name = None
        affs = []
        for i, tag in enumerate(children):
            if tag.name == 'br' and not parse_affs and not parsed_affs:
                parse_affs = True
            elif tag.name == 'br' and parse_affs and affs:
                parsed_affs = True
                parse_affs = False
            elif parse_affs:
                aff_id = None
                org = None
                if tag.name == 'sup':
                    aff_id = tag.text.strip(' ,')
                    org = children[i + 1].text.strip()
                elif tag.previous_sibling.name != 'sup':
                    org = tag.text
                if org:
                    affs.append(
                        Affiliation(aff_id=aff_id, organization=org))
            elif not parse_affs and not parsed_affs and not parse_abs and isinstance(tag, NavigableString):
                name = tag.text.strip(' ,')
                if not name:
                    continue
                aff_ids = []
                _tag = tag
                sups = []
                while _tag.next_sibling and _tag.next_sibling.name == 'sup':
                    sups.append(_tag.next_sibling)
                    _tag = _tag.next_sibling
                if sups:
                    aff_ids = [aff_id.strip(' ,') for sup in sups for aff_id in sup.text.split(',')]
                authors.append(Author(name=name,
                                      aff_ids=aff_ids))
            elif tag.name == 'strong':
                parse_abs = True
            else:
                if 'correspondence' in tag.text.lower():
                    corresponding_name = tag.text.split(':')[-1].strip()

            if parse_abs:
                abstract += tag.text.strip() + '\n'
        if corresponding_name:
            for author in authors:
                name = HumanName(corresponding_name)
                name2 = HumanName(author.name)
                if name.first == name2.first and name.last == name2.last:
                    author.is_corresponding = True
        authors = self.merge_authors_affiliations(authors=authors, affiliations=affs)
        return {'authors': authors,
                'abstract': abstract}
