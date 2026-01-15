import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, CheckCircle, Clock, FileText, CreditCard, Banknote, ArrowLeft, Phone, Shield, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ApplicationStatus {
  referenceNumber: string;
  customerName: string;
  loanAmount: number;
  appliedDate: string;
  currentStage: number;
  stages: {
    name: string;
    status: 'completed' | 'current' | 'pending';
    date?: string;
    description: string;
  }[];
}

// Mock data for demo
const mockApplications: Record<string, ApplicationStatus> = {
  'TATA-12345678': {
    referenceNumber: 'TATA-12345678',
    customerName: 'Rahul Sharma',
    loanAmount: 300000,
    appliedDate: '2024-12-01',
    currentStage: 3,
    stages: [
      { name: 'Application Submitted', status: 'completed', date: '2024-12-01', description: 'Your loan application has been received' },
      { name: 'Document Verification', status: 'completed', date: '2024-12-02', description: 'All documents verified successfully' },
      { name: 'Credit Assessment', status: 'current', description: 'Credit score and eligibility being evaluated' },
      { name: 'Loan Sanctioned', status: 'pending', description: 'Final approval and sanction letter generation' },
      { name: 'Disbursement', status: 'pending', description: 'Loan amount credited to your account' },
    ]
  },
  'TATA-87654321': {
    referenceNumber: 'TATA-87654321',
    customerName: 'Priya Patel',
    loanAmount: 200000,
    appliedDate: '2024-11-28',
    currentStage: 4,
    stages: [
      { name: 'Application Submitted', status: 'completed', date: '2024-11-28', description: 'Your loan application has been received' },
      { name: 'Document Verification', status: 'completed', date: '2024-11-29', description: 'All documents verified successfully' },
      { name: 'Credit Assessment', status: 'completed', date: '2024-11-30', description: 'Credit approved - Score: 720' },
      { name: 'Loan Sanctioned', status: 'current', date: '2024-12-01', description: 'Sanction letter ready for download' },
      { name: 'Disbursement', status: 'pending', description: 'Awaiting e-signature for disbursement' },
    ]
  },
  'TATA-091B8949': {
    referenceNumber: 'TATA-091B8949',
    customerName: 'Asha Verma',
    loanAmount: 200000,
    appliedDate: new Date().toISOString().split('T')[0],
    currentStage: 5,
    stages: [
      { name: 'Application Submitted', status: 'completed', date: new Date().toISOString().split('T')[0], description: 'Loan application received for CUST001' },
      { name: 'Document Verification', status: 'completed', date: new Date().toISOString().split('T')[0], description: 'KYC and Salary documents verified' },
      { name: 'Credit Assessment', status: 'completed', date: new Date().toISOString().split('T')[0], description: 'Credit Score 745 - Approved' },
      { name: 'Loan Sanctioned', status: 'completed', date: new Date().toISOString().split('T')[0], description: 'Sanction Letter TATA-091B8949 generated' },
      { name: 'Disbursement', status: 'completed', date: new Date().toISOString().split('T')[0], description: 'Funds transferred to XXXX-XXXX-1234' },
    ]
  },
};

