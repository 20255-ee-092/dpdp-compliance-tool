import pymupdf4llm

# Convert PDF to Markdown
md_text = pymupdf4llm.to_markdown("C:\\Users\\vella\\Downloads\\black-tea_-assam_-india-oht-spec-254-rev2.pdf")
print(md_text)
# Optionally, save the Markdown to a file
import pathlib
pathlib.Path("output.md").write_bytes(md_text.encode())
