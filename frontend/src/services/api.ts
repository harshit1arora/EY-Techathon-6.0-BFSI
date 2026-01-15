// services/api.ts - COMPLETE VERSION
const BASE_URL = 'http://localhost:8083'; // Your working API port

export interface ChatRequest {
  session_id: string;
  message: string;
}

export interface ChatResponse {
  response: string;
  flow_step: number;
  customer_id?: string;
  kyc_status: string;
  last_active_worker: string;
  debug_stage?: string;
  flow_stage?: string;
  underwriting_status?: string;
  sanction_letter_url?: string;
  negotiated_offer?: any;
  waiting_for_user?: boolean;
}

export interface HealthResponse {
  status: string;
  service: string;
  mcp_connected?: boolean;
  active_sessions?: number;
}

export interface ResetResponse {
  status: string;
  message?: string;
}

export interface APIInfo {
  service: string;
  status: string;
  mcp_backend: string;
  endpoints: {
    [key: string]: string;
  };
}

// Chat with backend API
export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  try {
    console.log('📡 [API] Sending message:', request.message);
    
    const response = await fetch(`${BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ [API] Error response:', errorText);
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data: ChatResponse = await response.json();
    console.log('📡 [API] Received response:', {
      agent: data.last_active_worker,
      step: data.flow_step,
      response: data.response.substring(0, 50) + '...'
    });
    
    return data;
    
  } catch (error) {
    console.error('❌ [API] Request failed:', error);
    throw error;
  }
}

// Health check
export async function checkHealth(): Promise<HealthResponse> {
  try {
    const response = await fetch(`${BASE_URL}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('❌ [API] Health check failed:', error);
    throw error;
  }
}

// Reset session
export async function resetSession(sessionId: string): Promise<ResetResponse> {
  try {
    const response = await fetch(`${BASE_URL}/reset/${sessionId}`);
    if (!response.ok) {
      throw new Error(`Reset failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('❌ [API] Reset failed:', error);
    throw error;
  }
}

// Get API info
export async function getAPIInfo(): Promise<APIInfo> {
  try {
    const response = await fetch(BASE_URL);
    if (!response.ok) {
      throw new Error(`API info failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('❌ [API] Get info failed:', error);
    throw error;
  }
}

// Test MCP customer data
export async function getCustomerInfo(customerId: string): Promise<any> {
  try {
    const response = await fetch('http://localhost:8000/call/get_customer_info', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ customer_id: customerId }),
    });

    if (!response.ok) {
      throw new Error(`Customer info failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('❌ [API] Get customer info failed:', error);
    throw error;
  }
}

// Test underwriting
export async function testUnderwriting(customerId: string, amount: number): Promise<any> {
  try {
    const response = await fetch('http://localhost:8000/call/underwrite_loan', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer_id: customerId,
        requested_amount: amount,
        tenure_months: 36,
        annual_rate: 12.0
      }),
    });

    if (!response.ok) {
      throw new Error(`Underwriting test failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('❌ [API] Underwriting test failed:', error);
    throw error;
  }
}

// Upload salary slip (mock)
export async function uploadSalarySlip(sessionId: string, file: File): Promise<any> {
  try {
    // For demo, simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    return {
      status: 'ok',
      message: 'Salary slip uploaded successfully',
      extracted_data: {
        employee_name: 'John Doe',
        monthly_salary: 50000,
        employer_name: 'Tech Corp',
        period: 'January 2024'
      }
    };
  } catch (error) {
    console.error('❌ [API] Upload failed:', error);
    throw error;
  }
}

// Test API connection
export async function testAPIConnection() {
  try {
    console.log('🧪 Testing API connection...');
    
    // Test 1: Check if server is running
    const health = await checkHealth();
    console.log('✅ Health check:', health);
    
    // Test 2: Send a test message
    const testSession = 'test_' + Date.now();
    const testMessage = await sendChatMessage({
      session_id: testSession,
      message: "Hello"
    });
    console.log('✅ Test message response:', {
      agent: testMessage.last_active_worker,
      step: testMessage.flow_step,
      response: testMessage.response.substring(0, 50) + '...'
    });
    
    // Test 3: Reset test session
    const reset = await resetSession(testSession);
    console.log('✅ Reset test:', reset);
    
    // Test 4: Get API info
    const info = await getAPIInfo();
    console.log('✅ API info:', info);
    
    return { 
      success: true, 
      health, 
      testMessage, 
      reset, 
      info,
      summary: 'All API tests passed successfully!' 
    };
    
  } catch (error: any) {
    console.error('❌ API Connection Test Failed:', error);
    return { 
      success: false, 
      error: error.message,
      summary: 'API connection test failed. Make sure backend is running on port 8083.'
    };
  }
}

