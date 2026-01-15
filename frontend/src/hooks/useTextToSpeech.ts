import { useState, useCallback, useRef, useEffect } from 'react';

interface TextToSpeechHook {
  speak: (text: string) => void;
  stop: () => void;
  isSpeaking: boolean;
  isSupported: boolean;
  setVoice: (voice: SpeechSynthesisVoice) => void;
  voices: SpeechSynthesisVoice[];
  setRate: (rate: number) => void;
  setPitch: (pitch: number) => void;
}

export const useTextToSpeech = (language: 'en' | 'hi' = 'en'): TextToSpeechHook => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [selectedVoice, setSelectedVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [rate, setRate] = useState(1);
  const [pitch, setPitch] = useState(1);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const isSupported = typeof window !== 'undefined' && 'speechSynthesis' in window;

  useEffect(() => {
    if (!isSupported) return;

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);
      
      // Try to find a voice matching the language
      const langCode = language === 'hi' ? 'hi' : 'en';
      const matchingVoice = availableVoices.find(v => v.lang.startsWith(langCode)) || availableVoices[0];
      if (matchingVoice && !selectedVoice) {
        setSelectedVoice(matchingVoice);
      }
    };

    loadVoices();
    window.speechSynthesis.onvoiceschanged = loadVoices;

    return () => {
      window.speechSynthesis.onvoiceschanged = null;
    };
  }, [isSupported, language]);

  // Update voice when language changes
  useEffect(() => {
    if (voices.length > 0) {
      const langCode = language === 'hi' ? 'hi' : 'en';
      const matchingVoice = voices.find(v => v.lang.startsWith(langCode)) || voices[0];
      setSelectedVoice(matchingVoice);
    }
  }, [language, voices]);

  const speak = useCallback((text: string) => {
    if (!isSupported || !text) return;

    // Stop any ongoing speech
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    
    if (selectedVoice) {
      utterance.voice = selectedVoice;
    }

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [isSupported, selectedVoice, rate, pitch, language]);

  const stop = useCallback(() => {
    if (!isSupported) return;
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  }, [isSupported]);

  const setVoice = useCallback((voice: SpeechSynthesisVoice) => {
    setSelectedVoice(voice);
  }, []);

  return {
    speak,
    stop,
    isSpeaking,
    isSupported,
    setVoice,
    voices,
    setRate,
    setPitch,
  };
};
