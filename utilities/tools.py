from pprint import pformat
from pydantic import BaseModel, Extra, Field
from typing import Any, Dict
import requests
from time import sleep


class clinvarInput(BaseModel):
    variant: str = Field()
    gene: str = Field()
class ClinVarAPIWrapper(BaseModel):
    """Wrapper around ClinVar.

        Example:
            .. code-block:: python
                from utilities.tools import ClinVarAPIWrapper
                clinvar = ClinVarAPIWrapper()
    """

    name = "ClinVar API"
    description = "Use the ClinVar API to get information about a variant."
    args_schema = clinvarInput


    BASE_URL = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
    session: Any = requests.Session()

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    """
    TODO:
    Change the way the API is called, so it is more dynamic.
    And the agent can decide which function to call.
        --> Not sure how to do this yet.
        Maybe by using a dictionary with the function names as keys?
        
    """

    def _request(self, endpoint, params=None):
        url = self.BASE_URL + endpoint
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Raise an exception if the request was unsuccessful
        return response.json()  # Assumes that the response body is JSON

    def _search_variant(self, term):
        """Search for a variant. And return the list of IDs."""
        params = {'db': 'clinvar', 'term': term, 'retmode': 'json'}
        return ','.join(self._request('esearch.fcgi', params)['esearchresult']['idlist'])

    def _fetch_variant(self, id):
        """Fetch a variant by ID."""
        params = {'db': 'clinvar', 'id': id, 'retmode': 'json'}
        return self._request('efetch.fcgi', params)

    def _fetch_summary(self, id):
        """Fetch a variant summary by ID."""
        params = {'db': 'clinvar', 'id': id, 'retmode': 'json'}
        return self._request('esummary.fcgi', params)

    def run(self, variant: str, gene: str) -> str:
        """Fetch a variant summary by ID."""
        term = variant + " + " + gene
        params = {'db': 'clinvar', 'id': self._search_variant(term) , 'retmode': 'json'}
        sleep(0.5)
        return self._outputParser(self._request('esummary.fcgi', params))

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
                          "trait_set": output['result'][id]["trait_set"],
                          "keys": output['result'][id].keys()}
        formatted = pformat(vardic)
        if len(formatted) > 3000:
            return f"Too many results were found. Only giving first 2000 characters.\n {formatted[:3000]}"
        return


class PubMedInput(BaseModel):
    search_term: str = Field()

class PubMedAPIWrapper:
    """Wrapper around PubMed.

            Example:
                .. code-block:: python
                    from utilities.tools import PubMedAPIWrapper
                    pubmed = PubMedAPIWrapper()
    """


    name = "PubMed API"
    description = "Use the PubMed API to get information out of the latest articles about a variant."

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

    def search_variant(self, search_term : str) -> str:
        """Search for a variant in PubMed."""
        params = {'db': 'pubmed', 'term': search_term, 'retmode': 'json'}
        return self._request('esearch.fcgi', params)
