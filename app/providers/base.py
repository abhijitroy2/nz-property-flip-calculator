from typing import Protocol
from .. import models

class Provider(Protocol):
    async def fetch(self, address: str) -> models.DataPoints:
        ...