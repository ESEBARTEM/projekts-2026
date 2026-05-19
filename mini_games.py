
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


TOKEN = "7825614818:AAEEaczJ8SjloTrTH-ooKa1P6mO38lXexT8"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    keyboard = [
        ["1 - Krustiņi un nullītes"],
        ["2 - Uzmini skaitli"],
        ["3 - Akmens, šķēres, papīrs"]
    ]

    await update.message.reply_text(
        "🎮 Izvēlies spēli:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Spēles:\n"
        "1 - Krustiņi un nullītes\n"
        "2 - Uzmini skaitli\n"
        "3 - Akmens, šķēres, papīrs\n\n"
        "Raksti /start lai sāktu\n"
        "Raksti stop lai beigtu spēli"
    )


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text.lower() == "stop":
        context.user_data.clear()
        await update.message.reply_text("Spēle apturēta. Raksti /start")
        return

    game = context.user_data.get("game")

    if game is None:
        if text.startswith("1"):
            context.user_data["game"] = "tictactoe"
            context.user_data["board"] = [[" "] * 3 for _ in range(3)]
            context.user_data["turn"] = "X"

            await update.message.reply_text(
                "Krustiņi un nullītes!\n"
                "Raksti: rinda stabs\n"
                "Piemērs: 0 2"
            )
            return

        elif text.startswith("2"):
            context.user_data["game"] = "guess"
            context.user_data["number"] = random.randint(1, 250)
            context.user_data["tries"] = 10

            await update.message.reply_text(
                "Uzmini skaitli no 1 līdz 250! Tev ir 10 mēģinājumi."
            )
            return

        elif text.startswith("3"):
            context.user_data["game"] = "rps"

            await update.message.reply_text(
                "Akmens, šķēres, papīrs!\n"
                "1 - Akmens\n"
                "2 - Šķēres\n"
                "3 - Papīrs\n"
                "Izvēlies:"
            )
            return

        else:
            await update.message.reply_text("Raksti /start lai izvēlētos spēli")
            return

    if game == "tictactoe":
        try:
            r, c = map(int, text.split())

            board = context.user_data["board"]
            turn = context.user_data["turn"]

            if not (0 <= r <= 2 and 0 <= c <= 2):
                await update.message.reply_text("Raksti tikai skaitļus no 0 līdz 2!")
                return

            if board[r][c] != " ":
                await update.message.reply_text("Šī vieta jau ir aizņemta!")
                return

            board[r][c] = turn

            board_text = "\n".join(
                [" | ".join(cell if cell != " " else "-" for cell in row) for row in board]
            )

            await update.message.reply_text(board_text)

            lines = (
                board +
                [[board[r][c] for r in range(3)] for c in range(3)] +
                [[board[i][i] for i in range(3)]] +
                [[board[i][2 - i] for i in range(3)]]
            )

            for line in lines:
                if line == ["X", "X", "X"]:
                    await update.message.reply_text("❌ X uzvarēja!")
                    context.user_data.clear()
                    return

                if line == ["O", "O", "O"]:
                    await update.message.reply_text("⭕ O uzvarēja!")
                    context.user_data.clear()
                    return

            if all(cell != " " for row in board for cell in row):
                await update.message.reply_text("Neizšķirts 🤝")
                context.user_data.clear()
                return

            context.user_data["turn"] = "O" if turn == "X" else "X"
            await update.message.reply_text(f"Gājiens: {context.user_data['turn']}")

        except:
            await update.message.reply_text("Raksti šādi: 0 2")

    elif game == "guess":
        try:
            guess = int(text)
            number = context.user_data["number"]
            context.user_data["tries"] -= 1

            if guess < number:
                await update.message.reply_text(
                    f"Lielāks ⬆️ ({context.user_data['tries']} mēģinājumi palikuši)"
                )

            elif guess > number:
                await update.message.reply_text(
                    f"Mazāks ⬇️ ({context.user_data['tries']} mēģinājumi palikuši)"
                )

            else:
                await update.message.reply_text("Pareizi ✅")
                context.user_data.clear()
                return

            if context.user_data["tries"] <= 0:
                await update.message.reply_text(f"Beidzās! Skaitlis bija {number}")
                context.user_data.clear()

        except:
            await update.message.reply_text("Ievadi skaitli!")

    elif game == "rps":
        try:
            user = int(text)
            computer = random.randint(1, 3)

            choices = {
                1: "Akmens",
                2: "Šķēres",
                3: "Papīrs"
            }

            if user not in choices:
                raise ValueError

            result = f"Tu: {choices[user]}\nDators: {choices[computer]}\n"

            if user == computer:
                result += "Neizšķirts"
            elif (
                (user == 1 and computer == 2) or
                (user == 2 and computer == 3) or
                (user == 3 and computer == 1)
            ):
                result += "Tu uzvarēji 🎉"
            else:
                result += "Dators uzvarēja 💻"

            await update.message.reply_text(result)
            context.user_data.clear()

        except:
            await update.message.reply_text("Izvēlies 1, 2 vai 3")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

print("Bot is running...")
app.run_polling()
