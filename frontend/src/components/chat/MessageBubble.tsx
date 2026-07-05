import { ChatMessage } from '../../types';
import { Badge } from '../ui/Badge';
import { Scale } from 'lucide-react';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[80%]">
          <div className="bg-gray-900 text-white rounded-2xl rounded-tr-sm px-4 py-3">
            <p className="text-sm whitespace-pre-wrap">{message.content}</p>
          </div>
          <p className="text-xs text-gray-400 text-right mt-1">
            {new Date(message.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="flex gap-3 max-w-[85%]">
        <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
          <Scale className="h-4 w-4 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-2 mb-1">
            {message.agent_used && (
              <Badge variant="info" className="text-xs">{message.agent_used}</Badge>
            )}
            {message.confidence_score !== undefined && (
              <span className="text-xs text-gray-500">
                Confidence: {Math.round(message.confidence_score * 100)}%
              </span>
            )}
          </div>
          <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
            <p className="text-sm whitespace-pre-wrap text-gray-800">{message.content}</p>
          </div>
          <p className="text-xs text-gray-400 mt-1">
            {new Date(message.timestamp).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    </div>
  );
}
