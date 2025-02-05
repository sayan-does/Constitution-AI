import React, { useState } from 'react';
import { Send, Upload, X, MessageSquare, Scale } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'bot';
  content: string;
  context?: string;
  legalReference?: {
    law: string;
    reference: string;
  };
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [context, setContext] = useState('');
  const [isContextVisible, setIsContextVisible] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      context: context || undefined,
    };

    // Simulated bot response
    const botResponse: Message = {
      id: (Date.now() + 1).toString(),
      type: 'bot',
      content: "Based on the provided context, here's my legal analysis...",
      legalReference: {
        law: "Indian Contract Act, 1872",
        reference: "Section 10 - All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object."
      }
    };

    setMessages([...messages, userMessage, botResponse]);
    setInput('');
    setContext('');
    setIsContextVisible(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-indigo-700 text-white py-4 px-6 shadow-lg">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <Scale className="w-8 h-8" />
          <h1 className="text-2xl font-bold">Indian Legal Assistant</h1>
        </div>
      </header>

      {/* Chat Container */}
      <div className="flex-1 max-w-4xl w-full mx-auto p-4 flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.type === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] ${
                  message.type === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white'
                } rounded-lg shadow-md p-4`}
              >
                {message.context && (
                  <div className="text-sm bg-indigo-100 text-indigo-800 p-2 rounded mb-2">
                    Context: {message.context}
                  </div>
                )}
                <p className="text-sm">{message.content}</p>
                {message.legalReference && (
                  <div className="mt-3 border-t pt-2">
                    <div className="bg-gray-50 p-3 rounded text-sm">
                      <p className="font-semibold text-indigo-700">{message.legalReference.law}</p>
                      <p className="text-gray-600 mt-1">{message.legalReference.reference}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          {isContextVisible && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-700">Context</label>
                <button
                  onClick={() => setIsContextVisible(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              <textarea
                value={context}
                onChange={(e) => setContext(e.target.value)}
                className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                rows={3}
                placeholder="Paste your context here or upload a document..."
              />
              <div className="mt-2 flex gap-2">
                <button className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-800">
                  <Upload className="w-4 h-4" />
                  Upload Document
                </button>
                <span className="text-sm text-gray-500">(PDF, DOC, or Image)</span>
              </div>
            </div>
          )}

          <div className="flex gap-2">
            {!isContextVisible && (
              <button
                onClick={() => setIsContextVisible(true)}
                className="flex items-center justify-center p-2 text-gray-500 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
              >
                <Upload className="w-5 h-5" />
              </button>
            )}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask your legal question..."
              className="flex-1 p-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <button
              onClick={handleSend}
              className="flex items-center justify-center p-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;