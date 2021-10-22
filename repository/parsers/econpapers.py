from repository.parsers.parser import RepositoryParser


class EconPapers(RepositoryParser):
    parser_name = "EconPapers"

    def is_correct_parser(self):
        canonical_link = self.soup.find("link", {"rel": "canonical"})
        return (
            canonical_link
            and canonical_link.get("href")
            and 'econpapers.repec.org/repec:' in canonical_link.get("href").lower()
        )

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_publication_date"})

    def parse(self):
        if pub_date_tag := self.soup.find("meta", {"name": "citation_publication_date"}):
            if pub_date_content := pub_date_tag.get('content'):
                return {'published_date': pub_date_content}

        return {}

    test_cases = [
        {
            'page-id': 'D5uqBc9DcrRDT4Kx7Pgp',  # https://econpapers.repec.org/RePEc:oup:beheco:v:17:y:2006:i:2:p:222-226
            'result': {
                'published_date': '2006',
            }
        },
    ]
