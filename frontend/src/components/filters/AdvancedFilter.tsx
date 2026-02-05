/**
 * SecureRedLab - Advanced Search & Filter Component
 * Phase 8.4 - Interactive Components
 * 
 * Advanced filtering for scans, attacks, and vulnerabilities
 */

import React, { useState } from 'react';
import { Search, Filter, X, Calendar, Target, Shield, Zap } from 'lucide-react';
import Button from '../common/Button';
import Badge from '../common/Badge';

export interface FilterState {
  search: string;
  dateRange: {
    start: string;
    end: string;
  };
  severity: string[];
  status: string[];
  type: string[];
  target: string;
}

interface AdvancedFilterProps {
  onFilterChange: (filters: FilterState) => void;
  filterTypes?: {
    showSeverity?: boolean;
    showStatus?: boolean;
    showType?: boolean;
    showTarget?: boolean;
    showDateRange?: boolean;
  };
}

const AdvancedFilter: React.FC<AdvancedFilterProps> = ({
  onFilterChange,
  filterTypes = {
    showSeverity: true,
    showStatus: true,
    showType: true,
    showTarget: true,
    showDateRange: true
  }
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    search: '',
    dateRange: { start: '', end: '' },
    severity: [],
    status: [],
    type: [],
    target: ''
  });

  const severityOptions = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];
  const statusOptions = ['PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED'];
  const typeOptions = ['NMAP', 'NUCLEI', 'CUSTOM', 'METASPLOIT', 'SQLMAP'];

  const handleFilterChange = (key: keyof FilterState, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const toggleArrayFilter = (key: 'severity' | 'status' | 'type', value: string) => {
    const current = filters[key];
    const newValue = current.includes(value)
      ? current.filter(v => v !== value)
      : [...current, value];
    handleFilterChange(key, newValue);
  };

  const clearFilters = () => {
    const emptyFilters: FilterState = {
      search: '',
      dateRange: { start: '', end: '' },
      severity: [],
      status: [],
      type: [],
      target: ''
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const activeFilterCount = 
    (filters.search ? 1 : 0) +
    filters.severity.length +
    filters.status.length +
    filters.type.length +
    (filters.target ? 1 : 0) +
    (filters.dateRange.start || filters.dateRange.end ? 1 : 0);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      {/* Search Bar */}
      <div className="flex items-center gap-3 mb-3">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search scans, attacks, vulnerabilities..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <Button
          onClick={() => setIsExpanded(!isExpanded)}
          variant={isExpanded ? 'primary' : 'secondary'}
        >
          <Filter className="w-4 h-4 mr-2" />
          Filters
          {activeFilterCount > 0 && (
            <Badge variant="danger" className="ml-2">
              {activeFilterCount}
            </Badge>
          )}
        </Button>

        {activeFilterCount > 0 && (
          <Button onClick={clearFilters} variant="danger">
            <X className="w-4 h-4 mr-2" />
            Clear
          </Button>
        )}
      </div>

      {/* Advanced Filters */}
      {isExpanded && (
        <div className="space-y-4 pt-4 border-t border-gray-700">
          {/* Date Range */}
          {filterTypes.showDateRange && (
            <div>
              <label className="flex items-center text-sm font-medium text-gray-300 mb-2">
                <Calendar className="w-4 h-4 mr-2" />
                Date Range
              </label>
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="date"
                  value={filters.dateRange.start}
                  onChange={(e) => handleFilterChange('dateRange', { ...filters.dateRange, start: e.target.value })}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <input
                  type="date"
                  value={filters.dateRange.end}
                  onChange={(e) => handleFilterChange('dateRange', { ...filters.dateRange, end: e.target.value })}
                  className="px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* Target Filter */}
          {filterTypes.showTarget && (
            <div>
              <label className="flex items-center text-sm font-medium text-gray-300 mb-2">
                <Target className="w-4 h-4 mr-2" />
                Target
              </label>
              <input
                type="text"
                placeholder="Filter by target (e.g., 192.168.1.0/24)"
                value={filters.target}
                onChange={(e) => handleFilterChange('target', e.target.value)}
                className="w-full px-3 py-2 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Severity Filter */}
          {filterTypes.showSeverity && (
            <div>
              <label className="flex items-center text-sm font-medium text-gray-300 mb-2">
                <Shield className="w-4 h-4 mr-2" />
                Severity
              </label>
              <div className="flex flex-wrap gap-2">
                {severityOptions.map(severity => (
                  <Badge
                    key={severity}
                    variant={
                      severity === 'CRITICAL' ? 'danger' :
                      severity === 'HIGH' ? 'warning' :
                      severity === 'MEDIUM' ? 'info' :
                      'default'
                    }
                    onClick={() => toggleArrayFilter('severity', severity)}
                    className={`cursor-pointer transition-opacity ${
                      filters.severity.includes(severity) ? 'opacity-100 ring-2 ring-white' : 'opacity-50'
                    }`}
                  >
                    {severity}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Status Filter */}
          {filterTypes.showStatus && (
            <div>
              <label className="flex items-center text-sm font-medium text-gray-300 mb-2">
                <Zap className="w-4 h-4 mr-2" />
                Status
              </label>
              <div className="flex flex-wrap gap-2">
                {statusOptions.map(status => (
                  <Badge
                    key={status}
                    variant={
                      status === 'RUNNING' ? 'info' :
                      status === 'COMPLETED' ? 'success' :
                      status === 'FAILED' ? 'danger' :
                      'default'
                    }
                    onClick={() => toggleArrayFilter('status', status)}
                    className={`cursor-pointer transition-opacity ${
                      filters.status.includes(status) ? 'opacity-100 ring-2 ring-white' : 'opacity-50'
                    }`}
                  >
                    {status}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Type Filter */}
          {filterTypes.showType && (
            <div>
              <label className="flex items-center text-sm font-medium text-gray-300 mb-2">
                <Filter className="w-4 h-4 mr-2" />
                Type
              </label>
              <div className="flex flex-wrap gap-2">
                {typeOptions.map(type => (
                  <Badge
                    key={type}
                    variant="default"
                    onClick={() => toggleArrayFilter('type', type)}
                    className={`cursor-pointer transition-opacity ${
                      filters.type.includes(type) ? 'opacity-100 ring-2 ring-white' : 'opacity-50'
                    }`}
                  >
                    {type}
                  </Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AdvancedFilter;
