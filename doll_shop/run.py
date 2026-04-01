import uvicorn
from api.configurations.base import config

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=9999,
        reload=config.debug,
    )
