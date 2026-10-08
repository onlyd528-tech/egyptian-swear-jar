import discord
from discord.ext import commands
import json
import os
from threading import Thread
from flask import Flask

# إعدادات الـ Web Server البسيط عشان يفضل Koyeb صاحي ومشغل البوت أونلاين 24/7
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# إعدادات البوت والصلاحيات
intents = discord.Intents.default()
intents.message_content = True  # مهم جداً عشان البوت يقرا محتوى الرسائل
bot = commands.Bot(command_prefix="!", intents=intents)

# ملف حفظ العدادات
DATA_FILE = "swears_data.json"

# ==================== قائمة الشتائم الكاملة (عربي وفرانكو) ====================
SWEAR_WORDS = [
    # 1. الشتايم الأساسية (بالعربي)
    "احا", "احاا", "احااا",
    "خول", "خولي",
    "عرص", "عرصه",
    "متناك", "متناكة",
    "لبوة", "لبوه",
    "شرموط", "شرموطة", "شرموطه",
    "علق", "علقتنا",
    "خرا", "خرة",
    "زنا", "زاني", "زانية",
    "زبي", "زبك", "زبم", "زبها",
    "زنجي", "نيجر",
    "طيز", "طيزك", "طياز", "طيازك",
    "كس", "كسك", "كسو", "كسها", "كسكوس",
    "زب", "زوبر", "ازبار",
    "بزاز", "بزة",
    "مص", "مصمص", "مص زبي", "امص",

    # 2. شتايم العائلات والأمهات (مركبة)
    "كسم", "كسمك", "كسخك", "كسختك",
    "ابن العرص", "ابن المتناكة", "ابن الشرموطة", "ابن الكلب", "ابن الوسخة",
    "أخت العرص", "اخت المتناكة", "اخت الشرموطة",
    "خول ابن خول", "عرص ابن عرص",

    # 3. شتايم بذيئة وشتائم إضافية
    "منيوك", "منياك",
    "ديوث",
    "قحبة", "قحبه",
    "شراميط",
    "علوق",
    "خيلان",
    "خولات",
    "عراميس",
    "نجس", "نجسة",
    "قذر", "قذرة",
    "واطي", "واطية",
    "حتيلي", "عرصين",

    # 4. الفرانكو والشات (Franco & Discord Slang)
    "aha", "ah2", "ahaa",
    "5ol", "khol", "5ool",
    "ars", "ar9", "er9",
    "mtnak", "mtna2", "mtaynak",
    "lbwa", "labwa",
    "sharmot", "sharmota", "shrmota", "shrmotah", "sharmotah",
    "3ala2", "alag", "ala2", "$ala2",
    "khr", "5ra",
    "zby", "zbak", "ziby",
    "tiz", "teez", "tizk", "teezak",
    "kes", "kos", "ks", "kosk", "ksk",
    "zob", "zop", "zobak",
    "kosm", "ksm", "kosmak", "ksmak",
    "ebn el 5ol", "ebn el ars", "ebn el sharmota", "ibn el mtnak"
]
# ======================================================================

# تحميل البيانات القديمة لو موجودة
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# حفظ البيانات
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("------")

@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات عشان البوت ما يعدش على نفسه
    if message.author.bot:
        return

    # فحص الرسالة لو فيها شتيمة
    content_lower = message.content.lower()
    found_swear = False
    
    for word in SWEAR_WORDS:
        if word in content_lower:
            found_swear = True
            break

    if found_swear:
        data = load_data()
        user_id = str(message.author.id)
        
        # لو المستخدم مش موجود في القائمة، ابدأ عداد من الصفر
        if user_id not in data:
            data[user_id] = {"name": message.author.name, "count": 0}
        
        # زيادة العداد بواقع 1
        data[user_id]["count"] += 1
        save_data(data)

    # مهم جداً عشان الأوامر الثانية زي !jar تشتغل
    await bot.process_commands(message)

# أمر لعرض عداد الشتايم (Leaderboard)
@bot.command(name="jar", help="بيعرض ترتيب الشتايم في السيرفر")
async def jar(ctx):
    data = load_data()
    if not data:
        await ctx.send("برطمان الشتايم فاضي تماماً لحد دلوقتي! ناس محترمة والله 😇")
        return

    # ترتيب المستخدمين تنازلياً حسب عدد الشتايم
    sorted_users = sorted(data.items(), key=lambda x: x[1]["count"], reverse=True)
    
    embed = discord.Embed(title="🏺 برطمان الشتايم (Swear Jar)", color=discord.Color.red())
    
    for index, (uid, info) in enumerate(sorted_users, 1):
        embed.add_field(
            name=f"{index}. {info['name']}",
            value=f"عدد الشتايم: **{info['count']}**",
            inline=False
        )
    
    await ctx.send(embed=embed)

# تشغيل السيرفر الوهمي الأول في الخلفية
keep_alive()

# تشغيل البوت وسحب التوكن سراً من إعدادات الاستضافة
bot.run(os.environ.get("BOT_TOKEN"))
