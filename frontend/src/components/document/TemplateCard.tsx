import { Template } from '../../types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { FileText } from 'lucide-react';

interface TemplateCardProps {
  template: Template;
  onSelect: (template: Template) => void;
}

const categoryColors: Record<string, 'info' | 'success' | 'warning' | 'danger' | 'neutral'> = {
  Notices: 'warning',
  Agreements: 'success',
  'Court Filings': 'danger',
  Family: 'info',
  Property: 'neutral',
  Corporate: 'info',
  Consumer: 'success',
};

export function TemplateCard({ template, onSelect }: TemplateCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow flex flex-col">
      <div className="flex items-start gap-3 mb-3">
        <div className="p-2 bg-gray-100 rounded-lg">
          <FileText className="h-5 w-5 text-gray-700" />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-gray-900 text-sm leading-tight">{template.name}</h3>
          <div className="mt-1">
            <Badge variant={categoryColors[template.category] || 'neutral'}>{template.category}</Badge>
          </div>
        </div>
      </div>

      <p className="text-xs text-gray-500 mb-3 flex-1 line-clamp-2">{template.description}</p>

      <p className="text-xs text-gray-400 mb-3">
        <span className="font-medium text-gray-600">Law:</span> {template.applicable_law}
      </p>

      <div className="flex flex-wrap gap-1 mb-4">
        {template.fields.slice(0, 4).map((field) => (
          <span key={field} className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
            {field.replace(/_/g, ' ')}
          </span>
        ))}
        {template.fields.length > 4 && (
          <span className="text-xs bg-gray-100 text-gray-600 px-1.5 py-0.5 rounded">
            +{template.fields.length - 4} more
          </span>
        )}
      </div>

      <Button size="sm" onClick={() => onSelect(template)} className="w-full">
        Use Template
      </Button>
    </div>
  );
}
