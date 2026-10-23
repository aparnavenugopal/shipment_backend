import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .core.rate_limiter import limiter
from contextlib import asynccontextmanager
from .router.user import router as user_router
from .model import ShipmentCreate, ShipmentModify
from .router.shipments import router as shipments_router
from .router.customer import router as customer_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: runs before the app handles requests
    print("shipment tracker is starting")

    yield

    # shutdown: runs when the app shuts down
    print("shipment tracker is shutting down")

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

@app.middleware("http")
async def measure_request_time(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(duration)

    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


allowed_fields = {
        "content",
        "status",
        "destination"
    }

app.include_router(shipments_router)
app.include_router(customer_router)
app.include_router(user_router)












        

   



    




   


@app.get("/scalar", include_in_schema = False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url = app.openapi_url,
        title = "Delivery API"
    )
