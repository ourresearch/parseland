import re

from publisher.parsers.parser import PublisherParser


class UniversityOfTorontoPress(PublisherParser):
    parser_name = "university_of_toronto_press"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('utpjournals.press')

    def authors_found(self):
        return bool(self.soup.select('.contribDegrees'))

    def parse_authors(self):
        author_tags = self.soup.select('.contribDegrees')
        authors = []
        corresponding_text = ''
        if corresponding_tag := self.soup.find('corresp'):
            corresponding_text = corresponding_tag.text
        for author_tag in author_tags:
            name = author_tag.select_one('a.entryAuthor').text.strip()
            is_corresponding = name in corresponding_text
            affs = []
            if affs_tag := author_tag.select_one('div[class*=ui-helper-hidden]'):
                affs = re.split('\d+\W(?=[A-Z])', affs_tag.text)
                affs = [aff for aff in affs if len(aff) > 2]
            author = {'name': name, 'affiliations': affs, 'is_corresponding': is_corresponding}
            authors.append(author)
        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('.abstractInFull p'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(), 'abstract': self.parse_abstract()}

