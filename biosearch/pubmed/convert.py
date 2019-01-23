# coding: utf-8
"""
Content conversion into Elasticsearch compatible JSON

"""

#from lxml import etree
import xml.etree.ElementTree as ET
import re
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
                    abstract_list.append('')
                    if section != 'UNASSIGNED':
                        abstract_list.append('')
                        abstract_list.append(abstract_chunk.attrib.get(
                            category, ''))
                    abstract_chunk_text = ''.join(
                        abstract_chunk.itertext()).strip()
                    abstract_chunk_text = cleanup_text(abstract_chunk_text)
                    abstract_list.append(abstract_chunk_text)
                abstract = '\n'.join(abstract_list).strip()
                abstract = re.sub('\n{3,}', '\n\n', abstract)
            else:
                try:
                    abstract_chunk = xml_record.find(
                        'Article/Abstract/AbstractText')
                    abstract = ''.join(abstract_chunk.itertext()).strip()
                except:
                    abstract = ''
        elif xml_record.find('Abstract') is not None:
            try:
                abstract_chunk = xml_record.find('Abstract')
                abstract = ''.join(abstract_chunk.itertext()).strip()
            except:
                abstract = ''
        else:
            abstract = ''
        return abstract


    def get_author_info(self, xml_record):
        """
        Extract author/contributor info: names and affiliations

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns authors, tupule with list of author details:
            [full name, affiliation] where full name is in the format:
            "LastName, ForeName Initials" and affiliation is a semicolon
            separated string of affiliations.
        """
        authors = list()
        author_info_chunk = xml_record.find('Article/AuthorList')
        if author_info_chunk is not None:
            for author_chunk in author_info_chunk.findall('Author'):
                #print('author_chunk:', author_chunk)
                try:
                    last_name = author_chunk.find('LastName').text
                except:
                    last_name = ''
                try:
                    first_name = author_chunk.find('ForeName').text
                except:
                    first_name = ''
                try:
                    initials = author_chunk.find('Initials').text
                except:
                    initials = ''
                name = '%s, %s %s' % (last_name, first_name, initials)
                all_auth_affs = list()
                aff_chunk = author_chunk.find('AffiliationInfo')
                try:
                    for aff in aff_chunk.findall('Affiliation'):
                        all_auth_affs.append(aff.text)
                except:
                    pass
                    #print('missing affiliations')
                authors.append((name, '; '.join(all_auth_affs)))
        else:
            print('author_chunk: None')
        return authors


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


    def get_journal_info(self, xml_record):
        """
        Extract journal info from article MedlineCitation element

        Args:
            xml_record: PubMed article MedlineCitation element

        Returns journal_info, dictionary of journal properties: name, issue,
            volume, etc.

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
        <Pagination>
            <MedlinePgn>950-968</MedlinePgn>
        </Pagination>
        """
        journal_info = dict()
        journal_chunk = xml_record.find('Article/Journal')
        issn_chunk = journal_chunk.find('ISSN')
        try:
            issn_type = issn_chunk.attrib.get('IssnType', '')
            if issn_type is not None:
                journal_info['ISSN'] = issn_chunk.text
        except:
            pass
        journal_info['title'] = journal_chunk.find('Title').text
        journal_info['abbrev'] = journal_chunk.find('ISOAbbreviation').text
        issue_chunk = journal_chunk.find('JournalIssue')
        try:
            journal_info['volume'] = issue_chunk.find('Volume').text
        except:
            pass
        try:
            journal_info['issue'] = issue_chunk.find('Issue').text
        except:
            pass
        pubdate_chunk = issue_chunk.find('PubDate')
        try:
            journal_info['pubyear'] = pubdate_chunk.find('Year').text
        except:
            pass
        try:
            journal_info['pubmonth'] = pubdate_chunk.find('Month').text
        except:
            pass
        journal_chunk = xml_record.find('Article/Pagination')
        try:
            journal_info['pages'] = journal_chunk.find('MedlinePgn').text
        except:
            pass
        return journal_info


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
        #print(kwds_chunk)
        try:
            for k in kwds_chunk.findall('Keyword'):
                if k.text is not None:
                    keyword_list.append(k.text.strip())
        except Exception as e:
            pass

        return keyword_list

##----------------------------------------------------------------------------##

def cleanup_text(chunk):
    lines = re.split('\n', chunk)
    clean_lines = list()
    for line in lines:
        # strip HTML tags
        line = re.sub('<.*?>', '', line)
        clean_lines.append(line.strip())
    return '\n'.join(clean_lines)


def xml_to_json(xml_chunk):
    """
    """
    P = PubMed_XML_Parser(xml_chunk)

    json_record = {}
    yield json_record


##----------------------------------------------------------------------------##

if __name__ == "__main__":

    # test with a sample XML files

    with open('example.xml', 'r') as fhin:
        xml_chunk = fhin.read()

    P = PubMed_XML_Parser(xml_chunk)
    PubmedArticleSet = ET.fromstring(xml_chunk)

    for PubmedArticle in PubmedArticleSet:
        print('-'*80)
        MedlineCitation = PubmedArticle.find('MedlineCitation')
        #pmid = MedlineCitation.find('PMID').text
        pmid = P.get_pmid(MedlineCitation)
        print('PMID:', pmid)
        title = P.get_title(MedlineCitation)
#        print('Title:', title)
        pubtype = P.get_pub_type(MedlineCitation)
#        print('Pub Type:', ', '.join(pubtype))
        mesh = P.get_mesh_terms(MedlineCitation)
#        print('MeSH Headings:', mesh)
        chem = P.get_chemical_substances(MedlineCitation)
#        print('Chemical Substances:', chem)
        kwds = P.get_keywords(MedlineCitation)
#        print('Keywords:', kwds)
        abstract = P.get_abstract(MedlineCitation)
#        print('Abstract:', len(abstract), 'characters')
        authors = P.get_author_info(MedlineCitation)
#        print('Authors:', authors)
        journal_info = P.get_journal_info(MedlineCitation)
        print('Journal:', journal_info)

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
