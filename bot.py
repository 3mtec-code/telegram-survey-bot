"""
================================================================================
  Incubation Engagement & Startup Readiness Predictor — Telegram Survey Bot
  All 20 questions from the new questionnaire (Sections A–E) — Strict Linear Flow
  Built with python-telegram-bot v20+ (async/await)
================================================================================
"""

import csv
import logging
import os
import sys
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from supabase import create_client, Client

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 6223188903

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate required environment variables
missing_vars = []
if not BOT_TOKEN:
    missing_vars.append("TELEGRAM_TOKEN")
if not SUPABASE_URL:
    missing_vars.append("SUPABASE_URL")
if not SUPABASE_KEY:
    missing_vars.append("SUPABASE_KEY")
if missing_vars:
    print(f"Error: Missing environment variables: {', '.join(missing_vars)}")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ─────────────────────────────────────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# CONVERSATION STATES  (one per question)
# ─────────────────────────────────────────────────────────────────────────────
(
    Q1_GENDER,
    Q2_COLLEGE,
    Q3_YEAR,
    Q4_AWARE,
    Q5_UNDERSTAND,
    Q6_CHANNEL,
    Q7_RELATIONSHIP,
    Q8_PARTICIPATED,
    Q9_FAIR,
    Q10_HAS_IDEA,
    Q11_STAGE,
    Q12_SECTOR,
    Q13_SUBMITTED,
    Q14_REASON,
    Q15_MARKET,
    Q16_KNOWLEDGE,
    Q17_COMPETITION,
    Q18_BARRIERS,
    Q19_SUPPORT,
    Q20_INVITE,
    Q20_PHONE,
) = range(21)

