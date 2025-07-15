import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import fitz  # PyMuPDF

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me an image to convert to PDF or a PDF to convert to images.")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document or update.message.photo[-1]
    file_info = await file.get_file()
    file_bytes = await file_info.download_as_bytearray()

    if file.file_name and file.file_name.lower().endswith(".pdf"):
        await convert_pdf_to_images(update, file_bytes)
    else:
        await convert_images_to_pdf(update, file_bytes)

async def convert_images_to_pdf(update, file_bytes):
    try:
        img = Image.open(file_bytes)
        img = img.convert("RGB")
        output_path = "/tmp/output.pdf"
        img.save(output_path, "PDF")
        with open(output_path, "rb") as f:
            await update.message.reply_document(document=InputFile(f, filename="converted.pdf"))
    except Exception as e:
        await update.message.reply_text(f"Image to PDF failed: {e}")

async def convert_pdf_to_images(update, file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for i, page in enumerate(doc):
            pix = page.get_pixmap()
            img_path = f"/tmp/page_{i + 1}.png"
            pix.save(img_path)
            with open(img_path, "rb") as f:
                await update.message.reply_photo(photo=InputFile(f))
    except Exception as e:
        await update.message.reply_text(f"PDF to Image failed: {e}")

if __name__ == "__main__":
    print("🔥 Starting bot")  # This will show up in logs to confirm correct file
    if not BOT_TOKEN:
        print("❌ Missing BOT_TOKEN environment variable.")
        exit(1)

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
    app.run_polling()
