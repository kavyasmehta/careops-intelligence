from fastapi import APIRouter

from app.db.mongo import ping_mongo
from app.db.neo4j import ping_neo4j

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    mongo_ok = await ping_mongo()
    neo4j_ok = await ping_neo4j()
    status_ = "ok" if mongo_ok and neo4j_ok else "degraded"
    return {
        "data": {
            "status": status_,
            "dependencies": {"mongo": mongo_ok, "neo4j": neo4j_ok},
        }
    }
