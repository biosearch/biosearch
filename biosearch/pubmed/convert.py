# coding: utf-8
"""
Content conversion into Elasticsearch compatible JSON.

"""

import xml.etree.ElementTree as ET
import re
import structlog

log = structlog.getLogger()


class PubMed_XML_Parser:
    """
    """

    def __init__(self, xml_chunk):
        pass

    def get_pmid(self, xml_record):
        """
        Extract PMID from article XML.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns pmid, string with article PMID.
        """
        try:
            return xml_record.find("PMID").text
        except Exception as e:
            log.info("")
            return None

    def get_title(self, xml_record):
        """
        Extract article title.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns title, string with title text.
        """
        article = xml_record.find("Article")
        try:
            title_chunk = article.find("ArticleTitle")  # .strip()
            title = "".join(title_chunk.itertext()).strip()
        except Exception:
            title = ""
        return title

    def get_abstract(self, xml_record):
        """
        Extract article abstract section text.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns abstract, string with abstract paragraph(s) text.
        """
        category = "NlmCategory"  # if nlm_category else 'Label'
        if xml_record.find("Article/Abstract/AbstractText") is not None:
            # parsing structured abstract
            if len(xml_record.findall("Article/Abstract/AbstractText")) > 1:
                abstract_list = list()
                for abstract_chunk in xml_record.findall("Article/Abstract/AbstractText"):
                    section = abstract_chunk.attrib.get(category, "")
                    # print('section:', section)
                    abstract_list.append("")
                    if section != "UNASSIGNED":
                        abstract_list.append("")
                        abstract_list.append(abstract_chunk.attrib.get(category, ""))
                    abstract_chunk_text = "".join(abstract_chunk.itertext()).strip()
                    abstract_chunk_text = cleanup_text(abstract_chunk_text)
                    abstract_list.append(abstract_chunk_text)
                abstract = "\n".join(abstract_list).strip()
                abstract = re.sub("\n{3,}", "\n\n", abstract)
            else:
                try:
                    abstract_chunk = xml_record.find("Article/Abstract/AbstractText")
                    abstract = "".join(abstract_chunk.itertext()).strip()
                except Exception:
                    abstract = ""
        elif xml_record.find("Abstract") is not None:
            try:
                abstract_chunk = xml_record.find("Abstract")
                abstract = "".join(abstract_chunk.itertext()).strip()
            except Exception:
                abstract = ""
        else:
            abstract = ""
        return abstract

    def get_author_info(self, xml_record):
        """
        Extract author/contributor info: names and affiliations.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns authors, tupule with list of author details:
            [full name, affiliation] where full name is in the format:
            "LastName, ForeName Initials" and affiliation is a semicolon
            separated string of affiliations.
        """
        authors = list()
        author_info_chunk = xml_record.find("Article/AuthorList")
        if author_info_chunk is not None:
            for author_chunk in author_info_chunk.findall("Author"):
                # print('author_chunk:', author_chunk)
                try:
                    last_name = author_chunk.find("LastName").text
                except Exception:
                    last_name = ""
                try:
                    first_name = author_chunk.find("ForeName").text
                except Exception:
                    first_name = ""
                try:
                    initials = author_chunk.find("Initials").text
                except Exception:
                    initials = ""
                name = "%s, %s %s" % (last_name, first_name, initials)
                all_auth_affs = list()
                aff_chunk = author_chunk.find("AffiliationInfo")
                try:
                    for aff in aff_chunk.findall("Affiliation"):
                        all_auth_affs.append(aff.text)
                except Exception:
                    pass
                    # print('missing affiliations')
                authors.append((name, "; ".join(all_auth_affs)))
        else:
            print("author_chunk: None")
        return authors

    def get_pub_type(self, xml_record):
        """
        Extract publication type(s) from article MedlineCitation element.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns pub_type_list, list of string publication types,
            e.g., ["Review", "Clinical Trial"].
        """
        pub_type_chunk = xml_record.find("Article/PublicationTypeList")
        # print('pub_type_chunk:', pub_type_chunk)
        pub_type_list = list()
        try:
            for ptp in pub_type_chunk.findall("PublicationType"):
                if ptp.text is not None:
                    pub_type_list.append(ptp.text)
        except Exception as e:
            log.warning("Could not get publication type - ADD XML Record ID here")

        return pub_type_list

    def get_journal_info(self, xml_record):
        """
        Extract journal info from article MedlineCitation element.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns journal_info, dictionary of journal properties: name, issue,
        volume, etc.

        Example of elements looked for:
        ...
        <Journal>
            <ISSN IssnType="Print">2095-1779</ISSN>
            <JournalIssue CitedMedium="Print">
                <Volume>7</Volume>
                <Issue>3</Issue>
                <PubDate>
                    <Year>2017</Year>
                    <Month>Jun</Month>
                </PubDate>
            </JournalIssue>
            <Title>Journal of pharmaceutical analysis</Title>
            <ISOAbbreviation>J Pharm Anal</ISOAbbreviation>
        </Journal>
        ...
        <Pagination>
            <MedlinePgn>950-968</MedlinePgn>
        </Pagination>
        ...

        Alternative format
        ...
        <Journal>
            <ISSN IssnType="Electronic">1615-5742</ISSN>
            <JournalIssue CitedMedium="Internet">
                <Volume>21</Volume>
                <Issue>6</Issue>
                <PubDate>
                    <MedlineDate>2018 Nov-Dec</MedlineDate>
                </PubDate>
            </JournalIssue>
            <Title>Pediatric and developmental pathology : the official journal of the Society for Pediatric Pathology and the Paediatric Pathology Society</Title>
            <ISOAbbreviation>Pediatr. Dev. Pathol.</ISOAbbreviation>
        </Journal>
        ...
        """
        journal_info = dict()
        journal_chunk = xml_record.find("Article/Journal")
        issn_chunk = journal_chunk.find("ISSN")
        try:
            issn_type = issn_chunk.attrib.get("IssnType", "")
            if issn_type is not None:
                journal_info["issn"] = issn_chunk.text
        except Exception:
            journal_info["issn"] = ""
        journal_info["title"] = journal_chunk.find("Title").text
        try:
            journal_info["abbrev"] = journal_chunk.find("ISOAbbreviation").text
        except Exception:
            journal_info["abbrev"] = ""
        issue_chunk = journal_chunk.find("JournalIssue")
        try:
            journal_info["volume"] = issue_chunk.find("Volume").text
        except Exception:
            journal_info["volume"] = ""
        try:
            journal_info["issue"] = issue_chunk.find("Issue").text
        except Exception:
            journal_info["issue"] = ""
        pubdate_chunk = issue_chunk.find("PubDate")
        try:
            journal_info["pubyear"] = pubdate_chunk.find("Year").text
        except Exception:
            journal_info["pubyear"] = "YYYY"
        try:
            journal_info["pubmonth"] = pubdate_chunk.find("Month").text
        except Exception:
            journal_info["pubmonth"] = "MMM"
        try:
            journal_info["pubday"] = pubdate_chunk.find("Day").text
        except Exception:
            journal_info["pubday"] = "dd"
        if journal_info["pubyear"] == "YYYY":
            try:
                medline_date = pubdate_chunk.find("MedlineDate").text
                bits = re.split("\s+", medline_date)
                if re.match("^\d\d\d\d$", bits[0]):
                    journal_info["pubyear"] = bits[0]
                    if len(bits) > 1:
                        journal_info["pubmonth"] = bits[1]
                    if len(bits) > 2:
                        journal_info["pubday"] = bits[2]
                elif bits[0] in ["Spring", "Summer", "Fall", "Winter"]:
                    journal_info["pubmonth"] = bits[0]
                    journal_info["pubyear"] = bits[1]
            except Exception:
                journal_info["pubyear"] = "YYYY"
        journal_chunk = xml_record.find("Article/Pagination")
        try:
            journal_info["pages"] = journal_chunk.find("MedlinePgn").text
        except Exception:
            journal_info["pages"] = ""
        return journal_info

    def get_mesh_terms(self, xml_record):
        """
        Extract MeSH headings from article MedlineCitation element.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns mesh_terms, list of MeSH (Medical Subject Headings) terms
        contained in the document.
        """
        try:
            mesh = xml_record.find("MeshHeadingList")
            mesh_term_list = [
                m.find("DescriptorName").attrib.get("UI", "") + ": " + m.find("DescriptorName").text
                for m in mesh.getchildren()
            ]
        except Exception as e:
            mesh_term_list = list()
        return mesh_term_list

        """
        convert.py:131: DeprecationWarning: This method will be removed in future versions.
        Use 'list(elem)' or iteration over elem instead.
        m.find('DescriptorName').text for m in mesh.getchildren()
        """

    def get_chemical_substances(self, xml_record):
        """
        Extract chemical substances from article MedlineCitation element.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns chem_list: list of chemical substancs contained in the document.
        """
        try:
            chem = xml_record.find("ChemicalList")
            chem_list = [
                m.find("NameOfSubstance").attrib.get("UI", "")
                + ": "
                + m.find("NameOfSubstance").text
                for m in chem.getchildren()
            ]
        except Exception as e:
            chem_list = list()
        return chem_list
        """
        convert.py:150: DeprecationWarning: This method will be removed in future versions.
        Use 'list(elem)' or iteration over elem instead.
        m.find('NameOfSubstance').text for m in chem.getchildren()
        """

    def get_keywords(self, xml_record):
        """
        Extract keywords from article MedlineCitation element.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns keywords: list of keyword phrases contained in the document.
        """
        keyword_list = list()
        kwds_chunk = xml_record.find("KeywordList")
        # print(kwds_chunk)
        try:
            for k in kwds_chunk.findall("Keyword"):
                if k.text is not None:
                    keyword_list.append(k.text.strip())
        except Exception as e:
            pass

        return keyword_list

    def get_reference_list(self, xml_record):
        """
        Extract a list of references articles from article PubmedData element.

        Args:
            xml_record: PubMed article PubmedData element

        Returns references: list tupules of article ids referenced by this
        article, with format of each reference ([IdType],[ArticleId]),
        e.g., ('pubmed','9050830').

        Example of elements looked for:

        ...
        <ReferenceList>
            <Reference>
                <Citation>Nature. 2001 Dec 20-27;414(6866):883-7</Citation>
                <ArticleIdList>
                    <ArticleId IdType="pubmed">11780055</ArticleId>
                </ArticleIdList>
            </Reference>
            ...
        </ReferenceList>
        ...
        """
        references = list()
        references_chunk = xml_record.find("ReferenceList")
        if not references_chunk:
            return references
        for ref_chunk in references_chunk.findall("Reference/ArticleIdList"):
            article_id_element = ref_chunk.find("ArticleId")
            try:
                id_type = article_id_element.attrib.get("IdType", "")
                if id_type is not None:
                    article_id = article_id_element.text
                    references.append((id_type, article_id))
            except Exception:
                pass

        return references

    def get_articles_ids(self, xml_record):
        """
        Extract PMC ID from article XML.

        Args:
            xml_record: PubMed article PubmedData element

        Returns pmc, string with article PMC ID.
        """
        articles_ids = {"pmc": "", "doi": ""}
        for article_id_element in xml_record.findall("ArticleIdList/ArticleId"):
            try:
                id_type = article_id_element.attrib.get("IdType", "")
                if id_type == "pmc":
                    articles_ids["pmc"] = article_id_element.text
                elif id_type == "doi":
                    articles_ids["doi"] = article_id_element.text
            except Exception:
                pass
        return articles_ids


