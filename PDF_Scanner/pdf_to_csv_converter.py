import os
import json
import re
from docling.document_converter import DocumentConverter
from datetime import datetime

def clean_text(text):
    """Clean and normalize text content."""
    # Remove HTML comments and tags
    text = re.sub(r'<!,-.*?-->', '', text)
    text = re.sub(r'<!-- .*? -->', '', text)
    text = re.sub(r'<.*?>', '', text)
    
    # Clean up markdown tables and formatting
    text = re.sub(r'\|[-|]+\|', '', text)  # Remove table separators
    text = re.sub(r'\s*\|\s*', ' | ', text)  # Normalize table cell spacing
    text = re.sub(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|', r'\1: \2', text)  # Convert table rows to key-value pairs
    
    # General text cleanup
    text = re.sub(r'[|\-]{2,}', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace(',-', '-')
    
    # Fix common formatting issues in the extracted text
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)  # Fix split numbers like "10 7" to "107"
    text = re.sub(r'<(\d+)\s+(\d+)', r'<\1\2', text)  # Fix values like "<10 3" to "<103"
    
    return text.strip()

def extract_key_value_pairs(text):
    """Extract key-value pairs from the text content with improved parsing."""
    text = clean_text(text)
    
    # Extract product name from the header
    product_name = None
    match = re.search(r'## Organic ([^\n]+)', text)
    if match:
        product_name = match.group(1).strip()
    
    lines = text.split('\n')
    pairs = []
    current_key = ''
    current_value = []
    section = ''
    
    # Add product name if found
    if product_name:
        pairs.append(('Product Name', product_name))
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Detect section headers
        if line.startswith('## '):
            section = line.replace('#', '').strip()
            continue
            
        # Handle table rows that might have been converted to key-value format
        if ':' in line:
            if current_key and current_value:
                pairs.append((current_key, ' '.join(current_value)))
                current_value = []
            
            parts = line.split(':', 1)
            current_key = parts[0].strip()
            if len(parts) > 1:
                current_value = [parts[1].strip()]
        else:
            # Handle lines that might be part of a value
            if current_key and not line.endswith(':'):
                current_value.append(line)
    
    if current_key and current_value:
        pairs.append((current_key, ' '.join(current_value)))
    
    # Special handling for packaging section
    packaging_data = {}
    for i, (key, value) in enumerate(pairs):
        if key == 'Outer Liner' and 'Brown paper packet' in value and 'White polypropylene' in value:
            # Split packaging information
            kilo_value = re.search(r'Brown paper packet', value)
            bulk_value = re.search(r'White polypropylene sack/2 ply\s+paper', value)
            
            if kilo_value:
                packaging_data['Kilo Outer Liner'] = 'Brown paper packet'
            if bulk_value:
                packaging_data['Bulk Outer Liner'] = 'White polypropylene sack/2 ply paper'
        
        elif key == 'Outer Seal' and 'Polypropylene tape' in value and 'Non re-sealable' in value:
            kilo_value = re.search(r'Polypropylene tape', value)
            bulk_value = re.search(r'Non re-sealable cable tie/stitching', value)
            
            if kilo_value:
                packaging_data['Kilo Outer Seal'] = 'Polypropylene tape'
            if bulk_value:
                packaging_data['Bulk Outer Seal'] = ' Non re-sealable cable tie/stitching'
        
        elif key == 'Inner Liner' and 'Food grade polythene liner' in value:
            packaging_data['Kilo Inner Liner'] = 'Food grade polythene liner'
            packaging_data['Bulk Inner Liner'] = 'Food grade polythene liner'
        
        elif key == 'Inner Seal' and 'Cellulose tape' in value and 'Releasable cable tie' in value:
            kilo_value = re.search(r'Cellulose tape', value)
            bulk_value = re.search(r'Releasable cable tie', value)
            
            if kilo_value:
                packaging_data['Kilo Inner Seal'] = 'Cellulose tape'
            if bulk_value:
                packaging_data['Bulk Inner Seal'] = 'Releasable cable tie'
    
    # Add packaging data to pairs
    for key, value in packaging_data.items():
        pairs.append((key, value))
    
    # Clean up pairs
    cleaned_pairs = []
    for key, value in pairs:
        key = key.strip()
        value = value.strip()
        
        if not key or not value or key == value:
            continue
        
        key = re.sub(r'^[|\s-]+|[|\s-]+$', '', key)
        value = re.sub(r'^[|\s-]+|[|\s-]+$', '', value)
        
        # Handle special cases
        if key == 'Product Name' and not value.startswith('"'):
            value = f'"{value}"'
        
        if key and value:
            cleaned_pairs.append((key, value))
    
    return cleaned_pairs

def extract_structured_data(pairs):
    """Convert flat key-value pairs into a structured JSON format."""
    structured_data = {}
    
    # Map common keys to their standardized names
    key_mapping = {
        'Product Name': 'product_name',
        'Botanical name': 'botanical_name',
        'Part of Plant': 'plant_part',
        'Typical country of origin': 'country',
        'Appearance Format': 'appearance_format',
        'Flavour': 'flavour',
        'Odour': 'odour',
        'Drying method': 'drying_method',
        'Further processing': 'further_processing',
        'TVC': 'tvc',
        'Salmonella': 'salmonella',
        'E.coli': 'e_coli',
        'Yeast and mould': 'yeast_and_mould',
        'Enterobacteriacae': 'enterobacteriacae',
        'Pesticides': 'pesticides',
        'Mycotoxins': 'mycotoxins',
        'Pyrrolizidine Alkaloids': 'pyrrolizidine_alkaloids',
        'Fe': 'fe',
        'Non-Fe': 'non_fe',
        'S/S': 's_s',
        'Outer Liner': 'outer_liner',
        'Outer Seal': 'outer_seal',
        'Inner Liner': 'inner_liner',
        'Inner Seal': 'inner_seal',
        'Issued by': 'issued_by',
        'Position': 'position'
    }
    
    # Extract product name from pairs
    for key, value in pairs:
        if key == 'Product Name':
            structured_data['product_name'] = value
            break
    
    # Extract basic product information
    for key, value in pairs:
        normalized_key = key_mapping.get(key, key.lower().replace(' ', '_'))
        
        if key == 'Botanical name':
            structured_data['botanical_name'] = value
        elif key == 'Part of Plant':
            structured_data['plant_part'] = value
        elif key == 'Typical country of origin':
            structured_data['country'] = {
                'Code': 'IN' if 'india' in value.lower() else '',
                'Name': 'India'
            }
    
    # Only set fields if they're not already extracted from the document
    if 'botanical_name' not in structured_data:
        for key, value in pairs:
            if 'botanical' in key.lower() or 'scientific' in key.lower():
                structured_data['botanical_name'] = value
                break
                
    if 'plant_part' not in structured_data:
        for key, value in pairs:
            if 'part' in key.lower() and 'plant' in key.lower():
                structured_data['plant_part'] = value
                break
                
    if 'country' not in structured_data:
        for key, value in pairs:
            if 'country' in key.lower() or 'origin' in key.lower():
                country_name = value
                country_code = ''
                
                # Try to extract country code
                if 'india' in value.lower():
                    country_code = 'IN'
                elif 'china' in value.lower():
                    country_code = 'CN'
                elif 'sri lanka' in value.lower():
                    country_code = 'LK'
                    
                structured_data['country'] = {
                    'Code': country_code,
                    'Name': country_name
                }
                break
    
    # Organoleptic description
    organoleptic = {}
    for key, value in pairs:
        if key == 'Appearance Format':
            organoleptic['appearance_format'] = value
        elif key == 'Flavour':
            organoleptic['flavour'] = value
        elif key == 'Odour':
            organoleptic['odour'] = value
    
    if organoleptic:
        structured_data['organoleptic_description'] = [organoleptic]
    else:
        # Try to find appearance, flavor, odor in other keys if standard keys not found
        for key, value in pairs:
            if any(word in key.lower() for word in ['appearance', 'look', 'color', 'colour']):
                organoleptic['appearance_format'] = value
            elif any(word in key.lower() for word in ['flavour', 'flavor', 'taste']):
                organoleptic['flavour'] = value
            elif any(word in key.lower() for word in ['odour', 'odor', 'smell', 'aroma']):
                organoleptic['odour'] = value
                
        # Only add if we found at least one property
        if organoleptic:
            structured_data['organoleptic_description'] = [organoleptic]
    
    # Processing details
    processing = {}
    for key, value in pairs:
        if key == 'Drying method':
            processing['drying_method'] = value.capitalize()
        elif key == 'Further processing':
            processing['further_processing'] = value if value else '*'
    
    if processing:
        structured_data['processing_details'] = [processing]
    
    # Microbiological analysis
    micro = {}
    for key, value in pairs:
        if key == 'TVC' or 'total viable count' in key.lower() or 'total count' in key.lower():
            micro['tvc'] = value
        elif 'salmonella' in key.lower():
            micro['salmonella'] = value
        elif 'e.coli' in key.lower() or 'e. coli' in key.lower():
            micro['e_coli'] = value
        elif ('yeast' in key.lower() and 'mould' in key.lower()) or ('yeast' in key.lower() and 'mold' in key.lower()):
            micro['yeast_and_mould'] = value
        elif 'enterobacteriacae' in key.lower() or 'enterobacteriaceae' in key.lower():
            micro['enterobacteriacae'] = value
    
    if micro:
        structured_data['microbiological_analysis'] = [micro]
    
    # Contaminants
    contaminants = {}
    for key, value in pairs:
        if key == 'Pesticides' or 'pesticide' in key.lower():
            contaminants['pesticides'] = value
        elif 'mycotoxin' in key.lower():
            contaminants['mycotoxins'] = value
        elif 'pyrrolizidine' in key.lower() or 'alkaloid' in key.lower():
            contaminants['pyrrolizidine_alkaloids'] = value
    
    if contaminants:
        structured_data['contaminants'] = [contaminants]
    
    # Metal detection
    metal = {}
    for key, value in pairs:
        if key == 'Fe' or 'ferrous' in key.lower() or 'iron' in key.lower():
            metal['fe'] = value
        elif key == 'Non-Fe' or 'non-ferrous' in key.lower() or 'non ferrous' in key.lower():
            metal['non_fe'] = value
        elif key == 'S/S' or 'stainless steel' in key.lower() or 'stainless-steel' in key.lower():
            metal['s_s'] = value
    
    if metal:
        structured_data['metal_detection'] = [metal]
    
    # Packaging - Extract from pairs
    kilo_packs = {}
    bulk_packs = {}
    
    # Look for packaging information in the pairs
    for key, value in pairs:
        if 'kilo' in key.lower() and 'outer liner' in key.lower():
            kilo_packs['outer_liner'] = value
        elif 'kilo' in key.lower() and 'outer seal' in key.lower():
            kilo_packs['outer_seal'] = value
        elif 'kilo' in key.lower() and 'inner liner' in key.lower():
            kilo_packs['inner_liner'] = value
        elif 'kilo' in key.lower() and 'inner seal' in key.lower():
            kilo_packs['inner_seal'] = value
        elif 'bulk' in key.lower() and 'outer liner' in key.lower():
            bulk_packs['outer_liner'] = value
        elif 'bulk' in key.lower() and 'outer seal' in key.lower():
            bulk_packs['outer_seal'] = value
        elif 'bulk' in key.lower() and 'inner liner' in key.lower():
            bulk_packs['inner_liner'] = value
        elif 'bulk' in key.lower() and 'inner seal' in key.lower():
            bulk_packs['inner_seal'] = value
    
    # Only add packaging data if we found any
    if kilo_packs:
        structured_data['kilo_packs'] = [kilo_packs]
    if bulk_packs:
        structured_data['bulk_packs'] = [bulk_packs]
    
    # Declaration
    declaration = {}
    for key, value in pairs:
        if key == 'Issued by' or 'issued by' in key.lower() or 'author' in key.lower():
            declaration['issued_by'] = value
        elif key == 'Position' or 'position' in key.lower() or 'title' in key.lower() or 'role' in key.lower():
            declaration['position'] = value
    
    if declaration:
        structured_data['declaration'] = [declaration]
    
    return structured_data

def convert_pdf_to_json(pdf_path):
    """Convert PDF to JSON with structured format and save raw text content."""
    try:
        # Convert PDF to text using docling
        converter = DocumentConverter()
        result = converter.convert(pdf_path)
        text_content = result.document.export_to_markdown()  # Using markdown output for better table preservation
        
        # Save raw text content to file
        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M')
        text_filename = f'{timestamp}_raw_content.md'
        text_output_path = os.path.join(os.path.dirname(pdf_path), text_filename)
        
        with open(text_output_path, 'w', encoding='utf-8') as textfile:
            textfile.write(text_content)
        
        # Extract key-value pairs
        pairs = extract_key_value_pairs(text_content)
        
        # Convert to structured format
        product_data = extract_structured_data(pairs)
        
        # Print JSON content to terminal with pretty formatting
        print("\n===== JSON CONTENT START =====\n")
        print(json.dumps(product_data, ensure_ascii=False, indent=4))
        print("\n===== JSON CONTENT END =====\n")
        
        # Generate JSON filename with timestamp
        output_filename = f'{timestamp}_product_data.json'
        output_path = os.path.join(os.path.dirname(pdf_path), output_filename)
        
        # Write to JSON file
        with open(output_path, 'w', encoding='utf-8') as jsonfile:
            json.dump(product_data, jsonfile, ensure_ascii=False, indent=4)
        
        print(f"Product data saved to {output_filename}")
        return output_path
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

def process_pdfs_in_directory(directory):
    """Process all PDF files in the given directory."""
    for filename in os.listdir(directory):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(directory, filename)
            output_path = convert_pdf_to_json(pdf_path)
            if output_path:
                print(f"Successfully converted {filename} to {output_path}")

if __name__ == '__main__':
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    process_pdfs_in_directory(current_dir)