const StatusTracker = () => {
  const [referenceNumber, setReferenceNumber] = useState('');
  const [application, setApplication] = useState<ApplicationStatus | null>(null);
  const [error, setError] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  const handleSearch = () => {
    setIsSearching(true);
    setError('');
    
    setTimeout(() => {
      const found = mockApplications[referenceNumber.toUpperCase()];
      if (found) {
        setApplication(found);
        setError('');
      } else {
        setApplication(null);
        setError('Application not found. Please check your reference number.');
      }
      setIsSearching(false);
    }, 1000);
  };

  const getStageIcon = (index: number) => {
    const icons = [FileText, CheckCircle, CreditCard, Shield, Banknote];
    const Icon = icons[index] || FileText;
    return Icon;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-blue-50 to-yellow-50">
      {/* Header */}
      <header className="bg-gradient-primary shadow-xl border-b-4 border-secondary">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Link to="/" className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors">
              <ArrowLeft className="w-5 h-5 text-white" />
            </Link>
            <div className="w-12 h-12 bg-gradient-to-br from-secondary to-secondary-dark rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-primary font-bold text-2xl">T</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">Application Status</h1>
              <p className="text-xs text-secondary-light font-semibold">Track your loan application</p>
            </div>
          </div>
          <div className="flex items-center space-x-3 bg-white/10 px-4 py-2 rounded-lg backdrop-blur-sm">
            <Phone className="w-5 h-5 text-secondary" />
            <span className="text-sm font-medium text-white">1860-267-6789</span>
          </div>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Search Section */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-8">
          <h2 className="text-lg font-bold text-foreground mb-4">Track Your Application</h2>
          <div className="flex gap-3">
            <Input
              type="text"
              placeholder="Enter Reference Number (e.g., TATA-12345678)"
              value={referenceNumber}
              onChange={(e) => setReferenceNumber(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button 
              onClick={handleSearch} 
              disabled={!referenceNumber.trim() || isSearching}
              className="bg-gradient-primary hover:shadow-glow"
            >
              {isSearching ? (
                <Clock className="w-5 h-5 animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
              <span className="ml-2">Track</span>
            </Button>
          </div>
          
          {/* Demo hint */}
          <p className="text-xs text-muted-foreground mt-3">
            Demo: Try <button onClick={() => setReferenceNumber('TATA-091B8949')} className="text-primary font-bold hover:underline">TATA-091B8949</button>, <button onClick={() => setReferenceNumber('TATA-12345678')} className="text-primary hover:underline">TATA-12345678</button> or <button onClick={() => setReferenceNumber('TATA-87654321')} className="text-primary hover:underline">TATA-87654321</button>
          </p>

          {error && (
            <div className="mt-4 p-4 bg-destructive/10 border border-destructive/20 rounded-xl flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-destructive" />
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}
        </div>

        {/* Application Details */}
        {application && (
          <div className="space-y-6 animate-slide-up">
            {/* Summary Card */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <p className="text-sm text-muted-foreground">Reference Number</p>
                  <p className="text-xl font-bold text-primary">{application.referenceNumber}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Applied On</p>
                  <p className="font-semibold">{new Date(application.appliedDate).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 p-4 bg-gradient-to-br from-primary/5 to-primary/10 rounded-xl">
                <div>
                  <p className="text-xs text-muted-foreground">Customer Name</p>
                  <p className="font-semibold">{application.customerName}</p>
                </div>
                <div>
                  <p className="text-xs text-muted-foreground">Loan Amount</p>
                  <p className="font-semibold text-primary">₹{application.loanAmount.toLocaleString('en-IN')}</p>
                </div>
              </div>
            </div>

            {/* Progress Timeline */}
            <div className="bg-white rounded-2xl shadow-xl p-6">
              <h3 className="text-lg font-bold text-foreground mb-6">Application Progress</h3>
              
              <div className="space-y-0">
                {application.stages.map((stage, index) => {
                  const Icon = getStageIcon(index);
                  const isLast = index === application.stages.length - 1;
                  
                  return (
                    <div key={index} className="flex gap-4">
                      {/* Icon & Line */}
                      <div className="flex flex-col items-center">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center shadow-md transition-all ${
                          stage.status === 'completed' 
                            ? 'bg-gradient-to-br from-green-500 to-green-600' 
                            : stage.status === 'current'
                            ? 'bg-gradient-primary animate-pulse-glow'
                            : 'bg-muted'
                        }`}>
                          <Icon className={`w-5 h-5 ${
                            stage.status === 'pending' ? 'text-muted-foreground' : 'text-white'
                          }`} />
                        </div>
                        {!isLast && (
                          <div className={`w-0.5 h-16 ${
                            stage.status === 'completed' ? 'bg-green-500' : 'bg-muted'
                          }`} />
                        )}
                      </div>
                      
                      {/* Content */}
                      <div className={`flex-1 pb-8 ${isLast ? 'pb-0' : ''}`}>
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className={`font-semibold ${
                            stage.status === 'pending' ? 'text-muted-foreground' : 'text-foreground'
                          }`}>
                            {stage.name}
                          </h4>
                          {stage.status === 'current' && (
                            <span className="px-2 py-0.5 bg-primary/10 text-primary text-xs font-medium rounded-full">
                              In Progress
                            </span>
                          )}
                          {stage.status === 'completed' && (
                            <CheckCircle className="w-4 h-4 text-green-500" />
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{stage.description}</p>
                        {stage.date && (
                          <p className="text-xs text-muted-foreground mt-1">
                            {new Date(stage.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Help Section */}
            <div className="bg-gradient-to-br from-secondary/20 to-secondary/30 rounded-2xl p-6 flex items-center justify-between">
              <div>
                <h4 className="font-semibold text-foreground">Need Help?</h4>
                <p className="text-sm text-muted-foreground">Our support team is available 24/7</p>
              </div>
              <Button variant="outline" className="border-primary text-primary hover:bg-primary hover:text-white">
                <Phone className="w-4 h-4 mr-2" />
                Contact Support
              </Button>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!application && !error && (
          <div className="text-center py-16">
            <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-10 h-10 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-foreground mb-2">Enter your reference number</h3>
            <p className="text-sm text-muted-foreground max-w-sm mx-auto">
              You received a reference number when you applied for the loan. Enter it above to track your application status.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatusTracker;
