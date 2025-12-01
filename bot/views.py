import json
import traceback
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import telebot
from telebot import TeleBot, types
from telebot.types import ReplyKeyboardRemove
from datetime import datetime

from conf.settings import HOST, TELEGRAM_BOT_TOKEN

from .models import (
    TgUser, Menu, JobCategory, Location, Position, JobApplication, PageContent
)

bot = TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def back_button():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row("⬅️ Ortga")
    return kb


@csrf_exempt
def telegram_webhook(request):
    try:
        if request.method == 'POST':
            update_data = request.body.decode('utf-8')
            update_json = json.loads(update_data)
            update = telebot.types.Update.de_json(update_json)

            if update.message:
                tg_user = update.message.from_user
                telegram_id = tg_user.id
                first_name = tg_user.first_name
                last_name = tg_user.last_name
                username = tg_user.username
                is_bot = tg_user.is_bot
                language_code = tg_user.language_code

                deleted = False

                tg_user_instance, _ = TgUser.objects.update_or_create(
                    telegram_id=telegram_id,
                    defaults={
                        'first_name': first_name,
                        'last_name': last_name,
                        'username': username,
                        'is_bot': is_bot,
                        'language_code': language_code,
                        'deleted': deleted,
                    }
                )

            try:
                if update.my_chat_member.new_chat_member.status == 'kicked':
                    telegram_id = update.my_chat_member.from_user.id
                    user = TgUser.objects.get(telegram_id=telegram_id)
                    user.deleted = True
                    user.save()
            except:
                pass

            bot.process_new_updates(
                [telebot.types.Update.de_json(request.body.decode("utf-8"))])

        return HttpResponse("ok")
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return HttpResponse("error")


@bot.message_handler(commands=['start'])
def send_main_menu(message):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Fetch all menus
    menus = list(Menu.objects.all())

    # Add buttons 2 per row
    row = []
    for i, menu in enumerate(menus, start=1):
        row.append(types.KeyboardButton(menu.title))
        if i % 2 == 0:  # every 2 buttons, add row to keyboard
            kb.row(*row)
            row = []

    # Add remaining button if odd number of menus
    if row:
        kb.row(*row)

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! Menyudan tanlang:",
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: True)
def menu_router(message):
    text = message.text

    # 🔍 Menu title bo‘yicha aniqlaymiz
    try:
        menu = Menu.objects.get(title=text)
    except Menu.DoesNotExist:
        return bot.send_message(message.chat.id, "Menyudan tanlang.")

    # === ABOUT ===
    if menu.key == "about":
        return send_page_content(message.chat.id, "about")

    # === CONTACT ===
    if menu.key == "contact":
        return send_page_content(message.chat.id, "contact")

    # === JOBS ===
    if menu.key == "jobs":
        return send_job_categories(message)


def send_page_content(chat_id, key):
    try:
        page = PageContent.objects.get(key=key)
        if page.image:
            # Send image with caption, allow HTML formatting
            bot.send_photo(
                chat_id,
                page.image.open(),
                caption=page.text,
                parse_mode="HTML"  # enables rich formatting
            )
        else:
            # Send plain text with HTML formatting (links, emojis, bold, etc.)
            bot.send_message(
                chat_id,
                page.text,
                parse_mode="HTML",
                disable_web_page_preview=False  # enable link preview
            )
    except PageContent.DoesNotExist:
        bot.send_message(chat_id, "Ma'lumot topilmadi.")



# ================================
#  Step 1 — Show job categories
# ================================
def send_job_categories(message):
    kb = types.InlineKeyboardMarkup()
    categories = list(JobCategory.objects.all())

    row = []
    for i, cat in enumerate(categories, start=1):
        row.append(types.InlineKeyboardButton(
            f"{cat.icon or ''} {cat.name}",
            callback_data=f"cat_{cat.id}"
        ))
        if i % 2 == 0:  # 2 buttons per row
            kb.row(*row)
            row = []
    if row:  # remaining button if odd
        kb.row(*row)

    bot.send_message(message.chat.id, "Bo‘limni tanlang:", reply_markup=kb)


