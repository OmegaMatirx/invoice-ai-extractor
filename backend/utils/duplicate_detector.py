"""
Duplicate invoice detection utilities
"""
import hashlib
import json
from typing import Dict, Any, Optional, Set
from collections import defaultdict
import time

class DuplicateDetector:
    """Simple in-memory duplicate detection for demo purposes"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_seconds = retention_hours * 3600
        self.processed_invoices: Dict[str, Dict[str, Any]] = {}
        self.invoice_hashes: Dict[str, str] = {}  # hash -> invoice_number
        self.client_invoices: Dict[str, Set[str]] = defaultdict(set)  # client_ip -> set of invoice_numbers
    
    def generate_content_hash(self, file_bytes: bytes) -> str:
        """Generate hash of file content"""
        return hashlib.sha256(file_bytes).hexdigest()
    
    def check_duplicate(self, client_ip: str, file_bytes: bytes, 
                       invoice_data: Dict[str, Any]) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        Check if invoice is duplicate
        Returns: (is_duplicate, previous_data)
        """
        # Clean old entries
        self._cleanup_old_entries()
        
        content_hash = self.generate_content_hash(file_bytes)
        invoice_number = invoice_data.get('extracted_data', {}).get('invoice_number')
        
        # Check by content hash (exact file duplicate)
        if content_hash in self.invoice_hashes:
            previous_invoice = self.invoice_hashes[content_hash]
            if previous_invoice in self.processed_invoices:
                return True, self.processed_invoices[previous_invoice]
        
        # Check by invoice number for same client
        if invoice_number and invoice_number in self.client_invoices[client_ip]:
            # Find the previous data
            for stored_number, data in self.processed_invoices.items():
                if stored_number == invoice_number and data.get('client_ip') == client_ip:
                    return True, data
        
        # Store this invoice
        if invoice_number:
            self.processed_invoices[invoice_number] = {
                'data': invoice_data,
                'timestamp': time.time(),
                'client_ip': client_ip,
                'content_hash': content_hash
            }
            self.invoice_hashes[content_hash] = invoice_number
            self.client_invoices[client_ip].add(invoice_number)
        
        return False, None
    
    def _cleanup_old_entries(self):
        """Remove entries older than retention period"""
        now = time.time()
        cutoff = now - self.retention_seconds
        
        # Find expired entries
        expired_invoices = []
        for invoice_number, data in self.processed_invoices.items():
            if data['timestamp'] < cutoff:
                expired_invoices.append(invoice_number)
        
        # Remove expired entries
        for invoice_number in expired_invoices:
            data = self.processed_invoices.pop(invoice_number)
            content_hash = data['content_hash']
            client_ip = data['client_ip']
            
            # Clean up related mappings
            if content_hash in self.invoice_hashes:
                del self.invoice_hashes[content_hash]
            
            if client_ip in self.client_invoices:
                self.client_invoices[client_ip].discard(invoice_number)
                if not self.client_invoices[client_ip]:
                    del self.client_invoices[client_ip]

# Global duplicate detector instance
duplicate_detector = DuplicateDetector()