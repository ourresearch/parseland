import re

from publisher.elements import Author, Affiliation
from publisher.parsers.parser import PublisherParser


class Frontiers(PublisherParser):
    parser_name = "frontiers"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("frontiersin.org")

    def authors_found(self):
        return self.soup.find("div", class_="authors")

    def parse(self):
        authors = self.get_authors()
        affiliations = self.get_affiliations()
        authors_affiliations = self.merge_authors_affiliations(authors, affiliations)
        return {
            "authors": authors_affiliations,
            "abstract": self.parse_abstract_meta_tags(),
        }

    def get_authors(self):
        authors = []
        author_soup = self.soup.find("div", class_="authors")
        author_soup = author_soup.findAll("img", class_="pr5")
        for author in author_soup:
            # set name
            name_soup = author.next_sibling
            name = name_soup.text

            # set aff_ids
            aff_id_soup = name_soup.next_element
            is_corresponding = False
            if aff_id_soup.name == "sup":
                aff_ids = aff_id_soup.text
                if "*" in aff_ids:
                    is_corresponding = True
            else:
                aff_ids = None

            aff_ids = self.format_ids(aff_ids) if aff_ids else []

            authors.append(
                Author(
                    name=name, aff_ids=aff_ids, is_corresponding_author=is_corresponding
                )
            )
        return authors

    def get_affiliations(self):
        aff_soup = self.soup.find("ul", class_="notes")

        results = []
        if aff_soup:
            affiliations = aff_soup.findAll("li")
            for aff_raw in affiliations:
                aff_id_raw = aff_raw.find("sup")
                if aff_id_raw:
                    aff_id = aff_id_raw.text
                else:
                    aff_id = None
                aff = aff_raw.text
                if aff_id:
                    aff = re.sub(rf"^\s*{aff_id}\s*", "", aff).strip()
                if aff_id != "*" and aff_id != "†":
                    aff_id = int(aff_id) if aff_id else None
                    results.append(Affiliation(aff_id=aff_id, organization=aff))
        return results

    @staticmethod
    def format_ids(ids):
        ids_cleaned = re.sub(
            "[^0-9^,]", "", ids
        )  # remove anything that is not a number or comma
        ids_split = ids_cleaned.split(",")
        aff_ids = []
        for aff_id in ids_split:
            if aff_id:
                aff_ids.append(int(aff_id))
        return aff_ids

    test_cases = [
        {
            "doi": "10.3389/fevo.2021.635552",
            "result": {
                "authors": [
                    {
                        "name": "Kohei Oguchi",
                        "affiliations": [
                            "Misaki Marine Biological Station, School of Science, The University of Tokyo, Miura, Japan",
                            "National Institute of Advanced Industrial Science and Technology, Tsukuba, Japan",
                        ],
                    },
                    {
                        "name": "Kiyoto Maekawa",
                        "affiliations": [
                            "Faculty of Science, Academic Assembly, University of Toyama, Gofuku, Japan",
                        ],
                    },
                    {
                        "name": "Toru Miura",
                        "affiliations": [
                            "Misaki Marine Biological Station, School of Science, The University of Tokyo, Miura, Japan"
                        ],
                    },
                ],
                "abstract": "Eusocial insects exhibit reproductive division of labor, in which only a part of colony members differentiates into reproductives. In termite colonies, the division of labors is performed among multiple types of individuals (i.e., castes), such as reproductives, workers, and soldiers to organize their society. Caste differentiation occurs according to extrinsic factors, such as social interactions, leading to developmental modifications during postembryonic development, and consequently, the caste ratio in a colony is appropriately coordinated. In particular, when the current reproductives die or become senescent, some immature individuals molt into supplementary reproductives, also known as “neotenics,” that take over the reproductive task in their natal colony. Neotenics exhibit variety of larval features, such as winglessness, and thus, immature individuals are suggested to differentiate by a partial release from arrested development, particularly in the reproductive organs. These neotenic features, which have long been assumed to develop via heterochronic regulation, provide us opportunities to understand the developmental mechanisms and evolutionary origin of the novel caste. This article overviews the accumulated data on the physiological and developmental mechanisms that regulate the neotenic differentiation in termites. Furthermore, the evolutionary trajectories leading to neotenic differentiation are discussed, namely the acquisition of a regulatory mechanism that enable the partial release from a developmentally arrested state.",
            },
        },
        {
            "doi": "10.3389/fgene.2021.642759",
            "result": {
                "authors": [
                    {
                        "name": "Seungjun Ahn",
                        "affiliations": [
                            "Department of Biostatistics, University of Florida, Gainesville, FL, United States"
                        ],
                    },
                    {
                        "name": "Tyler Grimes",
                        "affiliations": [
                            "Department of Biostatistics, University of Florida, Gainesville, FL, United States",
                        ],
                    },
                    {
                        "name": "Somnath Datta",
                        "affiliations": [
                            "Department of Biostatistics, University of Florida, Gainesville, FL, United States"
                        ],
                    },
                ],
                "abstract": "The tumor microenvironment is comprised of tumor cells, stroma cells, immune cells, blood vessels, and other associated non-cancerous cells. Gene expression measurements on tumor samples are an average over cells in the microenvironment. However, research questions often seek answers about tumor cells rather than the surrounding non-tumor tissue. Previous studies have suggested that the tumor purity (TP) – the proportion of tumor cells in a solid tumor sample – has a confounding effect on differential expression analysis of high versus low survival groups. We investigate three ways incorporating the TP information in the two statistical methods used for analyzing gene expression data, namely, differential network analysis (DNA) and differential expression analysis (DEA). Analysis 1 ignores the TP information completely, Analysis 2 uses a truncated sample by removing the low TP samples, and Analysis 3 uses TP as a covariate in the underlying statistical models. We use three gene expression data sets related to three different cancers from the Cancer Genome Atlas (TCGA) as test beds for our investigation. The networks from Analysis 2 have greater amount of differential connectivity in the two networks than that from Analysis 1 in all three cancer datasets. Similarly, Analysis 1 identified more differentially expressed genes than Analysis 2. Results of DNA and DEA using Analysis 3 were mostly consistent with those of Analysis 1 across three cancers. However, Analysis 3 identified additional cancer related genes in both DNA and DEA. Our findings suggest that using TP as a covariate in a linear model is appropriate for DEA, but a more robust model is needed for DNA. However, in the absence of ground truth, it is impossible to assess the accuracies of any of these methods. One option will be to study the statistical properties of these methods in simulated data sets which may be pursued elsewhere.",
            },
        },
        {
            "doi": "10.3389/fcvm.2021.697240",
            "result": {
                "authors": [
                    {
                        "name": "Sergey Kozhukhov",
                        "affiliations": [
                            "SI “National Scientific Center “The M.D.Strazhesko Institute of Cardiology,”” Kyiv, Ukraine"
                        ],
                    },
                    {
                        "name": "Nataliia Dovganych",
                        "affiliations": [
                            "SI “National Scientific Center “The M.D.Strazhesko Institute of Cardiology,”” Kyiv, Ukraine",
                        ],
                    },
                ],
                "abstract": "Aim. The collaboration of cardiologists, general practitioners (GPs), and oncologists is crucial in cancer patient management. We carried out a national-based survey - UkrNatSurv - on behalf of the Cardio-Oncology (CO) Working Group (WG) of the Ukrainian Society of Cardiology to analyze the level of knowledge in cardio-oncology. Methods. A short questionnaire was presented to specialists involved in the management of cancer patients across the country. The questionnaire was made up of 8 questions concerning referred cancer patients number, CV complications of cancer therapy, diagnostic methods to detect cardiotoxicity, drugs used for its treatment. Results. A total of 426 questionnaires of medical specialists from different regions of Ukraine were collected and analyzed; the majority of respondents were cardiologists (190), followed by GPs (177), 40 oncologists (mainly chemotherapists and hematologists), other - 19 (imaging specialists, neurologists, endocrinologists, etc.). All responders were equally involved in the management of cancer patients. However, less than half of patients have been seen before the start of cancer therapy. GPs observe the majority of patients after the end of treatment. All doctors are sufficiently aware of cancer-therapy-associated CV complications. However, the necessary diagnostic tools, mostly biomarkers, are not used widely by different specialists. The criteria for cardiotoxicity, in particular the level of reduction of the left ventricular ejection fraction (LVEF) as a marker of LV dysfunction, are not clearly understood. Specific knowledge in the management of CV complications in cancer is required. Conclusion. UkrNatSurv is the first survey in Ukraine to investigate awareness of CO care provided to cancer patients with CV diseases (CVD) or developed CV complications. Providing such surveys among doctors involved in CO is an excellent tool to investigate knowledge gaps in clinical practice. Therefore, the primary task is to develop a national educational CO program.",
            },
        },
        {
            "doi": "10.3389/frwa.2021.729592",
            "result": {
                "authors": [
                    {
                        "name": "Amol Patil",
                        "affiliations": [
                            "Institute of Geography, University of Augsburg, Augsburg, Germany"
                        ],
                    },
                    {
                        "name": "Benjamin Fersch",
                        "affiliations": [
                            "Institute of Meteorology and Climate Research (IMK-IFU), Karlsruhe Institute of Technology, Garmisch-Partenkirchen, Germany"
                        ],
                    },
                    {
                        "name": "Harrie-Jan Hendricks Franssen",
                        "affiliations": [
                            "Agrosphere (IBG-3), Forschungszentrum Jülich GmbH, Jülich, Germany"
                        ],
                    },
                    {
                        "name": "Harald Kunstmann",
                        "affiliations": [
                            "Institute of Geography, University of Augsburg, Augsburg, Germany",
                            "Institute of Meteorology and Climate Research (IMK-IFU), Karlsruhe Institute of Technology, Garmisch-Partenkirchen, Germany",
                        ],
                    },
                ],
                "abstract": "Cosmic-Ray Neutron Sensing (CRNS) offers a non-invasive method for estimating soil moisture at the field scale, in our case a few tens of hectares. The current study uses the Ensemble Adjustment Kalman Filter (EAKF) to assimilate neutron counts observed at four locations within a 655 Km2 pre-alpine river catchment into the Noah-MP land surface model (LSM) to improve soil moisture simulations and to optimize model parameters. The model runs with 100 m spatial resolution and uses the EU-SoilHydroGrids soil map along with the Mualem--van Genuchten soil water retention functions. Using the state estimation (ST) and joint state--parameter estimation (STP) technique, soil moisture states and model parameters controlling infiltration and evaporation rates were optimized, respectively. The added value of assimilation was evaluated for local and regional impacts using independent root zone soil moisture observations. The results show that during the assimilation period both ST and STP significantly improved the simulated soil moisture around the neutron sensors locations with improvements of the root mean square errors between 60 % and 62 % for ST and 55 % to 66 % for STP. STP could further enhance the model performance for the validation period at assimilation locations, mainly by reducing the Bias. Nevertheless, due to a lack of convergence of calculated parameters and a shorter evaluation period, performance during the validation phase degraded at a site further away from the assimilation locations. The comparison of modeled soil moisture with field-scale spatial patterns of a dense network of CRNS observations showed that STP helped to improve the average wetness conditions (reduction of spatial Bias from -0.038 cm3 cm-3 to -0.012 cm3 cm-3 for the validation period. However, the assimilation of neutron counts from only four stations showed limited success in enhancing the field-scale soil moisture patterns.",
            },
        },
    ]