# ================================
#  Step 2 — Show locations
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
def show_locations(call):
    cat_id = call.data.split("_")[1]
    kb = types.InlineKeyboardMarkup()
    locations = list(Location.objects.filter(category_id=cat_id))

    row = []
    for i, loc in enumerate(locations, start=1):
        row.append(types.InlineKeyboardButton(
            loc.name, callback_data=f"loc_{loc.id}"
        ))
        if i % 2 == 0:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)

    # ⬅️ ADD INLINE BACK BUTTON
    kb.row(types.InlineKeyboardButton("⬅️ Ortga", callback_data=f"back_cat"))

    bot.edit_message_text(
        "Joyni tanlang:",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=kb
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_cat")
def back_to_categories(call):
    send_job_categories(call.message)

# ================================
#  Step 3 — Create JobApplication
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("loc_"))
def start_application(call):
    loc_id = call.data.split("_")[1]
    location = Location.objects.get(id=loc_id)
    user = TgUser.objects.get(telegram_id=call.from_user.id)

    # Hide main keyboard
    bot.send_message(call.message.chat.id, "Ariza boshlanmoqda...", reply_markup=ReplyKeyboardRemove())

    # Send location if exists
    if location.latitude and location.longitude:
        bot.send_location(call.message.chat.id, latitude=location.latitude, longitude=location.longitude)

    # Create empty application
    application = JobApplication.objects.create(
        user=user,
        location=location,
        birth_date="2000-01-01",
        region="",
        phone_number="-",
    )

    bot.send_message(call.message.chat.id, "Tug‘ilgan sana (YYYY-MM-DD):", reply_markup=back_button())
    bot.register_next_step_handler(call.message, step_birth_date, application.id)


# ================================
#  Step — birth date
# ================================

def parse_date(date_text):
    formats = ['%d-%m-%Y', '%d.%m.%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_text, fmt).date()
        except ValueError:
            continue
    return None


def step_birth_date(message, app_id):
    if message.text == "⬅️ Ortga":
        return send_main_menu(message)  # FIX → goes to main menu

    app = JobApplication.objects.get(id=app_id)

    date_val = parse_date(message.text)
    if not date_val:
        bot.send_message(message.chat.id, "Noto‘g‘ri format!")
        return bot.register_next_step_handler(message, step_birth_date, app_id)

    app.birth_date = date_val
    app.save()

    bot.send_message(message.chat.id, "Viloyat:", reply_markup=back_button())
    bot.register_next_step_handler(message, step_region, app_id)



def step_region(message, app_id):
    if message.text == "⬅️ Ortga":
        bot.send_message(message.chat.id, "Tug‘ilgan sana:", reply_markup=back_button())
        return bot.register_next_step_handler(message, step_birth_date, app_id)

    app = JobApplication.objects.get(id=app_id)
    app.region = message.text
    app.save()

    bot.send_message(message.chat.id, "Tuman:", reply_markup=back_button())
    bot.register_next_step_handler(message, step_district, app_id)


def step_district(message, app_id):
    if message.text == "⬅️ Ortga":
        bot.send_message(message.chat.id, "Viloyat:", reply_markup=back_button())
        return bot.register_next_step_handler(message, step_region, app_id)

    app = JobApplication.objects.get(id=app_id)
    app.district = message.text
    app.save()

    kb = types.InlineKeyboardMarkup()
    positions = list(Position.objects.filter(category=app.location.category))

    row = []
    for i, pos in enumerate(positions, start=1):
        row.append(types.InlineKeyboardButton(
            pos.title, callback_data=f"pos_{pos.id}_{app_id}"
        ))
        if i % 2 == 0:
            kb.row(*row)
            row = []
    if row:
        kb.row(*row)

    bot.send_message(message.chat.id, "Lavozimni tanlang:", reply_markup=kb)


# ================================
#  Position selection
# ================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("pos_"))
def select_position(call):
    _, pos_id, app_id = call.data.split("_")

    app = JobApplication.objects.get(id=app_id)
    app.position_id = pos_id
    app.save()

    bot.send_message(call.message.chat.id, "Oldingi ish joyi:")
    bot.register_next_step_handler(call.message, step_prev_job, app_id)


def step_prev_job(message, app_id):
    if message.text == "⬅️ Ortga":
        bot.send_message(message.chat.id, "Tuman:", reply_markup=back_button())
        return bot.register_next_step_handler(message, step_district, app_id)

    app = JobApplication.objects.get(id=app_id)
    app.previous_job = message.text
    app.save()

    bot.send_message(message.chat.id, "Telefon raqam:")
    bot.register_next_step_handler(message, step_phone, app_id)


def step_phone(message, app_id):
    if message.text == "⬅️ Ortga":
        bot.send_message(message.chat.id, "Oldingi ish joyi:", reply_markup=back_button())
        return bot.register_next_step_handler(message, step_prev_job, app_id)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Fetch all menus
    menus = list(Menu.objects.all())

    # Add buttons 2 per row
    row = []
    for i, menu in enumerate(menus, start=1):
        row.append(types.KeyboardButton(menu.title))
        if i % 2 == 0:  # every 2 buttons, add row to keyboard
            kb.row(*row)
            row = []

    # Add remaining button if odd number of menus
    if row:
        kb.row(*row)
    app = JobApplication.objects.get(id=app_id)
    app.phone_number = message.text
    app.save()

    bot.send_message(message.chat.id, "Ariza qabul qilindi. Rahmat!", reply_markup=kb)


bot.set_webhook(url="https://" + HOST + "/webhook/")