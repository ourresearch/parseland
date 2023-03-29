from publisher.parsers.parser import PublisherParser


class Duke(PublisherParser):
    parser_name = 'duke'

    def parse(self):
        return self.parse_meta_tags()

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('dukeupress.edu')
