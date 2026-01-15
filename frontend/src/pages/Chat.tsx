import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Send, Upload, CheckCircle, Loader, MessageSquare, User, Bot, Phone, Download, Shield, Clock, Star, Globe, Mic, MicOff, FileSearch } from 'lucide-react';
import { translations, t, Language } from '@/data/translations';
import { extractSalarySlipData, formatExtractionForDisplay, extractionToJSON } from '@/utils/salaryExtractor';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { sendChatMessage } from '@/services/api';
import VoiceAssistant from '@/components/VoiceAssistant';
import EMICalculator from '@/components/EMICalculator';
import TypingIndicator from '@/components/TypingIndicator';
import DocumentPreview from '@/components/DocumentPreview';
import DocumentChecklist from '@/components/DocumentChecklist';
import FAQDrawer from '@/components/FAQDrawer';

// Complete Customer Data
const mockCustomers = [
  { id: 'CUST001', name: 'Asha Verma', phone: '9810000001', city: 'Pune', salary: 60000, score: 745, limit: 300000 },
  { id: 'CUST002', name: 'Rahul Sharma', phone: '9810000002', city: 'Delhi', salary: 45000, score: 712, limit: 200000 },
  { id: 'CUST003', name: 'Sneha Iyer', phone: '9810000003', city: 'Bengaluru', salary: 85000, score: 780, limit: 400000 },
  { id: 'CUST004', name: 'Vikram Singh', phone: '9810000004', city: 'Lucknow', salary: 30000, score: 690, limit: 150000 },
  { id: 'CUST005', name: 'Nisha Patel', phone: '9810000005', city: 'Ahmedabad', salary: 52000, score: 710, limit: 250000 },
  { id: 'CUST006', name: 'Arjun Rao', phone: '9810000006', city: 'Hyderabad', salary: 70000, score: 760, limit: 350000 },
  { id: 'CUST007', name: 'Meera Desai', phone: '9810000007', city: 'Surat', salary: 40000, score: 695, limit: 180000 },
  { id: 'CUST008', name: 'Karan Mehta', phone: '9810000008', city: 'Mumbai', salary: 65000, score: 735, limit: 320000 },
  { id: 'CUST009', name: 'Priya Nair', phone: '9810000009', city: 'Kochi', salary: 48000, score: 725, limit: 280000 },
  { id: 'CUST010', name: 'Sourav Ghosh', phone: '9810000010', city: 'Kolkata', salary: 90000, score: 790, limit: 500000 }
];

