from repository.parsers.parser import RepositoryParser


class DOAJ(RepositoryParser):
    parser_name = "DOAJ"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("doaj.org/article/")

    def authors_found(self):
        return self.soup.find("dl", {"id": "authors-affiliations"})

    def parse(self):
        authors = []
        dl = self.soup.find("dl", {"id": "authors-affiliations"})

        for dt in dl.find_all("dt"):
            author = {"name": dt.text, "affiliations": []}

            for dd_or_dt in dt.find_next_siblings():
                if dd_or_dt.name == "dd":
                    author["affiliations"].append(dd_or_dt.text)
                else:
                    break

            authors.append(author)

        return authors

    test_cases = [
        {
            "page-id": "VEXAwqyTcm3QfoybFTPa",  # https://doaj.org/article/f2d8edcb996c46ee98f9b41469254e52
            "result": [
                {"name": "Maria Cecília de Souza Minayo", "affiliations": []},
                {"name": "Luiza Gualhano", "affiliations": []},
            ],
        },
        {
            "page-id": "6FjYA6ZmfSDwwduEB3C3",  # https://doaj.org/article/f2d97de5957543f3ab139022fa91a2fc
            "result": [
                {
                    "name": "Jaime Pajuelo",
                    "affiliations": [
                        "Universidad Nacional Mayor de San Marcos",
                    ],
                },
                {
                    "name": "Ivon Bernui",
                    "affiliations": [
                        "Universidad Nacional Mayor de San Marcos",
                    ],
                },
                {
                    "name": "Jesús Rocca",
                    "affiliations": ["Hospital Nacional Dos de Mayo"],
                },
                {
                    "name": "Lizardo Torres",
                    "affiliations": ["Hospital Nacional Dos de Mayo"],
                },
                {
                    "name": "Lilia Soto",
                    "affiliations": ["Hospital Nacional Dos de Mayo"],
                },
            ],
        },
    ]