##----------------------------------------------------------------------------##


def cleanup_text(chunk):
    """
    Remove HTML tags form text lines.

    Args:
        chunk (str) - extracted abstract text chunk with potential HTML
        to be removed

    Returns newline-separated abstract lines with HTML tags removed.
    """
    lines = re.split("\n", chunk)
    clean_lines = list()
    for line in lines:
        # strip HTML tags
        line = re.sub("<.*?>", "", line)
        clean_lines.append(line.strip())
    return "\n".join(clean_lines)


def xml_to_json(xml_chunk):
    """
    """
    P = PubMed_XML_Parser(xml_chunk)

    for PubmedArticle in ET.fromstring(xml_chunk):
        json_record = {}
        MedlineCitation = PubmedArticle.find("MedlineCitation")
        PubmedData = PubmedArticle.find("PubmedData")
        json_record["pmid"] = P.get_pmid(MedlineCitation)
        json_record["pmc"] = P.get_articles_ids(PubmedData)["pmc"]
        json_record["doi"] = P.get_articles_ids(PubmedData)["doi"]
        json_record["title"] = P.get_title(MedlineCitation)
        json_record["pubtype"] = P.get_pub_type(MedlineCitation)
        json_record["mesh"] = P.get_mesh_terms(MedlineCitation)
        json_record["chem"] = P.get_chemical_substances(MedlineCitation)
        json_record["kwds"] = P.get_keywords(MedlineCitation)
        json_record["abstract"] = P.get_abstract(MedlineCitation)
        json_record["authors"] = P.get_author_info(MedlineCitation)
        journal_info = P.get_journal_info(MedlineCitation)
        json_record["journal_issn"] = journal_info["issn"]
        json_record["journal_title"] = journal_info["title"]
        json_record["journal_volume"] = journal_info["volume"]
        json_record["journal_issue"] = journal_info["issue"]
        json_record["journal_pages"] = journal_info["pages"]
        json_record["journal_abbrev"] = journal_info["abbrev"]
        json_record["journal_pubyear"] = journal_info["pubyear"]
        json_record["journal_pubmonth"] = journal_info["pubmonth"]
        json_record["journal_pubday"] = journal_info["pubday"]
        json_record["references"] = P.get_reference_list(PubmedData)
        yield json_record

    return


