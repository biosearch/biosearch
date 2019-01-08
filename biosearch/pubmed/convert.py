# coding: utf-8
"""
Content conversion into Elasticsearch compatible JSON

"""

class PubMed_XML_Parser:
    """
    """

    def __init__(self, xml_chunk):
        """
        """


    def get_pmid(self, xml_record):
        """
        Extract PMID from article XML.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns pmid, string with article PMID
        """
        try:
            return xml_record.find('PMID').text
        except:
            return None


    def get_pub_type(self, xml_record):
        """
        Extract publication type(s) from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns pub_type_list, list of string publication types,
            e.g., ["Review", "Clinical Trial"]
        """
        pub_type_chunk = xml_record.find('PublicationTypeList')
        pub_type_list = list()
        try:
            for ptp in pub_type_chunk.findall('PublicationType'):
                if ptp.text is not None:
                    pub_type_list.append(ptp.text)
        except:
            pass
        return pub_type_list


    def get_mesh_terms(xml_record):
        """
        Extract MeSH headings from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns mesh_terms, list of MeSH (Medical Subject Headings) terms
            contained in the document
        """
        try:
            mesh = xml_record.find('MeshHeadingList')
            mesh_term_list = [
                m.find('DescriptorName').attrib.get('UI', '') + ": " +
                m.find('DescriptorName').text for m in mesh.getchildren()
            ]
        except:
            mesh_term_list = list()
        return mesh_term_list


    def get_chemical_substances(xml_record):
        """
        Extract chemical substances from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns chem_list: list of chemical substancs contained in the document
        """
        try:
            chem = xml_record.find('ChemicalList')
            chem_list = [
                m.find('NameOfSubstance').attrib.get('UI', '') + ": " +
                m.find('NameOfSubstance').text for m in chem.getchildren()
            ]
        except:
            chem_list = list()
        return chem_list


    def get_keywords(xml_record):
        """
        Extract keywords from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns keywords: list of keyword phrases contained in the document
        """
        try:
            kwds = xml_record.find('KeywordList')
            for k in keyword_list.findall('Keyword'):
                if k.text is not None:
                    keyword_list.append(k.text.strip())
        except:
            keyword_list = list()
        return keyword_list

##----------------------------------------------------------------------------##


def xml_to_json(xml_chunk):
    """
    """

        yield json_record

##----------------------------------------------------------------------------##
