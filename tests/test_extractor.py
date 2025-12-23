"""
Tests for invoice data extraction
"""
import pytest
from backend.utils.extractor import extract_invoice_data, calculate_confidence
from backend.models.invoice_model import InvoiceModel

def test_invoice_model_extraction():
    """Test basic field extraction"""
    model = InvoiceModel()
    sample_text = "Invoice #: INV-2024-001 Date: 12/15/2024 Total: $2,898"
    
    result = model.extract_fields(sample_text)
    
    assert 'invoice_number' in result
    assert 'date' in result
    assert 'total' in result

def test_confidence_calculation():
    """Test confidence score calculation"""
    # All fields present
    complete_data = {
        'invoice_number': 'INV-001',
        'date': '12/15/2024',
        'total': 100.0,
        'vendor': 'Test Company'
    }
    assert calculate_confidence(complete_data) == 1.0
    
    # Half fields present
    partial_data = {
        'invoice_number': 'INV-001',
        'date': '12/15/2024'
    }
    assert calculate_confidence(partial_data) == 0.5

def test_data_validation():
    """Test data validation and cleaning"""
    model = InvoiceModel()
    raw_data = {
        'invoice_number': 'inv-001',
        'total': '123.45',
        'vendor': 'test company'
    }
    
    validated = model.validate_extraction(raw_data)
    
    assert validated['invoice_number'] == 'INV-001'
    assert validated['total'] == 123.45
    assert validated['vendor'] == 'Test Company'

if __name__ == "__main__":
    pytest.main([__file__])