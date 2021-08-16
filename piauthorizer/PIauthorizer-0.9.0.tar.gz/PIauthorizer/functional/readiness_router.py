from fastapi import APIRouter

readiness_router = APIRouter()


# Liveness probe for kubernetes status service
@readiness_router.get("/ready", tags=["Readiness"])
def get_readiness():
    return {"status": "ready"}
