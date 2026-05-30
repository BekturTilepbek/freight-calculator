"""
Скрипт начального наполнения БД тестовыми данными.
Запуск: docker compose exec backend python -m app.db.seed
"""
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from random import choice, randint, uniform

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.client import Client
from app.models.broker import Broker
from app.models.order import Order, OrderStatus


CLIENTS = [
    ("Walmart Logistics", "John Smith", "logistics@walmart.com"),
    ("Amazon Freight", "Sarah Connor", "freight@amazon.com"),
    ("Home Depot Supply", "Mike Johnson", "supply@homedepot.com"),
    ("Costco Wholesale", "Emily Davis", "trans@costco.com"),
    ("Target Distribution", "Robert Brown", "ops@target.com"),
]

BROKERS = [
    ("TQL Logistics", "MC-123456"),
    ("CH Robinson", "MC-234567"),
    ("XPO Logistics", "MC-345678"),
]

ROUTES = [
    ("Chicago, IL", "Dallas, TX", 925),
    ("Los Angeles, CA", "Phoenix, AZ", 372),
    ("Atlanta, GA", "Miami, FL", 661),
    ("Seattle, WA", "Denver, CO", 1316),
    ("Houston, TX", "New Orleans, LA", 348),
    ("New York, NY", "Boston, MA", 215),
    ("San Francisco, CA", "Las Vegas, NV", 569),
    ("Detroit, MI", "Cleveland, OH", 170),
    ("Philadelphia, PA", "Washington, DC", 140),
    ("Portland, OR", "San Diego, CA", 1095),
]

STATUSES_WEIGHTED = (
    [OrderStatus.DELIVERED] * 6
    + [OrderStatus.IN_TRANSIT] * 2
    + [OrderStatus.ASSIGNED] * 1
    + [OrderStatus.DRAFT] * 1
)


async def seed():
    async with AsyncSessionLocal() as db:
        # Проверяем, не наполняли ли уже
        existing = (await db.execute(select(Client).limit(1))).scalar_one_or_none()
        if existing:
            print("⚠️  База уже содержит данные. Сидер пропущен.")
            return

        # Клиенты
        clients = []
        for name, contact, email in CLIENTS:
            c = Client(name=name, contact_person=contact, email=email)
            db.add(c)
            clients.append(c)

        # Брокеры
        brokers = []
        for company, mc in BROKERS:
            b = Broker(company_name=company, mc_number=mc)
            db.add(b)
            brokers.append(b)

        await db.flush()  # чтобы получить id

        # Заявки
        for i in range(1, 41):
            origin, dest, distance = choice(ROUTES)
            rate = Decimal(str(round(uniform(1.2, 2.5), 2)))
            created = datetime.utcnow() - timedelta(days=randint(0, 60))
            pickup = created.date() + timedelta(days=1)
            delivery = pickup + timedelta(days=randint(1, 5))

            order = Order(
                order_number=f"FR-{1000 + i}",
                origin_address=origin,
                destination_address=dest,
                distance_miles=Decimal(str(distance)),
                rate_per_mile=rate,
                cargo_type=choice(["Electronics", "Food", "Textiles", "Auto Parts", "General"]),
                weight_lbs=Decimal(str(randint(5000, 45000))),
                pickup_date=pickup,
                delivery_date=delivery,
                status=choice(STATUSES_WEIGHTED),
                client_id=choice(clients).id,
                broker_id=choice(brokers).id,
                created_at=created,
                updated_at=created,
            )
            db.add(order)

        await db.commit()
        print(f"✅ Создано: {len(CLIENTS)} клиентов, {len(BROKERS)} брокеров, 40 заявок")


if __name__ == "__main__":
    asyncio.run(seed())