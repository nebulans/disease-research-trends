from itertools import izip_longest
from lxml import etree
import re
import requests
import os


NCBI_SEARCH_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_FETCH_URL = "http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

def grouper(iterable, n, fillvalue=None):
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


class NCBIArticle(object):

    def __init__(self, title, year):
        self.title = title
        self.year = year

    def __str__(self):
        return "{} ({})".format(self.title, self.year)

    @classmethod
    def from_etree(cls, tree):
        title = tree.find(".Item[@Name='Title']").text.encode("utf-8")  # NCBI API seems confused about encoding, we know it should be UTF-8
        pub_date = tree.find(".Item[@Name='PubDate']").text
        year = None
        match = re.search("\d{4}", pub_date)
        if match:
            year = match.group(0)
        return cls(title, year)


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
        kwargs["retmode"] = "xml"
        kwargs["rettype"] = "docsum"
        kwargs["retmax"] = self.fetch_number
        kwargs["retstart"] = 0
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
        Instantiate NCBIArticle objects for each, append to self.articles
        :return: None
        """
        id_list = list(self.article_ids)  # Need list to allow indexing here
        for ids in grouper(id_list, self.fetch_number, ""):  # Fixed number of API requests here, no danger of endless fetching
            data = self.get_fetch_params(id=",".join(ids))
            result = requests.post(NCBI_FETCH_URL, data)
            root = etree.fromstring(result.content)
            for article in root.findall("./DocSum"):
                self.articles.append(NCBIArticle.from_etree(article))

    def run(self):
        """
        Get all article ids and contents
        """
        self.get_all_ids()
        self.get_article_details()

    def articles_by_year(self):
        """
        Calculate total number of articles in this search for each year with articles
        :return:
        """
        result = {}
        for a in self.articles:
            if a.year not in result:
                result[a.year] = 0
            result[a.year] += 1
        return result


