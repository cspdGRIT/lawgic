export function cn(...classes: (string | undefined | boolean | null)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatINR(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}

export function generateSessionId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

// Real Case.status values (backend/app/models/case.py): open, in_progress, closed,
// won, lost, appealed. 'analyzed'/'pending' are not real values — a couple of pages
// used to compare against them, which meant those checks could never match.
export function caseStatusStyle(status: string): string {
  const styles: Record<string, string> = {
    open: 'bg-zinc-800 text-gray-400',
    in_progress: 'bg-yellow-950 text-yellow-400',
    won: 'bg-green-950 text-green-400',
    lost: 'bg-red-950 text-red-400',
    appealed: 'bg-blue-950 text-blue-400',
    closed: 'bg-zinc-800 text-gray-500',
  };
  return styles[status] || 'bg-zinc-800 text-gray-400';
}

export function caseTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    criminal: 'Criminal',
    civil: 'Civil',
    corporate: 'Corporate',
    family: 'Family',
    property: 'Property',
    labour: 'Labour',
    consumer: 'Consumer',
    taxation: 'Taxation',
    ip: 'Intellectual Property',
  };
  return labels[type] || type;
}
