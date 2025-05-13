from fastapi import Request
from app.utils.logger import logger
import time

async def log_requests(request: Request, call_next):
    """Middleware to log all incoming API requests."""
    start_time = time.time()
    
    logger.info(f"Request: {request.method} {request.url.path}")
    logger.debug(f"Headers: {dict(request.headers)}")
    logger.debug(f"Query Params: {dict(request.query_params)}")
    
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise
    
    # Calculate response time
    process_time = (time.time() - start_time) * 1000
    logger.info(f"Response: {response.status_code} (Time: {process_time:.2f}ms)")
    
    return response
