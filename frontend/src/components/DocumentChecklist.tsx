import React, { useState } from 'react';
import { FileCheck, FileX, Upload, ChevronDown, X, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';

interface Document {
  id: string;
  name: string;
  required: boolean;
  uploaded: boolean;
  fileName?: string;
}

interface LoanTypeDocuments {
  [key: string]: Document[];
}

const documentsByLoanType: LoanTypeDocuments = {
  personal: [
    { id: 'pan', name: 'PAN Card', required: true, uploaded: false },
    { id: 'aadhar', name: 'Aadhar Card', required: true, uploaded: false },
    { id: 'salary', name: 'Salary Slip (Last 3 months)', required: true, uploaded: false },
    { id: 'bank', name: 'Bank Statement (Last 6 months)', required: true, uploaded: false },
    { id: 'photo', name: 'Passport Photo', required: true, uploaded: false },
    { id: 'address', name: 'Address Proof', required: false, uploaded: false },
  ],
  home: [
    { id: 'pan', name: 'PAN Card', required: true, uploaded: false },
    { id: 'aadhar', name: 'Aadhar Card', required: true, uploaded: false },
    { id: 'salary', name: 'Salary Slip (Last 6 months)', required: true, uploaded: false },
    { id: 'bank', name: 'Bank Statement (Last 12 months)', required: true, uploaded: false },
    { id: 'itr', name: 'ITR (Last 2 years)', required: true, uploaded: false },
    { id: 'property', name: 'Property Documents', required: true, uploaded: false },
    { id: 'agreement', name: 'Sale Agreement', required: true, uploaded: false },
    { id: 'photo', name: 'Passport Photo', required: true, uploaded: false },
  ],
  business: [
    { id: 'pan', name: 'PAN Card (Personal & Business)', required: true, uploaded: false },
    { id: 'aadhar', name: 'Aadhar Card', required: true, uploaded: false },
    { id: 'gst', name: 'GST Registration', required: true, uploaded: false },
    { id: 'itr', name: 'ITR (Last 3 years)', required: true, uploaded: false },
    { id: 'bank', name: 'Bank Statement (Last 12 months)', required: true, uploaded: false },
    { id: 'balance', name: 'Balance Sheet & P&L', required: true, uploaded: false },
    { id: 'incorporation', name: 'Incorporation Certificate', required: false, uploaded: false },
    { id: 'photo', name: 'Passport Photo', required: true, uploaded: false },
  ],
};

interface DocumentChecklistProps {
  onUpload?: (docId: string, file: File) => void;
}

const DocumentChecklist: React.FC<DocumentChecklistProps> = ({ onUpload }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loanType, setLoanType] = useState<string>('personal');
  const [documents, setDocuments] = useState<Document[]>(documentsByLoanType.personal);

  const handleLoanTypeChange = (type: string) => {
    setLoanType(type);
    setDocuments(documentsByLoanType[type].map(doc => ({ ...doc, uploaded: false })));
  };

  const handleFileUpload = (docId: string, event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setDocuments(prev => 
        prev.map(doc => 
          doc.id === docId 
            ? { ...doc, uploaded: true, fileName: file.name }
            : doc
        )
      );
      onUpload?.(docId, file);
    }
  };

  const requiredDocs = documents.filter(d => d.required);
  const uploadedRequired = requiredDocs.filter(d => d.uploaded).length;
  const progress = (uploadedRequired / requiredDocs.length) * 100;

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button 
          className="fixed bottom-44 right-6 z-40 rounded-full w-12 h-12 shadow-xl bg-primary hover:bg-primary/90"
          size="icon"
        >
          <FileCheck className="w-5 h-5" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md max-h-[85vh] overflow-hidden flex flex-col">
        <DialogHeader>
          <DialogTitle className="flex items-center space-x-2">
            <FileCheck className="w-5 h-5 text-primary" />
            <span>Document Checklist</span>
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4 flex-1 overflow-y-auto pr-2">
          {/* Loan Type Selector */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-foreground">Loan Type</label>
            <Select value={loanType} onValueChange={handleLoanTypeChange}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="Select loan type" />
              </SelectTrigger>
              <SelectContent className="bg-card border-border z-[60]">
                <SelectItem value="personal">Personal Loan</SelectItem>
                <SelectItem value="home">Home Loan</SelectItem>
                <SelectItem value="business">Business Loan</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Progress */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Upload Progress</span>
              <span className="font-medium text-foreground">{uploadedRequired}/{requiredDocs.length} Required</span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {/* Document List */}
          <div className="space-y-2">
            {documents.map((doc) => (
              <div 
                key={doc.id}
                className={`flex items-center justify-between p-3 rounded-lg border transition-colors ${
                  doc.uploaded 
                    ? 'bg-green-50 border-green-200 dark:bg-green-900/20 dark:border-green-800' 
                    : 'bg-card border-border hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center space-x-3">
                  {doc.uploaded ? (
                    <CheckCircle2 className="w-5 h-5 text-green-600" />
                  ) : doc.required ? (
                    <AlertCircle className="w-5 h-5 text-amber-500" />
                  ) : (
                    <FileX className="w-5 h-5 text-muted-foreground" />
                  )}
                  <div>
                    <p className="text-sm font-medium text-foreground">{doc.name}</p>
                    {doc.uploaded && doc.fileName && (
                      <p className="text-xs text-muted-foreground truncate max-w-[150px]">{doc.fileName}</p>
                    )}
                    {!doc.uploaded && doc.required && (
                      <p className="text-xs text-amber-600">Required</p>
                    )}
                  </div>
                </div>
                
                <label className="cursor-pointer">
                  <input
                    type="file"
                    className="hidden"
                    accept=".pdf,.jpg,.jpeg,.png"
                    onChange={(e) => handleFileUpload(doc.id, e)}
                  />
                  <div className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    doc.uploaded 
                      ? 'bg-green-600 text-white hover:bg-green-700' 
                      : 'bg-primary text-primary-foreground hover:bg-primary/90'
                  }`}>
                    {doc.uploaded ? 'Replace' : 'Upload'}
                  </div>
                </label>
              </div>
            ))}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default DocumentChecklist;
