from aiogram import types
from aiogram.dispatcher import FSMContext
from .states import _ProfileStatesGroup
from ...bot_config import dp, bot, ADMIN
from ...keyboards import admin_main_ikb, get_mail_lists_kb, users_work_ikb
from database import Database



@dp.message_handler(commands=['begin', 'main_menu'], user_id=ADMIN)
async def begin_work(message: types.Message) -> None:
    await message.answer(
        text='📝📝<b>Главное меню</b>📝📝',
        reply_markup=admin_main_ikb, parse_mode='HTML'
    )


@dp.callback_query_handler(lambda callback: callback.data == 'add_mail_list')
async def add_mail_list(callback: types.CallbackQuery) -> None:
    await callback.answer('Введите название списка')
    await _ProfileStatesGroup.get_mail_list_name.set()
    await bot.send_message(
        chat_id=ADMIN, text='Введите название списка'
    )


@dp.message_handler(state=_ProfileStatesGroup.get_mail_list_name)
async def get_list_name(message: types.Message, state: FSMContext) -> None:
    mail_list = message.text
    db = Database()

    mail_lists = db.get_all_table_elements(
        query='SELECT list_name FROM mail_lists',
        element='list_name'
    )
    if mail_list in mail_lists:
        await message.reply(
            '🔴🔴Список с таким названием уже есть, введите другое название🔴🔴'
        )
    else:
        await state.finish()
        db.action(
            f"INSERT INTO mail_lists (list_name) VALUES ('{mail_list}');"
        )
        await message.answer('✅Список расслыки добавлен')


@dp.callback_query_handler(lambda callback: callback.data == 'view_mail_lists')
async def view_mail_lists(callback: types.CallbackQuery) -> None:
    db = Database()
    data = db.get_all_table_elements(
        query='SELECT list_name FROM mail_lists;', element='list_name'
    )

    msg_text = 'Списки:\n'
    for list_ in data:
        msg_text += f'{list_}\n'

    await callback.answer('Списки рассылки')
    await bot.send_message(
        chat_id=ADMIN, text=msg_text
    )


@dp.callback_query_handler(lambda callback: callback.data == 'remove_mail_list')
async def get_del_mail_list(callback: types.CallbackQuery) -> None:
    db = Database()
    mail_lists = db.get_all_table_elements(
        query='SELECT list_name FROM mail_lists;', element='list_name'
    )
    await callback.answer('Введите название списка')
    await _ProfileStatesGroup.get_delete_mail_list.set()
    await bot.send_message(
        chat_id=ADMIN, text='Введите название списка, который хотите удалить',
        reply_markup=get_mail_lists_kb(mail_lists)
    )


@dp.message_handler(state=_ProfileStatesGroup.get_delete_mail_list)
async def remove_mail_list(message: types.Message, state: FSMContext) -> None:
    mail_list = message.text
    db = Database()

    mail_lists = db.get_all_table_elements(
        query='SELECT list_name FROM mail_lists;', element='list_name'
    )

    if mail_list not in mail_lists:
        await message.reply(
            '🔴🔴Списка с таким названием в базе нет, введите другое название🔴🔴'
        )
    else:
        await state.finish()

        mail_list_id = db.get_one_data_cell(
            f"SELECT id FROM mail_lists WHERE list_name = '{mail_list}';",
            column='id'
        )
        db.action(
            f"DELETE FROM mail_lists WHERE list_name = '{mail_list}';"
        )
        db.action(
            f"DELETE FROM bundle WHERE list_id = {mail_list_id};"
        )

        await message.answer(
            '✅Список расслыки удален', reply_markup=types.ReplyKeyboardRemove()
        )


@dp.callback_query_handler(lambda callback: callback.data == 'view_users')
async def view_users(callback: types.CallbackQuery) -> None:
    db = Database()
    data = db.get_users_full_data()

    msg_text = 'Юзеры:\n'
    for user_id, value in data.items():
        username = list(value.keys())[0]
        string = f"<em>{user_id}</em> - <b>{username}</b>\nПодписки:"

        mail_list = value.get(username)
        for item in mail_list:
            string += f" {item}"
        msg_text += f"{string}\n"

    await callback.answer('Список юзеров')
    await bot.send_message(
        chat_id=ADMIN, text=msg_text,
        parse_mode='HTML', reply_markup=users_work_ikb
    )