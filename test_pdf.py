from capabilities.pdf import PDFCapability


pdf = PDFCapability()

result = pdf.execute(
    "Summarize this PDF",
    {
        "pdf_path": r"C:\Users\shrid\Downloads\SY_DE_Lab_Manual (1).pdf"
    }
)

print(result)