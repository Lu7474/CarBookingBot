from core.database.models import async_session
from core.database.models import User, Car, Booking
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

async def set_user(tg_id, name, phone=None):
    async with async_session() as session:
        user = await session.scalar(select(User).filter(User.tg_id == tg_id))

        if not user:
            user = User(tg_id=tg_id, name=name, phone=phone if phone else None)
            session.add(user)
            await session.commit()


async def get_cars():
    async with async_session() as session:
        return await session.execute(select(Car)).scalars().all()


async def get_car_booking(car_id):
    async with async_session() as session:
        return (
            await session.execute(select(Booking).where(Booking.car_id == car_id))
            .scalars()
            .all()
        )


async def add_booking(user_id, total_price, payment_status):
    async with async_session() as session:
        booking = Booking(
            user_id=user_id,
            car_id=None,
            start_date=datetime.now(),
            end_date=datetime.now(),
            total_price=total_price,
            payment_status=payment_status,
        )
        session.add(booking)
        await session.commit()
        return booking


async def get_bookings():
    async with async_session() as session:
        return await session.execute(select(Booking)).scalars().all()


async def get_booking(booking_id):
    async with async_session() as session:
        return await session.scalar(select(Booking).where(Booking.id == booking_id))


async def add_car(
    brand, model, car_type, description, price_per_day, image_url, session: AsyncSession
):
    car = Car(
        brand=brand,
        model=model,
        type=car_type,
        description=description,
        price_per_day=price_per_day,
        image_url=image_url,
    )
    session.add(car)
    await session.commit()
    return car


async def delete_car(car_id, session: AsyncSession):
    car = await session.get(Car, car_id)
    if car:
        await session.delete(car)
        await session.commit()
        return True
    return False


async def get_all_cars(session: AsyncSession):
    result = await session.scalars(select(Car))
    return result.all()


async def get_car_by_id(car_id, session: AsyncSession):
    return await session.get(Car, car_id)


async def get_all_bookings(session: AsyncSession):
    result = await session.scalars(select(Booking))
    return result.all()


async def get_booking_by_id(booking_id, session: AsyncSession):
    return await session.get(Booking, booking_id)


async def confirm_booking(booking_id, session: AsyncSession):
    booking = await session.get(Booking, booking_id)
    if booking:
        booking.payment_status = "confirmed"
        await session.commit()
        return True
    return False


async def cancel_booking(booking_id, session: AsyncSession):
    booking = await session.get(Booking, booking_id)
    if booking:
        booking.payment_status = "cancelled"
        await session.commit()
        return True
    return False
