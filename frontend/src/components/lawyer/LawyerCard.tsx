import { Lawyer } from '../../types';
import { Badge } from '../ui/Badge';
import { Button } from '../ui/Button';
import { formatINR } from '../../lib/utils';
import { Star, MapPin, CheckCircle, Clock } from 'lucide-react';

interface LawyerCardProps {
  lawyer: Lawyer;
  onBook?: (lawyer: Lawyer) => void;
  onView?: (lawyer: Lawyer) => void;
  matchReason?: string;
}

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <Star
          key={star}
          className={`h-3.5 w-3.5 ${star <= Math.round(rating) ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
        />
      ))}
      <span className="text-xs text-gray-600 ml-1">{rating.toFixed(1)}</span>
    </div>
  );
}

export function LawyerCard({ lawyer, onBook, onView, matchReason }: LawyerCardProps) {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3 mb-3">
        <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white text-lg font-bold flex-shrink-0">
          {lawyer.full_name.charAt(0).toUpperCase()}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-gray-900 truncate">{lawyer.full_name}</h3>
            {lawyer.verified && (
              <CheckCircle className="h-4 w-4 text-blue-500 flex-shrink-0" />
            )}
          </div>
          <StarRating rating={lawyer.rating} />
          <p className="text-xs text-gray-500 mt-0.5">{lawyer.review_count} reviews</p>
        </div>
        <div className="text-right flex-shrink-0">
          <p className="text-sm font-bold text-gray-900">{formatINR(lawyer.hourly_rate)}/hr</p>
          <p className="text-xs text-gray-500">Consult: {formatINR(lawyer.consultation_fee)}</p>
        </div>
      </div>

      <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
        <MapPin className="h-3 w-3" />
        {lawyer.city}, {lawyer.state}
        <span className="mx-1">·</span>
        <Clock className="h-3 w-3" />
        {lawyer.years_experience} yrs exp
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {lawyer.specializations.slice(0, 3).map((spec) => (
          <Badge key={spec} variant="neutral" className="text-xs">
            {spec}
          </Badge>
        ))}
        {lawyer.specializations.length > 3 && (
          <Badge variant="neutral" className="text-xs">+{lawyer.specializations.length - 3}</Badge>
        )}
      </div>

      <div className="flex flex-wrap gap-1 mb-3">
        {lawyer.languages.slice(0, 3).map((lang) => (
          <span key={lang} className="text-xs text-gray-500 bg-gray-100 px-1.5 py-0.5 rounded">
            {lang}
          </span>
        ))}
      </div>

      {matchReason && (
        <p className="text-xs text-blue-700 bg-blue-50 rounded p-2 mb-3">
          AI Match: {matchReason}
        </p>
      )}

      {!lawyer.available && (
        <Badge variant="warning" className="mb-3">Not Available</Badge>
      )}

      <div className="flex gap-2 mt-3">
        <Button size="sm" variant="secondary" onClick={() => onView?.(lawyer)} className="flex-1">
          View Profile
        </Button>
        <Button size="sm" onClick={() => onBook?.(lawyer)} className="flex-1" disabled={!lawyer.available}>
          Book Consultation
        </Button>
      </div>
    </div>
  );
}
