import React, { useState, useMemo } from 'react';
import { Calculator, X, IndianRupee, Calendar, Percent, TrendingUp } from 'lucide-react';
import { Language } from '@/data/translations';

interface EMICalculatorProps {
  language: Language;
}

const EMICalculator: React.FC<EMICalculatorProps> = ({ language }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [loanAmount, setLoanAmount] = useState(300000);
  const [interestRate, setInterestRate] = useState(10.5);
  const [tenure, setTenure] = useState(24);

  const labels = {
    en: {
      title: 'EMI Calculator',
      loanAmount: 'Loan Amount',
      interestRate: 'Interest Rate',
      tenure: 'Tenure',
      months: 'months',
      emi: 'Monthly EMI',
      totalInterest: 'Total Interest',
      totalPayment: 'Total Payment',
      breakdown: 'Payment Breakdown',
      principal: 'Principal',
      interest: 'Interest'
    },
    hi: {
      title: 'EMI कैलकुलेटर',
      loanAmount: 'लोन राशि',
      interestRate: 'ब्याज दर',
      tenure: 'अवधि',
      months: 'महीने',
      emi: 'मासिक EMI',
      totalInterest: 'कुल ब्याज',
      totalPayment: 'कुल भुगतान',
      breakdown: 'भुगतान विवरण',
      principal: 'मूलधन',
      interest: 'ब्याज'
    }
  };

  const t = labels[language];

  const calculations = useMemo(() => {
    const r = interestRate / (12 * 100);
    const n = tenure;
    const emi = Math.round((loanAmount * r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1));
    const totalPayment = emi * n;
    const totalInterest = totalPayment - loanAmount;
    const principalPercentage = (loanAmount / totalPayment) * 100;
    const interestPercentage = (totalInterest / totalPayment) * 100;

    return { emi, totalPayment, totalInterest, principalPercentage, interestPercentage };
  }, [loanAmount, interestRate, tenure]);

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN')}`;
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-24 left-6 z-50 w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all duration-300 transform hover:scale-110 bg-gradient-to-br from-secondary to-secondary-dark hover:shadow-lg"
        aria-label="Open EMI Calculator"
      >
        <Calculator className="w-6 h-6 text-primary" />
      </button>

      {/* Calculator Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-gradient-to-br from-background via-blue-50 to-yellow-50 w-full max-w-lg mx-4 rounded-3xl shadow-2xl overflow-hidden animate-scale-up">
            {/* Header */}
            <div className="bg-gradient-primary px-6 py-4 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-secondary rounded-full flex items-center justify-center">
                  <Calculator className="w-5 h-5 text-primary" />
                </div>
                <h3 className="text-white font-bold text-lg">{t.title}</h3>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 bg-white/20 rounded-full text-white hover:bg-white/30 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Calculator Body */}
            <div className="p-6 space-y-6">
              {/* Loan Amount Slider */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <IndianRupee className="w-4 h-4 text-primary" />
                    {t.loanAmount}
                  </label>
                  <span className="text-lg font-bold text-primary">{formatCurrency(loanAmount)}</span>
                </div>
                <input
                  type="range"
                  min="50000"
                  max="2000000"
                  step="10000"
                  value={loanAmount}
                  onChange={(e) => setLoanAmount(Number(e.target.value))}
                  className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>₹50K</span>
                  <span>₹20L</span>
                </div>
              </div>

              {/* Interest Rate Slider */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <Percent className="w-4 h-4 text-primary" />
                    {t.interestRate}
                  </label>
                  <span className="text-lg font-bold text-primary">{interestRate}%</span>
                </div>
                <input
                  type="range"
                  min="8"
                  max="24"
                  step="0.5"
                  value={interestRate}
                  onChange={(e) => setInterestRate(Number(e.target.value))}
                  className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>8%</span>
                  <span>24%</span>
                </div>
              </div>

              {/* Tenure Slider */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-foreground flex items-center gap-2">
                    <Calendar className="w-4 h-4 text-primary" />
                    {t.tenure}
                  </label>
                  <span className="text-lg font-bold text-primary">{tenure} {t.months}</span>
                </div>
                <input
                  type="range"
                  min="6"
                  max="60"
                  step="6"
                  value={tenure}
                  onChange={(e) => setTenure(Number(e.target.value))}
                  className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-primary"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>6</span>
                  <span>60</span>
                </div>
              </div>

              {/* Results */}
              <div className="bg-white rounded-2xl p-5 shadow-lg border border-border space-y-4">
                {/* EMI Highlight */}
                <div className="text-center pb-4 border-b border-border">
                  <p className="text-sm text-muted-foreground mb-1">{t.emi}</p>
                  <p className="text-4xl font-bold text-primary">{formatCurrency(calculations.emi)}</p>
                </div>

                {/* Breakdown */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 bg-gradient-to-br from-primary/5 to-primary/10 rounded-xl">
                    <p className="text-xs text-muted-foreground mb-1">{t.totalInterest}</p>
                    <p className="text-lg font-bold text-primary">{formatCurrency(calculations.totalInterest)}</p>
                  </div>
                  <div className="text-center p-3 bg-gradient-to-br from-secondary/20 to-secondary/30 rounded-xl">
                    <p className="text-xs text-muted-foreground mb-1">{t.totalPayment}</p>
                    <p className="text-lg font-bold text-secondary-dark">{formatCurrency(calculations.totalPayment)}</p>
                  </div>
                </div>

                {/* Visual Breakdown Bar */}
                <div className="space-y-2">
                  <p className="text-xs font-medium text-muted-foreground">{t.breakdown}</p>
                  <div className="h-4 rounded-full overflow-hidden flex">
                    <div 
                      className="bg-gradient-to-r from-primary to-primary-light transition-all duration-300"
                      style={{ width: `${calculations.principalPercentage}%` }}
                    />
                    <div 
                      className="bg-gradient-to-r from-secondary-dark to-secondary transition-all duration-300"
                      style={{ width: `${calculations.interestPercentage}%` }}
                    />
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="flex items-center gap-1">
                      <span className="w-3 h-3 rounded-full bg-primary" />
                      {t.principal} ({calculations.principalPercentage.toFixed(1)}%)
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-3 h-3 rounded-full bg-secondary" />
                      {t.interest} ({calculations.interestPercentage.toFixed(1)}%)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default EMICalculator;
