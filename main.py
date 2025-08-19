import telebot
from telebot import types
import json
import os
owner = '@altaee_z' #يوزر المالك
#كلمة السر لتأكيد اعادة ضبط المصنع
FACTORY_RESET_PASSWORD = "ali"
#اسم البوت
bot_name = 'بوت الاستثمار العراقي'   
TOKEN = "8413470357:AAF-Y-YrM8TaZtaHjee-I_REjVXqsFZLBwo" #توكنك
ADMIN_ID = "6454550864" #ايدي الادمن
ADMINo_ID = 6454550864  #ايديك حتى تطلع عندك لوحة المتصدرين بالنقاط .

bot = telebot.TeleBot(TOKEN)
import threading
import time

def auto_add_points():
    while True:
        try:
            config = load_config()
            if not config.get("auto_send_enabled", True):
                time.sleep(5)
                continue

            with open("a.json", "r") as f:
                data = json.load(f)

            users = load_users()

            for uid, pts in data.items():
                if uid in users:
                    users[uid]["points"] += pts
                    bot.send_message(uid, f"تمت إضافة {pts} نقطة إلى رصيدك.\nرصيدك الحالي: {users[uid]['points']}\nتصنيفك: {get_rank(users[uid]['points'])}")

            save_users(users)

        except Exception as e:
            print("خطأ في التحديث التلقائي:", e)

        time.sleep(5)
threading.Thread(target=auto_add_points, daemon=True).start()        
def get_rank(points):
    if points < 100:
        return "مبتدئ"
    elif points < 1000:
        return "متوسط"
    else:
        return "محترف"
#رأي المستخدم عن البوت
@bot.message_handler(commands=["poll"])
def poll(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return
    poll_question = "عزيزي المستخدم يرجى منك تقييم هذا البوت من حيث الاستخدام والخدمات المتوفرة 🤍"
    poll_options = ["جيد🔹", "متوسط🔸", "سيء🔺"]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for option in poll_options:
        markup.add(option)
    bot.send_message(message.chat.id, poll_question, reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["جيد🔹", "متوسط🔸", "سيء🔺"])
def handle_poll_answer(message):
    response = message.text
    user_id = str(message.from_user.id)
    username = message.from_user.username if message.from_user.username else "غير معروف"
    name = message.from_user.first_name

    # إرسال التقرير للمشرف
    bot.send_message(ADMIN_ID, f"تم التصويت: {response} من:\n"
                               f"الاسم: {name}\n"
                               f"المستخدم: @{username}\n"
                               f"المعرف: {user_id}")

    # رسالة الشكر
    bot.send_message(message.chat.id, f"شكراً لتصويتك! لقد اخترت: {response}")

    # الرجوع للقائمة الرئيسية تلقائياً
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        return

    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add("🔘 عرض السلع 🔘")
    reply_markup.add("🎁 الهدية اليومية")
    reply_markup.add("مشترياتي")
    reply_markup.add("🕵️ السوق السري")
    reply_markup.add("تجربة الكوبون")
    reply_markup.add("الدعم الفني")
    reply_markup.add("من نحن؟")
    reply_markup.add("الاسئلة الشائعة")
    reply_markup.add("لصناعة بوت مماثل")
    bot.send_message(message.chat.id, "تم الرجوع للقائمة الرئيسية.", reply_markup=reply_markup)
    #لعرض قائمة المستخدمين بملف txt
@bot.message_handler(commands=['userss'])
def send_users_txt(message):
    users = load_users()
    file_content = "قائمة المستخدمين:\n\n"

    for uid, data in users.items():
        name = data.get('name', 'غير معروف')
        username = f"@{data.get('username')}" if data.get('username') else "لا يوجد"
        points = data.get('points', 0)
        file_content += f"الاسم: {name}\nالمعرف: {username}\nالآيدي: {uid}\nالنقاط: {points}\n\n"

    with open("users_list.txt", "w", encoding="utf-8") as f:
        f.write(file_content)

    with open("users_list.txt", "rb") as f:
        bot.send_document(message.chat.id, f)
        
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

if not os.path.exists("products.json"):
    with open("products.json", "w") as f:
        json.dump({}, f)

def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_products():
    with open("products.json", "r") as f:
        return json.load(f)

def save_products(products):
    with open("products.json", "w") as f:
        json.dump(products, f)
##
##
from datetime import datetime

CHANNEL_ID = "@my00002"  #قناة الاشعارات
CHANNEL_ID2 = "@Ali_Altaee2" #قناة الشراء
from datetime import datetime, timedelta
##
#رسالة البدء
@bot.message_handler(commands=['start'])
def start(message):
    # التحقق من الحظر
    user_id = str(message.from_user.id)
    users = load_users()
    if users.get(user_id, {}).get("banned", False):
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return

    # التحقق من حالة البوت
    status = load_bot_status()
    if not status.get("active", True):
        bot.send_message(message.chat.id, f"❌ البوت متوقف مؤقتاً.\nالسبب: {status.get('reason', 'غير معروف')}\nيعود للعمل في: {status.get('resume_time', 'غير معروف')}")
        return

    user_id = str(message.from_user.id)
    users = load_users()

    # استخراج الإحالة من الرسالة (إن وُجدت)
    args = message.text.split()
    ref = args[1] if len(args) > 1 else None

    if user_id not in users:
        users[user_id] = {
            "name": message.from_user.first_name,
            "username": message.from_user.username,
            "points": 0,
            "purchases": 0,
            "referrals": 0,
            "banned": False,
            "role": "admin" if message.from_user.id == ADMIN_ID else "user",
            "last_claim": None
        }
        save_users(users)

        if ref and ref in users and ref != user_id:
            settings = load_edit()
            ref_points = settings.get("referral_points", 50)
            users[ref]["points"] += ref_points
            users[ref]["referrals"] += 1
            rank = get_rank(users[ref]["points"])
            update_user_rank(user_id)
            bot.send_message(ref, f"""ربحت {ref_points} نقطة من دعوة المستخدم {message.from_user.first_name}
تصنيفك الآن: {rank}
""")

        with open("users.json", "w") as f:
            json.dump(users, f)

        # إشعار للقناة
        name = message.from_user.first_name
        username = message.from_user.username or "لا يوجد"
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        notif_msg = f"مستخدم جديد دخل البوت\n\nالاسم: {name}\nالمعرف: @{username}\nالآيدي: {user_id}\nالتاريخ والوقت: {time_now}"
        bot.send_message(CHANNEL_ID, notif_msg)

    u = users[user_id]
    badge = get_badge(u)

    # تحقق من النقاط وتحقق من الحد المسبق
    check_milestones(user_id, u['points'])

    # الأزرار
    inline_markup = types.InlineKeyboardMarkup()
    inline_markup.add(
        types.InlineKeyboardButton("💬 الدعم الفني", url="https://t.me/altaee_z"),
        types.InlineKeyboardButton("📢 القناة", url="https://t.me/my00002")
    )

    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add("🔘 عرض السلع 🔘")
    reply_markup.add("🎁 الهدية اليومية")
    reply_markup.add("مشترياتي")
    reply_markup.add("🕵️ السوق السري")
    reply_markup.add("تجربة الكوبون")
    reply_markup.add("الدعم الفني")
    reply_markup.add("من نحن؟")
    reply_markup.add("الاسئلة الشائعة")
    reply_markup.add("لصناعة بوت مماثل")

    bot.send_message(message.chat.id, f"""
<b>✨ مرحباً {u['name']}!</b>

<b>📋 معلومات حسابك:</b>
<b>🆔 الآيدي:</b> <code>{user_id}</code>
<b>👤 الاسم:</b> {u['name']}
<b>🔎 المعرف:</b> @{u['username']}
<b>💰 رصيدك:</b> {u['points']} نقطة
<b>🛒 السلع المشتراة:</b> {u['purchases']}
<b>🤝 عدد الدعوات:</b> {u['referrals']}
<b>🎁 الهدايا اليومية:</b> {u.get("daily_gifts", 0)}

<b>🔗 رابط الدعوة الخاص بك:</b>
<code>https://t.me/{bot.get_me().username}?start={user_id}</code>

<b>🏅 شارتك:</b> {badge}

 للمزيد ارسل /help
 
<a href="https://t.me/altaee_z">⚙️ لصناعة بوت مماثل اضغط هنا</a>
""", 
reply_markup=inline_markup, parse_mode="HTML", disable_web_page_preview=True)
    bot.send_message(message.chat.id, "اختر أحد الأوامر:", reply_markup=reply_markup)


# دالة التحقق من النقاط وعند الوصول إلى الحد يتم إرسال التنبيه
def check_milestones(user_id, current_points):
    user_id = str(user_id)
    users = load_users()

    last_notified = users[user_id].get("last_milestone", 0)

    POINT_MILESTONES = [1000, 2000, 5000, 10000]

    for milestone in POINT_MILESTONES:
        if current_points >= milestone and milestone > last_notified:
            bot.send_message(user_id, f"🎉 مبروك! وصلت إلى {milestone} نقطة!")
            users[user_id]["last_milestone"] = milestone
            break

    save_users(users)


# السوق السري
hidden_market_items = [
    {"name": "بطاقة عشوائية", "price": 150},
    {"name": "رابط مميز", "price": 200},
    {"name": "هدية خاصة", "price": 300}
]
#زر الكوبون
@bot.message_handler(func=lambda m: m.text == "تجربة الكوبون")
def ask_for_coupon(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return    
    msg = bot.send_message(message.chat.id, "أرسل رمز الكوبون الذي تريد استخدامه:")
    bot.register_next_step_handler(msg, redeem_coupon_code)
def redeem_coupon_code(message):
    code = message.text.strip()
    user_id = str(message.from_user.id)
    users = load_users()
    coupons = load_coupons()

    if code in coupons:
        coupon = coupons[code]

        if user_id in coupon["used_by"]:
            bot.send_message(message.chat.id, "❌ لقد استخدمت هذا الكوبون من قبل.")
            return
        
        if len(coupon["used_by"]) >= coupon["max_uses"]:
            bot.send_message(message.chat.id, "❌ تم استهلاك الكوبون بالكامل.")
            return

        expire_time = datetime.strptime(coupon["expires_at"], "%Y-%m-%d %H:%M:%S")
        if datetime.now() > expire_time:
            bot.send_message(message.chat.id, "❌ انتهت صلاحية هذا الكوبون.")
            return

        users[user_id]["points"] += coupon["points"]
        coupon["used_by"].append(user_id)
        save_users(users)
        save_coupons(coupons)

        badge = get_badge(users[user_id])
        bot.send_message(message.chat.id, f"✅ تم تفعيل الكوبون!\nتمت إضافة {coupon['points']} نقطة.")

        bot.send_message(
            "@my00002",
            f"🎫 كوبون مستخدم!\n"
            f"الاسم: {message.from_user.first_name}\n"
            f"اليوزر: @{message.from_user.username or 'لا يوجد'}\n"
            f"الآيدي: {user_id}\n"
            f"النقاط المضافة: {coupon['points']}\n"
            f"الشارة: {badge}"
        )
    else:
        bot.send_message(message.chat.id, "❌ الكوبون غير صحيح.")    
#
def is_bot_active(message):
    status = load_bot_status()
    if not status.get("active", True):
        bot.send_message(
            message.chat.id,
            f"❌ البوت متوقف مؤقتاً.\nالسبب: {status.get('reason', 'غير معروف')}\nيعود للعمل في: {status.get('resume_time', 'غير معروف')}"
        )
        return False
    return True
    #
#السوق السري        
@bot.message_handler(func=lambda m: m.text == "🕵️ السوق السري")
def hidden_market(message):
    if not is_bot_active(message):
        return
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return

    u = users[user_id]
    badge = get_badge(u)

    # الشارات المسموح لها الدخول
    allowed_badges = ["مسوّق ذهبي", "أسطورة الدعوات"]

    if badge in allowed_badges:
        markup = types.InlineKeyboardMarkup()
        for item in hidden_market_items:
            button_text = f"{item['name']} - {item['price']} نقطة"
            callback_data = f"confirm_hidden_{item['name']}"
            markup.add(types.InlineKeyboardButton(button_text, callback_data=callback_data))

        bot.send_message(
            message.chat.id,
            "**مرحباً بك في السوق السري!**\n\nهنا فقط نخبة المستخدمين. استمتع بسلع نادرة وعروض مميزة!",
            parse_mode="Markdown",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "❌ عذراً، السوق السري مخصص فقط للي يمتلكون شارة:\n*مسوّق ذهبي* أو *أسطورة الدعوات*.",
            parse_mode="Markdown"
        )

# تأكيد الشراء
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_hidden_"))
def confirm_hidden_item(call):
    item_name = call.data.replace("confirm_hidden_", "")
    item = next((i for i in hidden_market_items if i["name"] == item_name), None)

    if not item:
        bot.answer_callback_query(call.id, "❌ السلعة غير موجودة.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ تأكيد الشراء", callback_data=f"buy_hidden_{item_name}"))
    markup.add(types.InlineKeyboardButton("❌ إلغاء", callback_data="cancel_hidden"))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"هل أنت متأكد أنك تريد شراء *{item_name}* بـ *{item['price']}* نقطة؟",
        parse_mode="Markdown",
        reply_markup=markup
    )

