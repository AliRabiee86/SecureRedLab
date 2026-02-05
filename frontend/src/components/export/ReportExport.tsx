/**
 * SecureRedLab - Report Export Component
 * Phase 8.4 - Interactive Components
 * 
 * Export reports in multiple formats (PDF, JSON, CSV, HTML)
 */

import React, { useState } from 'react';
import { Download, FileText, FileJson, FileSpreadsheet, FileCode, Loader2 } from 'lucide-react';
import Button from '../common/Button';
import type { Scan, Attack, Vulnerability, Report } from '@/types';

type ExportFormat = 'pdf' | 'json' | 'csv' | 'html';

interface ReportExportProps {
  data: {
    scans?: Scan[];
    attacks?: Attack[];
    vulnerabilities?: Vulnerability[];
    report?: Report;
  };
  title?: string;
  onExport?: (format: ExportFormat) => void;
}

const ReportExport: React.FC<ReportExportProps> = ({
  data,
  title = 'SecureRedLab Report',
  onExport
}) => {
  const [isExporting, setIsExporting] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('pdf');

  const exportFormats = [
    { value: 'pdf', label: 'PDF', icon: FileText, description: 'Professional report' },
    { value: 'json', label: 'JSON', icon: FileJson, description: 'Machine-readable data' },
    { value: 'csv', label: 'CSV', icon: FileSpreadsheet, description: 'Excel-compatible' },
    { value: 'html', label: 'HTML', icon: FileCode, description: 'Web-viewable report' }
  ];

  const handleExport = async (format: ExportFormat) => {
    setIsExporting(true);
    setSelectedFormat(format);

    try {
      let content: string;
      let filename: string;
      let mimeType: string;

      switch (format) {
        case 'json':
          content = JSON.stringify(data, null, 2);
          filename = `${title.replace(/\s+/g, '_')}_${Date.now()}.json`;
          mimeType = 'application/json';
          break;

        case 'csv':
          content = generateCSV(data);
          filename = `${title.replace(/\s+/g, '_')}_${Date.now()}.csv`;
          mimeType = 'text/csv';
          break;

        case 'html':
          content = generateHTML(data, title);
          filename = `${title.replace(/\s+/g, '_')}_${Date.now()}.html`;
          mimeType = 'text/html';
          break;

        case 'pdf':
          // For PDF, we would typically call backend API
          console.log('PDF export requires backend API');
          if (onExport) {
            onExport(format);
          }
          setIsExporting(false);
          return;

        default:
          throw new Error('Unsupported format');
      }

      // Create download link
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      if (onExport) {
        onExport(format);
      }
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
        <Download className="w-5 h-5 mr-2" />
        Export Report
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
        {exportFormats.map(({ value, label, icon: Icon, description }) => (
          <button
            key={value}
            onClick={() => handleExport(value as ExportFormat)}
            disabled={isExporting}
            className={`
              flex items-start p-4 rounded-lg border transition-all
              ${isExporting && selectedFormat === value
                ? 'bg-blue-600 border-blue-500'
                : 'bg-gray-900 border-gray-700 hover:border-blue-500'
              }
              ${isExporting ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <div className="flex-shrink-0 mr-3">
              {isExporting && selectedFormat === value ? (
                <Loader2 className="w-6 h-6 text-white animate-spin" />
              ) : (
                <Icon className="w-6 h-6 text-blue-400" />
              )}
            </div>
            <div className="flex-1 text-left">
              <div className="font-medium text-white">{label}</div>
              <div className="text-sm text-gray-400">{description}</div>
            </div>
          </button>
        ))}
      </div>

      <div className="text-sm text-gray-400">
        <p>
          <strong className="text-gray-300">Included Data:</strong>
        </p>
        <ul className="list-disc list-inside mt-2 space-y-1">
          {data.scans && <li>{data.scans.length} scan(s)</li>}
          {data.attacks && <li>{data.attacks.length} attack(s)</li>}
          {data.vulnerabilities && <li>{data.vulnerabilities.length} vulnerability(ies)</li>}
          {data.report && <li>Report metadata</li>}
        </ul>
      </div>
    </div>
  );
};

// Helper function to generate CSV
function generateCSV(data: any): string {
  const rows: string[] = [];

  // Add header
  rows.push('Type,ID,Target,Status,Created At,Details');

  // Add scans
  if (data.scans) {
    data.scans.forEach((scan: Scan) => {
      rows.push([
        'Scan',
        scan.id,
        scan.target,
        scan.status,
        scan.created_at,
        `Type: ${scan.scan_type}, Progress: ${scan.progress}%`
      ].map(escapeCSV).join(','));
    });
  }

  // Add attacks
  if (data.attacks) {
    data.attacks.forEach((attack: Attack) => {
      rows.push([
        'Attack',
        attack.id,
        attack.target,
        attack.status,
        attack.created_at,
        `Type: ${attack.attack_type}, Module: ${attack.module}`
      ].map(escapeCSV).join(','));
    });
  }

  // Add vulnerabilities
  if (data.vulnerabilities) {
    data.vulnerabilities.forEach((vuln: Vulnerability) => {
      rows.push([
        'Vulnerability',
        vuln.id,
        vuln.affected_service || 'N/A',
        vuln.severity,
        vuln.discovered_at,
        vuln.name
      ].map(escapeCSV).join(','));
    });
  }

  return rows.join('\n');
}

// Helper function to escape CSV values
function escapeCSV(value: string | number): string {
  const str = String(value);
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

// Helper function to generate HTML
function generateHTML(data: any, title: string): string {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title}</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1f2937;
            border-bottom: 3px solid #3b82f6;
            padding-bottom: 10px;
        }
        h2 {
            color: #374151;
            margin-top: 30px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background-color: #f3f4f6;
            font-weight: 600;
            color: #1f2937;
        }
        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .badge-critical { background: #fee2e2; color: #991b1b; }
        .badge-high { background: #fed7aa; color: #9a3412; }
        .badge-medium { background: #fef3c7; color: #92400e; }
        .badge-low { background: #dbeafe; color: #1e40af; }
        .badge-info { background: #e0e7ff; color: #3730a3; }
        .meta {
            color: #6b7280;
            font-size: 14px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>${title}</h1>
        <div class="meta">Generated: ${new Date().toLocaleString()}</div>
        
        ${data.scans ? `
        <h2>Scans (${data.scans.length})</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Target</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>Created</th>
                </tr>
            </thead>
            <tbody>
                ${data.scans.map((scan: Scan) => `
                <tr>
                    <td>${scan.id}</td>
                    <td>${scan.target}</td>
                    <td>${scan.scan_type}</td>
                    <td>${scan.status}</td>
                    <td>${scan.progress}%</td>
                    <td>${new Date(scan.created_at).toLocaleDateString()}</td>
                </tr>
                `).join('')}
            </tbody>
        </table>
        ` : ''}
        
        ${data.attacks ? `
        <h2>Attacks (${data.attacks.length})</h2>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Target</th>
                    <th>Type</th>
                    <th>Module</th>
                    <th>Status</th>
                    <th>Progress</th>
                </tr>
            </thead>
            <tbody>
                ${data.attacks.map((attack: Attack) => `
                <tr>
                    <td>${attack.id}</td>
                    <td>${attack.target}</td>
                    <td>${attack.attack_type}</td>
                    <td>${attack.module}</td>
                    <td>${attack.status}</td>
                    <td>${attack.progress}%</td>
                </tr>
                `).join('')}
            </tbody>
        </table>
        ` : ''}
        
        ${data.vulnerabilities ? `
        <h2>Vulnerabilities (${data.vulnerabilities.length})</h2>
        <table>
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Severity</th>
                    <th>Service</th>
                    <th>CVE</th>
                    <th>CVSS</th>
                    <th>Discovered</th>
                </tr>
            </thead>
            <tbody>
                ${data.vulnerabilities.map((vuln: Vulnerability) => `
                <tr>
                    <td>${vuln.name}</td>
                    <td><span class="badge badge-${vuln.severity.toLowerCase()}">${vuln.severity}</span></td>
                    <td>${vuln.affected_service || 'N/A'}</td>
                    <td>${vuln.cve_id || 'N/A'}</td>
                    <td>${vuln.cvss_score || 'N/A'}</td>
                    <td>${new Date(vuln.discovered_at).toLocaleDateString()}</td>
                </tr>
                `).join('')}
            </tbody>
        </table>
        ` : ''}
    </div>
</body>
</html>
  `.trim();
}

export default ReportExport;
