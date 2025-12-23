import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import toast, { Toaster } from 'react-hot-toast';
import { saveAs } from 'file-saver';
import { 
  Upload, 
  FileText, 
  Download, 
  Copy, 
  Mail, 
  Github, 
  Calendar,
  AlertCircle,
  CheckCircle,
  Clock,
  Eye,
  Edit3
} from 'lucide-react';
import './styles/App.css';

const API_BASE = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [extractedData, setExtractedData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [processingTime, setProcessingTime] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [editedData, setEditedData] = useState({});
  const [showOriginal, setShowOriginal] = useState(false);
  const [usageStats, setUsageStats] = useState(null);

  // Fetch usage stats on component mount
  React.useEffect(() => {
    fetchUsageStats();
  }, []);

  const fetchUsageStats = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/stats`);
      setUsageStats(response.data);
    } catch (error) {
      console.error('Failed to fetch usage stats:', error);
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0];
    if (selectedFile) {
      // Validate file size (10MB limit)
      if (selectedFile.size > 10 * 1024 * 1024) {
        toast.error('File size must be less than 10MB');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png', 'image/tiff'];
      if (!allowedTypes.includes(selectedFile.type)) {
        toast.error('Please upload a PDF, JPG, PNG, or TIFF file');
        return;
      }
      
      setFile(selectedFile);
      setExtractedData(null);
      setEditedData({});
      toast.success('File selected successfully!');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif']
    },
    multiple: false
  });

  const handleExtract = async () => {
    if (!file) {
      toast.error('Please select a file first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setLoading(true);
    const startTime = Date.now();

    try {
      const response = await axios.post(`${API_BASE}/api/extract`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      const endTime = Date.now();
      setProcessingTime((endTime - startTime) / 1000);
      setExtractedData(response.data);
      setEditedData(response.data.extracted_data || {});
      
      if (response.data.duplicate_detected) {
        toast.error('Duplicate invoice detected!');
      } else {
        toast.success('Invoice processed successfully!');
      }
      
      // Refresh usage stats
      fetchUsageStats();
    } catch (error) {
      console.error('Error extracting invoice data:', error);
      if (error.response?.status === 429) {
        toast.error('Rate limit exceeded. Try again in 24 hours.');
      } else {
        toast.error('Failed to process invoice. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!file) {
      toast.error('Please process an invoice first');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API_BASE}/api/export/${format}`, formData, {
        responseType: 'blob'
      });
      
      const filename = `invoice_data_${Date.now()}.${format === 'excel' ? 'xlsx' : format}`;
      saveAs(response.data, filename);
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (error) {
      console.error('Export failed:', error);
      toast.error('Export failed. Please try again.');
    }
  };

  const copyToClipboard = () => {
    if (extractedData) {
      navigator.clipboard.writeText(JSON.stringify(extractedData.extracted_data, null, 2));
      toast.success('Data copied to clipboard!');
    }
  };

  const handleFieldEdit = (field, value) => {
    setEditedData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="App">
      <Toaster position="top-right" />
      
      {/* Header */}
      <header className="App-header">
        <div className="header-content">
          <div>
            <h1>Invoice AI Extractor</h1>
            <p>Extract data from invoices using advanced AI/ML techniques</p>
          </div>
          <div className="header-actions">
            <a 
              href="https://github.com/omegamatrix/invoice-ai-extractor" 
              target="_blank" 
              rel="noopener noreferrer"
              className="btn btn-outline"
            >
              <Github size={16} />
              View Source Code
            </a>
            <a
              href="https://omegamatrix.in/contact"
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              <Calendar size={16} />
              Schedule Custom Implementation
            </a>
          </div>
        </div>
      </header>

      {/* Usage Stats */}
      {usageStats && (
        <div className="usage-stats">
          <div className="stat">
            <span className="stat-label">Remaining Today:</span>
            <span className="stat-value">{usageStats.rate_limit.remaining_requests}/10</span>
          </div>
          <div className="stat">
            <span className="stat-label">Max File Size:</span>
            <span className="stat-value">10MB</span>
          </div>
          <div className="stat">
            <span className="stat-label">Formats:</span>
            <span className="stat-value">PDF, JPG, PNG, TIFF</span>
          </div>
        </div>
      )}

      {/* Limitations Notice */}
      <div className="limitations-notice">
        <AlertCircle size={16} />
        <span>
          This is a generic demo. Custom implementations provide 95%+ accuracy for your specific invoice formats.
        </span>
      </div>

      <main className="main-content">
        {/* Upload Section */}
        <div className="upload-section">
          <div {...getRootProps()} className={`dropzone ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <Upload size={48} />
            {isDragActive ? (
              <p>Drop the invoice here...</p>
            ) : (
              <div>
                <p>Drag & drop an invoice here, or click to select</p>
                <small>Supports PDF, JPG, PNG, TIFF up to 10MB</small>
              </div>
            )}
          </div>

          {file && (
            <div className="file-info">
              <FileText size={16} />
              <span>{file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
          )}

          <button 
            onClick={handleExtract} 
            disabled={!file || loading}
            className="btn btn-primary btn-large"
          >
            {loading ? (
              <>
                <Clock size={16} className="animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <FileText size={16} />
                Extract Data
              </>
            )}
          </button>
        </div>

        {/* Sample Invoices */}
        <div className="sample-section">
          <h3>Try Sample Invoices</h3>
          <div className="sample-buttons">
            <button className="btn btn-outline">Service Invoice</button>
            <button className="btn btn-outline">Product Invoice</button>
            <button className="btn btn-outline">Multi-page PDF</button>
          </div>
        </div>

        {/* Results Section */}
        {extractedData && (
          <div className="results-section">
            <div className="results-header">
              <h2>Extracted Data</h2>
              <div className="results-actions">
                <button 
                  onClick={() => setEditMode(!editMode)}
                  className="btn btn-outline"
                >
                  <Edit3 size={16} />
                  {editMode ? 'View Mode' : 'Edit Mode'}
                </button>
                <button 
                  onClick={() => setShowOriginal(!showOriginal)}
                  className="btn btn-outline"
                >
                  <Eye size={16} />
                  {showOriginal ? 'Hide Original' : 'Show Original'}
                </button>
              </div>
            </div>

            {/* Processing Info */}
            <div className="processing-info">
              <div className="info-item">
                <Clock size={16} />
                <span>Processing Time: {processingTime?.toFixed(2)}s</span>
              </div>
              <div className="info-item">
                <CheckCircle size={16} className={getConfidenceColor(extractedData.overall_confidence)} />
                <span>
                  Overall Confidence: {(extractedData.overall_confidence * 100).toFixed(1)}% 
                  ({getConfidenceLabel(extractedData.overall_confidence)})
                </span>
              </div>
              {extractedData.math_validation?.calculations_correct && (
                <div className="info-item">
                  <CheckCircle size={16} className="text-green-600" />
                  <span>Math Validation: Passed</span>
                </div>
              )}
            </div>

            {/* Data Display */}
            <div className="data-display">
              {showOriginal && (
                <div className="original-view">
                  <h3>Original Text</h3>
                  <pre className="raw-text">{extractedData.raw_text}</pre>
                </div>
              )}

              <div className="extracted-fields">
                <h3>Extracted Fields</h3>
                <div className="fields-grid">
                  {Object.entries(extractedData.extracted_data || {}).map(([field, value]) => {
                    if (field === 'line_items') return null;
                    
                    const confidence = extractedData.field_confidence?.[field] || 0;
                    
                    return (
                      <div key={field} className="field-item">
                        <label>{field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</label>
                        {editMode ? (
                          <input
                            type="text"
                            value={editedData[field] || ''}
                            onChange={(e) => handleFieldEdit(field, e.target.value)}
                            className="field-input"
                          />
                        ) : (
                          <span className="field-value">{value || 'Not found'}</span>
                        )}
                        <span className={`confidence ${getConfidenceColor(confidence)}`}>
                          {(confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Line Items */}
              {extractedData.extracted_data?.line_items && (
                <div className="line-items">
                  <h3>Line Items</h3>
                  <div className="table-container">
                    <table>
                      <thead>
                        <tr>
                          <th>Description</th>
                          <th>Quantity</th>
                          <th>Unit Price</th>
                          <th>Line Total</th>
                        </tr>
                      </thead>
                      <tbody>
                        {extractedData.extracted_data.line_items.map((item, index) => (
                          <tr key={index}>
                            <td>{item.description}</td>
                            <td>{item.quantity}</td>
                            <td>${item.unit_price?.toFixed(2)}</td>
                            <td>${item.line_total?.toFixed(2)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Missing Fields Warning */}
              {extractedData.missing_required_fields?.length > 0 && (
                <div className="missing-fields">
                  <AlertCircle size={16} />
                  <span>
                    Missing required fields: {extractedData.missing_required_fields.join(', ')}
                  </span>
                </div>
              )}
            </div>

            {/* Export Actions */}
            <div className="export-actions">
              <h3>Export Options</h3>
              <div className="export-buttons">
                <button onClick={() => handleExport('json')} className="btn btn-outline">
                  <Download size={16} />
                  JSON
                </button>
                <button onClick={() => handleExport('csv')} className="btn btn-outline">
                  <Download size={16} />
                  CSV
                </button>
                <button onClick={() => handleExport('excel')} className="btn btn-outline">
                  <Download size={16} />
                  Excel
                </button>
                <button onClick={copyToClipboard} className="btn btn-outline">
                  <Copy size={16} />
                  Copy to Clipboard
                </button>
                <button className="btn btn-outline">
                  <Mail size={16} />
                  Email Results
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="footer">
        <div className="footer-content">
          <div>
            <p>© 2025 Invoice AI Extractor - Open Source MIT License</p>
            <p>Built with ❤️ in India by <a href="https://omegamatrix.in" target="_blank" rel="noopener noreferrer">Omega Matrix</a></p>
            <p>No data is stored. All processing happens locally for your privacy.</p>
          </div>
          <div className="footer-links">
            <a href="https://omegamatrix.in/privacy" target="_blank" rel="noopener noreferrer">Privacy Policy</a>
            <a href="https://omegamatrix.in/terms" target="_blank" rel="noopener noreferrer">Terms of Service</a>
            <a href="https://omegamatrix.in/contact" target="_blank" rel="noopener noreferrer">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
