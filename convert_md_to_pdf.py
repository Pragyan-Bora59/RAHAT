from markdown_pdf import MarkdownPdf, Section

def convert_md_to_pdf(input_file, output_file):
    pdf = MarkdownPdf(toc_level=0)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    pdf.add_section(Section(md_content))
    pdf.save(output_file)
    print(f"Successfully converted {input_file} to {output_file}")

if __name__ == "__main__":
    convert_md_to_pdf("rahat_qa_material.md", "rahat_qa_material.pdf")
