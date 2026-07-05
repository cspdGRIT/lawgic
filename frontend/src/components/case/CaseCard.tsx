import { Case } from '../../types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { formatDate, caseTypeLabel } from '../../lib/utils';
import { Scale, Calendar } from 'lucide-react';

interface CaseCardProps {
  case_: Case;
  onView: (id: number) => void;
}

function statusVariant(status: Case['status']): 'success' | 'warning' | 'danger' | 'info' | 'neutral' {
  const map: Record<Case['status'], 'success' | 'warning' | 'danger' | 'info' | 'neutral'> = {
    open: 'info',
    in_progress: 'warning',
    closed: 'neutral',
    won: 'success',
    lost: 'danger',
    appealed: 'warning',
  };
  return map[status];
}

export function CaseCard({ case_, onView }: CaseCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0 pr-3">
          <h3 className="font-semibold text-gray-900 truncate">{case_.title}</h3>
          <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">{case_.description}</p>
        </div>
        <Badge variant={statusVariant(case_.status)}>
          {case_.status.replace('_', ' ').toUpperCase()}
        </Badge>
      </div>

      <div className="flex items-center gap-4 text-xs text-gray-500 mb-4">
        <span className="flex items-center gap-1">
          <Scale className="h-3 w-3" />
          {caseTypeLabel(case_.case_type)}
        </span>
        <span>{case_.jurisdiction}</span>
        <span className="flex items-center gap-1">
          <Calendar className="h-3 w-3" />
          {formatDate(case_.created_at)}
        </span>
      </div>

      {case_.confidence_score !== undefined && (
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xs text-gray-500">AI Confidence:</span>
          <div className="flex-1 bg-gray-200 rounded-full h-1.5">
            <div
              className="bg-gray-900 h-1.5 rounded-full"
              style={{ width: `${case_.confidence_score * 100}%` }}
            />
          </div>
          <span className="text-xs font-medium">{Math.round((case_.confidence_score || 0) * 100)}%</span>
        </div>
      )}

      <Button size="sm" variant="secondary" onClick={() => onView(case_.id)} className="w-full">
        View Details
      </Button>
    </div>
  );
}
