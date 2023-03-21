import re
from unicodedata import normalize

from publisher.elements import AuthorAffiliations
from publisher.parsers.parser import PublisherParser


class Wiley(PublisherParser):
    parser_name = "wiley"

    def is_publisher_specific_parser(self):
        return self.domain_in_meta_og_url("onlinelibrary.wiley.com") or self.text_in_meta_og_site_name('Wiley Online Library')

    def authors_found(self):
        return self.soup.find("div", class_="loa-authors")

    def parse(self):
        return {"authors": self.get_authors(), "abstract": self.get_abstract()}

    def get_authors(self):
        results = []
        if author_soup := self.soup.find("div", class_="loa-authors"):
            authors = author_soup.findAll("span", class_="accordion__closed")
        else:
            authors = []
        for author in authors:
            affiliations = []
            name = author.a.text
            aff_soup = author.findAll("p", class_=None)

            is_corresponding = False

            author_type = author.find("p", class_="author-type")
            if author_type and "corresponding" in author_type.text.lower() or author.select_one('a[href*=mailto]'):
                is_corresponding = True

            for aff in aff_soup:
                if "correspondence" in aff.text.lower() or "e-mail" in aff.text.lower():
                    is_corresponding = True

            for aff in aff_soup:
                if (
                    "correspondence" in aff.text.lower()[:25]
                    or "address reprint" in aff.text.lower()[:40]
                    or "author deceased" in aff.text.lower()
                    or "e-mail:" in aff.text.lower()
                    or aff.text.lower().startswith("contribution")
                    or aff.text.lower().startswith("joint first authors")
                    or aff.text.lower().startswith("†joint")
                ):
                    break
                affiliations.append(normalize("NFKD", aff.text))
            results.append(
                AuthorAffiliations(
                    name=name,
                    affiliations=affiliations,
                    is_corresponding=is_corresponding,
                )
            )
        return results

    def get_abstract(self):

        if abs_headings := self.soup.find_all(
            lambda tag: re.match('^h[1-6]$', tag.name) and (tag.text.lower().strip() == 'abstract' or tag.text.lower() == 'summary')
        ):
            for abstract_heading in abs_headings:
                # if graphical abstract is the only abstract, then take it, otherwise try to find actual abstract
                if any(['graphical' in cls for cls in abstract_heading['class']]) and len(abs_headings) > 1:
                    continue
                if abstract_body := abstract_heading.find_next_sibling():
                    if (abstract := abstract_body.text.strip()) and len(abstract_body.text.strip()) > 100:
                        return abstract
        if paragraphs := self.soup.select('div.article__body p'):
            return '\n'.join([p.text for p in paragraphs])

    test_cases = [
        {
            "doi": "10.1096/fba.2020-00145",
            "result": {
                "authors": [
                    {
                        "name": "Lia Tadesse Gebremedhin",
                        "affiliations": ["Minister of Health, Addis Ababa, Ethiopia"],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Tedla W. Giorgis",
                        "affiliations": [
                            "Advisor to the Minister, Ministry of Health, Addis Ababa, Ethiopia"
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Heran Gerba",
                        "affiliations": [
                            "Director-General, Ethiopian Food and Drug Administration, Addis Ababa, Ethiopia"
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": 'In Ethiopia, noncommunicable diseases (NCDs) represent 18.3% of premature mortality, consume 23% of the household expenditures, and cost 1.8% of the gross domestic product. Risk factors such as alcohol, khat, and cannabis use are on the rise and are correlated with a substantial portion of NCDs. Associated NCDs include depression, anxiety, hypertension, coronary heart disease, and myocardial infarction. The multi-faceted nature of mental health and substance abuse disorders require multi-dimensional interventions. The article draws upon participant observation and literature review to examine the policies, delivery models, and lessons learned from the Federal Ministry of Health (FMOH) experience in integrating Mental Health and Substance Abuse (MH/SA) services into primary care in Ethiopia. In 2019, FMOH developed national strategies for both NCDs and mental health to reach its population. Ethiopia integrated MH/SA services at all levels within the government sector, with an emphasis on primary health care. FMOH launched the Ethiopian Primary Health Care Clinical Guidelines, which includes the delivery of NCD services, to standardize the care given at the primary health care level. To date, the guidelines have been implemented by over 800 health centers and are expected to improve the quality of service and health outcomes. Existing primary care programs were expanded to include prevention, early detection, treatment, and rehabilitation for MH/SA. This included training and leveraging an array of health professionals, including traditional healers and those from faith-based institutions and community-based organizations. A total of 244 health centers completed training in the Mental Health Gap Action Programme (mhGAP). In 2020, 5,000 urban Health Extension Workers (HEWs) participated in refresher training, which includes mental health and NCDs. A similar curriculum for rural health workers is in development. Ethiopia\'s experience has many lessons learned about stakeholder buy-in, roles, training, logistics, and sustainability that are transferable to other countries. Lessons include that "buy-in" by leaders of public health care facilities requires consistent and persistent nurturing. Ensure the gradual and calibrated integration of MH/SA services so that the task-sharing will not be viewed as "task dumping." Supervision and mentorship of the newly trained is important for the delivery of quality care and acquisition of skills.',
            },
        },
        {
            "doi": "10.1002/ptr.6273",
            "result": {
                "authors": [
                    {
                        "name": "Chunyu Li",
                        "affiliations": [
                            "Department of Integrated Chinese Traditional and Western Medicine, International Medical School, Tianjin Medical University, Tianjin, China"
                        ],
                        "is_corresponding": True,
                    },
                    {
                        "name": "Qi Wang",
                        "affiliations": [
                            "Department of Oncology, Shanghai Pulmonary Hospital Affiliated Tongji University, Shanghai, China"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Shen Shen",
                        "affiliations": [
                            "Department of Integrated Chinese Traditional and Western Medicine, International Medical School, Tianjin Medical University, Tianjin, China"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Xiaolu Wei",
                        "affiliations": [
                            "Department of Integrated Chinese Traditional and Western Medicine, International Medical School, Tianjin Medical University, Tianjin, China"
                        ],
                        "is_corresponding": False,
                    },
                    {
                        "name": "Guoxia Li",
                        "affiliations": [
                            "Department of Integrated Chinese Traditional and Western Medicine, International Medical School, Tianjin Medical University, Tianjin, China"
                        ],
                        "is_corresponding": False,
                    },
                ],
                "abstract": "Tumor metastasis is still the leading cause of melanoma mortality. Luteolin, a natural flavonoid, is found in fruits, vegetables, and medicinal herbs. The pharmacological action and mechanism of luteolin on the metastasis of melanoma remain elusive. In this study, we investigated the effect of luteolin on A375 and B16-F10 cell viability, migration, invasion, adhesion, and tube formation of human umbilical vein endothelial cells. Epithelial–mesenchymal transition (EMT) markers and pivotal molecules in HIF-1α/VEGF signaling expression were analysed using western blot assays or quantitative real-time polymerase chain reaction. Results showed that luteolin inhibits cellular proliferation in A375 and B16-F10 melanoma cells in a time-dependent and concentration-dependent manner. Luteolin significantly inhibited the migratory, invasive, adhesive, and tube-forming potential of highly metastatic A375 and B16-F10 melanoma cells or human umbilical vein endothelial cells at sub-IC50 concentrations, where no significant cytotoxicity was observed. Luteolin effectively suppressed EMT by increased E-cadherin and decreased N-cadherin and vimentin expression both in mRNA and protein levels. Further, luteolin exerted its anti-metastasis activity through decreasing the p-Akt, HIF-1α, VEGF-A, p-VEGFR-2, MMP-2, and MMP-9 proteins expression. Overall, our findings first time suggests that HIF-1α/VEGF signaling-mediated EMT and angiogenesis is critically involved in anti-metastasis effect of luteolin as a potential therapeutic candidate for melanoma.",
            },
        },
    ]
