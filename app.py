from aiogram import Bot, Dispatcher, executor, types


from emoji import emojize 
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove

import config
from product import PRODUCT_DICT #Список продуктов вынесен в отдельный файл со словарем
import keyboards # Импортируем кнопки

storage = MemoryStorage() #Добавил хранилище, чтоб без ошибок отрабатывала машина состояний

# Токен бота
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=storage)

roma_id=config.EMPLOYEE_ID # message_id сотрудника, куда отправится сообщение с заказом

# Вычисляем макс. длину строк для списка продуктов (чтоб к почти табличному виду привести)
product_list = []
price_list = []
for brand, items in PRODUCT_DICT['product'].items(): # цикл по бренду, продукту
    for name, price in items.items():   # цикл по наименованию, ценнику
        product_list.append(name)       # список наименований
        price_list.append(str(price))   # список цен
max_len_1 = max(map(len, product_list)) # макс. длина 1 столбца
max_len_2 = max(map(len, price_list))   # макс. длина 2 столбца
max_len = max_len_1 + max_len_2 + 10    # макс. длина таблицы

# формируем список продуктов с норм табуляцией
products = ''
for brand, items in PRODUCT_DICT['product'].items():
    #text = text + "<pre>{:_^{max_len}}</pre>".format(brand,max_len=max_len) + '\n' ## Здесь были заголовки с наименованием бренда
    for name, price in items.items():
        products = products + "<pre>{:<{max_len1}} - {} руб. </pre>".format(name, price, max_len1=max_len_1) + '\n' 
    products = products + "<pre>{:-^{max_len}}</pre>".format('',max_len=max_len) + '\n' #это пунктирная черта под каждым блоком (брендом)
products = products + "<pre>{:<{max_len1}} - {} руб. </pre>".format(list(PRODUCT_DICT['delivery'].items())[0][0],
                                                                    list(PRODUCT_DICT['delivery'].items())[0][1],
                                                                    max_len1=max_len_1) + '\n' #инфа о доставке



sticker="CAACAgIAAxkBAAEBBUJfBbfswT2j_HSjg0k8pqS_SLEYcQACXgkAAnlc4gnVx7KyK5sdjBoE" # Стикер путина (можно вынести в отдельный файл, бд)




# Класс состояний для диалога
class order_dialog(StatesGroup):
    name = State()
    phone = State()
    order = State()


# Инициализируем клавиатуру
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_sticker(message.from_user.id, f"{sticker}")  # стикер
    await bot.send_message(message.from_user.id, "Здравствуйте!\nДля выбора команд, воспользуйтесь интерактивной клавиатурой", reply_markup=keyboards.markup1)

# Для обработки сообщений
@dp.message_handler()
async def message (message: types.Message, state: FSMContext):

   #Если пользователь написал привет
    if message.text.lower()=="привет":
        await bot.send_sticker(message.from_user.id, f"{ sticker}") #Отвечаем стикером
        await bot.send_message(message.from_user.id, "Для выбора команд, воспользуйтесь интерактивной клавиатурой")

        # Оформление заказа
    if message.text.lower() == "оформить заказ":
        await order_dialog.name.set()  # вот мы указали начало работы состояний для последующего диалога
        await bot.send_message(message.from_user.id, "Напишите, пожалуйста, имя, по которому к вам можно обращаться.",
                           reply_markup=ReplyKeyboardRemove()) #удаляем клавиатуру

    # Контактные номера
    elif message.text.lower() == "контактные номера":
        # Курьеры
        Name1="Роман"
        Contacts1="8-999-222-55-66"
        Name2 = "Константин"
        Contacts2 = "8-999-222-11-11"
        await bot.send_message(message.from_user.id,f"{Name1}\n{Contacts1}\n{Name2}\n{Contacts2}")
    # перечень товара
    elif message.text.lower()=="перечень товара":
        await bot.send_message(message.from_user.id, products, parse_mode='HTML') # products - текстовое поле со списком товаров. parse_mode='HTML'!

    else:
       await bot.send_sticker(message.from_user.id, f"{sticker}")  # Отвечаем стикером
       await bot.send_message(message.from_user.id,"Для выбора команд, воспользуйтесь интерактивной клавиатурой",reply_markup=keyboards.markup1)


# Обработка диалога для оформления заказа, получаем ответ, указывая состояние и передавая сообщение пользователя
@dp.message_handler(state=order_dialog.name)
async def message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text # сюда пишется ответ пользователя
    await order_dialog.next() # выбирается следующее состояние
    await message.reply("Напишите, пожалуйста, номер вашего телефона (или user_name), чтобы мы могли с вами связаться.")

@dp.message_handler(state=order_dialog.phone)
async def message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    await order_dialog.next()
    await message.reply("Напишите, пожалуйста, что вы хотите заказать.")

# Отправка данных сотруднику
@dp.message_handler(state=order_dialog.order)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        await bot.send_message(
            roma_id,
            data['name'] + '\n' + data['phone'] + '\n' + data['text'],
            parse_mode='HTML',
        )
        await bot.send_message(message.from_user.id, "Спасибо за ваш заказ! Наш сотрудник скоро свяжется с вами!",
                               reply_markup=keyboards.markup1) # возвращаем кнопки
    # Finish conversation
    await state.finish()  # закончили работать с сотояниями


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


