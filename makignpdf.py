from weasyprint import HTML

def convert_html_to_pdf(html_string, output_path):
    # Generate a PDF file from HTML string
    HTML(string=html_string).write_pdf(output_path)

# Example HTML with CSS
html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        h1 {
            color: blue;
        }
    </style>
</head>
<body>
    <h1>Hello, this is a sample HTML with CSS!</h1>
    <p>This is a paragraph.</p>
</body>
</html>
"""

# Output PDF file path
pdf_output_path = "output.pdf"

# Convert HTML to PDF
convert_html_to_pdf(html_content, pdf_output_path)