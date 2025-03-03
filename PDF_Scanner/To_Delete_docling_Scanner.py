from docling.document_converter import DocumentConverter

source = "C:\\Users\\vella\\Downloads\\black-tea_-assam_-india-oht-spec-254-rev2.pdf"  # local PDF file path
converter = DocumentConverter()
result = converter.convert(source)
print(result.document.export_to_dict()) 