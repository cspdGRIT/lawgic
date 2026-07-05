import { useLocation } from 'react-router-dom';
import { Bell, ChevronRight } from 'lucide-react';
import { useAppStore } from '../../store';

const routeMap: Record<string, { title: string; breadcrumb: string[] }> = {
  '/dashboard': { title: 'Dashboard', breadcrumb: ['Home', 'Dashboard'] },
  '/assistant': { title: 'AI Assistant', breadcrumb: ['Home', 'AI Assistant'] },
  '/cases': { title: 'Case Analysis', breadcrumb: ['Home', 'Case Analysis'] },
  '/documents': { title: 'Document Generator', breadcrumb: ['Home', 'Documents'] },
  '/lawyers': { title: 'Find Lawyers', breadcrumb: ['Home', 'Lawyers'] },
  '/research': { title: 'Legal Research', breadcrumb: ['Home', 'Research'] },
  '/education': { title: 'Legal Education', breadcrumb: ['Home', 'Education'] },
};

export default function Header() {
  const { pathname } = useLocation();
  const user = useAppStore((s) => s.user);
  const route = routeMap[pathname] || { title: 'Lawgic', breadcrumb: ['Home'] };

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div>
        <h1 className="text-xl font-serif font-semibold text-gray-900">{route.title}</h1>
        <div className="flex items-center gap-1 text-xs text-gray-500 mt-0.5">
          {route.breadcrumb.map((crumb, idx) => (
            <span key={crumb} className="flex items-center gap-1">
              {idx > 0 && <ChevronRight className="h-3 w-3" />}
              <span className={idx === route.breadcrumb.length - 1 ? 'text-gray-900 font-medium' : ''}>
                {crumb}
              </span>
            </span>
          ))}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors relative">
          <Bell className="h-5 w-5 text-gray-600" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-gray-900 rounded-full" />
        </button>

        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center text-white text-sm font-bold">
            {user?.full_name?.charAt(0)?.toUpperCase() || 'U'}
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-gray-900">{user?.full_name || 'User'}</p>
            <p className="text-xs text-gray-500 capitalize">{user?.user_type || 'client'}</p>
          </div>
        </div>
      </div>
    </header>
  );
}
