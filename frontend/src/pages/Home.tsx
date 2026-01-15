import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { 
  MessageSquare, 
  Handshake, 
  FileCheck, 
  Calculator, 
  Shield, 
  FileText, 
  Server, 
  Cpu,
  ArrowRight,
  Zap,
  Target,
  Gift,
  Award,
  Bot,
  Clock,
  MessageCircle
} from "lucide-react";

const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: { opacity: 1, y: 0 }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};

const scaleIn = {
  hidden: { opacity: 0, scale: 0.8 },
  visible: { opacity: 1, scale: 1 }
};

const Home = () => {
  const navigate = useNavigate();

  const features = [
    { icon: MessageSquare, title: "Conversational AI Chatbot", description: "Natural language interaction for seamless loan inquiries" },
    { icon: Handshake, title: "Negotiates Just Like Humans", description: "Smart negotiation capabilities for personalized offers" },
    { icon: FileCheck, title: "PAN & Salary Slip Verification", description: "Automated document verification and validation" },
    { icon: Calculator, title: "Automated EMI & Offer Calculation", description: "Instant EMI computation with best rates" },
    { icon: Shield, title: "Loan Underwriting & Risk Engine", description: "AI-powered credit assessment and risk scoring" },
    { icon: FileText, title: "Instant Sanction Letter PDF", description: "Generate loan sanction documents instantly" },
    { icon: Server, title: "Fully Tested Backend APIs", description: "Robust and reliable FastAPI backend" },
    { icon: Cpu, title: "Works with LangGraph Agents", description: "Advanced multi-agent orchestration" },
  ];

  const agents = [
    { name: "Master Agent", role: "Controls Full Flow", color: "bg-primary" },
    { name: "Sales Agent", role: "Offers & EMI", color: "bg-agent-sales" },
    { name: "Verification Agent", role: "PAN, Salary Slip", color: "bg-agent-verification" },
    { name: "Underwriting Agent", role: "Risk Scoring", color: "bg-agent-underwriting" },
    { name: "Sanction Agent", role: "PDF Letter", color: "bg-agent-sanction" },
  ];

  const metrics = [
    { value: "48hrs → 2min", label: "Processing Time Reduced", icon: Clock },
    { value: "80%", label: "Automation Rate", icon: Zap },
    { value: "97%", label: "Accuracy Score", icon: Target },
    { value: "Smart", label: "Personalised Offers", icon: Gift },
    { value: "Best", label: "Negotiators", icon: Award },
  ];

  const team = [
    { name: "Harshit Arora", college: "VIT, Bhopal" },
    { name: "Dharanikota Lavnesh Rao", college: "VIT, Vellore" },
    { name: "Pulkit Agrawal", college: "VIT, Bhopal" },
    { name: "Akshat Majila", college: "VIT, Chennai" },
    { name: "Tejas Ranjeet", college: "IIT, Madras" },
  ];

  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-background to-secondary/10" />
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-secondary/20 rounded-full blur-3xl" />
        
        <div className="relative container mx-auto px-6 py-24 md:py-32">
          <motion.div 
            className="max-w-4xl mx-auto text-center"
            initial="hidden"
            animate="visible"
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} transition={{ duration: 0.5 }}>
              <Badge variant="secondary" className="mb-6 px-4 py-2 text-sm font-medium">
                <Bot className="w-4 h-4 mr-2 inline" />
                Multi-Agent AI System
              </Badge>
            </motion.div>
            
            <motion.h1 
              className="text-4xl md:text-6xl lg:text-7xl font-bold text-foreground mb-6 leading-tight"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Tata Capital
              <span className="block text-primary">AI Powered Loan Assistant</span>
            </motion.h1>
            
            <motion.p 
              className="text-lg md:text-xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              A multi-agent conversational AI that automates loan inquiry, verification, 
              underwriting and sanctioning — just like real loan officers.
            </motion.p>
            
            <motion.div variants={fadeInUp} transition={{ duration: 0.6, delay: 0.3 }}>
              <Button 
                size="lg" 
                onClick={() => navigate('/chat')}
                className="group px-8 py-6 text-lg font-semibold shadow-xl hover:shadow-2xl transition-all duration-300"
              >
                Launch AI Loan Assistant
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* About Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <motion.div 
            className="max-w-4xl mx-auto"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div 
              className="flex items-center gap-3 mb-6"
              variants={fadeInUp}
              transition={{ duration: 0.5 }}
            >
              <div className="w-12 h-1 bg-primary rounded-full" />
              <span className="text-primary font-bold uppercase tracking-wider text-base md:text-lg">About The Project</span>
            </motion.div>
            
            <motion.h2 
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-8"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Built by Team <span className="text-primary">Code Catalysts</span>
            </motion.h2>
            
            <motion.p 
              className="text-lg md:text-xl text-muted-foreground leading-relaxed"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              We built an AI Powered Loan Assistant using a multi-agent architecture. It simulates 
              how real loan officers in Tata Capital work across <strong>Sales</strong>, <strong>Verification</strong>, 
              <strong> Underwriting</strong> and <strong>Sanctioning</strong>. The system guides the user from 
              loan inquiry → verification → underwriting → sanction letter automatically, improving 
              speed, accuracy and customer experience.
            </motion.p>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} transition={{ duration: 0.5 }}>
              <Badge variant="outline" className="mb-4 text-base px-4 py-2">Features</Badge>
            </motion.div>
            <motion.h2 
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Powerful Capabilities
            </motion.h2>
          </motion.div>
          
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={staggerContainer}
          >
            {features.map((feature, index) => (
              <motion.div
                key={index}
                variants={scaleIn}
                transition={{ duration: 0.5, delay: index * 0.05 }}
              >
                <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-border/50 bg-card/50 backdrop-blur h-full">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                      <feature.icon className="w-6 h-6 text-primary" />
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground text-sm">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* System Flow Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} transition={{ duration: 0.5 }}>
              <Badge variant="outline" className="mb-4 text-base px-4 py-2">Architecture</Badge>
            </motion.div>
            <motion.h2 
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Multi-Agent System Flow
            </motion.h2>
          </motion.div>
          
          <motion.div 
            className="flex flex-wrap justify-center gap-4 md:gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={staggerContainer}
          >
            {agents.map((agent, index) => (
              <motion.div 
                key={index} 
                className="flex items-center"
                variants={scaleIn}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="p-6 bg-card border-border/50 hover:shadow-lg transition-all duration-300">
                  <div className={`w-4 h-4 rounded-full ${agent.color} mb-3`} />
                  <h3 className="font-bold text-foreground">{agent.name}</h3>
                  <p className="text-sm text-muted-foreground">{agent.role}</p>
                </Card>
                {index < agents.length - 1 && (
                  <ArrowRight className="w-6 h-6 text-muted-foreground mx-2 hidden md:block" />
                )}
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Metrics Section */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} transition={{ duration: 0.5 }}>
              <Badge variant="outline" className="mb-4 text-base px-4 py-2">Impact</Badge>
            </motion.div>
            <motion.h2 
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Transforming Loan Processing
            </motion.h2>
          </motion.div>
          
          <motion.div 
            className="grid grid-cols-2 md:grid-cols-5 gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={staggerContainer}
          >
            {metrics.map((metric, index) => (
              <motion.div
                key={index}
                variants={scaleIn}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="p-6 text-center bg-gradient-to-br from-card to-muted/30 border-border/50 hover:shadow-lg transition-all duration-300 h-full">
                  <metric.icon className="w-8 h-8 text-primary mx-auto mb-4" />
                  <div className="text-2xl md:text-3xl font-bold text-foreground mb-2">{metric.value}</div>
                  <p className="text-sm text-muted-foreground">{metric.label}</p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-muted/30">
        <div className="container mx-auto px-6">
          <motion.div 
            className="text-center mb-16"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-100px" }}
            variants={staggerContainer}
          >
            <motion.div variants={fadeInUp} transition={{ duration: 0.5 }}>
              <Badge variant="outline" className="mb-4 text-base px-4 py-2">Team</Badge>
            </motion.div>
            <motion.h2 
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground"
              variants={fadeInUp}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Code Catalysts from VIT
            </motion.h2>
          </motion.div>
          
          <motion.div 
            className="flex flex-wrap justify-center gap-6"
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, margin: "-50px" }}
            variants={staggerContainer}
          >
            {team.map((member, index) => (
              <motion.div
                key={index}
                variants={scaleIn}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card className="p-6 bg-card border-border/50 hover:shadow-lg transition-all duration-300 min-w-[200px]">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-primary-foreground">
                      {member.name.charAt(0)}
                    </span>
                  </div>
                  <h3 className="font-bold text-foreground text-center">{member.name}</h3>
                  <p className="text-sm text-muted-foreground text-center">{member.college}</p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* CTA Section */}
      <motion.section 
        className="py-20"
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        variants={fadeInUp}
        transition={{ duration: 0.8 }}
      >
        <div className="container mx-auto px-6">
          <Card className="p-12 bg-gradient-to-r from-primary/10 via-background to-secondary/10 border-primary/20 text-center">
            <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-6">
              Ready to Experience AI-Powered Lending?
            </h2>
            <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
              Start your loan journey with our intelligent assistant. Get instant offers, 
              quick verification, and automated approval — all in minutes.
            </p>
            <Button 
              size="lg" 
              onClick={() => navigate('/chat')}
              className="group px-8 py-6 text-lg font-semibold"
            >
              Get Started Now
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Button>
          </Card>
        </div>
      </motion.section>

      {/* Footer */}
      <motion.footer 
        className="py-8 border-t border-border"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <div className="container mx-auto px-6 text-center">
          <p className="text-muted-foreground">
            Made with ❤️ for <span className="font-semibold text-foreground">EY Techathon 6.0</span>
          </p>
        </div>
      </motion.footer>

      {/* Floating Chat Button */}
      <motion.button
        onClick={() => navigate('/chat')}
        className="fixed bottom-6 right-6 w-14 h-14 bg-primary rounded-full flex items-center justify-center shadow-xl hover:shadow-2xl hover:scale-110 transition-all duration-300 z-50"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 1, type: "spring", stiffness: 200 }}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        <MessageCircle className="w-6 h-6 text-primary-foreground" />
      </motion.button>
    </div>
  );
};

export default Home;
