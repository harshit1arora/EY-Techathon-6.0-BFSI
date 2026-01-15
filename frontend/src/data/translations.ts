// Multilingual translations for Tata Capital Loan Chatbot

export type Language = 'en' | 'hi';

export const translations = {
  en: {
    // Header
    appTitle: 'Tata Capital',
    appSubtitle: 'AI Loan Assistant',
    helpline: 'Helpline',
    
    // Stages
    stageConversation: 'Conversation',
    stageVerification: 'Verification',
    stageCreditCheck: 'Credit Check',
    stageSanction: 'Sanction',
    
    // Greetings & Messages
    welcomeMessage: "🙏 Namaste! Welcome to Tata Capital. I'm your AI Personal Loan Assistant. May I know your name?",
    askPhone: 'Thank you, {name}! Please share your registered 10-digit mobile number for verification.',
    phoneVerified: '✅ Mobile verified successfully!',
    phoneNotFound: '❌ Mobile number not found in our records. Please try again or contact support.',
    invalidPhone: 'Please enter a valid 10-digit mobile number.',
    
    // Profile
    profileTitle: 'Your Profile',
    creditScore: 'Credit Score',
    preApproved: 'Pre-approved Limit',
    
    // Loan Details
    askAmount: 'Great news! You have a pre-approved offer of ₹{amount}!\n\nHow much would you like to borrow?',
    chooseTenure: 'Choose your preferred tenure:',
    instantApproval: '✨ Instant approval available!',
    needsVerification: 'Needs salary slip verification',
    
    // EMI
    emiPerMonth: '/month',
    months: 'months',
    
    // Document Upload
    uploadSalarySlip: '📄 Please upload your latest salary slip for verification.',
    uploadButton: 'Upload Document',
    uploadSuccess: '✅ Document uploaded successfully!',
    uploadError: 'Upload failed. Please try again.',
    fileSizeError: 'File must be under 5MB',
    
    // Credit Check
    checkingCredit: '🔍 Checking credit score and eligibility...',
    approved: '✅ APPROVED!',
    declined: '❌ Application Declined',
    emiRatio: 'EMI Ratio',
    
    // Sanction
    generatingLetter: '📄 Generating sanction letter...',
    congratulations: '🎊 CONGRATULATIONS',
    loanSanctioned: 'LOAN SANCTIONED',
    referenceNumber: 'Reference Number',
    disbursalTime: 'Funds will be disbursed within 24 hours!',
    downloadLetter: 'Download Sanction Letter',
    eSign: 'E-Sign Agreement',
    
    // Rejection Reasons
    rejectionAge: 'Age restriction: {age} years (Required: 21-60)',
    rejectionSalary: 'Monthly salary below ₹15,000',
    rejectionCredit: 'Credit score {score} is below 700',
    rejectionExcess: 'Amount exceeds 2x pre-approved limit',
    rejectionEmiRatio: 'High EMI ratio exceeds 50%',
    
    // Trust Bar
    rbiRegistered: 'RBI Registered',
    secure: 'Secure',
    disbursalTime24hr: '24hr Disbursal',
    
    // Input
    typePlaceholder: 'Type your message...',
    
    // Actions
    proceed: 'Yes, Proceed',
    generateLetter: 'Generate Letter',
    contactSupport: 'Contact Support',
    tryAnother: 'Try Another Amount',
    
    // Agents
    agentMaster: 'Master Agent',
    agentSales: 'Sales Agent',
    agentVerification: 'Verification Agent',
    agentUnderwriting: 'Underwriting Agent',
    agentDocument: 'Document Agent',
    agentSanction: 'Sanction Agent',
    
    // Extraction
    extractionSuccess: 'Document verified successfully',
    extractionFailed: 'Document verification failed',
  },
  
  hi: {
    // Header
    appTitle: 'टाटा कैपिटल',
    appSubtitle: 'AI लोन सहायक',
    helpline: 'हेल्पलाइन',
    
    // Stages
    stageConversation: 'बातचीत',
    stageVerification: 'सत्यापन',
    stageCreditCheck: 'क्रेडिट जांच',
    stageSanction: 'मंजूरी',
    
    // Greetings & Messages
    welcomeMessage: "🙏 नमस्ते! टाटा कैपिटल में आपका स्वागत है। मैं आपका AI पर्सनल लोन सहायक हूं। क्या मैं आपका नाम जान सकता हूं?",
    askPhone: 'धन्यवाद, {name}! कृपया सत्यापन के लिए अपना पंजीकृत 10 अंकों का मोबाइल नंबर साझा करें।',
    phoneVerified: '✅ मोबाइल सफलतापूर्वक सत्यापित!',
    phoneNotFound: '❌ मोबाइल नंबर हमारे रिकॉर्ड में नहीं मिला। कृपया पुनः प्रयास करें या सहायता से संपर्क करें।',
    invalidPhone: 'कृपया एक वैध 10 अंकों का मोबाइल नंबर दर्ज करें।',
    
    // Profile
    profileTitle: 'आपकी प्रोफाइल',
    creditScore: 'क्रेडिट स्कोर',
    preApproved: 'पूर्व-स्वीकृत सीमा',
    
    // Loan Details
    askAmount: 'शुभ समाचार! आपके पास ₹{amount} की पूर्व-स्वीकृत पेशकश है!\n\nआप कितना उधार लेना चाहेंगे?',
    chooseTenure: 'अपनी पसंदीदा अवधि चुनें:',
    instantApproval: '✨ तत्काल मंजूरी उपलब्ध!',
    needsVerification: 'वेतन पर्ची सत्यापन आवश्यक',
    
    // EMI
    emiPerMonth: '/माह',
    months: 'महीने',
    
    // Document Upload
    uploadSalarySlip: '📄 कृपया सत्यापन के लिए अपनी नवीनतम वेतन पर्ची अपलोड करें।',
    uploadButton: 'दस्तावेज़ अपलोड करें',
    uploadSuccess: '✅ दस्तावेज़ सफलतापूर्वक अपलोड हुआ!',
    uploadError: 'अपलोड विफल। कृपया पुनः प्रयास करें।',
    fileSizeError: 'फ़ाइल 5MB से कम होनी चाहिए',
    
    // Credit Check
    checkingCredit: '🔍 क्रेडिट स्कोर और पात्रता की जांच हो रही है...',
    approved: '✅ स्वीकृत!',
    declined: '❌ आवेदन अस्वीकृत',
    emiRatio: 'EMI अनुपात',
    
    // Sanction
    generatingLetter: '📄 मंजूरी पत्र तैयार हो रहा है...',
    congratulations: '🎊 बधाई हो',
    loanSanctioned: 'लोन मंजूर',
    referenceNumber: 'संदर्भ संख्या',
    disbursalTime: '24 घंटे के भीतर राशि वितरित की जाएगी!',
    downloadLetter: 'मंजूरी पत्र डाउनलोड करें',
    eSign: 'ई-हस्ताक्षर समझौता',
    
    // Rejection Reasons
    rejectionAge: 'आयु प्रतिबंध: {age} वर्ष (आवश्यक: 21-60)',
    rejectionSalary: 'मासिक वेतन ₹15,000 से कम',
    rejectionCredit: 'क्रेडिट स्कोर {score} 700 से कम है',
    rejectionExcess: 'राशि पूर्व-स्वीकृत सीमा के 2x से अधिक है',
    rejectionEmiRatio: 'उच्च EMI अनुपात 50% से अधिक',
    
    // Trust Bar
    rbiRegistered: 'RBI पंजीकृत',
    secure: 'सुरक्षित',
    disbursalTime24hr: '24 घंटे वितरण',
    
    // Input
    typePlaceholder: 'अपना संदेश लिखें...',
    
    // Actions
    proceed: 'हाँ, आगे बढ़ें',
    generateLetter: 'पत्र बनाएं',
    contactSupport: 'सहायता से संपर्क करें',
    tryAnother: 'दूसरी राशि आज़माएं',
    
    // Agents
    agentMaster: 'मास्टर एजेंट',
    agentSales: 'सेल्स एजेंट',
    agentVerification: 'सत्यापन एजेंट',
    agentUnderwriting: 'अंडरराइटिंग एजेंट',
    agentDocument: 'दस्तावेज़ एजेंट',
    agentSanction: 'मंजूरी एजेंट',
    
    // Extraction
    extractionSuccess: 'दस्तावेज़ सफलतापूर्वक सत्यापित',
    extractionFailed: 'दस्तावेज़ सत्यापन विफल',
  }
};

export function t(key: keyof typeof translations.en, lang: Language, params?: Record<string, string | number>): string {
  let text = translations[lang][key] || translations.en[key] || key;
  
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      text = text.replace(`{${k}}`, String(v));
    });
  }
  
  return text;
}