const TataCapitalLoanChatbot = () => {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sessionId] = useState(() => {
    const saved = localStorage.getItem('loan_chat_session_id');
    if (saved) return saved;
    const newId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('loan_chat_session_id', newId);
    return newId;
  });
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [previewFile, setPreviewFile] = useState<File | null>(null);
  const [currentStage, setCurrentStage] = useState('conversation');
  const [language, setLanguage] = useState<Language>('en');
  const [sessionData, setSessionData] = useState({
    customerData: null as any,
    loanAmount: null as number | null,
    tenure: null as number | null,
    interestRate: 10.5,
    emi: null as number | null,
    phoneVerified: false,
    eligibilityStatus: null,
    userName: ''
  });
  const [conversationState, setConversationState] = useState('greeting');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Speech recognition hook
  const { isListening, transcript, startListening, stopListening, isSupported: isSpeechSupported } = useSpeechRecognition(language);

  const stages = [
    { id: 'conversation', label: t('stageConversation', language), icon: MessageSquare },
    { id: 'verification', label: t('stageVerification', language), icon: CheckCircle },
    { id: 'underwriting', label: t('stageCreditCheck', language), icon: Star },
    { id: 'sanction', label: t('stageSanction', language), icon: CheckCircle }
  ];

  useEffect(() => {
    addBotMessage(t('agentMaster', language), t('welcomeMessage', language));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addBotMessage = (agent: string, content: string, options: any = {}) => {
    setMessages(prev => [...prev, {
      id: Date.now() + Math.random(), type: 'bot', agent, content,
      timestamp: new Date(), ...options
    }]);
  };

  const addUserMessage = (content: string) => {
    setMessages(prev => [...prev, {
      id: Date.now(), type: 'user', content, timestamp: new Date()
    }]);
  };

  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'hi' : 'en');
  };

  const processConversation = async (userInput: string) => {
    setIsTyping(true);
    try {
      const response = await sendChatMessage({
        session_id: sessionId,
        message: userInput
      });

      setIsTyping(false);
      
      // Map backend stage to frontend stage
      if (response.debug_stage) {
        const stageMap: Record<string, string> = {
          'start': 'conversation',
          'sales': 'conversation',
          'verification': 'verification',
          'underwriting': 'underwriting',
          'sanction': 'sanction'
        };
        const mappedStage = stageMap[response.debug_stage];
        if (mappedStage) {
          setCurrentStage(mappedStage);
        }
      }

      // Extract agent name from debug_stage or use default
      let agentName = t('agentMaster', language);
      if (response.debug_stage) {
        const agentMap: Record<string, string> = {
          'sales': t('agentSales', language),
          'verification': t('agentVerification', language),
          'underwriting': t('agentUnderwriting', language),
          'sanction': t('agentSanction', language)
        };
        agentName = agentMap[response.debug_stage] || agentName;
      }

      addBotMessage(agentName, response.response, {
        downloadable: !!response.sanction_letter_url,
        sanctionUrl: response.sanction_letter_url
      });

      // Handle salary slip requirement in UI
      if (response.underwriting_status === 'require_salary_slip') {
        addBotMessage(t('agentUnderwriting', language), "You can upload your salary slip using the attachment icon below.", { 
          showUpload: true 
        });
      }

    } catch (error) {
      console.error('Chat API Error:', error);
      setIsTyping(false);
      addBotMessage(t('agentMaster', language), "Temporary issue. Please retry.", { error: true });
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreviewFile(file);
  };

  const handleFileUploadConfirm = async () => {
    if (!previewFile) return;

    setUploadedFile(previewFile);
    setPreviewFile(null);
    addUserMessage(`📎 ${previewFile.name}`);
    setIsTyping(true);
    
    // Use salary extractor
    const extractionResult = await extractSalarySlipData(previewFile, sessionData.customerData?.name);
    
    setIsTyping(false);
    
    if (extractionResult.success) {
      const displayText = formatExtractionForDisplay(extractionResult);
      const jsonData = extractionToJSON(extractionResult);
      
      // Add a message showing the extraction result
      addBotMessage(t('agentVerification', language), displayText);
      
      // Send extracted data to backend
      processConversation(`upload documents`);
    } else {
      addBotMessage(t('agentVerification', language), `${t('uploadError', language)}\n\n${extractionResult.errors?.join('\n')}`);
    }
  };

  const handleFileUploadCancel = () => {
    setPreviewFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Update input when speech recognition provides transcript
  useEffect(() => {
    if (transcript && !isListening) {
      setInput(transcript);
    }
  }, [transcript, isListening]);

  const handleSend = () => {
    const messageToSend = input.trim() || transcript.trim();
    if (!messageToSend) return;
    
    if (isListening) {
      stopListening();
    }
    
    addUserMessage(messageToSend);
    processConversation(messageToSend);
    setInput('');
  };

  const handleSuggestionClick = (s: string) => {
    addUserMessage(s);
    processConversation(s);
  };

  // Handle voice assistant messages
  const handleVoiceMessage = useCallback((message: string) => {
    addUserMessage(message);
    processConversation(message);
  }, []);

  // Get last bot message for TTS
  const lastBotMessage = messages.filter(m => m.type === 'bot').slice(-1)[0]?.content;

  const getAgentColor = (agent: string) => {
    const colors: Record<string, string> = {
      [t('agentMaster', 'en')]: 'from-agent-master to-agent-master/80',
      [t('agentMaster', 'hi')]: 'from-agent-master to-agent-master/80',
      [t('agentSales', 'en')]: 'from-agent-sales to-agent-sales/80',
      [t('agentSales', 'hi')]: 'from-agent-sales to-agent-sales/80',
      [t('agentVerification', 'en')]: 'from-agent-verification to-agent-verification/80',
      [t('agentVerification', 'hi')]: 'from-agent-verification to-agent-verification/80',
      [t('agentUnderwriting', 'en')]: 'from-agent-underwriting to-agent-underwriting/80',
      [t('agentUnderwriting', 'hi')]: 'from-agent-underwriting to-agent-underwriting/80',
      [t('agentDocument', 'en')]: 'from-agent-document to-agent-document/80',
      [t('agentDocument', 'hi')]: 'from-agent-document to-agent-document/80',
      [t('agentSanction', 'en')]: 'from-agent-sanction to-agent-sanction/80',
      [t('agentSanction', 'hi')]: 'from-agent-sanction to-agent-sanction/80',
    };
    return `bg-gradient-to-r ${colors[agent] || 'from-primary to-primary/80'}`;
  };

  const stageIdx = stages.findIndex(s => s.id === currentStage);

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-background via-blue-50 to-yellow-50">
      {/* Header */}
      <header className="bg-gradient-primary shadow-xl border-b-4 border-secondary">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-14 h-14 bg-gradient-to-br from-secondary to-secondary-dark rounded-xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform">
              <span className="text-primary font-bold text-3xl">T</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">{t('appTitle', language)}</h1>
              <p className="text-xs text-secondary-light font-semibold tracking-wide">{t('appSubtitle', language)}</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {/* Track Status Link */}
            <Link 
              to="/status"
              className="flex items-center space-x-2 bg-secondary hover:bg-secondary-light px-4 py-2 rounded-lg transition-all transform hover:scale-105"
            >
              <FileSearch className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-primary">{language === 'hi' ? 'स्थिति देखें' : 'Track Status'}</span>
            </Link>
            {/* Language Toggle */}
            <button 
              onClick={toggleLanguage}
              className="flex items-center space-x-2 bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg backdrop-blur-sm transition-all"
            >
              <Globe className="w-5 h-5 text-secondary" />
              <span className="text-sm font-medium text-white">{language === 'en' ? 'हिंदी' : 'English'}</span>
            </button>
            <div className="flex items-center space-x-3 bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm">
              <Phone className="w-5 h-5 text-secondary" />
              <span className="text-sm font-medium text-white">1860-267-6789</span>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      {currentStage !== 'landing' && (
        <div className="bg-white shadow-md px-4 py-6 border-b">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            {stages.map((stage, idx) => {
              const Icon = stage.icon;
              const done = idx < stageIdx;
              const curr = idx === stageIdx;
              const active = idx <= stageIdx;
              
              return (
                <React.Fragment key={stage.id}>
                  <div className="flex flex-col items-center">
                    <div className={`w-14 h-14 rounded-full flex items-center justify-center transition-all duration-300 ${
                      done ? 'bg-gradient-to-br from-secondary to-secondary-dark shadow-lg' : 
                      curr ? 'bg-gradient-primary shadow-glow animate-pulse-glow' : 
                      'bg-muted'
                    }`}>
                      {done ? <CheckCircle className="w-7 h-7 text-white" /> : 
                       <Icon className={`w-7 h-7 ${active ? 'text-white' : 'text-muted-foreground'}`} />}
                    </div>
                    <span className={`text-xs mt-2 font-semibold ${active ? 'text-primary' : 'text-muted-foreground'}`}>
                      {stage.label}
                    </span>
                  </div>
                  {idx < stages.length - 1 && (
                    <div className="flex-1 h-2 mx-2 bg-muted rounded-full overflow-hidden">
                      <div className={`h-full bg-gradient-secondary transition-all duration-500 ${done ? 'w-full' : 'w-0'}`} />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
              <div className={`flex items-start space-x-3 max-w-2xl ${msg.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                <div className={`w-12 h-12 rounded-full flex items-center justify-center shadow-lg ${
                  msg.type === 'user' ? 'bg-gradient-to-br from-primary to-primary-light' : 'bg-gradient-to-br from-accent to-accent/80'
                }`}>
                  {msg.type === 'user' ? <User className="w-6 h-6 text-white" /> : <Bot className="w-6 h-6 text-white" />}
                </div>
                <div className="flex-1">
                  {msg.agent && (
                    <span className={`inline-block px-4 py-1 rounded-full text-xs font-bold mb-2 ${getAgentColor(msg.agent)} text-white shadow-md`}>
                      {msg.agent}
                    </span>
                  )}
                  <div className={`px-5 py-4 rounded-2xl shadow-lg ${
                    msg.type === 'user' 
                      ? 'bg-gradient-to-br from-primary to-primary-light text-white' 
                      : 'bg-white text-foreground border border-border'
                  }`}>
                    <p className="whitespace-pre-line text-sm leading-relaxed">{msg.content}</p>
                    {msg.showLoader && (
                      <div className="flex items-center space-x-2 mt-3">
                        <Loader className="w-5 h-5 animate-spin text-primary" />
                        <span className="text-xs text-muted-foreground">Processing...</span>
                      </div>
                    )}
                    {msg.downloadable && (
                      <button 
                        onClick={() => window.open(msg.sanctionUrl, '_blank')}
                        className="mt-4 px-5 py-2.5 bg-gradient-secondary text-primary rounded-lg text-sm font-semibold flex items-center space-x-2 shadow-md hover:shadow-lg transition-all transform hover:scale-105"
                      >
                        <Download className="w-4 h-4" />
                        <span>{t('downloadLetter', language)}</span>
                      </button>
                    )}
                    {msg.needsUpload || msg.showUpload ? (
                      <button onClick={() => fileInputRef.current?.click()}
                        className="mt-4 px-5 py-2.5 bg-gradient-secondary text-primary rounded-lg text-sm font-semibold flex items-center space-x-2 shadow-md hover:shadow-lg transition-all transform hover:scale-105"
                      >
                        <Upload className="w-4 h-4" />
                        <span>{t('uploadSalarySlip', language)}</span>
                      </button>
                    ) : null}
                  </div>
                  {msg.suggestions && (
                    <div className="flex flex-wrap gap-2 mt-3">
                      {msg.suggestions.map((s: string, i: number) => (
                        <button key={i} onClick={() => handleSuggestionClick(s)}
                          className="px-4 py-2 bg-white border-2 border-primary/20 text-primary rounded-full text-xs font-medium hover:bg-primary hover:text-white hover:border-primary transition-all shadow-sm hover:shadow-md transform hover:scale-105">
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
          
          {isTyping && <TypingIndicator agentName={language === 'hi' ? 'AI सहायक' : 'AI Assistant'} />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Trust Bar */}
      <div className="bg-gradient-to-r from-blue-50 to-yellow-50 border-t px-4 py-3">
        <div className="max-w-4xl mx-auto flex justify-center items-center space-x-8 text-xs text-foreground">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-secondary" />
            <span className="font-semibold">{t('rbiRegistered', language)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="w-5 h-5 text-secondary" />
            <span className="font-semibold">{t('secure', language)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-5 h-5 text-secondary" />
            <span className="font-semibold">{t('disbursalTime24hr', language)}</span>
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="bg-white border-t-2 border-primary/10 px-4 py-5 shadow-xl">
        <div className="max-w-4xl mx-auto flex items-center space-x-3">
          <input type="file" ref={fileInputRef} onChange={handleFileSelect}
            accept=".pdf,.jpg,.jpeg,.png" className="hidden" />
          <button onClick={() => fileInputRef.current?.click()}
            className="p-3 bg-gradient-to-br from-muted to-muted/50 hover:from-primary/10 hover:to-primary/5 rounded-xl border-2 border-primary/20 transition-all transform hover:scale-105">
            <Upload className="w-5 h-5 text-primary" />
          </button>
          
          {/* Voice Input Button */}
          {isSpeechSupported && (
            <button 
              onClick={isListening ? stopListening : startListening}
              className={`p-3 rounded-xl border-2 transition-all transform hover:scale-105 ${
                isListening 
                  ? 'bg-red-500 border-red-500 animate-pulse' 
                  : 'bg-gradient-to-br from-muted to-muted/50 border-primary/20 hover:from-primary/10 hover:to-primary/5'
              }`}
            >
              {isListening ? (
                <MicOff className="w-5 h-5 text-white" />
              ) : (
                <Mic className="w-5 h-5 text-primary" />
              )}
            </button>
          )}
          
          <input type="text" value={isListening ? transcript : input} 
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isListening ? (language === 'hi' ? 'बोलिए...' : 'Listening...') : t('typePlaceholder', language)}
            className={`flex-1 px-5 py-3 border-2 rounded-xl focus:ring-2 focus:ring-primary focus:border-primary outline-none transition-all bg-background ${
              isListening ? 'border-red-300 bg-red-50' : 'border-border'
            }`} 
          />
          <button onClick={handleSend} disabled={!input.trim() && !transcript.trim()}
            className="p-3 bg-gradient-primary hover:shadow-glow disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all transform hover:scale-105 shadow-lg">
            <Send className="w-5 h-5 text-white" />
          </button>
        </div>
      </div>

      {/* Voice Assistant Floating Button */}
      <VoiceAssistant 
        language={language}
        onMessage={handleVoiceMessage}
        lastBotMessage={lastBotMessage}
      />

      {/* EMI Calculator Widget */}
      <EMICalculator language={language} />

      {/* Document Checklist */}
      <DocumentChecklist />

      {/* FAQ Drawer */}
      <FAQDrawer />

      {/* Document Preview Modal */}
      {previewFile && (
        <DocumentPreview
          file={previewFile}
          onConfirm={handleFileUploadConfirm}
          onCancel={handleFileUploadCancel}
        />
      )}
    </div>
  );
};

export default TataCapitalLoanChatbot;
