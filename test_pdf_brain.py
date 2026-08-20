from brain.brain import Brain


brain = Brain()

result = brain.process(
    "Summarize this PDF",
    {
        "pdf_path": r"C:\Users\shrid\Downloads\SY_DE_Lab_Manual (1).pdf"
    }
)

print(result)