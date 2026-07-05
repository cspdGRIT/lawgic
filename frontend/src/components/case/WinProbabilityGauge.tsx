interface WinProbabilityGaugeProps {
  probability: number;
}

export function WinProbabilityGauge({ probability }: WinProbabilityGaugeProps) {
  const radius = 80;
  const circumference = Math.PI * radius;
  const dashOffset = circumference - (probability / 100) * circumference;

  const getColor = () => {
    if (probability >= 60) return '#16a34a';
    if (probability >= 40) return '#ca8a04';
    return '#dc2626';
  };

  const getLabel = () => {
    if (probability >= 70) return 'Strong';
    if (probability >= 50) return 'Moderate';
    if (probability >= 30) return 'Weak';
    return 'Low';
  };

  const color = getColor();

  return (
    <div className="flex flex-col items-center">
      <svg width="220" height="130" viewBox="0 0 220 130">
        {/* Background arc */}
        <path
          d="M 20 110 A 90 90 0 0 1 200 110"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth="16"
          strokeLinecap="round"
        />
        {/* Foreground arc */}
        <path
          d="M 20 110 A 90 90 0 0 1 200 110"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
          style={{ transition: 'stroke-dashoffset 1s ease-in-out, stroke 0.3s ease' }}
        />
        {/* Center text */}
        <text x="110" y="90" textAnchor="middle" className="text-4xl font-bold">
          <tspan fontSize="36" fontWeight="bold" fill={color}>
            {probability}%
          </tspan>
        </text>
        <text x="110" y="112" textAnchor="middle">
          <tspan fontSize="12" fill="#6b7280">
            {getLabel()} Chances
          </tspan>
        </text>
      </svg>
      <p className="text-sm font-medium text-gray-600 mt-1">Win Probability</p>
    </div>
  );
}
