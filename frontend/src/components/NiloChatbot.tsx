import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  X,
  Send,
  Bot,
  User,
  Copy,
  Check,
  Code2,
  Bug,
  HelpCircle,
  Lightbulb,
  Terminal,
  Zap
} from 'lucide-react';
import { api } from '../services/api';

interface NiloChatbotProps {
  isOpen: boolean;
  onClose: () => void;
  activeCode?: string;
  activeError?: string;
  activeStage?: string;
}

interface Message {
  id: string;
  sender: 'nilo' | 'user';
  text: string;
  timestamp: string;
  suggestedActions?: string[];
  ruleReferences?: string[];
}

export const NiloChatbot: React.FC<NiloChatbotProps> = ({
  isOpen,
  onClose,
  activeCode,
  activeError,
  activeStage
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'init-1',
      sender: 'nilo',
      text: `👋 Hey Engineer! I'm **Nilo**, your AI DevOps & Code Migration Specialist.\n\nI can help you debug AST parse warnings, translate breaking PayFlow v1 patterns to v2, or diagnose why sandboxed Pytest validations failed.\n\nSelect a quick prompt below or ask me anything!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggestedActions: [
        'Why did my patch fail validation?',
        'Explain PayFlow v2 breaking changes',
        'How to run local benchmark',
        'Teach me AST analysis'
      ]
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Contextual helper when activeError changes
  useEffect(() => {
    if (activeError && activeError.trim()) {
      // Offer prompt button in chat
    }
  }, [activeError]);

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isTyping) return;

    const userMsg: Message = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const resp = await api.chatWithNilo({
        message: textToSend,
        code_context: activeCode,
        error_context: activeError,
        current_stage: activeStage
      });

      const niloMsg: Message = {
        id: `nilo-${Date.now()}`,
        sender: 'nilo',
        text: resp.reply,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggestedActions: resp.suggested_actions,
        ruleReferences: resp.rule_references
      };
      setMessages(prev => [...prev, niloMsg]);
    } catch (err) {
      const errorMsg: Message = {
        id: `err-${Date.now()}`,
        sender: 'nilo',
        text: "I encountered a hiccup connecting to the local migration engine. Make sure the backend server is running!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const quickActionChips = [
    { label: 'Why did my patch fail validation?', icon: Bug },
    { label: 'Explain PayFlow v2 breaking changes', icon: Zap },
    { label: 'How to run local benchmark', icon: Terminal },
    { label: 'Teach me AST analysis', icon: Code2 }
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="w-full max-w-lg h-full flex flex-col bg-[#FBF9F5] dark:bg-[#121218] border-l border-black/10 dark:border-white/10 shadow-2xl shadow-[#87A7D0]/15 transition-colors">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-black/10 dark:border-white/10 bg-white/50 dark:bg-[#0B0C10]/60 backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#87A7D0] to-[#5C85B7] p-0.5 shadow-md shadow-[#87A7D0]/25">
                <div className="w-full h-full rounded-[10px] bg-[#0B0C10] flex items-center justify-center">
                  <Bot className="w-5 h-5 text-[#87A7D0]" />
                </div>
              </div>
              <span className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-white dark:border-[#0B0C10] rounded-full" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm tracking-wide text-gray-900 dark:text-white">
                  Nilo AI Assistant
                </h3>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#87A7D0]/15 text-[#3D6390] dark:text-[#87A7D0] border border-[#87A7D0]/30 font-bold">
                  DevOps Specialist
                </span>
              </div>
              <p className="text-[11px] text-gray-500 dark:text-gray-400">
                Deterministic Code Migration & Sandbox Diagnostics
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5 transition cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Quick Diagnostic Banner if active error exists */}
        {activeError && (
          <div className="px-4 py-2.5 bg-amber-500/10 border-b border-amber-500/20 flex items-center justify-between text-xs text-amber-700 dark:text-amber-300">
            <div className="flex items-center gap-2 truncate pr-2">
              <Bug className="w-4 h-4 shrink-0 text-amber-500" />
              <span className="truncate font-mono">Failure trace detected in workspace</span>
            </div>
            <button
              onClick={() => handleSend("Diagnose the validation failure in my workspace")}
              className="shrink-0 px-2 py-1 rounded bg-amber-500/20 hover:bg-amber-500/30 font-medium transition text-[11px]"
            >
              Diagnose
            </button>
          </div>
        )}

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((m) => (
            <div
              key={m.id}
              className={`flex gap-3 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {m.sender === 'nilo' && (
                <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-[#87A7D0] to-[#5C85B7] p-0.5 shrink-0 mt-0.5 shadow-sm">
                  <div className="w-full h-full rounded-[6px] bg-[#0B0C10] flex items-center justify-center">
                    <Sparkles className="w-3.5 h-3.5 text-[#87A7D0]" />
                  </div>
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl px-4 py-3 text-xs leading-relaxed transition-colors shadow-sm ${
                  m.sender === 'user'
                    ? 'bg-[#87A7D0] text-slate-950 font-medium rounded-tr-sm'
                    : 'bg-white dark:bg-[#1A1A24] border border-black/10 dark:border-white/10 text-gray-800 dark:text-gray-200 rounded-tl-sm'
                }`}
              >
                {/* Message Body with Markdown formatting support */}
                <div className="prose prose-sm dark:prose-invert max-w-none text-xs space-y-2 whitespace-pre-wrap">
                  {m.text}
                </div>

                {/* Suggested Action Chips */}
                {m.suggestedActions && m.suggestedActions.length > 0 && (
                  <div className="mt-3 pt-2.5 border-t border-black/10 dark:border-white/10 flex flex-wrap gap-1.5">
                    {m.suggestedActions.map((action, i) => (
                      <button
                        key={i}
                        onClick={() => handleSend(action)}
                        className="text-[11px] px-2.5 py-1 rounded-lg bg-[#87A7D0]/10 hover:bg-[#87A7D0]/20 text-[#3D6390] dark:text-[#87A7D0] border border-[#87A7D0]/25 transition flex items-center gap-1 font-semibold cursor-pointer"
                      >
                        <Lightbulb className="w-3 h-3 text-[#D4AF37]" />
                        {action}
                      </button>
                    ))}
                  </div>
                )}

                {/* Footer time and copy */}
                <div className="mt-2 flex items-center justify-between text-[10px] text-gray-400">
                  <span>{m.timestamp}</span>
                  {m.sender === 'nilo' && (
                    <button
                      onClick={() => handleCopy(m.text, m.id)}
                      className="hover:text-gray-600 dark:hover:text-gray-200 transition"
                      title="Copy response"
                    >
                      {copiedId === m.id ? (
                        <Check className="w-3 h-3 text-emerald-400" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  )}
                </div>
              </div>

              {m.sender === 'user' && (
                <div className="w-7 h-7 rounded-lg bg-indigo-700 text-white flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))}

          {isTyping && (
            <div className="flex gap-3 justify-start items-center">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-[#87A7D0] to-[#5C85B7] p-0.5 shrink-0 shadow-sm">
                <div className="w-full h-full rounded-[6px] bg-[#0B0C10] flex items-center justify-center">
                  <Sparkles className="w-3.5 h-3.5 text-[#87A7D0]" />
                </div>
              </div>
              <div className="px-4 py-2 rounded-2xl bg-white dark:bg-[#1A1A24] border border-black/10 dark:border-white/10 text-xs text-gray-400 flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-[#87A7D0] animate-bounce" />
                <div className="w-1.5 h-1.5 rounded-full bg-[#5C85B7] animate-bounce [animation-delay:0.2s]" />
                <div className="w-1.5 h-1.5 rounded-full bg-[#D4AF37] animate-bounce [animation-delay:0.4s]" />
                <span className="ml-1 text-[11px]">Nilo is analyzing...</span>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Quick Action Chips Bar */}
        <div className="px-4 py-2 border-t border-black/10 dark:border-white/10 bg-black/5 dark:bg-[#0B0C10]/40 overflow-x-auto flex gap-1.5 scrollbar-none">
          {quickActionChips.map((chip, idx) => {
            const Icon = chip.icon;
            return (
              <button
                key={idx}
                onClick={() => handleSend(chip.label)}
                className="shrink-0 flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] font-semibold bg-white dark:bg-white/5 hover:bg-[#87A7D0]/10 text-gray-700 dark:text-gray-300 border border-black/10 dark:border-white/10 hover:border-[#87A7D0]/40 transition cursor-pointer"
              >
                <Icon className="w-3 h-3 text-[#3D6390] dark:text-[#87A7D0]" />
                <span>{chip.label}</span>
              </button>
            );
          })}
        </div>

        {/* Input Footer */}
        <div className="p-4 border-t border-black/10 dark:border-white/10 bg-white/70 dark:bg-[#0B0C10]/70">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Nilo about AST errors, PayFlow v2, or Pytest..."
              className="flex-1 px-3.5 py-2.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 text-xs focus:outline-none focus:border-[#87A7D0] text-gray-900 dark:text-white placeholder-gray-400"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="p-2.5 rounded-xl bg-[#87A7D0] hover:bg-[#7295BF] text-slate-950 font-bold disabled:opacity-40 transition shadow-md shadow-[#87A7D0]/20 cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="mt-2 flex items-center justify-between text-[10px] text-gray-400">
            <span>Powered by deterministic AST & localized rules</span>
            <kbd className="font-mono">Esc to close</kbd>
          </div>
        </div>
      </div>
    </div>
  );
};
