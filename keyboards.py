from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

#Кнопки
button1=KeyboardButton("перечень товара")
button2=KeyboardButton("оформить заказ")
button3=KeyboardButton("контактные номера")

markup1=ReplyKeyboardMarkup(resize_keyboard=True).add(button1,button2,button3) #В ряд
