from pprint import pformat
from pydantic import BaseModel, Extra, Field
from typing import Any, Dict
import requests
from time import sleep


class clinvarInput(BaseModel):
    term: str = Field(default="")
    method: str = Field(default="Search")

class ClinVarAPIWrapper(BaseModel):
    """Wrapper around ClinVar.

        Example:
            .. code-block:: python
                from utilities.tools import ClinVarAPIWrapper
                clinvar = ClinVarAPIWrapper()
    """

    name = "ClinVar API"
    description = """
                    Use the ClinVar API to get information about a variant.
                    You have the following options:
                    - term: The term to search for.
                    - method: The method to use. "Search" or "Fetch".
                    
                    Example:
                        term: "c.1187G>A AND CMTR1[gene]" or "p.Arg396Gln AND CMTR1[gene]"
                        method: "Search"
                        
                    This returns a list of IDs. Which can be used to fetch the summary.
                    
                    If you want to fetch the summary, use the following:
                        term: "123456" (Single ID from the search to avoid token limit)
                        method: "Fetch"
                  """
    args_schema = clinvarInput


    BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    session: Any = requests.Session()

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def _request(self, endpoint, params=None):
        url = self.BASE_URL + endpoint
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        return response.json()  # Assumes that the response body is JSON

    def _search_variant(self, term):
        """Search for a variant. And return the list of IDs."""
        params = {'db': 'clinvar', 'term': term, 'retmode': 'json'}
        return ','.join(self._request('esearch.fcgi', params)['esearchresult']['idlist'])

    def _fetch_summary(self, id):
        """Fetch a variant summary by ID."""
        params = {'db': 'clinvar', 'id': id, 'retmode': 'json'}
        return self._request('esummary.fcgi', params)

    def run(self, term: str, method: str) -> str:
        """Fetch a variant summary by ID."""
        if method == "Search":
            result = self._search_variant(term)
        elif method == "Fetch":
            result = self._fetch_summary(term)
            result = self._outputParser(result)
        else:
            result = "Method not found."
        return result

    def _outputParser(self, output: Dict[str, Any]) -> str:
        """Parse the output of the ClinVar API."""
        vardic = {}
        if len(output['result']['uids']) == 0:
            return "No results found."
        for id in output['result']['uids']:
            vardic[id] = {"title": output['result'][id]['title'],
                          "accession": output['result'][id]["accession"],
                          "supporting_submissions": output['result'][id]['supporting_submissions'],
                          "clinical_significance": output['result'][id]['clinical_significance'],
                          "record_status": output['result'][id]['record_status'],
                          "trait_set": output['result'][id]["trait_set"]}
        formatted = pformat(vardic)
        if len(formatted) > 3000:
            return f"Too many results were found. Only giving first 3000 characters.\n {formatted[:3000]}"
        return formatted


class PubMedInput(BaseModel):
    term: str = Field(default="")
    method: str = Field(default="run")

class PubMedAPIWrapper:
    """Wrapper around PubMed.

            Example:
                .. code-block:: python
                    from utilities.tools import PubMedAPIWrapper
                    pubmed = PubMedAPIWrapper()
    """


    name = "PubMed API"
    description = """
                        Use the PubMed API to get literature about a variant.
                        You have the following options:
                        - term: The term to search for.
                        - method: The method to use. "Search" or "Fetch".
                        Search returns a list of IDs. Which can be used to fetch the summary.

                        Example:
                            term: "c.1187G>A AND CMTR1[gene]" or "p.Arg396Gln AND CMTR1[gene]"
                            method: "Search"

                        If you want to fetch the summary, use the following:
                            term: "123456" (Single ID from the search to avoid token limit)
                            method: "Fetch"
                      """
    BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    session: Any = requests.Session()
    arg_scheme = PubMedInput

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True


    def _request(self, endpoint, params=None):
        url = self.BASE_URL + endpoint
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        return response.json()  # Assumes that the response body is JSON

    def _search_variant(self, search_term : str) -> str:
        """Search for a variant in PubMed."""
        params = {'db': 'pubmed', 'term': search_term, 'retmode': 'json', 'retmax': 5}
        return self._request('esearch.fcgi', params)

    def _fetch_summary(self, id):
        """Fetch a variant summary by ID."""
        params = {'db': 'pubmed', 'id': id, 'retmode': 'json'}
        return self._request('esummary.fcgi', params)

    def run(self, term: str, method: str) -> str:
        """Fetch a variant summary by ID."""
        if method == "Search":
            result = self._search_variant(term)
        elif method == "Fetch":
            result = self._fetch_summary(term)
        else:
            result = "Method not found."
        return result

class omimInput(BaseModel):
    id: str = Field(default="")
    database: str = Field(default="omim")

class OmimAPIWrapper:
    """Wrapper around OMIM.

            Example:
                .. code-block:: python
                    from utilities.tools import OmimAPIWrapper
                    omim = OmimAPIWrapper()
    """


    name = "OMIM API"
    description = """
                        Use the OMIM API to get information about a variant.
                        You have the following options:
                        - id: The id to search for.
                        - database: The database to search, available: 'OMIM', 'MeSH', 'MedGen'.
                        
                        If you want to fetch the summary, use the following:
                            term: "123456" (Single ID from the search to avoid token limit)
                            database: "OMIM"
                        
                        # Fetches the summary of the variant based on ID in the database of choice
                      """
    BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    session: Any = requests.Session()
    arg_scheme = PubMedInput

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True


    def _request(self, endpoint, params=None):
        url = self.BASE_URL + endpoint
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        return response.json()  # Assumes that the response body is JSON

    def _search_variant(self, search_term : str) -> str:
        """Search for a variant in PubMed."""
        params = {'db': 'omim', 'term': search_term, 'retmode': 'json', 'retmax': 5}
        return self._request('esearch.fcgi', params)

    def _fetch_summary(self, id, database):
        """Fetch a variant summary by ID."""
        params = {'db': database, 'id': id, 'retmode': 'json'}
        return self._request('esummary.fcgi', params)

    def run(self, id: str, database: str) -> str:
        """Fetch a variant summary by ID."""

        result = self._fetch_summary(id, database)

        return result