import React, { useState, useMemo } from 'react';
import { HelpCircle, Search, ChevronDown, ChevronUp, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerTrigger, DrawerClose } from '@/components/ui/drawer';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';

interface FAQ {
  id: string;
  question: string;
  answer: string;
  category: string;
}

const faqs: FAQ[] = [
  {
    id: '1',
    question: 'What is the minimum credit score required for a loan?',
    answer: 'We typically require a minimum credit score of 700 for instant approval. However, applicants with scores between 650-700 may qualify for conditional approval with additional documentation.',
    category: 'Eligibility'
  },
  {
    id: '2',
    question: 'How long does the loan approval process take?',
    answer: 'For pre-approved customers, instant approval is possible. For others, the process typically takes 24-48 hours after document verification.',
    category: 'Process'
  },
  {
    id: '3',
    question: 'What documents do I need to apply?',
    answer: 'Required documents include PAN Card, Aadhar Card, last 3 months salary slips, 6 months bank statements, and a passport-sized photo. Additional documents may be required based on loan type.',
    category: 'Documents'
  },
  {
    id: '4',
    question: 'What is the maximum loan amount I can apply for?',
    answer: 'The maximum loan amount depends on your income, credit score, and existing obligations. Generally, you can apply for up to 2x your pre-approved limit with proper documentation.',
    category: 'Eligibility'
  },
  {
    id: '5',
    question: 'How is the EMI calculated?',
    answer: 'EMI is calculated using the formula: EMI = [P x R x (1+R)^N]/[(1+R)^N-1], where P is principal, R is monthly interest rate, and N is number of months. You can use our EMI calculator for exact amounts.',
    category: 'EMI'
  },
  {
    id: '6',
    question: 'Can I prepay my loan?',
    answer: 'Yes, you can prepay your loan after 6 months from disbursal. A nominal prepayment charge of 2-4% may apply depending on the outstanding amount.',
    category: 'Repayment'
  },
  {
    id: '7',
    question: 'What happens if I miss an EMI payment?',
    answer: 'Missing an EMI payment attracts a late payment fee and may negatively impact your credit score. We recommend setting up auto-debit to avoid missing payments.',
    category: 'Repayment'
  },
  {
    id: '8',
    question: 'How do I check my loan application status?',
    answer: 'You can check your application status by visiting our Status Tracker page or by providing your application ID in the chat.',
    category: 'Process'
  },
  {
    id: '9',
    question: 'Is my data secure?',
    answer: 'Yes, we use bank-grade 256-bit encryption to protect your data. All communications are secured with SSL/TLS protocols.',
    category: 'Security'
  },
  {
    id: '10',
    question: 'What interest rates do you offer?',
    answer: 'Interest rates start from 10.5% per annum for personal loans. The actual rate depends on your credit profile, income, and loan amount.',
    category: 'EMI'
  },
];

const categories = ['All', 'Eligibility', 'Process', 'Documents', 'EMI', 'Repayment', 'Security'];

const FAQDrawer: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filteredFaqs = useMemo(() => {
    return faqs.filter(faq => {
      const matchesSearch = 
        faq.question.toLowerCase().includes(search.toLowerCase()) ||
        faq.answer.toLowerCase().includes(search.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || faq.category === selectedCategory;
      return matchesSearch && matchesCategory;
    });
  }, [search, selectedCategory]);

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <Drawer open={isOpen} onOpenChange={setIsOpen}>
      <DrawerTrigger asChild>
        <Button 
          className="fixed bottom-44 left-6 z-40 rounded-full w-12 h-12 shadow-xl bg-secondary hover:bg-secondary/90"
          size="icon"
        >
          <HelpCircle className="w-5 h-5 text-secondary-foreground" />
        </Button>
      </DrawerTrigger>
      <DrawerContent className="max-h-[85vh]">
        <DrawerHeader className="border-b border-border pb-4">
          <div className="flex items-center justify-between">
            <DrawerTitle className="flex items-center space-x-2">
              <HelpCircle className="w-5 h-5 text-primary" />
              <span>Frequently Asked Questions</span>
            </DrawerTitle>
          </div>
        </DrawerHeader>

        <div className="p-4 space-y-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input
              placeholder="Search FAQs..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-10"
            />
          </div>

          {/* Categories */}
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <Badge
                key={category}
                variant={selectedCategory === category ? 'default' : 'outline'}
                className="cursor-pointer transition-colors"
                onClick={() => setSelectedCategory(category)}
              >
                {category}
              </Badge>
            ))}
          </div>

          {/* FAQ List */}
          <ScrollArea className="h-[50vh]">
            <div className="space-y-2 pr-4">
              {filteredFaqs.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No FAQs found matching your search.
                </div>
              ) : (
                filteredFaqs.map(faq => (
                  <div
                    key={faq.id}
                    className="border border-border rounded-lg overflow-hidden bg-card"
                  >
                    <button
                      onClick={() => toggleExpand(faq.id)}
                      className="w-full flex items-center justify-between p-4 text-left hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex-1 pr-4">
                        <p className="font-medium text-foreground">{faq.question}</p>
                        <Badge variant="secondary" className="mt-1 text-xs">
                          {faq.category}
                        </Badge>
                      </div>
                      {expandedId === faq.id ? (
                        <ChevronUp className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                      )}
                    </button>
                    {expandedId === faq.id && (
                      <div className="px-4 pb-4 pt-0 text-muted-foreground text-sm border-t border-border bg-muted/30">
                        <p className="pt-4">{faq.answer}</p>
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </DrawerContent>
    </Drawer>
  );
};

export default FAQDrawer;
