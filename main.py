import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import fitz  # PyMuPDF
import img2pdf
from PIL import Image

BOT_TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a PDF or image and I’ll convert it!")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    file_path = f"/tmp/{file.file_unique_id}_{file.file_path.split('/')[-1]}"
    await file.download_to_drive(file_path)

    if file_path.endswith(".pdf"):
        images = convert_pdf_to_images(file_path)
        if images:
            await update.message.reply_photo(images[0])
        else:
            await update.message.reply_text("Failed to convert PDF to image.")
    elif file_path.lower().endswith((".jpg", ".jpeg", ".png")):
        pdf_path = file_path.rsplit(".", 1)[0] + ".pdf"
        with open(pdf_path, "wb") as f:
            f.write(img2pdf.convert(file_path))
        await update.message.reply_document(InputFile(pdf_path))
    else:
        await update.message.reply_text("Unsupported file type.")

def convert_pdf_to_images(pdf_path):
    images = []
    doc = fitz.open(pdf_path)
    for page in doc:
        pix = page.get_pixmap()
        output = f"/tmp/page.png"
        pix.save(output)
        images.append(open(output, "rb"))
        break
    return images

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    app.run_polling()
