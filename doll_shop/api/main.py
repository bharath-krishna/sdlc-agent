from api.routers import dolls, customers, orders, reservations
from api.configurations.base import config
from fastapi import FastAPI


class Application(FastAPI):
    def __init__(self, **kwargs):
        config.logger.info("Application starting")
        super().__init__(**kwargs)


app = Application(
    docs_url='/docs',
    swagger_ui_oauth2_redirect_url='/callback',
    title=config.title,
    description="Doll Shop API",
    version="0.0.1",
)

app.include_router(dolls.router, prefix=config.prefix)
app.include_router(customers.router, prefix=config.prefix)
app.include_router(orders.router, prefix=config.prefix)
app.include_router(reservations.router, prefix=config.prefix)
