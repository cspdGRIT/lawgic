import { NavLink, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  LayoutDashboard,
  Compass,
  Bot,
  Scale,
  FileText,
  Users,
  Search,
  GraduationCap,
  LogOut,
  CreditCard,
  Zap,
  ShieldCheck,
} from 'lucide-react';
import { useAppStore } from '../../store';
import { paymentsAPI, authAPI } from '../../lib/api';
import { cn } from '../../lib/utils';
import type { Subscription } from '../../types';

interface SidebarProps {
  onClose?: () => void;
}

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/issue-navigator', icon: Compass, label: 'Describe Your Issue', badge: 'New' },
  { to: '/assistant', icon: Bot, label: 'AI Assistant', badge: 'AI' },
  { to: '/cases', icon: Scale, label: 'Case Analysis' },
  { to: '/documents', icon: FileText, label: 'Documents' },
  { to: '/lawyers', icon: Users, label: 'Find Lawyers' },
  { to: '/research', icon: Search, label: 'Legal Research' },
  { to: '/education', icon: GraduationCap, label: 'Education' },
  { to: '/pricing', icon: CreditCard, label: 'Plans & Billing' },
];

const adminNavItem = { to: '/admin/requests', icon: ShieldCheck, label: 'Access Requests' };

const PLAN_BADGE_CLASS: Record<string, string> = {
  free:  'bg-gray-700 text-gray-300',
  pro:   'bg-blue-600 text-white',
  firm:  'bg-purple-600 text-white',
};

export default function Sidebar({ onClose }: SidebarProps) {
  const { user, logout } = useAppStore();
  const navigate = useNavigate();

  const { data: sub } = useQuery<Subscription>({
    queryKey: ['subscription'],
    queryFn: paymentsAPI.subscription,
    enabled: !!user,
    staleTime: 1000 * 60 * 5,
  });
  const currentPlan = sub?.plan ?? 'free';

  const handleLogout = async () => {
    try { await authAPI.logout() } catch { /* ignore — cookie cleared server-side best-effort */ }
    logout();
    navigate('/login');
  };

  return (
    <div className="flex flex-col h-full bg-gray-900 text-white w-64">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Scale className="h-6 w-6 text-white" />
          <span className="text-xl font-serif font-bold tracking-wide">LAWGIC</span>
        </div>
        <p className="text-xs text-gray-400 mt-1">The Legal AId</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {(user?.user_type === 'admin' ? [...navItems, adminNavItem] : navItems).map(({ to, icon: Icon, label, badge }: any) => (
          <NavLink
            key={to}
            to={to}
            onClick={onClose}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors group',
                isActive
                  ? 'bg-white text-gray-900'
                  : 'text-gray-300 hover:bg-gray-800 hover:text-white'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon className={cn('h-4 w-4 flex-shrink-0', isActive ? 'text-gray-900' : 'text-gray-400 group-hover:text-white')} />
                <span className="flex-1">{label}</span>
                {badge && (
                  <span className={cn(
                    'text-xs px-1.5 py-0.5 rounded font-semibold',
                    isActive ? 'bg-gray-900 text-white' : 'bg-gray-700 text-gray-300'
                  )}>
                    {badge}
                  </span>
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* User section */}
      <div className="border-t border-gray-700 p-4">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-9 h-9 bg-gray-600 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.full_name || 'User'}</p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className={cn('text-xs px-1.5 py-0.5 rounded font-semibold uppercase', PLAN_BADGE_CLASS[currentPlan])}>
                {currentPlan}
              </span>
              {currentPlan === 'free' && (
                <button
                  onClick={() => { navigate('/pricing'); onClose?.(); }}
                  className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-0.5"
                >
                  <Zap className="w-3 h-3" />
                  Upgrade
                </button>
              )}
            </div>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 text-gray-400 hover:text-white text-xs transition-colors w-full px-2 py-1.5 rounded hover:bg-gray-800"
        >
          <LogOut className="h-3.5 w-3.5" />
          Sign Out
        </button>
      </div>
    </div>
  );
}
