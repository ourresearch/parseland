from publisher.parsers.parser import PublisherParser


class Duke(PublisherParser):

    def authors_found(self):
        pass

    def parse(self):
        pass

    parser_name = 'duke'

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url('dukeupress.edu')
