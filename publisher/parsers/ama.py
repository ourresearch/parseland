from publisher.parsers.generic import GenericPublisherParser
from publisher.parsers.parser import PublisherParser


class AMA(PublisherParser):
    parser_name = "american_medical_association"

    def is_publisher_specific_parser(self):
        return self.domain_in_canonical_link('jamanetwork.com')

    def authors_found(self):
        return bool(self.soup.select('span.wi-fullname'))

    def parse(self):
        generic = GenericPublisherParser(self.soup)
        msg = generic.parse()
        if corresponding_tag := self.soup.select_one('p.authorInfoSection'):
            corr_text = corresponding_tag.text
            for author in msg['authors']:
                if author['name'] in corr_text:
                    author['is_corresponding'] = True
        return msg
