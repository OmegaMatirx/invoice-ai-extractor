"""
Invoice data extraction model with comprehensive field extraction
"""
import re
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

class InvoiceModel:
    """Enhanced model for extracting structured data from invoice text"""
    
    def __init__(self):
        self.patterns = {
            # Vendor Information
            'vendor_name': [
                r'(?:from|vendor|company|bill from|sold by)[:\s]*([A-Za-z0-9\s&.,\-]+?)(?:\n|address|phone|email|tax)',
                r'^([A-Za-z0-9\s&.,\-]+?)(?:\n.*address|phone|email)',
                r'([A-Z][A-Za-z\s&.,\-]+(?:inc|llc|ltd|corp|company))',
            ],
            'vendor_address': [
                r'(?:address|addr)[:\s]*([A-Za-z0-9\s,.\-#]+?)(?:\n\n|phone|email|tax|invoice)',
                r'(\d+\s+[A-Za-z\s,.\-]+\d{5})',
            ],
            'vendor_tax_id': [
                r'(?:tax\s*id|gst|vat|ein)[:\s#]*([A-Z0-9\-]+)',
                r'(?:federal\s*id|employer\s*id)[:\s#]*([A-Z0-9\-]+)',
            ],
            'vendor_contact': [
                r'(?:phone|tel|contact)[:\s]*([0-9\-\(\)\s+]+)',
                r'(?:email|e-mail)[:\s]*([A-Za-z0-9@.\-_]+)',
            ],
            
            # Invoice Details
            'invoice_number': [
                r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
                r'inv\s*#?\s*:?\s*([A-Z0-9\-]+)',
                r'#\s*([A-Z0-9\-]+)',
                r'invoice\s*number[:\s]*([A-Z0-9\-]+)',
            ],
            'invoice_date': [
                r'(?:invoice\s*)?date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'(?:invoice\s*)?date\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            ],
            'due_date': [
                r'due\s*date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
                r'payment\s*due\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            ],
            'po_number': [
                r'(?:po|purchase\s*order)\s*#?\s*:?\s*([A-Z0-9\-]+)',
                r'p\.?o\.?\s*#?\s*:?\s*([A-Z0-9\-]+)',
            ],
            'payment_terms': [
                r'(?:payment\s*terms|terms)[:\s]*(net\s*\d+|due\s*on\s*receipt|[A-Za-z0-9\s]+)',
                r'(net\s*\d+)',
            ],
            
            # Financial Summary
            'subtotal': [
                r'subtotal\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'sub\s*total\s*:?\s*\$?([0-9,]+\.?\d*)',
            ],
            'tax_amount': [
                r'tax\s*(?:amount)?\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'(?:sales\s*tax|vat)\s*:?\s*\$?([0-9,]+\.?\d*)',
            ],
            'tax_rate': [
                r'tax\s*(?:rate)?\s*:?\s*([0-9.]+)%',
                r'(?:sales\s*tax|vat)\s*(?:rate)?\s*:?\s*([0-9.]+)%',
            ],
            'discount': [
                r'discount\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'less\s*:?\s*\$?([0-9,]+\.?\d*)',
            ],
            'shipping': [
                r'(?:shipping|freight|delivery)\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'(?:handling|ship)\s*:?\s*\$?([0-9,]+\.?\d*)',
            ],
            'total': [
                r'total\s*(?:amount)?\s*(?:due)?\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'amount\s*due\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'grand\s*total\s*:?\s*\$?([0-9,]+\.?\d*)',
                r'\$([0-9,]+\.?\d*)',
            ],
            'currency': [
                r'(\$|USD|EUR|GBP|CAD)',
                r'currency[:\s]*([A-Z]{3})',
            ],
            
            # Additional Fields
            'bank_details': [
                r'(?:bank|routing|account)\s*(?:number|#)?\s*:?\s*([0-9\-]+)',
                r'(?:swift|iban)\s*:?\s*([A-Z0-9]+)',
            ],
            'notes': [
                r'(?:notes|comments|memo)[:\s]*([A-Za-z0-9\s.,\-]+?)(?:\n\n|$)',
            ],
            'payment_method': [
                r'(?:payment\s*method|pay\s*via)[:\s]*([A-Za-z\s]+)',
                r'(?:check|cash|credit|wire|ach)',
            ],
        }
        
        # Line item patterns
        self.line_item_patterns = {
            'description': r'([A-Za-z][A-Za-z0-9\s\-.,]+)',
            'quantity': r'(\d+(?:\.\d+)?)',
            'unit_price': r'\$?([0-9,]+\.?\d*)',
            'line_total': r'\$?([0-9,]+\.?\d*)',
        }
    
    def extract_fields(self, text: str) -> Dict[str, Any]:
        """Extract key fields from invoice text"""
        text_lower = text.lower()
        extracted = {}
        
        for field, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE)
                if match:
                    extracted[field] = match.group(1).strip()
                    break
        
        # Extract line items
        line_items = self.extract_line_items(text)
        if line_items:
            extracted['line_items'] = line_items
        
        return extracted
    
    def extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from invoice text"""
        lines = text.split('\n')
        line_items = []
        
        # Look for table-like structures
        for line in lines:
            # Skip headers and empty lines
            if not line.strip() or any(header in line.lower() for header in 
                ['description', 'qty', 'quantity', 'price', 'total', 'amount']):
                continue
            
            # Try to match line item pattern
            parts = line.split()
            if len(parts) >= 3:
                # Simple heuristic: description + numbers
                numbers = [p for p in parts if re.match(r'^\$?[0-9,]+\.?\d*$', p)]
                if len(numbers) >= 2:  # At least qty and price
                    item = {
                        'description': ' '.join(parts[:-len(numbers)]),
                        'quantity': self.clean_number(numbers[0]) if len(numbers) > 0 else None,
                        'unit_price': self.clean_number(numbers[-2]) if len(numbers) > 1 else None,
                        'line_total': self.clean_number(numbers[-1]) if len(numbers) > 0 else None,
                    }
                    line_items.append(item)
        
        return line_items[:10]  # Limit to 10 items
    
    def clean_number(self, value: str) -> float:
        """Clean and convert number string to float"""
        if not value:
            return None
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[\$,]', '', str(value))
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def validate_extraction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean extracted data with confidence scores"""
        validated = {}
        field_confidence = {}
        
        # Clean and validate each field
        for field, value in data.items():
            if field == 'line_items':
                validated[field] = value
                field_confidence[field] = 0.8 if value else 0.0
                continue
                
            cleaned_value, confidence = self.validate_field(field, value)
            if cleaned_value is not None:
                validated[field] = cleaned_value
                field_confidence[field] = confidence
        
        # Mathematical validation
        math_validation = self.validate_mathematics(validated)
        
        # Overall confidence
        overall_confidence = self.calculate_overall_confidence(field_confidence, math_validation)
        
        return {
            'extracted_data': validated,
            'field_confidence': field_confidence,
            'math_validation': math_validation,
            'overall_confidence': overall_confidence,
            'missing_required_fields': self.get_missing_required_fields(validated)
        }
    
    def validate_field(self, field: str, value: str) -> tuple:
        """Validate individual field and return (cleaned_value, confidence)"""
        if not value:
            return None, 0.0
        
        try:
            if field in ['subtotal', 'tax_amount', 'discount', 'shipping', 'total']:
                cleaned = self.clean_number(value)
                return cleaned, 0.9 if cleaned is not None else 0.0
            
            elif field in ['invoice_date', 'due_date']:
                # Basic date validation
                if re.match(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}', value):
                    return value, 0.8
                return value, 0.5
            
            elif field == 'invoice_number':
                return value.upper(), 0.9
            
            elif field == 'vendor_name':
                return value.title(), 0.7
            
            else:
                return value, 0.6
                
        except Exception:
            return value, 0.3
    
    def validate_mathematics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate mathematical relationships in the invoice"""
        validation = {
            'subtotal_tax_total_match': False,
            'line_items_sum_match': False,
            'calculations_correct': False
        }
        
        try:
            subtotal = data.get('subtotal', 0) or 0
            tax_amount = data.get('tax_amount', 0) or 0
            total = data.get('total', 0) or 0
            discount = data.get('discount', 0) or 0
            shipping = data.get('shipping', 0) or 0
            
            # Check if subtotal + tax + shipping - discount = total
            calculated_total = subtotal + tax_amount + shipping - discount
            if abs(calculated_total - total) < 0.01:
                validation['subtotal_tax_total_match'] = True
            
            # Check line items sum
            line_items = data.get('line_items', [])
            if line_items:
                line_total_sum = sum(item.get('line_total', 0) or 0 for item in line_items)
                if abs(line_total_sum - subtotal) < 0.01:
                    validation['line_items_sum_match'] = True
            
            validation['calculations_correct'] = validation['subtotal_tax_total_match']
            
        except Exception:
            pass
        
        return validation
    
    def calculate_overall_confidence(self, field_confidence: Dict[str, float], 
                                   math_validation: Dict[str, Any]) -> float:
        """Calculate overall document confidence score"""
        if not field_confidence:
            return 0.0
        
        # Base confidence from field extractions
        base_confidence = sum(field_confidence.values()) / len(field_confidence)
        
        # Boost for mathematical validation
        math_boost = 0.1 if math_validation.get('calculations_correct') else 0.0
        
        # Penalty for missing required fields
        required_fields = ['invoice_number', 'invoice_date', 'total', 'vendor_name']
        missing_penalty = sum(0.05 for field in required_fields 
                            if field not in field_confidence)
        
        final_confidence = min(1.0, base_confidence + math_boost - missing_penalty)
        return round(final_confidence, 2)
    
    def get_missing_required_fields(self, data: Dict[str, Any]) -> List[str]:
        """Get list of missing required fields"""
        required_fields = ['invoice_number', 'invoice_date', 'total', 'vendor_name']
        return [field for field in required_fields if field not in data or not data[field]]