if __name__ == "__main__":

    # test with a sample XML files

    with open("example_2019.xml", "r") as fhin:
        # with open("example_2018.xml", "r") as fhin:
        xml_chunk = fhin.read()

    P = PubMed_XML_Parser(xml_chunk)
    PubmedArticleSet = ET.fromstring(xml_chunk)

    for PubmedArticle in PubmedArticleSet:
        print("-" * 80)
        MedlineCitation = PubmedArticle.find("MedlineCitation")
        PubmedData = PubmedArticle.find("PubmedData")
        pmid = P.get_pmid(MedlineCitation)
        print("PMID:", pmid)
        pmc = P.get_articles_ids(PubmedData)["pmc"]
        print("PMC:", pmc)
        doi = P.get_articles_ids(PubmedData)["doi"]
        print("doi:", doi)
        title = P.get_title(MedlineCitation)
        print("Title:", title)
        pubtype = P.get_pub_type(MedlineCitation)
        print("Pub Type:", ", ".join(pubtype))
        mesh = P.get_mesh_terms(MedlineCitation)
        print("MeSH Headings:", mesh)
        chem = P.get_chemical_substances(MedlineCitation)
        print("Chemical Substances:", chem)
        kwds = P.get_keywords(MedlineCitation)
        print("Keywords:", kwds)
        abstract = P.get_abstract(MedlineCitation)
        print("Abstract:", len(abstract), "characters")
        authors = P.get_author_info(MedlineCitation)
        print("Authors:", authors)
        journal_info = P.get_journal_info(MedlineCitation)
        print("Journal:", journal_info)
        print("PubYear:", journal_info["pubyear"])
        references = P.get_reference_list(PubmedData)
        print("References:", references)
        print("\n")
