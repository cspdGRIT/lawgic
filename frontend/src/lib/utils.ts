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
