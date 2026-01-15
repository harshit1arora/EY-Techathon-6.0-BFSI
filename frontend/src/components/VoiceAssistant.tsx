import React, { useState, useEffect, useCallback } from 'react';
import { Mic, MicOff, X, Volume2, VolumeX, MessageCircle } from 'lucide-react';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useTextToSpeech } from '@/hooks/useTextToSpeech';
import { t, Language } from '@/data/translations';

interface VoiceAssistantProps {
  language: Language;
  onMessage: (message: string) => void;
  lastBotMessage?: string;
}

const VoiceAssistant: React.FC<VoiceAssistantProps> = ({ 
  language, 
  onMessage,
  lastBotMessage 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [conversationHistory, setConversationHistory] = useState<Array<{
    type: 'user' | 'bot';
    text: string;
  }>>([]);

  const { 
    isListening, 
    transcript, 
    startListening, 
    stopListening, 
    isSupported: speechSupported,
    error: speechError
  } = useSpeechRecognition(language);

  const {
    speak,
    stop: stopSpeaking,
    isSpeaking,
    isSupported: ttsSupported
  } = useTextToSpeech(language);

  // Speak bot messages when TTS is enabled
  useEffect(() => {
    if (lastBotMessage && ttsEnabled && isOpen && ttsSupported) {
      // Clean the message for TTS (remove emojis and special formatting)
      const cleanMessage = lastBotMessage
        .replace(/[\u{1F600}-\u{1F6FF}]/gu, '')
        .replace(/[📋💰📅💳📊✅✨🎉⏱️👤🔍]/g, '')
        .replace(/\n+/g, '. ')
        .trim();
      
      if (cleanMessage) {
        speak(cleanMessage);
      }
    }
  }, [lastBotMessage, ttsEnabled, isOpen, speak, ttsSupported]);

  // Handle transcript completion
  useEffect(() => {
    if (transcript && !isListening && isOpen) {
      // User finished speaking, send the message
      setConversationHistory(prev => [...prev, { type: 'user', text: transcript }]);
      onMessage(transcript);
    }
  }, [transcript, isListening, isOpen, onMessage]);

  // Add bot response to conversation history
  useEffect(() => {
    if (lastBotMessage && isOpen) {
      setConversationHistory(prev => {
        const lastEntry = prev[prev.length - 1];
        if (lastEntry?.type === 'bot' && lastEntry.text === lastBotMessage) {
          return prev;
        }
        return [...prev, { type: 'bot', text: lastBotMessage }];
      });
    }
  }, [lastBotMessage, isOpen]);

  const toggleVoiceAssistant = useCallback(() => {
    if (isOpen) {
      stopListening();
      stopSpeaking();
      setIsOpen(false);
    } else {
      setIsOpen(true);
      setConversationHistory([]);
    }
  }, [isOpen, stopListening, stopSpeaking]);

  const handleMicToggle = useCallback(() => {
    if (isListening) {
      stopListening();
    } else {
      if (isSpeaking) {
        stopSpeaking();
      }
      startListening();
    }
  }, [isListening, isSpeaking, startListening, stopListening, stopSpeaking]);

  const toggleTTS = useCallback(() => {
    if (isSpeaking) {
      stopSpeaking();
    }
    setTtsEnabled(prev => !prev);
  }, [isSpeaking, stopSpeaking]);

  if (!speechSupported) {
    return null;
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={toggleVoiceAssistant}
        className={`fixed bottom-24 right-6 z-50 w-16 h-16 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 transform hover:scale-110 ${
          isOpen 
            ? 'bg-red-500 hover:bg-red-600' 
            : 'bg-gradient-to-br from-primary to-primary-light hover:shadow-glow'
        }`}
        aria-label={isOpen ? 'Close voice assistant' : 'Open voice assistant'}
      >
        {isOpen ? (
          <X className="w-7 h-7 text-white" />
        ) : (
          <MessageCircle className="w-7 h-7 text-white" />
        )}
      </button>

      {/* Voice Assistant Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-gradient-to-br from-background via-blue-50 to-yellow-50 w-full max-w-md mx-4 rounded-3xl shadow-2xl overflow-hidden animate-scale-up">
            {/* Header */}
            <div className="bg-gradient-primary px-6 py-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                  <span className="text-primary font-bold text-xl">T</span>
                </div>
                <div>
                  <h3 className="text-white font-bold">
                    {language === 'hi' ? 'वॉइस असिस्टेंट' : 'Voice Assistant'}
                  </h3>
                  <p className="text-secondary-light text-xs">
                    {language === 'hi' ? 'बोलकर बात करें' : 'Speak to interact'}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleTTS}
                  className={`p-2 rounded-full transition-colors ${
                    ttsEnabled ? 'bg-white/20 text-white' : 'bg-white/10 text-white/50'
                  }`}
                  aria-label={ttsEnabled ? 'Disable voice output' : 'Enable voice output'}
                >
                  {ttsEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
                </button>
                <button
                  onClick={toggleVoiceAssistant}
                  className="p-2 bg-white/20 rounded-full text-white hover:bg-white/30 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Conversation Area */}
            <div className="h-64 overflow-y-auto p-4 space-y-3">
              {conversationHistory.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
                  <Mic className="w-12 h-12 mb-3 opacity-30" />
                  <p className="text-sm">
                    {language === 'hi' 
                      ? 'माइक बटन दबाएं और बोलना शुरू करें' 
                      : 'Tap the mic button and start speaking'}
                  </p>
                </div>
              ) : (
                conversationHistory.map((entry, idx) => (
                  <div
                    key={idx}
                    className={`flex ${entry.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm ${
                        entry.type === 'user'
                          ? 'bg-primary text-white rounded-br-sm'
                          : 'bg-white text-foreground border border-border rounded-bl-sm shadow-sm'
                      }`}
                    >
                      {entry.text.length > 150 
                        ? entry.text.substring(0, 150) + '...' 
                        : entry.text}
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Status & Controls */}
            <div className="px-6 py-4 bg-white/50 border-t border-border">
              {/* Status Text */}
              <div className="text-center mb-4">
                {isListening && (
                  <div className="flex items-center justify-center space-x-2 text-red-500">
                    <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                    <span className="text-sm font-medium">
                      {language === 'hi' ? 'सुन रहा है...' : 'Listening...'}
                    </span>
                  </div>
                )}
                {isSpeaking && !isListening && (
                  <div className="flex items-center justify-center space-x-2 text-primary">
                    <Volume2 className="w-4 h-4 animate-pulse" />
                    <span className="text-sm font-medium">
                      {language === 'hi' ? 'बोल रहा है...' : 'Speaking...'}
                    </span>
                  </div>
                )}
                {transcript && isListening && (
                  <p className="text-sm text-muted-foreground mt-2 italic">
                    "{transcript}"
                  </p>
                )}
                {speechError && (
                  <p className="text-sm text-red-500 mt-2">
                    {language === 'hi' ? 'त्रुटि: ' : 'Error: '}{speechError}
                  </p>
                )}
              </div>

              {/* Main Mic Button */}
              <div className="flex justify-center">
                <button
                  onClick={handleMicToggle}
                  className={`w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 transform hover:scale-105 ${
                    isListening
                      ? 'bg-red-500 animate-pulse shadow-lg shadow-red-500/50'
                      : 'bg-gradient-to-br from-primary to-primary-light shadow-lg hover:shadow-glow'
                  }`}
                >
                  {isListening ? (
                    <MicOff className="w-8 h-8 text-white" />
                  ) : (
                    <Mic className="w-8 h-8 text-white" />
                  )}
                </button>
              </div>

              {/* Hint */}
              <p className="text-center text-xs text-muted-foreground mt-4">
                {isListening 
                  ? (language === 'hi' ? 'बोलना बंद करने के लिए टैप करें' : 'Tap to stop')
                  : (language === 'hi' ? 'बोलने के लिए टैप करें' : 'Tap to speak')}
              </p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default VoiceAssistant;
