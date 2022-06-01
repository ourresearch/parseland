from exceptions import UnusualTrafficError
from publisher.parsers.parser import PublisherParser


class IOP(PublisherParser):
    parser_name = "IOP"

    def is_publisher_specific_parser(self):
        if "iopscience.iop.org" in str(
            self.soup
        ) and "your activity and behavior on this site made us think that you are a bot" in str(
            self.soup
        ):
            raise UnusualTrafficError(f"Page blocked within parser {self.parser_name}")
        stylesheet = self.soup.find("link", {"rel": "stylesheet"})
        if stylesheet and "static.iopscience.com" in stylesheet.get("href"):
            return True

    def authors_found(self):
        return self.soup.find("meta", {"name": "citation_author"})

    def parse(self):
        # displayed author affiliations are not available in the content, so we have to use meta tags.
        return self.parse_meta_tags()

    # test not passing due to page being blocked
    # test_cases = [
    #     {
    #         "doi": "10.1088/1361-6560/ac212a",
    #         "result": [
    #             {
    #                 "name": "Nicolaus Kratochwil",
    #                 "affiliations": [
    #                     "CERN, Esplanade des Particules 1, 1211 Meyrin, Switzerland",
    #                     "University of Vienna, Universitaetsring 1, A-1010 Vienna, Austria",
    #                 ],
    #                 "is_corresponding": False,
    #             },
    #             {
    #                 "name": "Stefan Gundacker",
    #                 "affiliations": [
    #                     "CERN, Esplanade des Particules 1, 1211 Meyrin, Switzerland",
    #                     "Department of Physics of Molecular Imaging Systems, Institute for Experimental Molecular Imaging, RWTH Aachen University, Forckenbeckstrasse 55, D-52074 Aachen, Germany",
    #                 ],
    #                 "is_corresponding": False,
    #             },
    #             {
    #                 "name": "Etiennette Auffray",
    #                 "affiliations": [
    #                     "CERN, Esplanade des Particules 1, 1211 Meyrin, Switzerland"
    #                 ],
    #                 "is_corresponding": False,
    #             },
    #         ],
    #     },
    # ]
