from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_user, create_user, update_user_lesson

router = Router()

# Bu yerda video ID lari yoki havolalarini saqlaymiz.
# Test uchun oddiy YouTube havolalar qo'yib turaman.
# Haqiqiy loyihada fayl_id ishlatgan ma'qul.
LESSONS = {
    1: {"video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "title": "1-Dars: Kirish", "test": {
        "question": "1-Darsning asosiy mavzusi nima edi?",
        "options": [
            {"text": "Mavzu A (To'g'ri)", "is_correct": True},
            {"text": "Mavzu B", "is_correct": False},
            {"text": "Mavzu C", "is_correct": False}
        ]
    }},
    2: {"video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "title": "2-Dars: Asosiy qoidalar", "test": {
        "question": "2-Darsdagi eng muhim qoida qaysi?",
        "options": [
            {"text": "Qoida 1", "is_correct": False},
            {"text": "Qoida 2 (To'g'ri)", "is_correct": True},
            {"text": "Qoida 3", "is_correct": False}
        ]
    }},
    3: {"video": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "title": "3-Dars: Amaliyot", "test": {
        "question": "3-Darsda qanday amaliyot qildik?",
        "options": [
            {"text": "Amaliyot A", "is_correct": False},
            {"text": "Amaliyot B", "is_correct": False},
            {"text": "Amaliyot C (To'g'ri)", "is_correct": True}
        ]
    }}
}

VIP_CHANNEL_LINK = "https://t.me/+SizningVIPKanalHavolangiz"

def get_test_keyboard(lesson_num: int):
    lesson = LESSONS.get(lesson_num)
    if not lesson:
        return None
    
    keyboard = []
    for i, opt in enumerate(lesson["test"]["options"]):
        # callback_data format: test_lessonNum_isCorrect
        cb_data = f"test_{lesson_num}_{'1' if opt['is_correct'] else '0'}"
        keyboard.append([InlineKeyboardButton(text=opt["text"], callback_data=cb_data)])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    telegram_id = message.from_user.id
    username = message.from_user.username
    
    # Deep linking args (masalan, instagram)
    args = command.args
    joined_from = args if args else "organic"

    user = get_user(telegram_id)
    if not user:
        user = create_user(telegram_id, username, joined_from)
        await message.answer(f"Assalomu alaykum, {message.from_user.full_name}! Botimizga xush kelibsiz.\nSiz bizning bepul darslarimizga qo'shildingiz!")
    else:
        await message.answer("Siz botdan ro'yxatdan o'tgansiz. Darslarni davom ettirishingiz mumkin.")

    await send_lesson(message, user.current_lesson)

async def send_lesson(message: Message, lesson_num: int):
    if lesson_num > 3:
        # Barcha darslar tugadi
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="VIP Kanalga Qo'shilish", url=VIP_CHANNEL_LINK)]
        ])
        await message.answer("Tabriklaymiz! Siz barcha bepul darslarni muvaffaqiyatli yakunladingiz.\n\nEndi VIP kanalimizga qo'shilib to'liq darslarni o'rganishingiz mumkin:", reply_markup=keyboard)
        return

    lesson = LESSONS.get(lesson_num)
    
    # Videoni va testni yuborish
    # Haqiqiy botda message.answer_video ishlatish ma'qul, hozir youtube havola yuboriladi
    await message.answer(f"🎬 {lesson['title']}\n\nVideoni ko'ring: {lesson['video']}\n\n👇 Videoni ko'rib bo'lgach, quyidagi savolga javob bering:")
    
    test_kb = get_test_keyboard(lesson_num)
    await message.answer(f"❓ Savol:\n{lesson['test']['question']}", reply_markup=test_kb)


@router.callback_query(F.data.startswith("test_"))
async def handle_test_answer(callback: CallbackQuery):
    _, lesson_str, correct_str = callback.data.split("_")
    lesson_num = int(lesson_str)
    is_correct = correct_str == '1'

    telegram_id = callback.from_user.id
    user = get_user(telegram_id)

    if not user:
        await callback.answer("Foydalanuvchi topilmadi, /start bosing.")
        return

    if user.current_lesson != lesson_num:
        await callback.answer("Bu test allaqachon topshirilgan yoki hozirgi darsingiz emas.", show_alert=True)
        return

    if is_correct:
        await callback.answer("✅ To'g'ri javob!", show_alert=True)
        
        # Keyingi darsga o'tkazish
        next_lesson = lesson_num + 1
        update_user_lesson(telegram_id, next_lesson)
        
        # Keyingi darsni yuborish
        await send_lesson(callback.message, next_lesson)
    else:
        await callback.answer("❌ Noto'g'ri javob. Videoni qayta ko'rib chiqib, to'g'ri javobni toping!", show_alert=True)
