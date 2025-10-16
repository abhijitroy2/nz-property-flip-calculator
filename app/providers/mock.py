import random
from .base import Provider
from .. import models

class MockProvider(Provider):
    async def fetch(self, address: str) -> models.DataPoints:
        rng = random.Random(hash(address) & 0xFFFFFFFF)
        est_purchase_price = rng.randint(150_000, 750_000)
        est_rehab_cost = rng.randint(20_000, 180_000)
        arv = int(est_purchase_price * rng.uniform(1.05, 1.45))
        crime_index = rng.uniform(5, 70)
        school_rating = rng.uniform(3, 9)
        dom = rng.randint(10, 120)
        comp_count = rng.randint(3, 20)
        return models.DataPoints(
            address=address,
            est_purchase_price=float(est_purchase_price),
            est_rehab_cost=float(est_rehab_cost),
            est_after_repair_value=float(arv),
            crime_index=float(crime_index),
            school_rating=float(school_rating),
            days_on_market_avg=int(dom),
            comp_count=int(comp_count),
        )