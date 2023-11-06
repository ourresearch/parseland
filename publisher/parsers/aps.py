from publisher.elements import Affiliation, AuthorAffiliations, Author
from publisher.parsers.parser import PublisherParser


class APS(PublisherParser):
    parser_name = "aps"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url(
            "journals.aps.org") or self.domain_in_meta_og_url(
            'journals.physiology.org')

    def authors_found(self):
        return bool(self.soup.select(
            'ul[title="list of authors"]')) or self.soup.select(
            'section.article.authors p')

    def parse_authors_1(self):
        authors = []
        author_tags = self.soup.select(
            'ul[title="list of authors"] + div [class*=accordion-tabbed__tab]')
        for author_tag in author_tags:
            name = author_tag.select_one('a.author-name').text
            is_corresponding = bool(author_tag.select('i.icon-Email'))
            affs_tag = author_tag.select_one('.author-info')
            affs_tag.select_one('.bottom-info').decompose()
            affiliations = [tag.text for tag in affs_tag.find_all('p') if
                            len(tag.text) > 3]
            authors.append({'name': name, 'affiliations': affiliations,
                            'is_corresponding': is_corresponding})
        return authors

    def parse_affs_2(self):
        affs = []
        if affs_tag := self.soup.select_one('section.article.authors ul'):
            aff_tags = affs_tag.select('li')
            for aff in aff_tags:
                sup = aff.find('sup')
                _id = sup.text.strip()
                sup.decompose()
                affs.append(
                    Affiliation(organization=aff.text.strip(), aff_id=_id))
        return affs

    def parse_authors_2(self):
        authors = []
        affs = self.parse_affs_2()
        author_tags = self.soup.select('section.article.authors p a')
        for author_tag in author_tags:
            aff_ids = author_tag.find_next_sibling('sup').text.strip().split(',')
            author = Author(name=author_tag.text.strip(), aff_ids=aff_ids)
            authors.append(author)
        return self.merge_authors_affiliations(authors=authors, affiliations=affs)

    def parse(self):
        return {
            "authors": self.parse_authors_1() or self.parse_authors_2(),
            "abstract": self.parse_abstract_meta_tags(),
        }

    test_cases = [
        {
            "doi": "10.1103/physreve.99.032306",
            "result": {
                "authors": [
                    {
                        "name": "Pedro H. T. Schimit",
                        "affiliations": [
                            "Informatics and Knowledge Management Graduate Program, Universidade Nove de Julho, Rua Vergueiro, 235/249, CEP 01504-000, São Paulo, São Paulo, Brazil"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Karan Pattni",
                        "affiliations": [
                            "Department of Mathematical Sciences, University of Liverpool, Mathematical Sciences Building, Liverpool L69 7ZL, United Kingdom"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Mark Broom",
                        "affiliations": [
                            "Department of Mathematics, City, University of London, Northampton Square, London EC1V 0HB, United Kingdom"
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "The modeling of evolution in structured populations has been significantly advanced by evolutionary graph theory, which incorporates pairwise relationships between individuals on a network. More recently, a new framework has been developed to allow for multiplayer interactions of variable size in more flexible and potentially changing population structures. While the theory within this framework has been developed and simple structures considered, there has been no systematic consideration of a large range of different population structures, which is the subject of this paper. We consider a large range of underlying graphical structures for the territorial raider model, the most commonly used model in the new structure, and consider a variety of important properties of our structures with the aim of finding factors that determine the fixation probability of mutants. We find that the graphical temperature and the average group size, as previously defined, are strong predictors of fixation probability, while all other properties considered are poor predictors, although the clustering coefficient is a useful secondary predictor when combined with either temperature or group size. The relationship between temperature or average group size and fixation probability is sometimes, however, nonmonotonic, with a directional reverse occurring around the temperature associated with what we term ``completely mixed'' populations in the case of the hawk-dove game, but not the public goods game.",
            },
        },
        {
            "doi": "10.1103/physrevb.103.235137",
            "result": {
                "authors": [
                    {
                        "name": "Christoph Schönle",
                        "affiliations": [
                            "Institut für Theoretische Physik, Georg-August-Universität Göttingen, D-37077 Göttingen, Germany"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "David Jansen",
                        "affiliations": [
                            "Institut für Theoretische Physik, Georg-August-Universität Göttingen, D-37077 Göttingen, Germany"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Fabian Heidrich-Meisner",
                        "affiliations": [
                            "Institut für Theoretische Physik, Georg-August-Universität Göttingen, D-37077 Göttingen, Germany"
                        ],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Lev Vidmar",
                        "affiliations": [
                            "Department of Theoretical Physics, J. Stefan Institute, SI-1000 Ljubljana, Slovenia",
                            "Department of Physics, Faculty of Mathematics and Physics, University of Ljubljana, SI-1000 Ljubljana, Slovenia",
                        ],
                        "is_corresponding": None,
                    },
                ],
                "abstract": "Matrix elements of observables in eigenstates of generic Hamiltonians are described by the Srednicki ansatz within the eigenstate thermalization hypothesis (ETH). We study a quantum chaotic spin-fermion model in a one-dimensional lattice, which consists of a spin-1/2 XX chain coupled to a single itinerant fermion. In our study, we focus on translationally invariant observables including the charge and energy current, thereby also connecting the ETH with transport properties. Considering observables with a Hilbert-Schmidt norm of one, we first perform a comprehensive analysis of ETH in the model taking into account latest developments. A particular emphasis is on the analysis of the structure of the offdiagonal matrix elements $|\\ensuremath{\\langle}\\ensuremath{\\alpha}|\\stackrel{\\ifmmode \\hat{}\\else \\^{}\\fi{}}{O}{|\\ensuremath{\\beta}\\ensuremath{\\rangle}|}^{2}$ in the limit of small eigenstate energy differences $\\ensuremath{\\omega}={E}_{\\ensuremath{\\beta}}\\ensuremath{-}{E}_{\\ensuremath{\\alpha}}$. Removing the dominant exponential suppression of $|\\ensuremath{\\langle}\\ensuremath{\\alpha}|\\stackrel{\\ifmmode \\hat{}\\else \\^{}\\fi{}}{O}{|\\ensuremath{\\beta}\\ensuremath{\\rangle}|}^{2}$, we find that (1) the current matrix elements exhibit a system-size dependence that is different from other observables under investigation and (2) matrix elements of several other observables exhibit a Drude-like structure with a Lorentzian frequency dependence. We then show how this information can be extracted from the autocorrelation functions as well. Finally, our study is complemented by a numerical analysis of the fluctuation-dissipation relation for eigenstates in the bulk of the spectrum. We identify the regime of $\\ensuremath{\\omega}$ in which the well-known fluctuation-dissipation relation is valid with high accuracy for finite systems.",
            },
        },
        {
            "doi": "10.1103/physrevd.103.029901",
            "result": {
                "authors": [
                    {
                        "name": "Josipa Majstorović",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Séverine Rosat",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                    {
                        "name": "Yves Rogister",
                        "affiliations": [],
                        "is_corresponding": None,
                    },
                ],
                "abstract": None,
            },
        },
    ]
