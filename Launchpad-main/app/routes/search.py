from fastapi import APIRouter
from fastapi.responses import FileResponse
from typing import Optional
from elasticsearch import Elasticsearch

router = APIRouter()
es = Elasticsearch("http://localhost:9200")
INDEX_NAME = "products"

@router.get("/search")
def search_products(
    q: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    category_id: Optional[int] = None,
    limit: int = 10,
    offset: int = 0
):
    must_clauses = []

    if q:
        must_clauses.append({
            "multi_match": {
                "query": q,
                "fields": ["name", "description"]
            }
        })

    if brand:
        must_clauses.append({"match": {"brand": brand}})

    if category_id is not None:
        must_clauses.append({"match": {"category_id": category_id}})

    filter_clauses = []
    if min_price is not None or max_price is not None:
        price_range = {}
        if min_price is not None:
            price_range["gte"] = min_price
        if max_price is not None:
            price_range["lte"] = max_price
        filter_clauses.append({"range": {"price": price_range}})

    query_body = {
        "query": {
            "bool": {
                "must": must_clauses,
                "filter": filter_clauses
            }
        },
        "from": offset,
        "size": limit
    }

    try:
        response = es.search(index=INDEX_NAME, body=query_body)
        hits = response["hits"]["hits"]
        results = []
        for hit in hits:
            product = hit["_source"]
            product["id"] = hit["_id"] 
            results.append(product)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}


@router.get("/search-page")
async def serve_search_page():
    return FileResponse("frontend/search.html")

