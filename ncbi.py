from lxml import etree
import requests
import os


NCBI_SEARCH_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_FETCH_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class NCBISearch(object):

    tool_name = "Disease Research Trends"
    tool_email = os.environ.get("disease_email")

    def __init__(self, term):
        self.term = term
        self.database = "pubmed"
        self.article_ids = set()
        self.search_number = 5
        self.fetch_number = 5
        self.articles = []

    def get_base_params(self, **kwargs):
        kwargs["db"] = self.database
        kwargs["tool"] = self.tool_name
        kwargs["email"] = self.tool_email
        return kwargs

    def get_search_params(self, **kwargs):
        kwargs = self.get_base_params(**kwargs)
        kwargs["term"] = self.term
        return kwargs

    def get_fetch_params(self, **kwargs):
        kwargs = self.get_base_params(**kwargs)
        kwargs["id"] = ",".join(self.article_ids)
        kwargs["retmode"] = "xml"
        kwargs["rettype"] = "docsum"
        kwargs["retmax"] = self.fetch_number
        return kwargs

    def get_all_ids(self):
        """
        Get all article IDs for this search, add
        to self.article_ids
        :return: None
        """
        while True:
            results = self.get_ids()
            ids = results["id_set"]
            if not ids - self.article_ids:
                break
            self.article_ids = self.article_ids | ids
            if len(self.article_ids) >= results["result_count"]:
                break

    def get_ids(self):
        """
        Get next batch of article ids from NCBI search.
        :return: set of article IDs fetched in this request
        """
        data = self.get_search_params(retmax=self.search_number, retstart=len(self.article_ids))
        result = requests.post(NCBI_SEARCH_URL, data)
        root = etree.fromstring(result.content)
        xml_ids = root.findall("./IdList/Id")
        ids = {tag.text for tag in xml_ids}
        count = int(root.find("./Count").text)
        return {"id_set": ids, "result_count": count}

    def get_article_details(self):
        """
        Get article details for all articles in self.article_ids
        :return:
        """
        data = self.get_fetch_params(retstart=0)
        result = requests.post(NCBI_FETCH_URL, data)
        pass




