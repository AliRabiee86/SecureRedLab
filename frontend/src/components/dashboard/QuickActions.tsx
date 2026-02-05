import type { HTMLAttributes } from 'react';
import { Scan, Target, FileText, Settings, Play, Plus } from 'lucide-react';
import Button from '../common/Button';
import Card from '../common/Card';

interface QuickActionsProps extends HTMLAttributes<HTMLDivElement> {
  onNewScan?: () => void;
  onNewAttack?: () => void;
  onViewReports?: () => void;
  onSettings?: () => void;
}

export function QuickActions({
  onNewScan,
  onNewAttack,
  onViewReports,
  onSettings,
  className,
  ...props
}: QuickActionsProps) {
  return (
    <Card className={className} {...props}>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
            Quick Actions
          </h3>
          <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center">
            <Play className="w-5 h-5 text-primary" />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {/* New Scan */}
          <Button
            variant="primary"
            onClick={onNewScan}
            className="justify-start space-x-3 h-auto py-4"
          >
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <Scan className="w-5 h-5" />
            </div>
            <div className="text-left">
              <div className="font-semibold">New Scan</div>
              <div className="text-xs opacity-90">Start a reconnaissance scan</div>
            </div>
            <Plus className="w-4 h-4 ml-auto" />
          </Button>

          {/* New Attack */}
          <Button
            variant="danger"
            onClick={onNewAttack}
            className="justify-start space-x-3 h-auto py-4"
          >
            <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center flex-shrink-0">
              <Target className="w-5 h-5" />
            </div>
            <div className="text-left">
              <div className="font-semibold">New Attack</div>
              <div className="text-xs opacity-90">Launch an exploitation</div>
            </div>
            <Plus className="w-4 h-4 ml-auto" />
          </Button>

          {/* View Reports */}
          <Button
            variant="secondary"
            onClick={onViewReports}
            className="justify-start space-x-3 h-auto py-4"
          >
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-primary" />
            </div>
            <div className="text-left">
              <div className="font-semibold text-gray-900 dark:text-white">View Reports</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Access all reports
              </div>
            </div>
          </Button>

          {/* Settings */}
          <Button
            variant="secondary"
            onClick={onSettings}
            className="justify-start space-x-3 h-auto py-4"
          >
            <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center flex-shrink-0">
              <Settings className="w-5 h-5 text-primary" />
            </div>
            <div className="text-left">
              <div className="font-semibold text-gray-900 dark:text-white">Settings</div>
              <div className="text-xs text-gray-600 dark:text-gray-400">
                Configure platform
              </div>
            </div>
          </Button>
        </div>

        {/* Tips Section */}
        <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="text-xs text-gray-600 dark:text-gray-400">
            💡 <span className="font-medium">Pro Tip:</span> Use Ctrl+K to quickly open command palette
          </div>
        </div>
      </div>
    </Card>
  );
}
