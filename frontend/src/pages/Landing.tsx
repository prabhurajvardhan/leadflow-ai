import { useState, useEffect, useRef } from 'react'
import { Link } from 'react-router-dom'
import { 
  Search, Brain, Mail, BarChart3, Zap, Shield, 
  ChevronRight, Play, Users, Target, TrendingUp,
  CheckCircle2, ArrowRight, Star, Sparkles, Globe,
  Bot, Database, Send, Layers, Cpu, Lock
} from 'lucide-react'

export default function Landing() {
  const [isVisible, setIsVisible] = useState(false)
  const [activeFeature, setActiveFeature] = useState(0)
  const [typedText, setTypedText] = useState('')
  const heroRef = useRef<HTMLDivElement>(null)
  
  const fullText = "Find, analyze, and outreach to your perfect leads"

  useEffect(() => {
    setIsVisible(true)
    
    // Typing animation
    let index = 0
    const timer = setInterval(() => {
      if (index <= fullText.length) {
        setTypedText(fullText.slice(0, index))
        index++
      } else {
        clearInterval(timer)
      }
    }, 50)
    
    return () => clearInterval(timer)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveFeature(prev => (prev + 1) % features.length)
    }, 4000)
    return () => clearInterval(interval)
  }, [])

  const features = [
    {
      icon: <Search className="w-6 h-6" />,
      title: "Lead Discovery",
      description: "Find businesses from OpenStreetMap data instantly. No API keys or payment required.",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: <Globe className="w-6 h-6" />,
      title: "Website Crawling",
      description: "Automatically extract emails, phone numbers, and technologies from any website.",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: <Brain className="w-6 h-6" />,
      title: "AI Analysis",
      description: "Score leads, detect opportunities, and generate personalized outreach with AI.",
      color: "from-amber-500 to-orange-500"
    },
    {
      icon: <Send className="w-6 h-6" />,
      title: "Email Outreach",
      description: "Send personalized emails at scale with reply tracking and follow-ups.",
      color: "from-green-500 to-emerald-500"
    }
  ]

  const steps = [
    {
      number: "01",
      title: "Discover Leads",
      description: "Search for businesses by industry, location, or keywords. Our free OpenStreetMap collector finds companies instantly.",
      icon: <Search className="w-8 h-8" />
    },
    {
      number: "02", 
      title: "Enrich Data",
      description: "Automatically crawl websites to extract contact info, technologies used, and business details.",
      icon: <Database className="w-8 h-8" />
    },
    {
      number: "03",
      title: "AI Analysis",
      description: "Let AI score your leads, identify opportunities, and generate personalized outreach content.",
      icon: <Bot className="w-8 h-8" />
    },
    {
      number: "04",
      title: "Send Outreach",
      description: "Launch email campaigns with tracking. Monitor opens, replies, and follow up automatically.",
      icon: <Send className="w-8 h-8" />
    }
  ]

  const stats = [
    { value: "50+", label: "Data Points per Lead" },
    { value: "10x", label: "Faster Lead Discovery" },
    { value: "95%", label: "Email Deliverability" },
    { value: "24/7", label: "Automated Pipeline" }
  ]

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "Head of Sales, TechStart",
      content: "LeadFlow AI cut our lead research time by 80%. The AI-generated emails get 3x more responses.",
      avatar: "SC"
    },
    {
      name: "Marcus Johnson", 
      role: "Founder, GrowthLab",
      content: "Finally, a tool that actually delivers on its promises. The OpenStreetMap integration is brilliant.",
      avatar: "MJ"
    },
    {
      name: "Emily Rodriguez",
      role: "VP Marketing, ScaleUp",
      content: "The quality of leads and the personalization capabilities are unmatched. Highly recommended.",
      avatar: "ER"
    }
  ]

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white overflow-x-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/20 rounded-full blur-[128px] animate-pulse" />
        <div className="absolute top-1/3 right-1/4 w-80 h-80 bg-blue-600/20 rounded-full blur-[128px] animate-pulse delay-1000" />
        <div className="absolute bottom-1/4 left-1/3 w-72 h-72 bg-pink-600/15 rounded-full blur-[128px] animate-pulse delay-500" />
      </div>

      {/* Navigation */}
      <nav className="relative z-50 border-b border-white/10 backdrop-blur-xl bg-black/20">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-white to-purple-200 bg-clip-text text-transparent">
                LeadFlow AI
              </span>
            </div>
            
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" className="text-gray-400 hover:text-white transition-colors">How it Works</a>
              <a href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</a>
            </div>
            
            <div className="flex items-center gap-4">
              <Link to="/login" className="text-gray-400 hover:text-white transition-colors">
                Sign In
              </Link>
              <Link 
                to="/register"
                className="px-5 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
              >
                Get Started <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section ref={heroRef} className="relative z-10 pt-20 pb-32 px-6">
        <div className="max-w-5xl mx-auto text-center">
          {/* Badge */}
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 mb-8 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
            <Sparkles className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-gray-300">Powered by Amazon Nova AI • Free Lead Discovery</span>
          </div>

          {/* Headline */}
          <h1 className={`text-5xl md:text-7xl font-bold mb-6 leading-tight transition-all duration-1000 delay-200 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <span className="bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent">
              Find Your Perfect Leads
            </span>
            <br />
            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
              Powered by AI
            </span>
          </h1>

          {/* Subheadline with typing effect */}
          <p className="text-xl md:text-2xl text-gray-400 mb-8 h-8">
            {typedText}
            <span className="animate-pulse">|</span>
          </p>

          {/* CTA Buttons */}
          <div className={`flex flex-col sm:flex-row items-center justify-center gap-4 transition-all duration-1000 delay-400 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            <Link 
              to="/register"
              className="group px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl font-semibold text-lg hover:shadow-lg hover:shadow-purple-500/25 transition-all flex items-center gap-2"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <button className="px-8 py-4 rounded-xl border border-white/20 font-semibold text-lg hover:bg-white/5 transition-all flex items-center gap-2">
              <Play className="w-5 h-5" />
              Watch Demo
            </button>
          </div>

          {/* Stats */}
          <div className={`grid grid-cols-2 md:grid-cols-4 gap-8 mt-16 pt-16 border-t border-white/10 transition-all duration-1000 delay-600 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
            {stats.map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                  {stat.value}
                </div>
                <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Hero Visual */}
        <div className={`relative z-20 max-w-6xl mx-auto mt-20 transition-all duration-1000 delay-800 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-12'}`}>
          <div className="relative rounded-2xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-1">
            <div className="bg-[#0d0d14] rounded-xl p-6">
              {/* Mock Dashboard */}
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-green-500" />
              </div>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2 bg-gradient-to-br from-purple-900/30 to-blue-900/30 rounded-xl p-6 border border-white/5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                      <Users className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold">Lead Pipeline</h3>
                      <p className="text-sm text-gray-400">Active leads in enrichment</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    {['SaaS Companies', 'E-commerce Stores', 'Local Businesses'].map((item, i) => (
                      <div key={i} className="flex items-center justify-between bg-white/5 rounded-lg p-3">
                        <span className="text-sm">{item}</span>
                        <span className="text-sm text-purple-400">{Math.floor(Math.random() * 50 + 20)}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-gradient-to-br from-amber-900/30 to-orange-900/30 rounded-xl p-6 border border-white/5">
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                      <Target className="w-5 h-5 text-amber-400" />
                    </div>
                    <div>
                      <h3 className="font-semibold">AI Score</h3>
                      <p className="text-sm text-gray-400">Lead quality</p>
                    </div>
                  </div>
                  <div className="text-4xl font-bold text-amber-400 mb-2">87.5</div>
                  <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                    <div className="w-[87%] h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full" />
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Glow effect */}
          <div className="absolute -inset-px bg-gradient-to-r from-purple-500/20 via-transparent to-blue-500/20 rounded-2xl blur-xl -z-10" />
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative z-10 py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Everything You Need to
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                Close More Deals
              </span>
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              From lead discovery to personalized outreach, automate your entire sales pipeline with AI.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, i) => (
              <div
                key={i}
                className="group relative p-6 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/10 hover:border-purple-500/50 transition-all duration-300"
                onMouseEnter={() => setActiveFeature(i)}
              >
                <div className={`w-14 h-14 rounded-xl bg-gradient-to-br ${feature.color} p-0.5 mb-4 group-hover:scale-110 transition-transform`}>
                  <div className="w-full h-full rounded-[10px] bg-[#0a0a0f] flex items-center justify-center text-white">
                    {feature.icon}
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
                
                {/* Hover glow */}
                <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity -z-10 blur-xl`} />
              </div>
            ))}
          </div>

          {/* Feature Highlight */}
          <div className="mt-20 relative">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-blue-600/10 rounded-3xl blur-3xl" />
            <div className="relative bg-gradient-to-b from-white/5 to-transparent rounded-3xl border border-white/10 p-8 md:p-12">
              <div className="grid md:grid-cols-2 gap-12 items-center">
                <div>
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-400 text-sm mb-4">
                    <Cpu className="w-4 h-4" />
                    AI-Powered
                  </div>
                  <h3 className="text-3xl md:text-4xl font-bold mb-4">
                    Intelligent Lead Scoring & Analysis
                  </h3>
                  <p className="text-gray-400 mb-6">
                    Our AI analyzes dozens of data points to score your leads. Understand which prospects are most likely to convert and why.
                  </p>
                  <ul className="space-y-3">
                    {[
                      'Automatic opportunity detection',
                      'Personalized email generation',
                      'Industry-specific insights',
                      'Competitive landscape analysis'
                    ].map((item, i) => (
                      <li key={i} className="flex items-center gap-3">
                        <CheckCircle2 className="w-5 h-5 text-green-400" />
                        <span className="text-gray-300">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="relative">
                  <div className="bg-gradient-to-br from-purple-900/40 to-blue-900/40 rounded-2xl p-6 border border-white/10">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-400">Lead Score</span>
                        <span className="text-2xl font-bold text-green-400">92/100</span>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Company Size</span>
                          <span className="text-purple-400">85%</span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                          <div className="w-[85%] h-full bg-purple-500 rounded-full" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Tech Stack</span>
                          <span className="text-blue-400">78%</span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                          <div className="w-[78%] h-full bg-blue-500 rounded-full" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Market Fit</span>
                          <span className="text-amber-400">94%</span>
                        </div>
                        <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                          <div className="w-[94%] h-full bg-amber-500 rounded-full" />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="relative z-10 py-32 px-6 bg-gradient-to-b from-transparent via-purple-950/20 to-transparent">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Four Simple Steps to
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                Success
              </span>
            </h2>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, i) => (
              <div key={i} className="relative">
                <div className="text-7xl font-bold text-white/5 absolute -top-4 -left-2">
                  {step.number}
                </div>
                <div className="relative pt-8">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 border border-purple-500/30 flex items-center justify-center text-purple-400 mb-4">
                    {step.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                  <p className="text-gray-400 text-sm">{step.description}</p>
                </div>
                {i < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-12 right-0 w-full h-px bg-gradient-to-r from-purple-500/50 to-transparent" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="relative z-10 py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Loved by Sales Teams
              </span>
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, i) => (
              <div 
                key={i}
                className="p-6 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/10"
              >
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, j) => (
                    <Star key={j} className="w-4 h-4 fill-amber-400 text-amber-400" />
                  ))}
                </div>
                <p className="text-gray-300 mb-6 italic">"{testimonial.content}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center text-sm font-bold">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="font-semibold">{testimonial.name}</div>
                    <div className="text-sm text-gray-400">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="relative z-10 py-32 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Simple, Transparent Pricing
              </span>
            </h2>
            <p className="text-xl text-gray-400">Start free. Scale as you grow.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Free */}
            <div className="p-8 rounded-2xl bg-gradient-to-b from-white/5 to-transparent border border-white/10">
              <h3 className="text-xl font-semibold mb-2">Starter</h3>
              <p className="text-gray-400 text-sm mb-6">Perfect for getting started</p>
              <div className="mb-6">
                <span className="text-4xl font-bold">$0</span>
                <span className="text-gray-400">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {[
                  '100 leads per month',
                  'Basic AI analysis',
                  'Email outreach (50/month)',
                  '1 workspace',
                  'Community support'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-gray-300">
                    <CheckCircle2 className="w-5 h-5 text-green-400" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link 
                to="/register"
                className="block text-center py-3 rounded-xl border border-white/20 font-semibold hover:bg-white/5 transition-colors"
              >
                Get Started Free
              </Link>
            </div>

            {/* Pro */}
            <div className="relative p-8 rounded-2xl bg-gradient-to-b from-purple-900/40 to-blue-900/40 border border-purple-500/50">
              <div className="absolute -top-3 right-8 px-3 py-1 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 text-xs font-semibold">
                Popular
              </div>
              <h3 className="text-xl font-semibold mb-2">Pro</h3>
              <p className="text-gray-400 text-sm mb-6">For growing teams</p>
              <div className="mb-6">
                <span className="text-4xl font-bold">$49</span>
                <span className="text-gray-400">/month</span>
              </div>
              <ul className="space-y-3 mb-8">
                {[
                  'Unlimited leads',
                  'Advanced AI analysis',
                  'Email outreach (1000/month)',
                  '5 workspaces',
                  'Priority support',
                  'Custom templates',
                  'API access'
                ].map((item, i) => (
                  <li key={i} className="flex items-center gap-3 text-gray-300">
                    <CheckCircle2 className="w-5 h-5 text-purple-400" />
                    {item}
                  </li>
                ))}
              </ul>
              <Link 
                to="/register"
                className="block text-center py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 font-semibold hover:opacity-90 transition-opacity"
              >
                Start 14-Day Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-32 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative p-12 rounded-3xl overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-purple-600/20 to-blue-600/20" />
            <div className="absolute inset-0 backdrop-blur-xl" />
            <div className="relative">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">
                Ready to Transform Your
                <br />
                <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                  Lead Generation?
                </span>
              </h2>
              <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                Join thousands of sales teams using AI to find and convert their best leads.
              </p>
              <Link 
                to="/register"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-gray-900 rounded-xl font-semibold text-lg hover:bg-gray-100 transition-colors"
              >
                Get Started Free <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-white/10 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold">LeadFlow AI</span>
            </div>
            
            <div className="flex items-center gap-8 text-sm text-gray-400">
              <a href="#" className="hover:text-white transition-colors">Privacy</a>
              <a href="#" className="hover:text-white transition-colors">Terms</a>
              <a href="#" className="hover:text-white transition-colors">Contact</a>
            </div>
            
            <p className="text-sm text-gray-500">
              © 2024 LeadFlow AI. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