# تنفيذ الشراء
@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_hidden_"))
def handle_hidden_purchase(call):
    item_name = call.data.replace("buy_hidden_", "")  # استخراج اسم السلعة
    user_id = str(call.from_user.id)
    users = load_users()  # تحميل قائمة المستخدمين
    u = users[user_id]  # الحصول على معلومات المستخدم الحالي

    # البحث عن السلعة في قائمة السلع المخفية
    item = next((i for i in hidden_market_items if i["name"] == item_name), None)
    
    if item is None:
        bot.answer_callback_query(call.id, "❌ السلعة غير موجودة.")
        return

    if u["points"] < item["price"]:
        bot.edit_message_text(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id,
            text="❌ لا تملك نقاط كافية للشراء."
        )
        return

    # تنفيذ الشراء (تخفيض النقاط وتسجيل السلعة في مشتريات المستخدم)
    u["points"] -= item["price"]
    u.setdefault("purchased_items", []).append(item_name)
    save_users(users)  # حفظ التغييرات في ملف المستخدمين

    # تحديث الرسالة لإعلام المستخدم بالشراء الناجح
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"✅ تم شراء *{item_name}* بنجاح!\nرصيدك الحالي: *{u['points']}* نقطة.",
        parse_mode="Markdown"
    )

    # إرسال إشعار للقناة مع تفاصيل الشراء
    channel_id = "@my00002"  # غيره إلى معرف قناتك
    badge = get_badge(u)  # الحصول على الشارة
    bot.send_message(
        channel_id,
        f"🛒 اشترى المستخدم:\n"
        f"الاسم: {call.from_user.first_name}\n"
        f"الآيدي: `{user_id}`\n"
        f"السلعة: {item_name}\n"
        f"الشارة: {badge}",
        parse_mode="Markdown"
    )
# إلغاء الشراء
@bot.callback_query_handler(func=lambda call: call.data == "cancel_hidden")
def cancel_hidden_purchase(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ تم إلغاء العملية."
    )
 #الهدية اليومية   
