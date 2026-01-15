// Mock Salary Slip Extractor for Hackathon
// Simulates OCR/AI extraction from salary slip documents

export interface SalarySlipData {
  name: string;
  employer: string;
  salary: number;
  net_pay: number;
  date: string;
  employee_id?: string;
  designation?: string;
  bank_account?: string;
  pf_deduction?: number;
  tax_deduction?: number;
}

// Mock extracted data based on filename patterns or random generation
const mockSalaryData: SalarySlipData[] = [
  {
    name: "Rahul Sharma",
    employer: "TCS Limited",
    salary: 75000,
    net_pay: 62500,
    date: "2024-11-30",
    employee_id: "TCS001234",
    designation: "Software Engineer",
    pf_deduction: 9000,
    tax_deduction: 3500
  },
  {
    name: "Priya Patel",
    employer: "Wipro Limited",
    salary: 55000,
    net_pay: 46500,
    date: "2024-11-30",
    employee_id: "WIP005678",
    designation: "Marketing Manager",
    pf_deduction: 6600,
    tax_deduction: 1900
  },
  {
    name: "Amit Kumar",
    employer: "Deloitte India",
    salary: 95000,
    net_pay: 78000,
    date: "2024-11-30",
    employee_id: "DEL009012",
    designation: "Senior Consultant",
    pf_deduction: 11400,
    tax_deduction: 5600
  },
  {
    name: "Sneha Reddy",
    employer: "Accenture",
    salary: 42000,
    net_pay: 36500,
    date: "2024-11-30",
    employee_id: "ACC003456",
    designation: "Business Analyst",
    pf_deduction: 5040,
    tax_deduction: 460
  },
  {
    name: "Rajesh Gupta",
    employer: "L&T Infotech",
    salary: 125000,
    net_pay: 98000,
    date: "2024-11-30",
    employee_id: "LTI007890",
    designation: "General Manager",
    pf_deduction: 15000,
    tax_deduction: 12000
  }
];

export interface ExtractionResult {
  success: boolean;
  data: SalarySlipData | null;
  confidence: number;
  processing_time_ms: number;
  errors?: string[];
}

// Simulate extraction delay and processing
export async function extractSalarySlipData(
  file: File,
  customerName?: string
): Promise<ExtractionResult> {
  // Simulate processing time (500ms - 2000ms)
  const processingTime = Math.floor(Math.random() * 1500) + 500;
  
  await new Promise(resolve => setTimeout(resolve, processingTime));

  // Validate file
  const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
  if (!validTypes.includes(file.type)) {
    return {
      success: false,
      data: null,
      confidence: 0,
      processing_time_ms: processingTime,
      errors: ['Invalid file type. Please upload PDF, JPG, or PNG.']
    };
  }

  // Check file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    return {
      success: false,
      data: null,
      confidence: 0,
      processing_time_ms: processingTime,
      errors: ['File size exceeds 5MB limit.']
    };
  }

  // Find matching mock data or generate random
  let extractedData: SalarySlipData;
  
  if (customerName) {
    const matchingData = mockSalaryData.find(
      d => d.name.toLowerCase().includes(customerName.toLowerCase())
    );
    extractedData = matchingData || mockSalaryData[Math.floor(Math.random() * mockSalaryData.length)];
  } else {
    extractedData = mockSalaryData[Math.floor(Math.random() * mockSalaryData.length)];
  }

  // Simulate confidence score (85-98%)
  const confidence = Math.floor(Math.random() * 13) + 85;

  return {
    success: true,
    data: extractedData,
    confidence,
    processing_time_ms: processingTime
  };
}

// Format extraction result for display
export function formatExtractionForDisplay(result: ExtractionResult): string {
  if (!result.success || !result.data) {
    return `❌ Extraction Failed\n${result.errors?.join('\n') || 'Unknown error'}`;
  }

  const { data, confidence } = result;
  return `✅ Salary Slip Verified (${confidence}% confidence)

📋 Extracted Details:
• Name: ${data.name}
• Employer: ${data.employer}
• Gross Salary: ₹${data.salary.toLocaleString('en-IN')}
• Net Pay: ₹${data.net_pay.toLocaleString('en-IN')}
• Pay Date: ${data.date}
${data.designation ? `• Designation: ${data.designation}` : ''}
${data.pf_deduction ? `• PF Deduction: ₹${data.pf_deduction.toLocaleString('en-IN')}` : ''}
${data.tax_deduction ? `• Tax Deduction: ₹${data.tax_deduction.toLocaleString('en-IN')}` : ''}`;
}

// Convert extraction result to JSON for underwriting agent
export function extractionToJSON(result: ExtractionResult): object {
  if (!result.success || !result.data) {
    return {
      success: false,
      error: result.errors?.[0] || 'Extraction failed'
    };
  }

  return {
    success: true,
    document_type: 'salary_slip',
    extracted_at: new Date().toISOString(),
    confidence_score: result.confidence,
    fields: {
      name: result.data.name,
      employer: result.data.employer,
      salary: result.data.salary,
      net_pay: result.data.net_pay,
      date: result.data.date
    },
    additional_fields: {
      employee_id: result.data.employee_id,
      designation: result.data.designation,
      pf_deduction: result.data.pf_deduction,
      tax_deduction: result.data.tax_deduction
    }
  };
}
