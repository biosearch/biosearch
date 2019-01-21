# coding: utf-8
"""
Content conversion into Elasticsearch compatible JSON

"""

#from lxml import etree
import xml.etree.ElementTree as ET

import structlog
log = structlog.getLogger()


class PubMed_XML_Parser:
    """
    """

    def __init__(self, xml_chunk):
        """
        """
        pass

    def get_pmid(self, xml_record):
        """
        Extract PMID from article XML.

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns pmid, string with article PMID
        """
        try:
            return xml_record.find('PMID').text
        except Exception as e:
            log.info('')
            return None


    def get_title(self, xml_record):
        """
        Extract article title

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns title, string with title text
        """
        article = xml_record.find('Article')
        try:
            title_chunk = article.find('ArticleTitle')#.strip()
            title = ''.join(title_chunk.itertext()).strip()
        except:
            title = ''
        return title


    def get_abstract(self, xml_record):
        """
        Extract article abstract section text

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns abstract, string with abstract paragraph(s) text
        """
        category = 'NlmCategory' #if nlm_category else 'Label'
        if xml_record.find('Article/Abstract/AbstractText') is not None:
            # parsing structured abstract
            if len(xml_record.findall('Article/Abstract/AbstractText')) > 1:
                abstract_list = list()
                for abstract_chunk in xml_record.findall(
                    'Article/Abstract/AbstractText'):
                    section = abstract_chunk.attrib.get(category, '')
                    #print('section:', section)
                    if section != 'UNASSIGNED':
                        abstract_list.append('')
                        abstract_list.append(abstract_chunk.attrib.get(
                            category, ''))
                        abstract_list.append('')
                    abstract_chunk_text = ''.join(
                        abstract_chunk.itertext()).strip()
                    abstract_list.append(abstract_chunk_text)
                abstract = '\n'.join(abstract_list).strip()
            else:
                try:
                    abstract_chunk = xml_record.find(
                        'Article/Abstract/AbstractText') #.strip()
                    abstract = ''.join(abstract_chunk.itertext()).strip()
                except:
                    abstract = ''
        elif xml_record.find('Abstract') is not None:
            try:
                abstract_chunk = xml_record.find('Abstract')#.strip()
                abstract = ''.join(abstract_chunk.itertext()).strip()
            except:
                abstract = ''
        else:
            abstract = ''
        return abstract



    def get_pub_type(self, xml_record):
        """
        Extract publication type(s) from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns pub_type_list, list of string publication types,
            e.g., ["Review", "Clinical Trial"]
        """
        pub_type_chunk = xml_record.find('Article/PublicationTypeList')
        #print('pub_type_chunk:', pub_type_chunk)
        pub_type_list = list()
        try:
            for ptp in pub_type_chunk.findall('PublicationType'):
                if ptp.text is not None:
                    pub_type_list.append(ptp.text)
        except Exception as e:
            log.warning('Could not get publication type - ADD XML Record ID here')

        return pub_type_list

    def get_mesh_terms(self, xml_record):
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
        except Exception as e:
            mesh_term_list = list()
        return mesh_term_list

        '''
        convert.py:131: DeprecationWarning: This method will be removed in future versions.
        Use 'list(elem)' or iteration over elem instead.
        m.find('DescriptorName').text for m in mesh.getchildren()
        '''

    def get_chemical_substances(self, xml_record):
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
        except Exception as e:
            chem_list = list()
        return chem_list
        '''
        convert.py:150: DeprecationWarning: This method will be removed in future versions.
        Use 'list(elem)' or iteration over elem instead.
        m.find('NameOfSubstance').text for m in chem.getchildren()
        '''

    def get_keywords(self, xml_record):
        """
        Extract keywords from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns keywords: list of keyword phrases contained in the document
        """
        keyword_list = list()
        kwds_chunk = xml_record.find('KeywordList')
        #rint(kwds_chunk)
        try:
            for k in kwds_chunk.findall('Keyword'):
                if k.text is not None:
                    keyword_list.append(k.text.strip())
        except Exception as e:
            pass

        return keyword_list

# #----------------------------------------------------------------------------##


def xml_to_json(xml_chunk):
    """
    """
    P = PubMed_XML_Parser(xml_chunk)

    json_record = {}
    yield json_record

# #----------------------------------------------------------------------------##

if __name__ == "__main__":

    # test with a sample XML files

    with open('example.xml', 'r') as fhin:
        xml_chunk = fhin.read()

    P = PubMed_XML_Parser(xml_chunk)
    PubmedArticleSet = ET.fromstring(xml_chunk)

    for PubmedArticle in PubmedArticleSet:
        MedlineCitation = PubmedArticle.find('MedlineCitation')
        #pmid = MedlineCitation.find('PMID').text
        pmid = P.get_pmid(MedlineCitation)
        print(pmid)
        title = P.get_title(MedlineCitation)
        print('Title:', title)
        pubtype = P.get_pub_type(MedlineCitation)
        print('Pub Type:', ', '.join(pubtype))
        mesh = P.get_mesh_terms(MedlineCitation)
        print('MeSH Headings:', mesh)
        chem = P.get_chemical_substances(MedlineCitation)
        print('Chemical Substances:', chem)
        kwds = P.get_keywords(MedlineCitation)
        print('Keywords:', kwds)
        abstract = P.get_abstract(MedlineCitation)
        print('Abstract:', abstract)
        print('\n')

    '''
    medline_citations = tree.findall('//MedlineCitationSet/MedlineCitation')
    if len(medline_citations) == 0:
        medline_citations = tree.findall('//MedlineCitation')
    for xml_record in medline_citations:
        pmid = P.get_pmid(MedlineCitation)
        print('PMID:', pmid)
    '''


##