@bot.message_handler(func=lambda m: m.text == "🎁 الهدية اليومية")
def claim_daily_gift(message):
    if not is_bot_active(message):
        return
    user_id = str(message.from_user.id)
    users = load_users()
    settings = load_edit()  # تحميل إعدادات النقاط

    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return

    u = users[user_id]
    rank = get_rank(u["points"])

    # تأكد من وجود العداد في ملف المستخدم
    if "daily_gifts" not in u:
        u["daily_gifts"] = 0  # إضافة العداد إذا لم يكن موجوداً

    if u["last_claim"] is None or datetime.now() - datetime.strptime(u["last_claim"], "%Y-%m-%d %H:%M:%S") > timedelta(days=1):
        # تحديد النقاط حسب الرتبة
        if rank == "VIP":
            gift_points = 20
        elif rank == "Partner":
            gift_points = 30
        else:
            gift_points = settings.get("daily_gift_points", 10)  # من ملف edit.json

        u["points"] += gift_points
        u["last_claim"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        u["daily_gifts"] += 1  # زيادة عدد مرات أخذ الهدية

        save_users(users)  # حفظ التغييرات في ملف users.json

        bot.send_message(message.chat.id, f"🎁 تهانينا!\nحصلت على هديتك اليومية: {gift_points} نقطة\nرتبتك: {rank}")
    else:
        last_claim_time = datetime.strptime(u["last_claim"], "%Y-%m-%d %H:%M:%S")
        time_remaining = timedelta(days=1) - (datetime.now() - last_claim_time)
        hours_left, remainder = divmod(time_remaining.seconds, 3600)
        minutes_left, _ = divmod(remainder, 60)

        bot.send_message(message.chat.id, f"⏳ لا يمكنك أخذ الهدية الآن.\nالوقت المتبقي: {hours_left} ساعة و {minutes_left} دقيقة.")
#زر المشتريات الخاصة بالعضو
@bot.message_handler(func=lambda m: m.text == "مشترياتي")
def show_purchases(message):
    if not is_bot_active(message):
        return
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return    
    users = load_users()
    user_id = str(message.from_user.id)

    purchases = users[user_id].get("purchases_list", [])
    if not purchases:
        bot.send_message(message.chat.id, "لم تقم بأي عملية شراء بعد.")
        return

    msg = "🧾 سجل مشترياتك:\n\n"
    for p in purchases:
        msg += f"- {p['item']} | {p['date']}\n"

    bot.send_message(message.chat.id, msg)
##
#زر عرض السلع        
@bot.message_handler(func=lambda m: m.text == "🔘 عرض السلع 🔘")
def buy_product(message):
    if not is_bot_active(message):
        return
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return    
    users = load_users()
    products = load_products()
    user_id = str(message.from_user.id)

    

    if not products:
        bot.send_message(message.chat.id, "لا توجد سلع حالياً.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name, data in products.items():
        markup.add(types.KeyboardButton(f"{name} - {data['price']} نقطة")) 
         # زر الرجوع       
    bot.send_message(message.chat.id, "اختر السلعة التي تريد شراءها:", reply_markup=markup.add("⬅️ رجوع للخلف") )
@bot.message_handler(func=lambda m: m.text == "⬅️ رجوع للخلف")
def back_to_menu(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id not in users or users[user_id]["banned"]:
        return

    u = users[user_id]

    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    reply_markup.add("🔘 عرض السلع 🔘")
    reply_markup.add("🎁 الهدية اليومية")
    reply_markup.add("مشترياتي")
    reply_markup.add("🕵️ السوق السري")
    reply_markup.add("تجربة الكوبون")
    reply_markup.add("الدعم الفني")
    reply_markup.add("من نحن؟")
    reply_markup.add("الاسئلة الشائعة")
    reply_markup.add("لصناعة بوت مماثل")

    bot.send_message(message.chat.id, "تم الرجوع للقائمة الرئيسية.", reply_markup=reply_markup)    
###
@bot.message_handler(func=lambda m: "-" in m.text)
def handle_purchase(message):
    users = load_users()
    products = load_products()
    user_id = str(message.from_user.id)

    item_name = message.text.split(" - ")[0]

    if item_name in products:
        price = products[item_name]["price"]
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ نعم", callback_data=f"confirm_buy:{item_name}"),
            types.InlineKeyboardButton("❌ لا", callback_data="cancel_buy")
        )
        bot.send_message(message.chat.id, f"هل تريد شراء {item_name} مقابل {price} نقطة؟", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "السلعة غير موجودة.")
###
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_buy") or call.data == "cancel_buy")
def confirm_purchase(call):
    users = load_users()
    products = load_products()
    user_id = str(call.from_user.id)

    if call.data == "cancel_buy":
        bot.edit_message_text("❌ تم إلغاء العملية.", call.message.chat.id, call.message.message_id)
        return

    item_name = call.data.split(":")[1]
    price = products[item_name]["price"]

    # التأكد من وجود المفتاح purchases_list
    if "purchases_list" not in users[user_id]:
        users[user_id]["purchases_list"] = []

    if users[user_id]["points"] >= price:
        users[user_id]["points"] -= price
        users[user_id]["purchases"] += 1
        users[user_id]["purchases_list"].append({
            "item": item_name,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_users(users)

        bot.edit_message_text(
            f"✅ تم شراء *{item_name}* بنجاح!\n"
            f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"رصيدك المتبقي: {users[user_id]['points']} نقطة.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )

        # إشعار للقناة
        bot.send_message(
            CHANNEL_ID2,
            f"""🛒 تم شراء سلعة جديدة:
السلعة: {item_name}
السعر: {price} نقطة
من: {users[user_id]['name']} (@{users[user_id]['username']})
الآيدي: {user_id}
📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        )
    else:
        bot.edit_message_text(
            "❌ رصيدك غير كافي لإتمام عملية الشراء.",
            call.message.chat.id,
            call.message.message_id
        )
#امر ارسال النقاط يدوياً         
@bot.message_handler(commands=['send'])
def send_points(message):
    if not is_bot_active(message):
        return
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return    
    # التأكد من أن المستخدم هو مرسل
    users = load_users()
    user_id = str(message.from_user.id)
    
    if users[user_id]["role"] != "sender" and user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "أنت لا تملك الصلاحية لإرسال النقاط.")
        return

    try:
        # استخراج الآيدي والنقاط من الأمر
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن تكون الصيغة: /send [آيدي المستخدم] [عدد النقاط].")
            return

        target_user_id = parts[1]
        points_to_send = int(parts[2])

        # التحقق من أن المستخدم المستهدف موجود
        if target_user_id not in users:
            bot.send_message(message.chat.id, "المستخدم غير موجود.")
            return

        # إرسال النقاط للمستخدم المستهدف مباشرة دون التحقق من رصيد المرسل
        users[target_user_id]["points"] += points_to_send
        save_users(users)

        bot.send_message(message.chat.id, f"تم إرسال {points_to_send} نقطة للمستخدم {target_user_id}.")
        bot.send_message(target_user_id, f"تم إضافة {points_to_send} نقطة إلى رصيدك من المرسل.")

    except ValueError:
        bot.send_message(message.chat.id, "حدث خطأ في تحويل النقاط إلى عدد صحيح. تأكد من إدخال رقم صالح للنقاط.")
        ##
        
        ##كشف بالايدي

@bot.message_handler(commands=['info'])
def info(message):
    if not is_bot_active(message):
        return
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return
    if users.get(user_id, {}).get("role") not in ["admin", "sender"] and user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "أنت لا تملك الصلاحية للوصول إلى هذه الميزة.")
        return
    try:
        # استخراج الآيدي من النص
        target_user_id = message.text.split()[1]
        
        # التأكد من أن المستخدم موجود
        if target_user_id not in users:
            bot.send_message(message.chat.id, "المستخدم غير موجود.")
            return

        target_user = users[target_user_id]
        u = users[user_id]
        badge = get_badge(u)
        
        # جمع معلومات المستخدم
        user_info = (
    f"📄 <b>معلومات المستخدم</b> <code>{target_user_id}</code>:\n"
    f"👤 <b>الاسم:</b> <code>{target_user.get('name', 'غير متوفر')}</code>\n"
    f"🔗 <b>اليوزر:</b> @{target_user.get('username', 'غير متوفر')}\n"
    f"🆔 <b>الآيدي:</b> <code>{target_user_id}</code>\n"
    f"💰 <b>النقاط:</b> <code>{target_user.get('points', 0)}</code>\n"
    f"🛍️ <b>السلع المشتراة:</b> <code>{', '.join(target_user.get('purchased_items', [])) or 'لا يوجد'}</code>\n"
    f"📨 <b>مشاركات رابط الدعوة:</b> <code>{target_user.get('referral_count', 0)}</code>\n"
    f"🎁 <b>عدد الهدايا اليومية:</b> <code>{target_user.get('daily_gifts', 0)}</code>\n"
    f"🏅 <b>شارتك:</b> <code>{badge}</code>"
)
        
        # إرسال التفاصيل للمستخدم
        bot.send_message(message.chat.id, user_info, parse_mode="HTML")

    except IndexError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يجب أن ترسل الأمر كالتالي: /info [آيدي المستخدم].")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ غير متوقع: {str(e)}")        
#امر ولوحة الادمن        
@bot.message_handler(commands=["admin"])
def admin_panel(message):
    user_id = str(message.from_user.id)
    users = load_users()
    if user_id not in users or users[user_id]["banned"]:
        bot.send_message(message.chat.id, "❌ لقد تم حظرك من استخدام هذا البوت.")
        return

    if user_id != ADMIN_ID and users.get(user_id, {}).get("role") != "admin":
        bot.send_message(message.chat.id, "❌ ليس لديك صلاحية الوصول إلى لوحة التحكم.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("إيقاف البوت", "تشغيل البوت")
    markup.add("🔒 حظر مستخدم", "🔓 إلغاء الحظر")
    markup.add("🆕 إضافة سلعة", "🗑 حذف سلعة")
    markup.add("🚫 إيقاف الإرسال", "✅ تفعيل الإرسال")
    markup.add("اضافة عداد","مسح عداد")
    markup.add("➕ تعيين نقاط الدعوة", "🎁 تعيين نقاط الهدية")
    markup.add("ازالة مرسل", "⬆️ رفع إلى مرسل")
    markup.add("➕ إرسال نقاط","خصم نقاط")
    markup.add("تصفير الكل")
    markup.add("اذاعة", "رفع ادمن")
    markup.add("📨 ارسال الى مستخدم")
    markup.add("🧼 تصفير الدعوة")
    markup.add("سجل الكوبون","انشاء كوبون")
    markup.add("📊 عرض الإحصائيات")
    markup.add("📋 عرض جميع الإعدادات")
    markup.add("إعادة ضبط المصنع")
     
    bot.send_message(message.chat.id, f"""<b>⚙️ لوحة التحكم - الأدمن</b>

مرحباً بك في لوحة التحكم الخاصة بالأدمن.

<b>📊 الأوامر المتاحة:</b>
• 🏆 لعرض المتصدرين بالنقاط: /top
• 📁 لعرض ملف الأعضاء: /userss
• ℹ️ لعرض معلومات مستخدم عن طريق الآيدي: /info
• 💸 لإرسال نقاط لمستخدم معين كـ مرسل: /send

<b>🆔 آيديك:</b> <code>{user_id}</code>
""", reply_markup=markup, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text in [ "🔒 حظر مستخدم", "🔓 إلغاء الحظر", "➕ إرسال نقاط", "⬆️ رفع إلى مرسل", "🆕 إضافة سلعة", "🗑 حذف سلعة", "📊 عرض الإحصائيات", "خصم نقاط", "اذاعة", "رفع ادمن","ازالة مرسل","تصفير الكل","سجل الكوبون","اضافة عداد","مسح عداد" ,"🚫 إيقاف الإرسال", "✅ تفعيل الإرسال","انشاء كوبون","إيقاف البوت", "تشغيل البوت","إعادة ضبط المصنع","➕ تعيين نقاط الدعوة", "🎁 تعيين نقاط الهدية","📋 عرض جميع الإعدادات","🧼 تصفير الدعوة","📨 ارسال الى مستخدم"])
def handle_admin_actions(message):
    user_id = str(message.from_user.id)
    users = load_users()

    if user_id != ADMIN_ID and users.get(user_id, {}).get("role") != "admin":
        bot.send_message(message.chat.id, "❌ لا تملك صلاحية تنفيذ هذا الإجراء.")
        return
    action = message.text
    msg = ""
    if action == "🔒 حظر مستخدم":
        msg = "أرسل آيدي المستخدم لحظره:"
        bot.register_next_step_handler(message, ban_user)
    elif action == "➕ تعيين نقاط الدعوة":
    	bot.send_message(message.chat.id, "أرسل عدد النقاط الجديد لرابط الدعوة:")
    	bot.register_next_step_handler(message, set_referral_points)

    elif action == "📨 ارسال الى مستخدم":
    	msg = bot.send_message(message.chat.id, "🔢 أرسل آيدي المستخدم الذي تريد إرسال الرسالة إليه:")
    	bot.register_next_step_handler(msg, get_user_id_for_message)
    
    elif action == "🎁 تعيين نقاط الهدية":
    	bot.send_message(message.chat.id, "أرسل عدد النقاط الجديد للهدية اليومية:")
    	bot.register_next_step_handler(message, set_gift_points)
    elif action == "إيقاف البوت":
    	msg = bot.send_message(message.chat.id, "🛑 أرسل سبب إيقاف البوت:")
    	bot.register_next_step_handler(msg, get_stop_reason)
    elif action == "تشغيل البوت":
    	save_bot_status({"active": True})
    	bot.send_message(message.chat.id, "✅ تم تشغيل البوت من جديد.")
    elif action == "🔓 إلغاء الحظر":
        msg = "أرسل آيدي المستخدم لإلغاء الحظر:"
        bot.register_next_step_handler(message, unban_user)
    elif action == "إعادة ضبط المصنع":
    	ask_factory_reset_password(message)
    elif action == "➕ إرسال نقاط":
        msg = "أرسل الآيدي ثم فراغ ثم عدد النقاط (مثال: 123456 50):"
        bot.register_next_step_handler(message, send_points)
    elif action == "⬆️ رفع إلى مرسل":
        msg = "أرسل آيدي المستخدم لرفعه إلى مرسل:"
        bot.register_next_step_handler(message, promote_sender)
    elif action == "🆕 إضافة سلعة":
        msg = "أرسل اسم السلعة ثم فراغ ثم السعر (مثال: ساعة 100):"
        bot.register_next_step_handler(message, add_product)
    elif action == "📋 عرض جميع الإعدادات":
    	msg = "سيتم عرض جميع الإعدادات الحالية للبوت."
    	bot.send_message(message.chat.id, msg)
    	show_all_settings(message)  # استدعاء دالة عرض الإعدادات
    elif action == "🗑 حذف سلعة":
        msg = "أرسل اسم السلعة المراد حذفها:"
        bot.register_next_step_handler(message, delete_product)
    elif action == "اذاعة":
          msg = "أرسل الرسالة التي تريد إرسالها لجميع المستخدمين (يمكن أن تكون نص، صورة، أو رابط):"
          bot.register_next_step_handler(message, broadcast_message)        
    elif action=="خصم نقاط":
          msg = "أرسل الآيدي ثم عدد النقاط التي تريد خصمها (مثال: 123456 20):"
          bot.register_next_step_handler(message, deduct_points)
    elif action == "رفع ادمن":
    	msg = "أرسل آيدي الشخص الذي تريد رفعه أدمن:"
    	bot.register_next_step_handler(message, promote_to_admin)

    elif action == "انشاء كوبون":
    	msg = "أرسل رمز الكوبون (مثال: GIFT2025):"
    	bot.send_message(message.chat.id, msg)
    	bot.register_next_step_handler(message, get_coupon_code)
    elif action == "🧼 تصفير الدعوة":
    	reset_all_referrals(message)
    elif action == "ازالة مرسل":
    	msg = "أرسل آيدي المرسل لإزالته:"
    	bot.register_next_step_handler(message, remove_sender)
    elif action == "تصفير الكل":
    	reset_all_users_points(message)
    elif action == "اضافة عداد":
    	bot.send_message(message.chat.id, "أرسل الآيدي متبوعاً بعدد النقاط، مثلًا:\n`123456789 100`", parse_mode="Markdown")
    	bot.register_next_step_handler(message, add_to_json)
    elif action == "مسح عداد":
    	 bot.send_message(message.chat.id, "أرسل الآيدي المراد حذفه من a.json:")
    	 bot.register_next_step_handler(message, delete_from_json)
    elif action == "سجل الكوبون":
        try:
            with open("coupons.json", "r", encoding="utf-8") as f:
                logs = f.readlines()  # آخر 20 سطر فقط
                if logs:
                    log_text = "".join(logs)
                    bot.send_message(message.chat.id, f"سجل العمليات للكوبون:\n\n{log_text}")
                else:
                    bot.send_message(message.chat.id, "لا يوجد عمليات حالياً.")
        except FileNotFoundError:
            bot.send_message(message.chat.id, "لم يتم العثور على ملف السجل.")
    elif action == "🚫 إيقاف الإرسال":
     	config = load_config()
     	config["auto_send_enabled"] = False
     	save_config(config)
     	bot.send_message(message.chat.id, "تم إيقاف الإرسال التلقائي للنقاط.")

    elif action == "✅ تفعيل الإرسال":
     	config = load_config()
     	config["auto_send_enabled"] = True
     	save_config(config)
     	bot.send_message(message.chat.id, "تم تفعيل الإرسال التلقائي للنقاط.")       			
    elif action == "📊 عرض الإحصائيات":
        users = load_users()
        total = len(users)
        banned = sum(1 for u in users.values() if u["banned"])
        senders = sum(1 for u in users.values() if u["role"] == "sender")


        msg = (
            f"📊 إحصائيات البوت:\n\n"
            f"👥 عدد المستخدمين الكلي: {total}\n"
            f"⛔ عدد المحظورين: {banned}\n"
            f"✉️ عدد المرسلين: {senders}\n"
            f"👑 المالك: [{owner}] \n"
            f"🤖 اسم البوت: {bot_name}"
        )
        bot.send_message(message.chat.id, msg, parse_mode="Markdown")
    if msg:
        bot.send_message(message.chat.id, msg)
def ask_factory_reset_password(message):
    msg = bot.send_message(message.chat.id, "🔐 أدخل كلمة السر لتنفيذ إعادة ضبط المصنع:")
    bot.register_next_step_handler(msg, check_factory_reset_password)
def check_factory_reset_password(message):
    if message.text.strip() == FACTORY_RESET_PASSWORD:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add("✅ تأكيد إعادة الضبط", "❌ إلغاء")
        msg = bot.send_message(message.chat.id, "⚠️ هل أنت متأكد أنك تريد مسح جميع المستخدمين؟", reply_markup=markup)
        bot.register_next_step_handler(msg, execute_factory_reset)
    else:
        bot.send_message(message.chat.id, "❌ كلمة السر غير صحيحة.")
def execute_factory_reset(message):
    if message.text == "✅ تأكيد إعادة الضبط":
        with open("users.json", "w") as f:
            json.dump({}, f)
        bot.send_message(message.chat.id, "✅ تم تنفيذ إعادة ضبط المصنع بنجاح.")
        bot.send_message(CHANNEL_ID, "⚠️ تم تنفيذ إعادة ضبط المصنع ومسح جميع بيانات المستخدمين.")
    else:
        bot.send_message(message.chat.id, "❌ تم إلغاء العملية.")            

def show_all_settings(message):
    settings = load_edit()
    users = load_users()
    banned_users = sum(1 for u in users.values() if u.get("banned") == True)

    # إعدادات من ملف edit.json
    daily_gift_points = settings.get("daily_gift_points", 10)
    referral_points = settings.get("referral_points", 50)
    gift_points = settings.get("gift_points", 90)

    total_users = len(users)
    

    total_points = sum(u.get("points", 0) for u in users.values())
    average_points = total_points // total_users if total_users else 0

    total_referrals = sum(u.get("referrals", 0) for u in users.values())
    total_purchases = sum(u.get("purchases", 0) for u in users.values())

    incomplete_users = sum(1 for u in users.values() if not u.get("name") or not u.get("username"))

    msg = f"""
<b>📊 الإعدادات الحالية للبوت:</b>

• 🎁 <b>نقاط الهدية اليومية:</b> <code>{daily_gift_points}</code>
• 🔗 <b>نقاط رابط الدعوة:</b> <code>{referral_points}</code>
• 🎉 <b>نقاط الهدايا الإضافية:</b> <code>{gift_points}</code>

• 👥 <b>عدد المستخدمين:</b> <code>{total_users}</code>
• 🚫 <b>عدد المحظورين:</b> <code>{banned_users}</code>
• 📈 <b>متوسط النقاط:</b> <code>{average_points}</code>
• 📬 <b>إجمالي الدعوات:</b> <code>{total_referrals}</code>
• 🛍️ <b>إجمالي المشتريات:</b> <code>{total_purchases}</code>
• ❗ <b>مستخدمين غير مكتملين:</b> <code>{incomplete_users}</code>
"""

    bot.send_message(message.chat.id, msg, parse_mode="HTML", disable_web_page_preview=True)
def ban_user(message):
    users = load_users()
    uid = message.text.strip()

    if uid in users:
        # طلب السبب من المسؤول
        bot.send_message(message.chat.id, "يرجى إدخال السبب:")
        bot.register_next_step_handler(message, process_ban, uid)
    else:
        bot.send_message(message.chat.id, "المستخدم غير موجود.")
        #
def reset_all_referrals(message):
    users = load_users()
    for user_id in users:
        users[user_id]['referrals'] = 0
    save_users(users)
    bot.send_message(message.chat.id, "✅ تم تصفير عداد الدعوات لجميع المستخدمين.")
    #        
def set_referral_points(message):
    try:
        new_points = int(message.text)
        settings = load_edit()
        settings["referral_points"] = new_points
        save_edit(settings)
        bot.send_message(message.chat.id, f"✅ تم تحديث نقاط رابط الدعوة إلى: {new_points}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ يجب أن ترسل رقم صحيح.")

def set_gift_points(message):
    try:
        new_points = int(message.text)
        settings = load_edit()
        settings["daily_gift_points"] = new_points
        save_edit(settings)
        bot.send_message(message.chat.id, f"✅ تم تحديث نقاط الهدية اليومية إلى: {new_points}")
    except ValueError:
        bot.send_message(message.chat.id, "❌ يجب أن ترسل رقم صحيح.")     
def get_coupon_code(message):
    coupon = {"code": message.text.strip()}
    msg = bot.send_message(message.chat.id, "كم عدد النقاط التي يعطيها الكوبون؟")
    bot.register_next_step_handler(msg, get_coupon_points, coupon)

def get_coupon_points(message, coupon):
    try:
        coupon["points"] = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ أرسل رقم صحيح.")
        return
    msg = bot.send_message(message.chat.id, "كم شخص يستطيع استخدام الكوبون؟")
    bot.register_next_step_handler(msg, get_coupon_max_uses, coupon)

def get_coupon_max_uses(message, coupon):
    try:
        coupon["max_uses"] = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ أرسل رقم صحيح.")
        return
    msg = bot.send_message(message.chat.id, "كم ثانية يستمر الكوبون قبل ما ينتهي؟")
    bot.register_next_step_handler(msg, get_coupon_expiry, coupon)

def get_coupon_expiry(message, coupon):
    try:
        seconds = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ أرسل رقم صحيح.")
        return

    expire_time = datetime.now() + timedelta(seconds=seconds)
    coupon["expires_at"] = expire_time.strftime("%Y-%m-%d %H:%M:%S")
    coupon["used_by"] = []

    coupons = load_coupons()
    coupons[coupon["code"]] = coupon
    save_coupons(coupons)

    # إرسال تأكيد للمسؤول
    bot.send_message(
        message.chat.id,
        f"✅ تم إنشاء الكوبون:\n"
        f"الرمز: `{coupon['code']}`\n"
        f"النقاط: {coupon['points']}\n"
        f"الحد الأقصى: {coupon['max_uses']} شخص\n"
        f"ينتهي بعد: {seconds} ثانية",
        parse_mode="Markdown"
    )

    # نشر في القناة
    bot.send_message(
        "@my00002",
        f"🎉 كوبون جديد متاح الآن!\n\n"
        f"استخدم الكود: `{coupon['code']}`\n"
        f"واكسب *{coupon['points']}* نقطة!\n"
        f"العدد المتاح: {coupon['max_uses']} شخص\n"
        f"سارع قبل انتهاء المهلة أو اكتمال العدد!",
        parse_mode="Markdown"
    )
def load_coupons():
    if not os.path.exists("coupons.json"):
        return {}
    with open("coupons.json", "r") as f:
        return json.load(f)

def save_coupons(data):
    with open("coupons.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_bot_status():
    if not os.path.exists("bot_status.json"):
        return {"active": True}
    with open("bot_status.json", "r") as f:
        return json.load(f)
def save_bot_status(status):
    with open("bot_status.json", "w") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)        
def load_edit():
    if not os.path.exists("edit.json"):
        return {"daily_gift_points": 10, "referral_points": 50}
    with open("edit.json", "r") as f:
        return json.load(f)

def save_edit(data):
    with open("edit.json", "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
def ask_daily_gift_points(message):
    msg = bot.send_message(message.chat.id, "🎁 أرسل عدد النقاط التي تريد تعيينها كهدية يومية:")
    bot.register_next_step_handler(msg, set_daily_gift_points)

def set_daily_gift_points(message):
    try:
        points = int(message.text.strip())
        data = load_edit()
        data["daily_gift_points"] = points
        save_edit(data)
        bot.send_message(message.chat.id, f"✅ تم تعيين {points} نقطة كهدية يومية.")
    except:
        bot.send_message(message.chat.id, "❌ أرسل رقم صحيح.")
def ask_referral_points(message):
    msg = bot.send_message(message.chat.id, "🔗 أرسل عدد النقاط التي يحصل عليها المستخدم عند دعوة شخص:")
    bot.register_next_step_handler(msg, set_referral_points)

def set_referral_points(message):
    try:
        points = int(message.text.strip())
        data = load_edit()
        data["referral_points"] = points
        save_edit(data)
        bot.send_message(message.chat.id, f"✅ تم تعيين {points} نقطة لرابط الدعوة.")
    except:
        bot.send_message(message.chat.id, "❌ أرسل رقم صحيح.")        
def process_ban(message, user_id):
    users = load_users()

    # الحصول على السبب من المسؤول
    reason = message.text.strip()

    # حظر المستخدم
    users[user_id]["banned"] = True
    save_users(users)

    # إرسال إشعار للمسؤول
    bot.send_message(message.chat.id, f"تم حظر المستخدم {user_id}.\nالسبب: {reason}")

    # إرسال إشعار للمستخدم
    bot.send_message(user_id, f"تم حظر حسابك.\nالسبب: {reason}")
def unban_user(message):
    users = load_users()
    uid = message.text.strip()
    if uid in users:
        users[uid]["banned"] = False
        save_users(users)
        bot.send_message(message.chat.id, "تم إلغاء الحظر.")
    else:
        bot.send_message(message.chat.id, "المستخدم غير موجود.")

# حط هذا السطر في أعلى الملف، خارج كل الدوال

POINT_MILESTONES = [1000, 2000, 5000, 10000]

def send_points(message):
    users = load_users()
    try:
        uid, pts = message.text.split()
        pts = int(pts)
        if uid in users:
            users[uid]["points"] = users[uid].get("points", 0)
            users[uid]["points"] += pts
            save_users(users)
            bot.send_message(message.chat.id, "تم إرسال النقاط.")
            bot.send_message(uid, f"تمت إضافة {pts} نقطة إلى رصيدك.\nرصيدك الحالي: {users[uid]['points']}")
            check_milestones(uid, users[uid]['points'])
        else:
            bot.send_message(message.chat.id, "المستخدم غير موجود.")
    except Exception as e:
        bot.send_message(message.chat.id, f"صيغة غير صحيحة.\nالخطأ: {e}")

def check_milestones(user_id, users):
    user_id = str(user_id)

    if user_id not in users:
        return

    user = users[user_id]
    current_points = user.get("points", 0)
    
    # أضف المفتاح إذا مو موجود
    if "last_milestone" not in user:
        user["last_milestone"] = 0

    last_notified = int(user["last_milestone"])

    for milestone in POINT_MILESTONES:
        if current_points >= milestone and milestone > last_notified:
            bot.send_message(user_id, f"🎉 مبروك! وصلت إلى {milestone} نقطة!")
            user["last_milestone"] = milestone
            break

    save_users(users)
CONFIG_FILE = "config.json"

def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)
def promote_sender(message):
    users = load_users()
    uid = message.text.strip()

    if uid in users:
        users[uid]["role"] = "sender"
        save_users(users)

        bot.send_message(message.chat.id, "تم رفع المستخدم إلى مرسل.")

        # إرسال تعليمات للمرسل الجديد
        bot.send_message(uid, "تم رفعك إلى دور مرسل! استخدم الأمر /send ثم آيدي المستخدم وعدد النقاط. مثال: /send 123456 20")
    else:
        bot.send_message(message.chat.id, "المستخدم غير موجود.")
def monitor_bot_status():
    while True:
        status = load_bot_status()
        if not status.get("active", True):
            try:
                resume_time = datetime.strptime(status["resume_time"], "%Y-%m-%d %H:%M:%S")
                if datetime.now() >= resume_time:
                    # إعادة تشغيل البوت تلقائياً
                    save_bot_status({"active": True})
                    msg = "✅ عاد البوت للعمل الآن تلقائياً."

                    users = load_users()
                    for uid in users:
                        try:
                            bot.send_message(uid, msg)
                        except:
                            continue

                    bot.send_message(CHANNEL_ID, msg)
            except Exception as e:
                print("خطأ في مراقبة حالة البوت:", e)

        time.sleep(1)  # فحص كل دقيقة        
def add_product(message):
    products = load_products()
    try:
        name, price = message.text.split()
        products[name] = {"price": int(price)}
        save_products(products)
        bot.send_message(message.chat.id, "تمت إضافة السلعة.")
    except:
        bot.send_message(message.chat.id, "صيغة غير صحيحة.")
def get_badge(user):
    referrals = user.get("referrals", 0)
    
    if referrals >= 50:
        return "أسطورة الدعوات"
    elif referrals >= 20:
        return "مسوّق ذهبي"
    elif referrals >= 10:
        return "مسوّق ناشئ"
    else:
        return "بدون شارة"
def delete_product(message):
    products = load_products()
    name = message.text.strip()
    if name in products:
        del products[name]
        save_products(products)
        bot.send_message(message.chat.id, "تم حذف السلعة.")
    else:
        bot.send_message(message.chat.id, "السلعة غير موجودة.")
def deduct_points_menu(message):
    bot.send_message(message.chat.id, "أرسل الآيدي ثم عدد النقاط التي تريد خصمها (مثال: 123456 20):")
    bot.register_next_step_handler(message, deduct_points)

def deduct_points(message):
    users = load_users()
    try:
        # التقسيم بين الآيدي وعدد النقاط
        user_id, points_to_deduct = message.text.split()
        points_to_deduct = int(points_to_deduct)

        # التحقق من وجود المستخدم
        if user_id not in users:
            bot.send_message(message.chat.id, "المستخدم غير موجود.")
            return

        # التحقق من وجود رصيد كافي للخصم
        if users[user_id]["points"] < points_to_deduct:
            bot.send_message(message.chat.id, f"المستخدم يملك فقط {users[user_id]['points']} نقطة.")
            return

        # طلب السبب من المسؤول
        bot.send_message(message.chat.id, "يرجى إدخال السبب:")
        bot.register_next_step_handler(message, process_deduction, user_id, points_to_deduct)

    except:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. أرسل الآيدي ثم عدد النقاط (مثال: 123456 20).")

def process_deduction(message, user_id, points_to_deduct):
    users = load_users()

    # الحصول على السبب من المسؤول
    reason = message.text.strip()

    # خصم النقاط من المستخدم
    users[user_id]["points"] -= points_to_deduct
    save_users(users)

    # إرسال إشعار للمسؤول
    bot.send_message(message.chat.id, f"تم خصم {points_to_deduct} نقطة من المستخدم {user_id}.\nالسبب: {reason}")

    # إرسال إشعار للمستخدم مع السبب والرصيد الجديد
    new_balance = users[user_id]["points"]
    bot.send_message(user_id, f"تم خصم {points_to_deduct} نقطة من رصيدك.\nأصبح رصيدك: {new_balance} نقطة.\nالسبب: {reason}")
def update_user_rank(user_id):
    users = load_users()
    user = users.get(user_id)
    if not user:
        return

    current_rank = user.get("rank", "مستخدم عادي")
    new_rank = get_rank(user["points"])

    if new_rank != current_rank:
        user["rank"] = new_rank
        save_users(users)
        bot.send_message(user_id, f"🎉 تم ترقيتك إلى رتبة <b>{new_rank}</b>!\nمبروك، لقد حصلت على ميزات خاصة.", parse_mode="HTML")    
def get_rank(points):
    if points >= 1000 and points < 3000:
        return "VIP"
    elif points >= 3000:
        return "Partner"
    else:
        return "مستخدم عادي"    
def promote_to_admin(message):
    try:
        user_id = str(message.text).strip()
        users = load_users()

        if user_id not in users:
            bot.send_message(message.chat.id, "المستخدم غير موجود في قاعدة البيانات.")
            return

        users[user_id]["role"] = "admin"
        save_users(users)

        bot.send_message(message.chat.id, "✅ تم رفع المستخدم إلى أدمن.")
        bot.send_message(user_id, "⭐️ تم رفعك إلى أدمن، يمكنك الآن استخدام لوحة التحكم بإرسال /admin")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ: {e}")    

def remove_sender(message):
    user_id = str(message.text)
    users = load_users()
    if user_id in users and users[user_id].get("role") == "sender":
        users[user_id]["role"] = "user"  # تغيير الدور إلى "مستخدم عادي"
        save_users(users)
        bot.send_message(message.chat.id, f"تمت إزالة المستخدم {user_id} من المرسلين.")
        
        # إرسال رسالة للمستخدم الذي تم إزالة دوره
        bot.send_message(user_id, "تم إزالة دور المرسل منك. إذا كنت بحاجة إلى المزيد من المساعدة، يمكنك التواصل مع مشرف البوت.")
    else:
        bot.send_message(message.chat.id, "المستخدم غير موجود أو ليس مرسل.")
def broadcast_message(message):
    users = load_users()
    for uid in users:
        try:
            if message.content_type == "text":
                bot.send_message(uid, message.text)
            elif message.content_type == "photo":
                bot.send_photo(uid, message.photo[-1].file_id, caption=message.caption or "")
            elif message.content_type == "video":
                bot.send_video(uid, message.video.file_id, caption=message.caption or "")
            elif message.content_type == "document":
                bot.send_document(uid, message.document.file_id, caption=message.caption or "")
        except:
            continue
    bot.send_message(message.chat.id, "تم إرسال الإذاعة لجميع المستخدمين.")
    
        ###    
def get_user_id_for_message(message):
    user_id = message.text.strip()
    try:
        int(user_id)  # التأكد من أن الآيدي رقمي
    except ValueError:
        bot.send_message(message.chat.id, "❌ يرجى إدخال آيدي مستخدم صحيح.")
        return
    
    msg = bot.send_message(message.chat.id, "📝 أرسل الرسالة التي تريد إرسالها للمستخدم:")
    bot.register_next_step_handler(msg, get_message_to_send, user_id)

def get_message_to_send(message, target_user_id):
    user_message = message.text
    msg = bot.send_message(message.chat.id, "🔗 هل ترغب في إرسال صورة مع الرسالة؟ (نعم/لا)")
    bot.register_next_step_handler(msg, send_message_with_optional_image, target_user_id, user_message)

def send_message_with_optional_image(message, target_user_id, user_message):
    if message.text.lower() == "نعم":
        msg = bot.send_message(message.chat.id, "📸 أرسل الصورة التي ترغب في إرسالها:")
        bot.register_next_step_handler(msg, send_image, target_user_id, user_message)
    elif message.text.lower() == "لا":
        bot.send_message(target_user_id, user_message)
        bot.send_message(message.chat.id, "✅ تم إرسال الرسالة بنجاح!")
    else:
        bot.send_message(message.chat.id, "❌ لم أفهم إجابتك. حاول مجددًا.")
        return

def send_image(message, target_user_id, user_message):
    try:
        photo = message.photo[-1].file_id
        bot.send_photo(target_user_id, photo, caption=user_message)
        bot.send_message(message.chat.id, "✅ تم إرسال الرسالة مع الصورة بنجاح!")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ حدث خطأ أثناء إرسال الصورة. تأكد من إرسال صورة صحيحة.")
        print(e)    

@bot.message_handler(commands=['top'])
def show_top_users(message):
    if message.from_user.id != ADMINo_ID:
        return  # تجاهل الطلب إذا مو أدمن

    users = load_users()
    sorted_users = sorted(users.items(), key=lambda x: x[1].get("points", 0), reverse=True)
    
    msg = "🏆 أفضل المستخدمين حسب النقاط:\n\n"
    for i, (uid, data) in enumerate(sorted_users[:10], 1):
        name = data.get("name", "غير معروف")
        username = f"@{data['username']}" if data.get("username") else "لا يوجد"
        points = data.get("points", 0)
        msg += f"{i}. {name} ({username}) - {points} نقطة\n"

    bot.send_message(message.chat.id, msg)
    
import json
import os

A_JSON_PATH = "a.json"

def load_a_json():
    if not os.path.exists(A_JSON_PATH):
        return {}
    with open(A_JSON_PATH, "r") as f:
        return json.load(f)

def save_a_json(data):
    with open(A_JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_to_json(message):
    try:
        parts = message.text.strip().split()
        user_id = str(parts[0])
        points = int(parts[1])

        data = load_a_json()
        data[user_id] = points
        save_a_json(data)

        bot.send_message(message.chat.id, f"✅ تم إضافة الآيدي `{user_id}` بعدد نقاط `{points}` إلى a.json", parse_mode="Markdown")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ فشل في الإضافة. تأكد من الصيغة الصحيحة: `آيدي نقاط`", parse_mode="Markdown")

def delete_from_json(message):
    user_id = message.text.strip()
    data = load_a_json()

    if user_id in data:
        del data[user_id]
        save_a_json(data)
        bot.send_message(message.chat.id, f"✅ تم حذف الآيدي `{user_id}` من a.json", parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, f"❌ الآيدي `{user_id}` غير موجود في a.json", parse_mode="Markdown")    
from datetime import datetime

@bot.message_handler(commands=["report"])
def report_user(message):
    msg = bot.send_message(message.chat.id, "من فضلك، اكتب تفاصيل التقرير عن الشخص المخالف.")
    bot.register_next_step_handler(msg, handle_report)
def reset_all_users_points(message):
    users = load_users()
    for uid in users:
        users[uid]["points"] = 0
    save_users(users)

    for uid in users:
        try:
            bot.send_message(uid, "⚠️ تم تصفير رصيدك من النقاط من قبل الإدارة.")
        except:
            continue

    bot.send_message(message.chat.id, "✅ تم تصفير النقاط لجميع المستخدمين وإبلاغهم.")
def get_stop_reason(message):
    reason = message.text.strip()
    msg = bot.send_message(message.chat.id, "⏱️ أرسل مدة الإيقاف (بالثواني أو الساعات):")
    bot.register_next_step_handler(msg, get_stop_duration, reason)

def get_stop_duration(message, reason):
    try:
        duration_input = message.text.strip()
        if duration_input.endswith("s"):
            seconds = int(duration_input[:-1])
        elif duration_input.endswith("h"):
            seconds = int(duration_input[:-1]) * 3600
        else:
            seconds = int(duration_input)
    except:
        bot.send_message(message.chat.id, "❌ أرسل وقت صحيح، مثل: 60s أو 1h أو فقط رقم.")
        return

    resume_time = (datetime.now() + timedelta(seconds=seconds)).strftime("%Y-%m-%d %H:%M:%S")
    save_bot_status({"active": False, "reason": reason, "resume_time": resume_time})

    msg = f"""❌ تم إيقاف البوت مؤقتاً.
السبب: {reason}
⏳ يعود للعمل في: {resume_time}"""

    # نشر للمستخدمين والقناة
    users = load_users()
    for uid in users:
        try:
            bot.send_message(uid, msg)
        except:
            continue
    bot.send_message(CHANNEL_ID, msg)

    bot.send_message(message.chat.id, "✅ تم إيقاف البوت بنجاح.")
def check_milestones(user_id, current_points):
    user_id = str(user_id)
    users = load_users()

    last_notified = users[user_id].get("last_milestone", 0)

    for milestone in POINT_MILESTONES:
        if current_points >= milestone and milestone > last_notified:
            bot.send_message(user_id, f"🎉 مبروك! وصلت إلى {milestone} نقطة!")
            users[user_id]["last_milestone"] = milestone
            break

    save_users(users)    
def handle_report(message):
    report_text = message.text
    user_id = message.from_user.id
    username = message.from_user.username if message.from_user.username else "غير معروف"
    name = message.from_user.first_name
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # إنشاء النص الذي سيتم إرساله إلى المشرف
    report_details = f"""
    تقرير جديد:
    - اسم المستخدم: {name}
    - اسم المستخدم في تيليجرام: @{username}
    - معرف المستخدم: {user_id}
    - التاريخ: {current_date}
    - الرسالة: {report_text}
    """
    
    # إرسال التقرير للمشرف
    bot.send_message(ADMIN_ID, report_details)
    
    # تأكيد للمستخدم بأن تقريره تم إرساله
    bot.send_message(message.chat.id, "تم إرسال تقريرك للمشرفين. شكراً لتعاونك.")
@bot.message_handler(commands=["help"])
def help_message(message):
    if not is_bot_active(message):
        return
    help_text = """
    مرحباً! إليك قائمة بالأوامر التي يمكنك استخدامها:
    - /start: لبدء التفاعل مع البوت.
    - /top: لعرض أفضل المستخدمين حسب النقاط.
    - /report: للإبلاغ عن مخالفات.
    - /admin: للوصول إلى لوحة التحكم الخاصة بك إذا كنت أدمن.
    - /invate  لمعرفة من دعاك
    """
    bot.send_message(message.chat.id, help_text) 

@bot.message_handler(commands=["invate"])
def my_tree(message):
    users = load_users()
    uid = str(message.from_user.id)
    if uid not in users:
        bot.send_message(message.chat.id, "أنت غير مسجل.")
        return

    text = ""
    referrals = users[uid].get("referrals")
    if referrals:
        name = users.get(referrals, {}).get("name", "مستخدم غير معروف")
        text += f"أنت دُعيت بواسطة: {name}\n"
    else:
        text += "لم يتم دعوتك من قبل أحد.\n"

    # الآن نبحث منو دعاهم هذا المستخدم
    invites = [u["name"] for u in users.values() if u.get("referrals") == uid]
    if invites:
        text += f"\nأنت دعوت:\n" + "\n".join(f"- {name}" for name in invites)
    else:
        text += "\nأنت لم تدعُ أحداً بعد."

    bot.send_message(message.chat.id, text)
    
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "الدعم الفني":
        bot.send_photo(message.chat.id, photo=open("A.jpg", "rb"), caption="للدعم الفني تواصل معنا عبر الأرقام التالية:\n📞 07801234567\n📞 07701234567")

    elif message.text == "من نحن؟":
        text = """
            
        البوت الذي تم تطويره يحتوي على مجموعة من الوظائف التي تهدف إلى إدارة وتفاعل المستخدمين بشكل فعال، ويتميز بالعديد من الخصائص التي تتعلق بإدارة المستخدمين، التحكم في النقاط والهديا، وكذلك الحظر والإعدادات الخاصة. إليك نبذة مفصلة عن البوت:

الوظائف الرئيسية للبوت:
1. إدارة المستخدمين:
البوت يتعامل مع قاعدة بيانات للمستخدمين، حيث يُسجل معلومات مثل الاسم، المعرف، الآيدي، النقاط، السلع المشتراة، وعدد الدعوات.
يمكن للبوت تقديم تفاصيل حول المستخدمين مثل النقاط، السلع التي تم شراؤها، وعدد الدعوات التي قاموا بها.
2. إرسال هدايا يومية:
يمكن للبوت منح نقاط هدية يومية للمستخدمين. النقاط يتم تخصيصها كهدية عند استخدام البوت بشكل يومي.
3. إدارة رابط الدعوة:
كل مستخدم يحصل على رابط دعوة خاص يمكنه مشاركته مع الآخرين. يحصل المستخدم على نقاط إضافية بناءً على عدد الأشخاص الذين يسجلون باستخدام رابط الدعوة.
4. إدارة الحظر:
البوت يحتوي على نظام حظر المستخدمين بشكل نهائي أو مؤقت. إذا تم حظر المستخدم، فإنه لا يستطيع التفاعل مع البوت بأي شكل.
يمكن للمشرفين متابعة حالة الحظر لمستخدميهم باستخدام أوامر معينة.
5. الأنشطة اليومية:
البوت يقوم بتوزيع الهدايا اليومية والتي تتعلق بنقاط يمكن للمستخدمين الحصول عليها كل يوم.
6. التصويت والتقييم:
يحتوي البوت على ميزة التصويت حيث يمكن للمستخدمين تقييم البوت باستخدام خيارات مثل: "جيد"، "متوسط"، و"سيء". بعد التصويت، يتم إرسال رسالة شكر للمستخدم وتوثيق التصويت من قبل المشرف.
7. إعدادات البوت:
يوفر البوت لوحة تحكم إدارية للمشرفين، حيث يمكنهم عرض الإعدادات الحالية للبوت مثل النقاط اليومية، والنقاط المتعلقة برابط الدعوة، وأعداد المستخدمين، وأعداد المستخدمين المحظورين.
يتم التحكم في هذه الإعدادات بشكل مرن ويسهل تعديلها.
8. إدارة التقارير:
عند إجراء أي تصويت أو اتخاذ إجراء متعلق بمستخدم (مثل الحظر أو إضافة نقاط)، يتم إرسال تقارير إلى المشرف تتضمن بيانات المستخدم مثل الآيدي، الاسم، والنقاط التي تم منحها.
9. وظائف إضافية:
يمكن للبوت أن يعرض قائمة المتصدرين بناءً على النقاط التي حصل عليها كل مستخدم.
يمكن للمشرفين إرسال نقاط لمستخدم معين باستخدام أوامر مخصصة.
الميزات:
حظر المستخدمين: يضمن البوت عدم قدرة أي مستخدم محظور على التفاعل معه.
إعدادات مرنة: يتيح البوت للمشرفين تغيير الإعدادات بسهولة مثل النقاط والهدايا اليومية.
إحصائيات ومتابعة: يتيح البوت جمع معلومات عن المستخدمين بشكل شامل، مثل عدد الدعوات، والهدايا، والنقاط.
إدارة التصويت: يمكن للمستخدمين تقييم البوت، مما يسمح للمشرفين بالحصول على ملاحظات قيمة لتحسين الخدمة.
دعم رابط الدعوة: يعزز البوت التفاعل بين المستخدمين من خلال روابط دعوة تحتوي على مكافآت بناءً على عدد المستخدمين الذين يسجلون.
الإدارة:
لوحة تحكم إدارية: يتمتع المشرفون بإمكانية الوصول إلى لوحة تحكم إدارية قوية لعرض الإعدادات، التقارير، وقائمة المتصدرين.
إشعارات وتقارير: يتم إرسال إشعارات وإحصائيات للمشرفين عند حدوث تغييرات أو تصويتات.
طريقة الاستخدام:
المستخدم يبدأ التفاعل مع البوت عن طريق إرسال أمر /start، حيث يقوم البوت بإظهار رسالة ترحيب ويبدأ التفاعل.
بعد التسجيل، يحصل المستخدم على رابط دعوة خاص به، ويمكنه استخدامه للحصول على مكافآت عندما يسجل أشخاص آخرون باستخدامه.
يمكن للمستخدمين التفاعل مع البوت يومياً للحصول على نقاط هدية يومية.
المشرفون يمكنهم إدارة كل هذه العمليات من خلال أوامر مخصصة مثل /top لعرض المتصدرين و/ban لحظر المستخدمين.
الأمان:
حظر نهائي للمستخدمين المخالفين: يتمكن المشرفون من حظر المستخدمين الذين يتصرفون بشكل غير لائق أو يسيئون استخدام البوت.
---
الختام:

البوت الذي تم تطويره يعتبر أداة شاملة لإدارة المجتمع والمستخدمين داخل تطبيق، ويتميز بالمرونة والقدرة على تخصيص الإعدادات بشكل سهل. يمكن استخدامه في العديد من السياقات مثل إدارة النقاط، توزيع الهدايا، إضافة مكافآت للرابط الدعوة، وتقييم الأداء.
نحن فريق مختص في البرمجة والتكنولوجيا
نهدف إلى تقديم خدمات رقمية متميزة
تابعنا للمزيد من المعلومات والتحديثات
t.me/@my00002

www.ali-altaee.free.nf."""
        bot.send_message(message.chat.id, text)

    elif message.text == "لصناعة بوت مماثل":
        text = (
        """
        راسلني 
        www.ali-altaee.free.nf
        """
        )
        bot.send_message(message.chat.id, text)
     
    elif message.text == "الاسئلة الشائعة":
    	text = "شاهد هذا الفيديو لمعرفة الأجوبة على الأسئلة الأكثر شيوعًا."
    	bot.send_message(message.chat.id, text)
import threading
threading.Thread(target=monitor_bot_status, daemon=True).start()        
print("تم التشغيل")
bot.polling()