# ─────────────────────────────────────────────────────────────────────────────
# KEYBOARDS
# ─────────────────────────────────────────────────────────────────────────────
KB_GENDER = ReplyKeyboardMarkup(
    [["♂ Male", "♀ Female"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_COLLEGE = ReplyKeyboardMarkup(
    [
        ["💻 Computer Science", "🖧 Information Technology"],
        ["🗄 Information System", "📊 Information Science"],
        ["🐾 Veterinary Medicine", "🌾 Agriculture"],
        ["🧬 Biotechnology", "📚 Other"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_YEAR = ReplyKeyboardMarkup(
    [["1st Year", "2nd Year"], ["3rd Year", "4th Year"], ["5th Year or Above"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_YESNO = ReplyKeyboardMarkup(
    [["✅ Yes", "❌ No"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_UNDERSTAND = ReplyKeyboardMarkup(
    [
        ["🟢 I understand them well"],
        ["🟡 I know them partially"],
        ["🔴 I have heard of it but don't know the services"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_CHANNEL = ReplyKeyboardMarkup(
    [
        ["✈ Telegram", "💬 WhatsApp"],
        ["📋 Campus Notice Board", "📱 Other Social Media"],
        ["🚫 I don't receive information"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_RELATIONSHIP = ReplyKeyboardMarkup(
    [
        ["🚀 I have used its services"],
        ["👀 I have visited but not used its services"],
        ["💤 I have never engaged with it"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_PARTICIPATED = ReplyKeyboardMarkup(
    [["🏆 Yes, more than once", "✅ Yes, once"], ["❌ No"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_LIKERT = ReplyKeyboardMarkup(
    [["1 – Strongly Disagree", "2 – Disagree", "3 – Neutral"],
     ["4 – Agree", "5 – Strongly Agree"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_HAS_IDEA = ReplyKeyboardMarkup(
    [["💡 Yes, I have an idea", "❌ No"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_STAGE = ReplyKeyboardMarkup(
    [
        ["💭 Idea only", "🔍 Researching it"],
        ["🛠 Prototype/MVP built", "👥 Has users"],
        ["💰 Generating revenue"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_SECTOR = ReplyKeyboardMarkup(
    [
        ["🌱 Agriculture (AgriTech)", "🏥 Health (HealthTech)"],
        ["📖 Education (EdTech)", "💳 Finance (FinTech)"],
        ["🚚 Commerce & Logistics", "🔧 Other"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_SUBMITTED = ReplyKeyboardMarkup(
    [["✅ Yes", "❌ No"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_REASON = ReplyKeyboardMarkup(
    [
        ["📭 Did not receive information"],
        ["💸 Lack of funds"],
        ["👤 No team member"],
        ["📚 Academic workload / lack of time"],
        ["🤔 Don't believe Center would help"],
        ["🕐 Idea not ready yet"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_MARKET = ReplyKeyboardMarkup(
    [["🔬 Yes, thoroughly", "🔍 Partially", "❌ No"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_COMPETITION = ReplyKeyboardMarkup(
    [["🥇 Yes, and I won a prize"], ["🎗 Yes, but I did not win"], ["❌ No"]],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_BARRIERS = ReplyKeyboardMarkup(
    [
        ["💸 Lack of funding"],
        ["🎓 Lack of expert guidance (mentors)"],
        ["🏗 Lack of workspace, lab, and materials"],
        ["📚 Academic workload"],
        ["⚖ Lack of legal and licensing knowledge"],
        ["👥 Not finding team members"],
        ["🌐 Internet cost"],
        ["📭 Lack of information"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_SUPPORT = ReplyKeyboardMarkup(
    [
        ["🌱 Seed funding"],
        ["🎓 Expert mentorship"],
        ["🏗 Free workspace and lab"],
        ["📖 Training (business, pitching, legal)"],
        ["🤝 Connection with investors"],
    ],
    one_time_keyboard=True, resize_keyboard=True,
)

KB_INVITE = ReplyKeyboardMarkup(
    [["📲 Yes, send me invitations", "🚫 No, thank you"]],
    one_time_keyboard=True, resize_keyboard=True,
)

# ─────────────────────────────────────────────────────────────────────────────
# CSV UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
# CSV utilities removed. Data will be saved to Supabase.


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def progress(step: int, total: int = 20) -> str:
    filled = int((step / total) * 10)
    bar = "█" * filled + "░" * (10 - filled)
    return f"[{bar}] {step}/{total}"


# ─────────────────────────────────────────────────────────────────────────────
# HANDLERS — Strict Linear Flow (Q1 to Q20)
# ─────────────────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    context.user_data.clear()
    logger.info("User %s started survey.", user.id)

    await update.message.reply_text(
        f"👋 Welcome, {user.first_name}!\n\n"
        "📋 *Incubation Engagement & Startup Readiness Predictor*\n"
        "Student Questionnaire\n\n"
        "This survey helps improve our university's Incubation Center services.\n"
        "✅ Your answers are *anonymous* and used for research only.\n"
        "⏱ Time: 5–7 minutes\n\n"
        "Type /cancel at any time to exit.\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Section A: Basic Profile*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{progress(1)}\n"
        "*Q1.* What is your gender?",
        parse_mode="Markdown",
        reply_markup=KB_GENDER,
    )
    return Q1_GENDER


async def q1_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q1_gender"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(2)}\n"
        "*Q2.* What is your college / field of study?",
        parse_mode="Markdown",
        reply_markup=KB_COLLEGE,
    )
    return Q2_COLLEGE


async def q2_college(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q2_college"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(3)}\n"
        "*Q3.* What is your year of study?",
        parse_mode="Markdown",
        reply_markup=KB_YEAR,
    )
    return Q3_YEAR


async def q3_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q3_year"] = update.message.text.strip()
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Section B: Incubation Center Awareness & Access*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{progress(4)}\n"
        "*Q4.* Are you aware that our university has an Incubation Center?",
        parse_mode="Markdown",
        reply_markup=KB_YESNO,
    )
    return Q4_AWARE


async def q4_aware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q4_aware"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(5)}\n"
        "*Q5.* How well do you understand the Center's services?",
        parse_mode="Markdown",
        reply_markup=KB_UNDERSTAND,
    )
    return Q5_UNDERSTAND


async def q5_understand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q5_understand"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(6)}\n"
        "*Q6.* Through which channel do you mainly receive information about "
        "incubation, competitions, and grants?",
        parse_mode="Markdown",
        reply_markup=KB_CHANNEL,
    )
    return Q6_CHANNEL


async def q6_channel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q6_channel"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(7)}\n"
        "*Q7.* What is your relationship with the Center?",
        parse_mode="Markdown",
        reply_markup=KB_RELATIONSHIP,
    )
    return Q7_RELATIONSHIP


async def q7_relationship(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q7_relationship"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(8)}\n"
        "*Q8.* Have you participated in any training, workshop, or hackathon "
        "organized by the Center or the campus?",
        parse_mode="Markdown",
        reply_markup=KB_PARTICIPATED,
    )
    return Q8_PARTICIPATED


async def q8_participated(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q8_participated"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(9)}\n"
        "*Q9.* The Center's processes and application procedures are clear and fair to students.\n\n"
        "1 = Strongly Disagree · 2 = Disagree · 3 = Neutral · 4 = Agree · 5 = Strongly Agree",
        parse_mode="Markdown",
        reply_markup=KB_LIKERT,
    )
    return Q9_FAIR


async def q9_fair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q9_fair"] = update.message.text.strip()
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Section C: Startup Idea & Stage*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{progress(10)}\n"
        "*Q10.* Do you have a startup or innovation idea?",
        parse_mode="Markdown",
        reply_markup=KB_HAS_IDEA,
    )
    return Q10_HAS_IDEA


async def q10_has_idea(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q10_has_idea"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(11)}\n"
        "*Q11.* What stage is your idea at?",
        parse_mode="Markdown",
        reply_markup=KB_STAGE,
    )
    return Q11_STAGE


async def q11_stage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q11_stage"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(12)}\n"
        "*Q12.* Which sector does your idea belong to?",
        parse_mode="Markdown",
        reply_markup=KB_SECTOR,
    )
    return Q12_SECTOR


async def q12_sector(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q12_sector"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(13)}\n"
        "*Q13.* Have you submitted your idea to the Incubation Center?",
        parse_mode="Markdown",
        reply_markup=KB_SUBMITTED,
    )
    return Q13_SUBMITTED


async def q13_submitted(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q13_submitted"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(14)}\n"
        "*Q14.* What is the main reason you have not submitted your idea?",
        parse_mode="Markdown",
        reply_markup=KB_REASON,
    )
    return Q14_REASON


async def q14_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q14_reason"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(15)}\n"
        "*Q15.* Have you done market research on your idea?",
        parse_mode="Markdown",
        reply_markup=KB_MARKET,
    )
    return Q15_MARKET


async def q15_market(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q15_market"] = update.message.text.strip()
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Section D: Readiness Level*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{progress(16)}\n"
        "*Q16.* My business, marketing, and finance knowledge is sufficient.\n\n"
        "1 = Strongly Disagree · 2 = Disagree · 3 = Neutral · 4 = Agree · 5 = Strongly Agree",
        parse_mode="Markdown",
        reply_markup=KB_LIKERT,
    )
    return Q16_KNOWLEDGE


async def q16_knowledge(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q16_knowledge"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(17)}\n"
        "*Q17.* Have you previously participated in an innovation competition?",
        parse_mode="Markdown",
        reply_markup=KB_COMPETITION,
    )
    return Q17_COMPETITION


async def q17_competition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q17_competition"] = update.message.text.strip()
    await update.message.reply_text(
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 *Section E: Barriers & Expected Support*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{progress(18)}\n"
        "*Q18.* Select your biggest barrier(s).\n"
        "_(You can pick up to 2 — send your first choice now)_",
        parse_mode="Markdown",
        reply_markup=KB_BARRIERS,
    )
    context.user_data["q18_barriers"] = []
    return Q18_BARRIERS


async def q18_barriers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text.strip()
    barriers: list = context.user_data.setdefault("q18_barriers", [])
    barriers.append(choice)

    if len(barriers) < 2:
        await update.message.reply_text(
            f"✅ Recorded: _{choice}_\n\n"
            "You can select *one more barrier* or tap *Done* to continue.",
            parse_mode="Markdown",
            reply_markup=ReplyKeyboardMarkup(
                [
                    ["💸 Lack of funding"],
                    ["🎓 Lack of expert guidance (mentors)"],
                    ["🏗 Lack of workspace, lab, and materials"],
                    ["📚 Academic workload"],
                    ["⚖ Lack of legal and licensing knowledge"],
                    ["👥 Not finding team members"],
                    ["🌐 Internet cost"],
                    ["📭 Lack of information"],
                    ["✅ Done – move to next question"],
                ],
                one_time_keyboard=True, resize_keyboard=True,
            ),
        )
        return Q18_BARRIERS

    context.user_data["q18_barriers"] = ", ".join(barriers)
    await update.message.reply_text(
        f"{progress(19)}\n"
        "*Q19.* What is the one support you most want from the Center?",
        parse_mode="Markdown",
        reply_markup=KB_SUPPORT,
    )
    return Q19_SUPPORT


async def q18_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    barriers: list = context.user_data.get("q18_barriers", [])
    context.user_data["q18_barriers"] = ", ".join(barriers)
    await update.message.reply_text(
        f"{progress(19)}\n"
        "*Q19.* What is the one support you most want from the Center?",
        parse_mode="Markdown",
        reply_markup=KB_SUPPORT,
    )
    return Q19_SUPPORT


async def q19_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q19_support"] = update.message.text.strip()
    await update.message.reply_text(
        f"{progress(20)}\n"
        "*Q20 (Optional).* Would you like to be invited to future startup training?",
        parse_mode="Markdown",
        reply_markup=KB_INVITE,
    )
    return Q20_INVITE


async def q20_invite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = update.message.text.strip()
    context.user_data["q20_invite"] = answer

    if "Yes" in answer:
        await update.message.reply_text(
            "📞 Please share your phone number so we can reach you:",
            reply_markup=ReplyKeyboardRemove(),
        )
        return Q20_PHONE

    context.user_data["q20_phone"] = ""
    return await finish(update, context)


async def q20_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["q20_phone"] = update.message.text.strip()
    return await finish(update, context)


# ─────────────────────────────────────────────────────────────────────────────
# FINISH — save & notify
# ─────────────────────────────────────────────────────────────────────────────

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    d = context.user_data

    row = {
        "timestamp":       datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id":         user.id,
        "username":        f"@{user.username}" if user.username else "N/A",
        "full_name":       user.full_name,
        "q1_gender":       d.get("q1_gender", ""),
        "q2_college":      d.get("q2_college", ""),
        "q3_year":         d.get("q3_year", ""),
        "q4_aware":        d.get("q4_aware", ""),
        "q5_understand":   d.get("q5_understand", ""),
        "q6_channel":      d.get("q6_channel", ""),
        "q7_relationship": d.get("q7_relationship", ""),
        "q8_participated": d.get("q8_participated", ""),
        "q9_fair":         d.get("q9_fair", ""),
        "q10_has_idea":    d.get("q10_has_idea", ""),
        "q11_stage":       d.get("q11_stage", ""),
        "q12_sector":      d.get("q12_sector", ""),
        "q13_submitted":   d.get("q13_submitted", ""),
        "q14_reason":      d.get("q14_reason", ""),
        "q15_market":      d.get("q15_market", ""),
        "q16_knowledge":   d.get("q16_knowledge", ""),
        "q17_competition": d.get("q17_competition", ""),
        "q18_barriers":    d.get("q18_barriers", ""),
        "q19_support":     d.get("q19_support", ""),
        "q20_invite":      d.get("q20_invite", ""),
        "q20_phone":       d.get("q20_phone", ""),
    }

    try:
        # Insert the response into Supabase table 'survey_responses'
        supabase.from_("survey_responses").insert(row).execute()
        logger.info("Survey response saved to Supabase for user %s", row.get("user_id"))
    except Exception as exc:
        logger.error("Supabase insert failed: %s", exc)

    # Save to local CSV file
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "survey_responses.csv")
        file_exists = os.path.isfile(csv_path)
        with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if not file_exists or os.path.getsize(csv_path) == 0:
                writer.writeheader()
            writer.writerow(row)
        logger.info("Survey response saved to CSV for user %s", row.get("user_id"))
    except Exception as exc:
        logger.error("CSV save failed: %s", exc)

    admin_msg = (
        "🆕 New Survey Response\n"
        "══════════════════════════\n"
        f"🕐 Time      : {row['timestamp']}\n"
        f"👤 User      : {row['full_name']} ({row['username']})\n"
        f"🆔 ID        : {row['user_id']}\n"
        "──────────────────────────\n"
        f"Q1  Gender   : {row['q1_gender']}\n"
        f"Q2  College  : {row['q2_college']}\n"
        f"Q3  Year     : {row['q3_year']}\n"
        "── Section B ─────────────\n"
        f"Q4  Aware    : {row['q4_aware']}\n"
        f"Q5  Understand: {row['q5_understand']}\n"
        f"Q6  Channel  : {row['q6_channel']}\n"
        f"Q7  Relation : {row['q7_relationship']}\n"
        f"Q8  Attended : {row['q8_participated']}\n"
        f"Q9  Fair     : {row['q9_fair']}\n"
        "── Section C ─────────────\n"
        f"Q10 Has Idea : {row['q10_has_idea']}\n"
        f"Q11 Stage    : {row['q11_stage']}\n"
        f"Q12 Sector   : {row['q12_sector']}\n"
        f"Q13 Submitted: {row['q13_submitted']}\n"
        f"Q14 Reason   : {row['q14_reason']}\n"
        f"Q15 Market   : {row['q15_market']}\n"
        "── Section D ─────────────\n"
        f"Q16 Knowledge: {row['q16_knowledge']}\n"
        f"Q17 Competed : {row['q17_competition']}\n"
        "── Section E ─────────────\n"
        f"Q18 Barriers : {row['q18_barriers']}\n"
        f"Q19 Support  : {row['q19_support']}\n"
        f"Q20 Invite   : {row['q20_invite']}\n"
        f"Q20 Phone    : {row['q20_phone']}\n"
        "══════════════════════════"
    )

    try:
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
        logger.info("Admin notified for user %s.", user.id)
    except Exception as exc:
        logger.error("Admin notify failed: %s", exc)

    await update.message.reply_text(
        "🎉 *Survey Complete!*\n\n"
        "✅ Thank you for your time and honest input.\n"
        "Your participation will help improve the Incubation Center for all students. 🙏\n\n"
        "💬 To retake the survey, type /start.",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove(),
    )
    context.user_data.clear()
    return ConversationHandler.END


# ─────────────────────────────────────────────────────────────────────────────
# /cancel
# ─────────────────────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    await update.message.reply_text(
        "❌ Survey cancelled.\n\nType /start to begin again. 👋",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def unexpected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "⚠️ Please choose one of the provided options, or type /cancel to exit."
    )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    DONE_FILTER = filters.Regex(r"✅ Done")

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            Q1_GENDER:       [MessageHandler(filters.TEXT & ~filters.COMMAND, q1_gender)],
            Q2_COLLEGE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q2_college)],
            Q3_YEAR:         [MessageHandler(filters.TEXT & ~filters.COMMAND, q3_year)],
            Q4_AWARE:        [MessageHandler(filters.TEXT & ~filters.COMMAND, q4_aware)],
            Q5_UNDERSTAND:   [MessageHandler(filters.TEXT & ~filters.COMMAND, q5_understand)],
            Q6_CHANNEL:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q6_channel)],
            Q7_RELATIONSHIP: [MessageHandler(filters.TEXT & ~filters.COMMAND, q7_relationship)],
            Q8_PARTICIPATED: [MessageHandler(filters.TEXT & ~filters.COMMAND, q8_participated)],
            Q9_FAIR:         [MessageHandler(filters.TEXT & ~filters.COMMAND, q9_fair)],
            Q10_HAS_IDEA:    [MessageHandler(filters.TEXT & ~filters.COMMAND, q10_has_idea)],
            Q11_STAGE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, q11_stage)],
            Q12_SECTOR:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q12_sector)],
            Q13_SUBMITTED:   [MessageHandler(filters.TEXT & ~filters.COMMAND, q13_submitted)],
            Q14_REASON:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q14_reason)],
            Q15_MARKET:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q15_market)],
            Q16_KNOWLEDGE:   [MessageHandler(filters.TEXT & ~filters.COMMAND, q16_knowledge)],
            Q17_COMPETITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, q17_competition)],
            Q18_BARRIERS: [
                MessageHandler(DONE_FILTER & ~filters.COMMAND, q18_done),
                MessageHandler(filters.TEXT & ~filters.COMMAND, q18_barriers),
            ],
            Q19_SUPPORT:     [MessageHandler(filters.TEXT & ~filters.COMMAND, q19_support)],
            Q20_INVITE:      [MessageHandler(filters.TEXT & ~filters.COMMAND, q20_invite)],
            Q20_PHONE:       [MessageHandler(filters.TEXT & ~filters.COMMAND, q20_phone)],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            MessageHandler(filters.COMMAND, cancel),
        ],
        allow_reentry=True,
        conversation_timeout=1800,
    )

    app.add_handler(conv)
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unexpected))

    logger.info("Bot is running… Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()