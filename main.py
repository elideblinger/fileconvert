import os
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from PIL import Image
import fitz  # PyMuPDF
import tempfile

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Convert images to PDF
async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photos = update.message.photo
    if not photos:
        await update.message.reply_text("Please send an image.")
        return

    photo_file = await photos[-1].get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as img_temp:
        await photo_file.download_to_drive(img_temp.name)
        pdf_path = img_temp.name.replace(".jpg", ".pdf")

        image = Image.open(img_temp.name).convert("RGB")
        image.save(pdf_path, "PDF")

        await update.message.reply_document(InputFile(pdf_path), filename="converted.pdf")

    os.remove(img_temp.name)
    os.remove(pdf_path)

# Convert PDF to images
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document or not document.file_name.endswith(".pdf"):
        await update.message.reply_text("Please send a PDF file.")
        return

    file = await document.get_file()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        await file.download_to_drive(temp_pdf.name)
        pdf_path = temp_pdf.name

    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        pix = page.get_pixmap()
        img_path = f"{pdf_path}_{i}.jpg"
        pix.save(img_path)

        await update.message.reply_photo(InputFile(img_path))

        os.remove(img_path)

    os.remove(pdf_path)

# Main
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
app.add_handler(MessageHandler(filters.PHOTO, handle_image))

app.run_polling()

