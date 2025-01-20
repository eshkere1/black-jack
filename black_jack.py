import requests
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
import os
from dotenv import load_dotenv


def start(update: Update, context: CallbackContext) -> None:
    deck_id = create_deck()
    context.user_data['deck_id'] = deck_id 
    context.user_data['player_cards'] = draw_cards(deck_id)
    context.user_data['dealer_cards'] = draw_cards(deck_id, 1) 
    keyboard = [
        [InlineKeyboardButton("Да", callback_data='yes')],
        [InlineKeyboardButton("Нет", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        "Привет! Сыграем в black jack?",
        reply_markup=reply_markup
    )


def start_game(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    deck_id = context.user_data.get('deck_id')
    player_cards = context.user_data.get('player_cards', [])
    dealer_cards = context.user_data.get('dealer_cards', [])
    if query.data == 'yes':
        query.edit_message_text(text="Начинаем игру!")
        for card in player_cards:
            context.bot.send_photo(chat_id=query.message.chat_id, photo=card['image'], caption=f"{card['value']} {card['suit']}")
        your_cards_text = f"Ваши карты: (Сумма: {total_value(player_cards)})"
        context.bot.send_message(chat_id=query.message.chat_id, text=your_cards_text)
        dealer_card = dealer_cards[0]
        context.bot.send_photo(chat_id=query.message.chat_id, photo=dealer_card['image'], caption=f"{dealer_card['value']} {dealer_card['suit']}")
        dealer_cards_text = f"Карты дилера: (Сумма: {total_value(dealer_cards)})"
        context.bot.send_message(chat_id=query.message.chat_id, text=dealer_cards_text)
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='take_card')],
            [InlineKeyboardButton("Нет", callback_data='stand')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=query.message.chat_id, text="Хотите взять карту?", reply_markup=reply_markup)
    elif query.data == 'no':
        query.edit_message_text(text="Ладно")    
        context.bot.send_message(chat_id=query.message.chat_id, text="До свидания!")
    elif query.data == 'take_card':
        new_card = draw_cards(deck_id, count=1)[0]
        player_cards.append(new_card)
        context.user_data['player_cards'] = player_cards
        context.bot.send_photo(chat_id=query.message.chat_id, photo=new_card['image'], caption=f"Вы получили карту: {new_card['value']} {new_card['suit']}")
        total = total_value(player_cards)
        player_cards_text = "Ваши карты:\n" + "\n".join(
            [f"{card['value']} {card['suit']}" for card in player_cards]
        )
        context.bot.send_message(chat_id=query.message.chat_id, text=f"{player_cards_text}\n(Сумма: {total})")
        if total > 21:
            context.bot.send_message(chat_id=query.message.chat_id, text="Вы проиграли (перебор)")
        elif total == 21:
            context.bot.send_message(chat_id=query.message.chat_id, text="Вы победили!")
        else:
            keyboard = [
                [InlineKeyboardButton("Да", callback_data='take_card')],
                [InlineKeyboardButton("Нет", callback_data='stand')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(chat_id=query.message.chat_id, text="Хотите взять карту?", reply_markup=reply_markup)
    elif query.data == 'stand':
        while total_value(dealer_cards) < 17:
            new_card = draw_cards(deck_id, count=1)[0]
            dealer_cards.append(new_card)
        while total_value(dealer_cards) > 17 and total_value(player_cards) > total_value(dealer_cards):
            new_card = draw_cards(deck_id, count=1)[0]
            dealer_cards.append(new_card)
        context.user_data['dealer_cards'] = dealer_cards  # Обновляем карты дилера
        for card in dealer_cards:
            context.bot.send_photo(chat_id=query.message.chat_id, photo=card['image'], caption=f"{card['value']} {card['suit']}")
        dealer_total = total_value(dealer_cards)
        dealer_cards_text = "Карты дилера:\n" + "\n".join(
            [f"{card['value']} {card['suit']}" for card in dealer_cards]
        )
        player_total = total_value(player_cards)
        context.bot.send_message(chat_id=query.message.chat_id, text=f"{dealer_cards_text}\n(Сумма: {dealer_total})")
        result = determine_winner(player_total, dealer_total)
        context.bot.send_message(chat_id=query.message.chat_id, text=result)


def create_deck():
    response = requests.get("https://deckofcardsapi.com/api/deck/new/shuffle/?deck_count=1")
    return response.json()['deck_id']


def draw_cards(deck_id, count=2):
    response = requests.get(f"https://deckofcardsapi.com/api/deck/{deck_id}/draw/?count={count}")
    return response.json()['cards']


def card_value(card):
    values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10,
              'JACK': 10, 'QUEEN': 10, 'KING': 10, 'ACE': 11}
    return values.get(card['value'], 0)


def total_value(cards):
    total = sum(card_value(card) for card in cards)
    aces = sum(1 for card in cards if card['value'] == 'ACE')
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def determine_winner(player_total, dealer_total):
    if player_total > 21:
        return "Вы проиграли (перебор)"
    if dealer_total > 21:
        return "Дилер проиграл (перебор)"
    if player_total > dealer_total:
        return "Вы победили!"
    elif player_total < dealer_total:
        return "Дилер победил!"
    else:
        return "Ничья!"


if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.environ["TELEGRAM_KEY"]
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(start_game))
    updater.start_polling()
    updater.idle()
