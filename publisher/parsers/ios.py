from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import split_name


class IOSPress(PublisherParser):
    parser_name = "ios_press"

    def is_publisher_specific_parser(self):
        if publisher_name_tag := self.soup.select_one('meta[name=citation_publisher]'):
            return 'ios press' in publisher_name_tag['content'].lower()
        return False

    def authors_found(self):
        return bool(self.soup.select('p.metadata-entry a[href*=author]'))

    def parse_affiliations(self):
        affs = {}
        aff_tags = self.soup.select('p.metadata-entry a[id*=aff]')
        if len(aff_tags) == 1:
            return aff_tags[0].next_element.next_element.text.strip()
        for aff_tag in aff_tags:
            sup = None
            elem = aff_tag
            aff = None
            while not sup:
                elem = elem.next_element
                if elem.text.strip().isalpha() and len(elem.text.strip()) == 1:
                    sup = elem.text.strip()
            while not aff:
                elem = elem.next_element
                if elem.next_element.name == 'a' or not elem.next_element:
                    aff = elem.text.strip('\r\n |')
            if 'correspondence' not in aff:
                affs[sup] = aff
        return affs

    def parse_authors(self):
        affs = self.parse_affiliations()
        author_tags = self.soup.select('p.metadata-entry a[href*=author]')
        authors = []
        for author_tag in author_tags:
            name = author_tag.next_element.text.strip()
            sups_text = author_tag.next_element.next_element.text
            sups = [sup.strip() for sup in sups_text.split(';') if sup.isalpha()]
            author_affs = []
            if isinstance(affs, str):
                author_affs = [affs]
            for sup in sups:
                if sup.isalpha():
                    author_affs.append(affs[sup])
            is_corresponding = '*' in sups_text
            author = {'name': name, 'affiliations': author_affs,
                      'is_corresponding': is_corresponding}
            authors.append(author)
        # if correspondence not indicated by * character, look for name(s) in corresponding text
        if all([not author['is_corresponding'] for author in authors]):
            corresponding_text = self.soup.select_one("span[id='*']").text
            for author in authors:
                name_split = split_name(author['name'])
                if all([part in corresponding_text for part in name_split]):
                    author['is_corresponding'] = True
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.find(lambda tag: tag.name == 'span' and 'abstract' in tag.text.lower()):
            if siblings := abs_tag.find_next_siblings('span'):
                return '\n'.join([tag.text for tag in siblings])
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
