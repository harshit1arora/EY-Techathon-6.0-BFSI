import React from 'react';
import { Bot } from 'lucide-react';

interface TypingIndicatorProps {
  agentName?: string;
}

const TypingIndicator: React.FC<TypingIndicatorProps> = ({ agentName = 'AI Assistant' }) => {
  return (
    <div className="flex items-start space-x-3 animate-fade-in">
      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-primary/80 flex items-center justify-center shadow-lg">
        <Bot className="w-5 h-5 text-primary-foreground" />
      </div>
      <div className="bg-card border border-border rounded-2xl rounded-tl-none px-4 py-3 shadow-md">
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-muted-foreground">{agentName} is typing</span>
          <div className="flex space-x-1">
            <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 bg-primary rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
