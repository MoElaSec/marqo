"""The API entrypoint for Neural Search"""
from models.api_models import SearchQuery, AddDocuments
from fastapi import FastAPI, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from marqo import utils
from typing import Union
from fastapi import FastAPI
from marqo.neural_search import neural_search
from marqo import config
from typing import List, Dict
import os
import inspect
import logging
OPENSEARCH_URL = os.environ["OPENSEARCH_URL"]
security = HTTPBasic()
app = FastAPI()


async def generate_config(creds: HTTPBasicCredentials = Depends(security)):
    authorized_url = utils.construct_authorized_url(
        url_base=OPENSEARCH_URL,
        username=creds.username,
        password=creds.password)
    return config.Config(url=authorized_url)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/indexes/{index_name}/search")
async def search(search_query: SearchQuery, index_name: str, marqo_config: config.Config = Depends(generate_config)):
    return neural_search.search(
        config=marqo_config, text=search_query.q,
        index_name=index_name, highlights=search_query.showHighlights,
        searchable_attributes=search_query.searchableAttributes,
        search_method=search_query.searchMethod,
        result_count=search_query.limit)


@app.post("/indexes/{index_name}/documents")
async def add_documents(docs: List[Dict], index_name: str,  refresh: bool = True,
                        marqo_config: config.Config = Depends(generate_config)):
    """add_documents endpoint"""
    return neural_search.add_documents(
        config=marqo_config,
        docs=docs,
        index_name=index_name, auto_refresh=refresh
    )

# try these curl commands:
"""
curl -XPOST  'http://admin:admin@localhost:8000/indexes/my-irst-ix/documents?refresh=true' -H 'Content-type:application/json' -d '
[
    {
        "Title": "Honey is a delectable food stuff",
        "Desc" : "some boring description",
        "_id": "honey_facts_119"
    }, {
        "Title": "Space exploration",
        "Desc": "mooooon! Space!!!!",
        "_id": "moon_fact_145"
    }
]'
"""

"""
curl -XPOST  http://admin:admin@localhost:8000/indexes/my-irst-ix/search -H 'Content-type:application/json' -d '{
    "q": "what do bears eat?",
    "searchableAttributes": ["Title", "Desc", "other"],
    "limit": 3, 
    "searchMethod": "NEURAL",
    "showHighlights": true
}'
"""