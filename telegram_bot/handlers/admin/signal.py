from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import ChatNotFound, CantInitiateConversation
from .states import _ProfileStatesGroup
from ...bot_config import dp, bot, ADMIN
from database import Database
from ...keyboards import get_mail_lists_kb



edit_text = ''
mail_lists = []


@dp.callback_query_handler(lambda callback: callback.data == 'edit_bet_signal')
async def edit_bet_signal(callback: types.CallbackQuery) -> None:
    await callback.answer('Отправьте отредактированный текст')
    await _ProfileStatesGroup.get_edit_message.set()
    await bot.send_message(
        chat_id=ADMIN, text='Отправьте отредактированный текст'
    )


@dp.message_handler(state=_ProfileStatesGroup.get_edit_message)
async def get_edit_message(message: types.Message) -> None:
    global edit_text
    edit_text = message.text

    db = Database()

    await _ProfileStatesGroup.get_mail_lists.set()
    await message.answer(
        '✅Текст изменен✅\nВыбирайте списки, если хотите закончить, жмите кнопку <b>стоп</b>',
        parse_mode='HTML',
        reply_markup=get_mail_lists_kb(
            mail_lists=db.get_all_table_elements(
                query='SELECT list_name FROM mail_lists;', element='list_name'
            ),
            stop='стоп'
        )
    )


@dp.message_handler(Text(equals='заново'), state=_ProfileStatesGroup.get_mail_lists)
async def again(message: types.Message) -> None:
    global mail_lists
    mail_lists.clear()
    await message.answer('Выбирайте списки сначала')

    
@dp.message_handler(Text(equals='стоп'), state=_ProfileStatesGroup.get_mail_lists)
async def mailing(message: types.Message, state=FSMContext) -> None:
    global edit_text, mail_lists

    if not mail_lists:
        await message.answer('Вы не выбрали ни одного списка, выберите хотя бы один')
    else:
        await state.finish()
        db = Database()
        users = db.get_chat_id_by_subscribes(mail_lists)

        for user in users:
            try:
                await bot.send_message(
                    chat_id=int(user), text=edit_text
                )
            except (ChatNotFound, CantInitiateConversation):
                username = db.get_one_data_cell(
                    f"SELECT nickname FROM subscribers WHERE chat_id = '{user}';"
                )
                await message.answer(
                    f'@{username} не создал чат с ботом'
                )

        edit_text = ''
        mail_lists.clear()

        await message.answer(
            '✅Сигнал отправлен пользователям',
            reply_markup=types.ReplyKeyboardRemove()
        )


@dp.message_handler(state=_ProfileStatesGroup.get_mail_lists)
async def add_mail_list(message: types.Message) -> None:
    global mail_lists
    mail_lists.append(message.text)

    await message.answer(
        "Список добавлен\nЖмите на название списка рассылки или кнопку <b>стоп</b>",
        parse_mode='HTML'
    )
    

@dp.callback_query_handler(lambda callback: callback.data == 'send_bet_signal')
async def send_bet_signal(callback: types.CallbackQuery) -> None:
    global edit_text
    edit_text = callback.message.text

    db = Database()

    await _ProfileStatesGroup.get_mail_lists.set()
    await bot.send_message(
        chat_id=ADMIN,
        text='Выбирайте списки, если хотите закончить, жмите кнопку <b>стоп</b>',
        parse_mode='HTML',
        reply_markup=get_mail_lists_kb(
            mail_lists=db.get_all_table_elements(
                query='SELECT list_name FROM mail_lists;', element='list_name'
            ),
            stop='стоп'
        )
    )