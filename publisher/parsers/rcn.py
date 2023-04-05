from publisher.parsers.parser import PublisherParser
from publisher.parsers.utils import email_matches_name, strip_suffix


class RoyalCollegeOfNursing(PublisherParser):
    parser_name = "royal_college_of_nursing"

    def is_publisher_specific_parser(self):
        return bool(self.soup.select('meta[content*="rcni.com"]'))

    def authors_found(self):
        return bool(self.soup.select(
            'h1 + .mar-bot-15'))

    def parse_authors(self):
        author_tag = self.soup.select_one('h1 + .mar-bot-15')
        corr_email = ''
        if corr_email_tag := self.soup.select_one('meta[name=correspondence]'):
            corr_email = corr_email_tag['content']
        authors = []
        for author_tag in author_tag.findChildren(recursive=False):
            name_tag = author_tag.find('strong')
            name = strip_suffix('@\w+', name_tag.text.strip())
            name_tag.decompose()
            aff = author_tag.text.strip()
            affs = [aff]
            is_corresponding = email_matches_name(corr_email, name)
            author = {'name': name, 'affiliations': affs,
                      'is_corresponding': is_corresponding}
            authors.append(author)

        return authors

    def parse_abstract(self):
        if abs_tag := self.soup.select_one('abstract'):
            return abs_tag.text
        return None

    def parse(self):
        return {'authors': self.parse_authors(),
                'abstract': self.parse_abstract()}
