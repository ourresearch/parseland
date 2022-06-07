import re

from repository.parsers.parser import RepositoryParser


class DergiPark(RepositoryParser):
    parser_name = "DergiPark"

    def is_correct_parser(self):
        return self.domain_in_meta_og_url("dergipark.org.tr")

    def authors_found(self):
        return self.soup.find("p", {"id": re.compile(r"^author\d+$")})

    def parse(self):
        authors = []

        for author_paragraph in self.soup.findAll(
            "p", {"id": re.compile(r"^author\d+$")}
        ):
            [s.extract() for s in author_paragraph.find_all("small")]
            [
                a.extract()
                for a in author_paragraph.find_all(
                    "a", {"class": re.compile(r"claim-authorship")}
                )
            ]
            author_strings = list(author_paragraph.stripped_strings)

            # format is name / affiliation (optional) / orcid (optional) / country
            if author_strings:
                author = {
                    "name": author_strings[0],
                    "affiliations": [],
                    "is_corresponding": None,
                }

                author_strings.pop(0)
                # format is affiliation (optional) / orcid (optional) / country

                if author_strings:
                    author_strings.pop(-1)
                    # format is affiliation (optional) / orcid (optional)

                    orcid_pattern = r"(?:[0-9]{4}-){3}[0-9]{3}[0-9Xx]"
                    for author_string in author_strings:
                        if re.search(orcid_pattern, author_string):
                            author["orcid"] = re.sub(
                                rf".*({orcid_pattern}).*", r"\1", author_string
                            ).upper()
                        else:
                            author["affiliations"].append(author_string)

                authors.append(author)

        return {"authors": authors}

    test_cases = [
        {
            "page-id": "P22Ue2DNUJWeypqQsKR6",  # https://dergipark.org.tr/tr/pub/esamdergisi/issue/64932/943374
            "result": {
                "authors": [
                    {
                        "name": "Mustafa YURTTADUR",
                        "affiliations": [
                            "Bandırma Onyedi Eylül Üniversitesi",
                        ],
                        "is_corresponding": None,
                    }
                ]
            },
        },
        {
            "page-id": "NAbiH6M9qKtsZFL7iptk",  # https://dergipark.org.tr/tr/pub/jhpr/issue/65540/957591
            "result": {
                "authors": [
                    {
                        "name": "Buse YILDIRIM",
                        "orcid": "0000-0001-5927-598X",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Zehra PAMUK",
                        "orcid": "0000-0002-5721-3483",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Otabek JEPBAROV",
                        "orcid": "0000-0003-1479-9127",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Esra PEHLİVAN",
                        "orcid": "0000-0002-1791-5392",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                ]
            },
        },
        {
            "page-id": "EKtna8dWy5oEhSgVzMRN",  # https://dergipark.org.tr/tr/pub/marumj/issue/65553/984215
            "result": {
                "authors": [
                    {
                        "name": "Cagatay CETINKAYA",
                        "orcid": "0000-0002-4342-8053",
                        "affiliations": ["MEMORIAL ATAŞEHİR HASTANESİ"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Zeynep BILGI",
                        "orcid": "0000-0003-4981-047X",
                        "affiliations": ["ISTANBUL MEDENIYET UNIVERSITY"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Tunc LACIN",
                        "orcid": "0000-0002-6584-7814",
                        "affiliations": ["MARMARA UNIVERSITY"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Korkut BOSTANCI",
                        "orcid": "0000-0002-1904-4404",
                        "affiliations": ["MARMARA UNIVERSITY"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Bedrettin YILDIZELI",
                        "orcid": "0000-0002-1316-4552",
                        "affiliations": ["MARMARA UNIVERSITY"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Mustafa YUKSEL",
                        "orcid": "0000-0001-9493-4194",
                        "affiliations": ["MARMARA UNIVERSITY"],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Hasan Fevzi BATIREL",
                        "orcid": "0000-0002-9349-7022",
                        "affiliations": ["MARMARA UNIVERSITY"],
                        "is_corresponding": None,
                    },
                ]
            },
        },
    ]
