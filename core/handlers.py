from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, LabeledPrice, ContentType
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram import types
from bot import bot
import config
import core.keyboards as kb
import core.database.requests as rq
from datetime import datetime

router = Router()
PRICE = LabeledPrice(label="Подписка на 1 месяц", amount=500 * 100)

class Register(StatesGroup):
    name = State()
    number = State()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = await rq.set_user(message.from_user.id, message.from_user.first_name)
    if user:
        await message.answer("Добро пожаловать в Car booking!", reply_markup=kb.main)
    else:
        await message.answer("Вы уже зарегистрированы!")


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("I'm here to help you.")


@router.message(F.text == "Каталог")
async def catalog(message: Message):
    cars = await rq.get_cars()
    if cars:
        car_names = "\n".join([f"{car.brand} {car.model}" for car in cars])
        await message.answer(f"Доступные машины:\n{car_names}", reply_markup=kb.catalog)
    else:
        await message.answer("Извините, машин нет в наличии.", reply_markup=kb.catalog)


@router.callback_query(F.data == "ff")
async def ff(callback: CallbackQuery):
    await callback.answer("Вы выбрали категорию")
    await callback.message.answer("ff ТУДА")


@router.message(F.text == "Регистрация")
async def register(message: Message, state: FSMContext):
    await state.set_state(Register.name)
    await message.answer("Введите ваше имя")


@router.message(Register.name)
async def register_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(Register.number)
    await message.answer("Введите ваш номер телефона", reply_markup=kb.get_number)


@router.message(Register.number, F.contact)
async def register_number(message: Message, state: FSMContext):
    if message.contact and message.contact.phone_number:
        await state.update_data(number=message.contact.phone_number)
        data = await state.get_data()
        await message.answer(f'Ваше имя: {data["name"]}\nНомер: {data["number"]}')
        await state.clear()
    else:
        await message.answer(
            "Номер телефона не был передан. Пожалуйста, отправьте контакт."
        )


@router.message(F.text == "buy")
async def buy(message: types.Message):
    if config.PAYMENTS_TOKEN.split(":")[1] == "TEST":
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(
        message.chat.id,
        title="Подписка на бота",
        description="Активация подписки на бота на 1 месяц",
        provider_token=config.PAYMENTS_TOKEN,
        currency="rub",
        photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
        photo_width=416,
        photo_height=234,
        photo_size=416,
        is_flexible=False,
        prices=[PRICE],
        start_parameter="one-month-subscription",
        payload="test-invoice-payload",
    )


@router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@router.message(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    user_id = message.from_user.id
    amount = message.successful_payment.total_amount / 100
    payment_status = "completed"
    booking = await rq.add_booking(user_id, amount, payment_status)

    await bot.send_message(
        message.chat.id,
        f"Платёж на сумму {amount} {message.successful_payment.currency} прошел успешно!",
    )