// Get all mock customers
export function getMockCustomers() {
  return [
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
}

// Simulate KYC verification
export async function simulateKYCVerification(customerId: string): Promise<any> {
  try {
    const response = await fetch('http://localhost:8000/call/verify_kyc', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        customer_id: customerId,
        phone: '9810000001' // Mock phone for demo
      }),
    });

    if (!response.ok) {
      throw new Error(`KYC verification failed: ${response.status}`);
    }
    return response.json();
  } catch (error) {
    console.error('❌ [API] KYC verification failed:', error);
    throw error;
  }
}

// Generate test data for debugging
export function generateTestData() {
  return {
    test_messages: [
      { id: 1, text: "CUST001", type: "user" },
      { id: 2, text: "Hi! I want to apply for a personal loan", type: "user" },
      { id: 3, text: "250000", type: "user" },
      { id: 4, text: "36 months", type: "user" },
      { id: 5, text: "upload documents", type: "user" },
      { id: 6, text: "yes, proceed", type: "user" }
    ],
    test_responses: [
      { id: 1, agent: "master", text: "Welcome to Tata Capital! Please provide your Customer ID.", step: 1 },
      { id: 2, agent: "master", text: "Hello Asha! How much loan do you need?", step: 2 },
      { id: 3, agent: "master", text: "Great! For how many months?", step: 3 },
      { id: 4, agent: "sales", text: "Your loan is approved! Amount: ₹250,000, EMI: ₹8,303/month", step: 4 },
      { id: 5, agent: "document", text: "Please upload your documents: Aadhaar, PAN, Bank Statements", step: 5 },
      { id: 6, agent: "sanction", text: "Sanction letter generated! Loan ready for disbursement.", step: 6 }
    ]
  };
}

// Utility function to format currency
export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(amount);
}

// Utility function to calculate EMI
export function calculateEMI(principal: number, annualRate: number, months: number): number {
  const monthlyRate = annualRate / 12 / 100;
  const emi = principal * monthlyRate * Math.pow(1 + monthlyRate, months) / 
              (Math.pow(1 + monthlyRate, months) - 1);
  return Math.round(emi);
}

// Check if backend is running
export async function isBackendRunning(): Promise<boolean> {
  try {
    await checkHealth();
    return true;
  } catch {
    return false;
  }
}

// Initialize chat session
export async function initializeChatSession(): Promise<{
  sessionId: string;
  timestamp: string;
  status: string;
}> {
  const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  const timestamp = new Date().toISOString();
  
  // Store in localStorage
  if (typeof window !== 'undefined') {
    localStorage.setItem('loan_chat_session_id', sessionId);
    localStorage.setItem('loan_chat_start_time', timestamp);
  }
  
  return {
    sessionId,
    timestamp,
    status: 'initialized'
  };
}

// Get session history
export function getSessionHistory(sessionId: string): any[] {
  if (typeof window === 'undefined') return [];
  
  const historyKey = `chat_history_${sessionId}`;
  const history = localStorage.getItem(historyKey);
  return history ? JSON.parse(history) : [];
}

// Save to session history
export function saveToSessionHistory(sessionId: string, message: any): void {
  if (typeof window === 'undefined') return;
  
  const historyKey = `chat_history_${sessionId}`;
  const history = getSessionHistory(sessionId);
  history.push({
    ...message,
    timestamp: new Date().toISOString()
  });
  
  // Keep only last 50 messages
  if (history.length > 50) {
    history.splice(0, history.length - 50);
  }
  
  localStorage.setItem(historyKey, JSON.stringify(history));
}

// Clear session history
export function clearSessionHistory(sessionId: string): void {
  if (typeof window === 'undefined') return;
  
  const historyKey = `chat_history_${sessionId}`;
  localStorage.removeItem(historyKey);
}