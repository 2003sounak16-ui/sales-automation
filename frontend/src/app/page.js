"use client";

import { useState, useEffect } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://sales-backend-env.eba-szk7ushs.us-east-1.elasticbeanstalk.com';

export default function Home() {

  const [activeTab, setActiveTab] = useState('dashboard');
  const [leads, setLeads] = useState([]);
  const [pendingLeads, setPendingLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [globalTimeline, setGlobalTimeline] = useState([]);
  const [dashboardSelectedLeadId, setDashboardSelectedLeadId] = useState(null);
  const [dashboardLeadEvents, setDashboardLeadEvents] = useState([]);
  const [websiteQuery, setWebsiteQuery] = useState('');
  const [industryQuery, setIndustryQuery] = useState('');
  const [countryQuery, setCountryQuery] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [subjectEdit, setSubjectEdit] = useState('');
  const [bodyEdit, setBodyEdit] = useState('');
  const [toast, setToast] = useState(null);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewHtml, setPreviewHtml] = useState('');
  const [previewLoading, setPreviewLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [logFilter, setLogFilter] = useState('ALL');
  const [campaignDropdownOpen, setCampaignDropdownOpen] = useState(false);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const fetchLeads = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/leads`);
      if (response.ok) {
        const data = await response.json();
        data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
        setLeads(data);
      }
    } catch (err) {
      showToast('Failed to fetch leads: ' + err.message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingLeads = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/pending`);
      if (response.ok) {
        const data = await response.json();
        setPendingLeads(data);
      }
    } catch (err) {
      console.error('Failed to fetch pending reviews', err);
    }
  };

  const fetchGlobalTimeline = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/timeline/recent`);
      if (response.ok) {
        const data = await response.json();
        setGlobalTimeline(data);
      }
    } catch (err) {
      console.error('Failed to load global timeline', err);
    }
  };

  const handleDashboardLeadClick = async (leadId) => {
    if (dashboardSelectedLeadId === leadId) {
      setDashboardSelectedLeadId(null);
      setDashboardLeadEvents([]);
    } else {
      setDashboardSelectedLeadId(leadId);
      try {
        const response = await fetch(`${API_BASE_URL}/api/timeline/${leadId}`);
        if (response.ok) {
          const data = await response.json();
          setDashboardLeadEvents(data);
        }
      } catch (err) {
        console.error('Failed to load dashboard lead timeline', err);
      }
    }
  };

  const loadTimeline = async (leadId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/timeline/${leadId}`);
      if (response.ok) {
        const data = await response.json();
        setTimelineEvents(data);
      }
    } catch (err) {
      console.error('Failed to load timeline', err);
    }
  };

  const handleAnalyze = async (e) => {
    e.preventDefault();
    if (!websiteQuery.trim()) return;
    setAnalyzing(true);
    showToast(`Initializing pipeline analysis for '${websiteQuery}'...`, 'info');
    try {
      const response = await fetch(`${API_BASE_URL}/api/company/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          website_url: websiteQuery.trim(),
          industry: industryQuery.trim() || null,
          country: countryQuery.trim() || null
        })
      });
      if (response.ok) {
        const lead = await response.json();
        showToast(`Successfully analyzed '${websiteQuery}'!`, 'success');
        setWebsiteQuery('');
        setIndustryQuery('');
        setCountryQuery('');
        fetchLeads();
        fetchPendingLeads();
        fetchGlobalTimeline();
        setSelectedLead(lead);
        loadTimeline(lead.id);
        setSubjectEdit(lead.ai_subject || '');
        setBodyEdit(lead.ai_body || '');
        setActiveTab('review');
        setIsModalOpen(false);
      } else {
        const err = await response.json();
        showToast(`Analysis failed: ${err.detail || 'Error'}`, 'error');
      }
    } catch (err) {
      showToast(`Network error: ${err.message}`, 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApprove = async () => {
    if (!selectedLead) return;
    try {
      const response = await fetch(`${API_BASE_URL}/api/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_id: selectedLead.id,
          ai_subject: subjectEdit,
          ai_body: bodyEdit
        })
      });
      if (response.ok) {
        const updated = await response.json();
        showToast('Email draft successfully approved!', 'success');
        setSelectedLead(updated);
        loadTimeline(updated.id);
        await fetchLeads();
        await fetchPendingLeads();
      } else {
        showToast('Failed to approve draft.', 'error');
      }
    } catch (err) {
      showToast('Network error: ' + err.message, 'error');
    }
  };

  const handleSend = async () => {
    if (!selectedLead) return;
    if (!selectedLead.contact_email) {
      showToast('Cannot send — no verified contact email address available for this lead.', 'error');
      return;
    }
    try {
      const response = await fetch(`${API_BASE_URL}/api/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lead_id: selectedLead.id })
      });
      if (response.ok) {
        const resData = await response.json();
        showToast('Outreach email successfully sent!', 'success');
        setSelectedLead(resData.lead);
        loadTimeline(resData.lead.id);
        await fetchLeads();
        await fetchPendingLeads();
        fetchGlobalTimeline();
      } else {
        showToast('Failed to send outreach.', 'error');
      }
    } catch (err) {
      showToast('Network error: ' + err.message, 'error');
    }
  };

  const selectLeadForReview = async (lead) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/leads`);
      if (response.ok) {
        const allLeads = await response.json();
        const freshLead = allLeads.find(l => l.id === lead.id);
        if (freshLead) {
          lead = freshLead;
        }
      }
    } catch (err) {
      // ignore
    }
    setSelectedLead(lead);
    setSubjectEdit(lead.ai_subject || '');
    setBodyEdit(lead.ai_body || '');
    loadTimeline(lead.id);
    setActiveTab('review');
  };

  const parseSocialLinks = (socialLinks) => {
    if (!socialLinks) return {};
    if (typeof socialLinks === 'string') {
      try { return JSON.parse(socialLinks); }
      catch { return {}; }
    }
    if (typeof socialLinks === 'object') return socialLinks;
    return {};
  };

  const hasValidEmail = (lead) => {
    return lead?.contact_email && lead.contact_email.trim() !== '';
  };

  const openEmailPreview = async () => {
    if (!selectedLead) return;
    setPreviewLoading(true);
    setPreviewOpen(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/preview-email`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          subject: subjectEdit,
          body: bodyEdit
        })
      });
      if (response.ok) {
        const data = await response.json();
        setPreviewHtml(data.html);
      } else {
        showToast('Failed to generate email preview.', 'error');
        setPreviewOpen(false);
      }
    } catch (err) {
      showToast('Network error: ' + err.message, 'error');
      setPreviewOpen(false);
    } finally {
      setPreviewLoading(false);
    }
  };

  const closePreview = () => {
    setPreviewOpen(false);
    setPreviewHtml('');
  };

  useEffect(() => {
    const initData = async () => {
      await fetchLeads();
      await fetchPendingLeads();
      await fetchGlobalTimeline();
    };
    initData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formatEventDescription = (event, fallbackName) => {
    const company = event.leads?.company_name || fallbackName || 'Unknown Company';
    switch(event.event_type) {
      case 'DISCOVERY_PENDING': return `Started analysis for ${company}`;
      case 'DISCOVERY_SUCCESS': return `Found website for ${company}`;
      case 'SCRAPER_SUCCESS': return `Scraped data for ${company}`;
      case 'AI_GENERATED': return `AI drafted email for ${company}`;
      case 'REVIEW_APPROVED': return `Approved outreach for ${company}`;
      case 'EMAIL_SENT': return `Sent email to ${company}`;
      default: return `${event.event_type.replace(/_/g, ' ')} for ${company}`;
    }
  };

  const totalCount = leads.length;
  const pendingCount = leads.filter(l => l.status === 'PENDING_REVIEW').length;
  const sentCount = leads.filter(l => l.status === 'SENT').length;
  const failedCount = leads.filter(l => l.status === 'FAILED').length;

  return (
    <div className="dashboard-layout">
      {toast && (
        <div className={`toast-notification ${toast.type}`}>
          {toast.message}
        </div>
      )}

      <header className="fixed top-0 right-0 left-64 h-16 bg-surface/40 backdrop-blur-md border-b border-white/5 flex justify-between items-center px-6 z-40">
        <div className="flex items-center bg-surface-container-low rounded-full px-4 py-1.5 border border-white/5 w-96 group focus-within:border-primary-container/50 transition-all">
          <span className="material-symbols-outlined text-on-surface-variant text-lg">search</span>
          <input className="bg-transparent border-none focus:ring-0 text-sm text-on-surface w-full placeholder:text-on-surface-variant/50 outline-none ml-2" placeholder="Search outreach history..." type="text"/>
          <span className="text-[10px] text-on-surface-variant/50 font-mono px-1.5 py-0.5 border border-white/10 rounded">⌘K</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-4">
            <button className="relative p-2 text-on-surface-variant hover:text-primary-container transition-colors active:opacity-80 bg-transparent border-none cursor-pointer">
              <span className="material-symbols-outlined">notifications</span>
              <span className="absolute top-2 right-2 w-2 h-2 bg-error rounded-full border-2 border-surface"></span>
            </button>
            <button className="p-2 text-on-surface-variant hover:text-primary-container transition-colors active:opacity-80 bg-transparent border-none cursor-pointer">
              <span className="material-symbols-outlined">bolt</span>
            </button>
          </div>
          <div className="h-6 w-[1px] bg-white/10"></div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-on-surface-variant">System Status: <span className="text-primary-container font-bold" style={{ textShadow: "0 0 10px rgba(0,242,254,0.5)" }}>OPTIMAL</span></span>
          </div>
        </div>
      </header>

      <aside className="h-screen w-64 fixed left-0 top-0 border-r border-white/10 bg-surface-dim/80 backdrop-blur-xl flex flex-col py-base z-50">
        <div className="px-6 py-8">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-primary-container text-3xl">bolt</span>
            <span className="font-headline-lg font-bold text-primary-container drop-shadow-[0_0_10px_rgba(0,242,254,0.3)]">SalesFlow</span>
          </div>
          <p className="text-on-surface-variant font-label-sm mt-1 ml-11">Automation Hub</p>
        </div>
        <nav className="flex-1 space-y-2 px-4 mt-4">
          <button 
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group active:scale-95 text-left bg-transparent border-none cursor-pointer ${activeTab === 'dashboard' ? 'text-primary-container bg-primary-container/10 border-l-4 border-primary-container font-bold' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/5'}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <span className="material-symbols-outlined group-hover:text-primary-container">dashboard</span>
            <span>Dashboard</span>
          </button>
          <button 
            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all duration-300 group active:scale-95 text-left bg-transparent border-none cursor-pointer ${activeTab === 'review' ? 'text-primary-container bg-primary-container/10 border-l-4 border-primary-container font-bold' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/5'}`}
            onClick={() => setActiveTab('review')}
          >
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined group-hover:text-primary-container">pending_actions</span>
              <span>Review Queue</span>
            </div>
            <span className="bg-tertiary-container text-on-tertiary-container text-[10px] font-bold px-2 py-0.5 rounded-full">{pendingLeads.length}</span>
          </button>
          <button 
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-300 group active:scale-95 text-left bg-transparent border-none cursor-pointer ${activeTab === 'history' ? 'text-primary-container bg-primary-container/10 border-l-4 border-primary-container font-bold' : 'text-on-surface-variant hover:text-on-surface hover:bg-white/5'}`}
            onClick={() => setActiveTab('history')}
          >
            <span className="material-symbols-outlined group-hover:text-primary-container">history</span>
            <span>Outreach Log</span>
          </button>
        </nav>
        <div className="border-t border-white/5 mt-auto pt-4 pb-6 px-4 space-y-1">
          <button className="w-full flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-all duration-300 rounded-lg text-left bg-transparent border-none cursor-pointer">
            <span className="material-symbols-outlined text-sm">settings</span>
            <span className="text-sm">Settings</span>
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-2 text-on-surface-variant hover:text-on-surface hover:bg-white/5 transition-all duration-300 rounded-lg text-left bg-transparent border-none cursor-pointer">
            <span className="material-symbols-outlined text-sm">help</span>
            <span className="text-sm">Support</span>
          </button>
          <div className="mt-6 flex items-center gap-3 px-4">
            <div className="w-10 h-10 rounded-full border border-primary-container/30 p-0.5">
              <img className="w-full h-full rounded-full object-cover" alt="Profile avatar" src="https://lh3.googleusercontent.com/aida-public/AB6AXuDWTVL_8QuQ8WxDEbtc0G1llNvbMnDe6e6BAMuIrlpwfSJqDGrTdHP5Xhqnf6r_bsYJSFesFLxSIWoIE2PIiSOqMfGBBXCvGHuihW93dW2c6JZy2qmaLDypy-dJlv60Um9BcPYPnmbYSSuuBdR4an5AQTo9hZoBC3u-TzExNB3AwPMqw4gpnqXZvfpo3x9Ennf-6R3iBR_ad9qt_hjvECeh76VxE-BPDWddOExo7ukmahAK4hcNJmVdqja0jeahA-O9wkppptj8ugY"/>
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-bold text-on-surface truncate m-0">Alex Rivera</p>
              <p className="text-[10px] text-on-surface-variant truncate m-0 mt-0.5">Growth Lead</p>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-viewport">
        {activeTab === 'dashboard' && (
          <div className="tab-pane">
            <div className="page-header text-left" style={{ marginBottom: '2rem' }}>
              <h1 className="text-3xl font-extrabold text-on-surface mb-2">Sales Pipeline Dashboard</h1>
              <p className="text-on-surface-variant">Monitoring automated lead discovery and outreach.</p>
            </div>

            <section className="stats-grid">
              <div className="stat-card">
                <div className="stat-icon-wrapper">
                  <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--status-warning)' }}>hourglass_empty</span>
                </div>
                <div className="stat-label">Pending Review</div>
                <div className="stat-value">{pendingCount}</div>
                <div className="stat-trend positive">
                  <span>2+</span> Increased from last month
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon-wrapper">
                  <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--status-success)' }}>send</span>
                </div>
                <div className="stat-label">Emails Sent</div>
                <div className="stat-value">{sentCount}</div>
                <div className="stat-trend positive">
                  <span>1+</span> Increased from last month
                </div>
              </div>
              <div className="stat-card">
                <div className="stat-icon-wrapper">
                  <span className="material-symbols-outlined" style={{ fontSize: '18px', color: 'var(--status-error)' }}>report</span>
                </div>
                <div className="stat-label">Failed Runs</div>
                <div className="stat-value" style={{ color: 'var(--status-error)' }}>{failedCount}</div>
                <div className="stat-trend">
                  On Discuss
                </div>
              </div>
            </section>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
              <div className="lg:col-span-2 space-y-4 text-left">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="font-bold text-on-surface text-lg m-0">Active Scrapes & Leads</h2>
                  <button 
                    onClick={() => setIsModalOpen(true)}
                    className="bg-primary-container text-on-primary-container font-bold px-4 py-2 rounded-full flex items-center gap-2 hover:opacity-90 active:scale-95 transition-all cursor-pointer border-none shadow-[0_0_15px_rgba(0,242,254,0.3)] text-sm"
                  >
                    <span className="material-symbols-outlined text-sm">add</span>
                    <span>New Target</span>
                  </button>
                </div>
                {loading ? (
                  <p className="text-on-surface-variant">Loading database leads...</p>
                ) : leads.length === 0 ? (
                  <div className="border border-white/5 bg-surface-container/40 backdrop-blur-md rounded-2xl p-8 text-center">
                    <h3 className="font-bold text-on-surface">No Active Targets</h3>
                    <p className="text-on-surface-variant text-sm mt-1">Click &quot;New Target&quot; to add your first prospect to the pipeline.</p>
                  </div>
                ) : (
                  leads.map((lead) => (
                    <div 
                      className={`border backdrop-blur-md rounded-2xl p-5 transition-all duration-300 group cursor-pointer ${dashboardSelectedLeadId === lead.id ? 'border-primary-container bg-primary-container/5 shadow-[0_0_15px_rgba(0,242,254,0.15)]' : 'border-white/5 bg-surface-container/40 hover:border-primary-container/30'}`}
                      key={lead.id}
                      onClick={() => handleDashboardLeadClick(lead.id)}
                    >
                      <div className="flex justify-between items-start gap-4 flex-wrap">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-xl bg-primary-container/10 border border-primary-container/20 flex items-center justify-center">
                            <span className="material-symbols-outlined text-primary-container text-2xl">public</span>
                          </div>
                          <div>
                            <h3 className="font-bold text-on-surface group-hover:text-primary-container transition-colors m-0 text-base">{lead.company_name}</h3>
                            <p className="text-on-surface-variant text-xs mt-1 m-0">
                              {lead.website ? (
                                <a href={lead.website} target="_blank" rel="noreferrer" className="text-on-surface-variant hover:text-primary-container" onClick={(e) => e.stopPropagation()}>
                                  {(() => {
                                    try { return new URL(lead.website).hostname.replace('www.', '') }
                                    catch { return lead.website }
                                  })()}
                                </a>
                              ) : (
                                <span>no-website.com</span>
                              )}
                              {" • "}{lead.industry || 'General'}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <div className="flex -space-x-2">
                            <div className="w-7 h-7 rounded-full bg-primary-container/20 border-2 border-surface flex items-center justify-center text-[10px] font-bold text-primary-container">AI</div>
                            <div className="w-7 h-7 rounded-full bg-surface-variant border-2 border-surface flex items-center justify-center text-[10px] font-bold text-on-surface">U</div>
                          </div>
                          <span className="px-3 py-1 bg-surface-container rounded-full text-xs font-bold text-on-surface border border-white/5">
                            {lead.status.replace('_', ' ')}
                          </span>
                          <button 
                            className="p-1 hover:text-primary-container transition-colors bg-transparent border-none cursor-pointer flex items-center"
                            onClick={(e) => {
                              e.stopPropagation();
                              selectLeadForReview(lead);
                            }}
                          >
                            <span className="material-symbols-outlined text-lg">chevron_right</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>

              <div className="space-y-4 text-left">
                <div className="border border-white/5 bg-surface-container/20 rounded-2xl p-5 space-y-4">
                  <h3 className="font-bold text-on-surface text-lg m-0 flex justify-between items-center">
                    <span>
                      {dashboardSelectedLeadId 
                        ? `${leads.find(l => l.id === dashboardSelectedLeadId)?.company_name || 'Lead'} Timeline` 
                        : 'Activity Timeline'}
                    </span>
                    {dashboardSelectedLeadId && (
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setDashboardSelectedLeadId(null);
                          setDashboardLeadEvents([]);
                        }}
                        className="text-[10px] bg-white/5 hover:bg-white/10 text-on-surface-variant px-2.5 py-1 rounded-full cursor-pointer border-none"
                      >
                        Clear
                      </button>
                    )}
                  </h3>
                  {dashboardSelectedLeadId ? (
                    <div className="space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-[1px] before:bg-white/10">
                      {dashboardLeadEvents.map((event, idx) => (
                        <div className="flex gap-4 relative" key={`gtl-${idx}`}>
                          <div className="w-6 h-6 rounded-full bg-surface-container-high border border-white/10 flex items-center justify-center z-10 flex-shrink-0">
                            <div className="w-2 h-2 rounded-full bg-primary-container shadow-[0_0_8px_rgba(0,242,254,0.8)]"></div>
                          </div>
                          <div>
                            <p className="text-sm font-bold text-on-surface m-0">{formatEventDescription(event, leads.find(l => l.id === dashboardSelectedLeadId)?.company_name)}</p>
                            <p className="text-[10px] text-on-surface-variant mt-1 m-0">{new Date(event.created_at).toLocaleString()}</p>
                          </div>
                        </div>
                      ))}
                      {dashboardLeadEvents.length === 0 && (
                        <p className="text-on-surface-variant text-sm m-0">No recent activity.</p>
                      )}
                    </div>
                  ) : (
                    <p className="text-on-surface-variant text-sm m-0 py-4">Select an active scrape or lead from the list to view its timeline.</p>
                  )}
                </div>
              </div>
            </div>

            {isModalOpen && (
              <div className="modal-overlay" onClick={() => setIsModalOpen(false)}>
                <div className="modal-content text-left" onClick={e => e.stopPropagation()}>
                  <button className="modal-close" onClick={() => setIsModalOpen(false)}>&times;</button>
                  <h2 className="text-lg font-bold text-on-surface mb-6">Analyze New Target</h2>
                  <form onSubmit={handleAnalyze}>
                    <div className="flex flex-col gap-4 mb-6">
                      <div className="flex flex-col gap-1.5">
                        <label className="text-xs font-bold text-on-surface-variant">Company Website *</label>
                        <input
                          type="url"
                          placeholder="e.g. https://openai.com"
                          value={websiteQuery}
                          onChange={(e) => setWebsiteQuery(e.target.value)}
                          disabled={analyzing}
                          required
                          className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-on-surface outline-none focus:border-primary-container/50 transition-all"
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-bold text-on-surface-variant">Industry (opt)</label>
                          <input
                            type="text"
                            placeholder="e.g. AI"
                            value={industryQuery}
                            onChange={(e) => setIndustryQuery(e.target.value)}
                            disabled={analyzing}
                            className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-on-surface outline-none focus:border-primary-container/50 transition-all"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-bold text-on-surface-variant">Country (opt)</label>
                          <input
                            type="text"
                            placeholder="e.g. US"
                            value={countryQuery}
                            onChange={(e) => setCountryQuery(e.target.value)}
                            disabled={analyzing}
                            className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-on-surface outline-none focus:border-primary-container/50 transition-all"
                          />
                        </div>
                      </div>
                    </div>
                    <button type="submit" className="btn-primary w-full py-3 rounded-full text-sm" disabled={analyzing}>
                      {analyzing ? 'Analyzing Target...' : 'Start Pipeline'}
                    </button>
                  </form>
                  {analyzing && (
                    <div className="mt-6 flex items-center gap-4">
                      <span className="spinner"></span>
                      <div>
                        <p className="text-sm font-bold text-on-surface m-0">Executing sales intelligence pipeline...</p>
                        <small className="text-xs text-on-surface-variant block mt-0.5">Resolving domain, scraping content, and structuring AI pitches.</small>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'review' && (
          <div className="tab-pane">
            <header className="page-header text-left mb-8">
              <h1 className="text-3xl font-extrabold text-primary-container mb-2">Pitch Verification & Approval</h1>
              <p className="text-on-surface-variant">Verify scraping outputs, edit AI generated subjects, and approve emails for delivery.</p>
            </header>

            <div className="flex gap-6 items-start w-full text-left">
              {/* Left Sidebar Queue */}
              <div className="w-1/4 border border-white/5 bg-surface-container/40 backdrop-blur-md rounded-2xl p-5 flex-shrink-0">
                <h3 className="font-bold text-on-surface text-base m-0 mb-4 flex items-center gap-2">
                  <span className="material-symbols-outlined text-lg">list_alt</span>
                  Awaiting Review
                </h3>
                {pendingLeads.length === 0 ? (
                  <p className="text-on-surface-variant text-sm">No prospects awaiting review.</p>
                ) : (
                  <div className="space-y-2">
                    {pendingLeads.map((p) => (
                      <div 
                        key={p.id}
                        className={`p-3 rounded-xl cursor-pointer transition-all duration-200 border ${selectedLead?.id === p.id ? 'bg-primary-container/10 border-primary-container text-primary-container font-bold' : 'bg-transparent border-transparent hover:bg-white/5 text-on-surface'}`}
                        onClick={() => selectLeadForReview(p)}
                      >
                        <div className="text-sm truncate m-0">{p.company_name}</div>
                        <div className="text-[10px] text-on-surface-variant truncate m-0 mt-1">{p.industry || 'Technology'}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Right Details & Form Editor */}
              <div className="w-3/4 flex-grow">
                {selectedLead ? (
                  <div className="border border-white/5 bg-surface-container/20 rounded-2xl p-6">
                    <div className="flex justify-between items-center border-b border-white/5 pb-4 mb-6">
                      <div>
                        <h2 className="font-bold text-on-surface text-xl m-0 flex items-center gap-2">
                          <span className="material-symbols-outlined text-xl text-primary-container">business</span>
                          {selectedLead.company_name}
                        </h2>
                        {selectedLead.website && (
                          <a href={selectedLead.website} target="_blank" rel="noreferrer" className="text-xs text-primary-container hover:underline mt-1 inline-flex items-center gap-1">
                            {selectedLead.website}
                            <span className="material-symbols-outlined text-[10px]">open_in_new</span>
                          </a>
                        )}
                      </div>
                      <span className="px-3 py-1 bg-surface-container rounded-full text-xs font-bold text-on-surface border border-white/5 uppercase tracking-wider">
                        {selectedLead.status.replace('_', ' ')}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Company Overview Block */}
                      <div className="border border-white/5 bg-surface-container-low rounded-2xl p-5 space-y-4">
                        <h3 className="font-bold text-on-surface text-sm m-0 pb-2 border-b border-white/5 flex items-center gap-2">
                          <span className="material-symbols-outlined text-base">info</span>
                          Company Overview
                        </h3>
                        <div className="flex justify-between py-1 border-b border-white/5">
                          <span className="text-xs text-on-surface-variant">Industry</span>
                          <span className="text-xs text-on-surface font-semibold">{selectedLead.industry || 'Not specified'}</span>
                        </div>
                        <div className="flex justify-between py-1 border-b border-white/5">
                          <span className="text-xs text-on-surface-variant">Country</span>
                          <span className="text-xs text-on-surface font-semibold">{selectedLead.country || 'Not specified'}</span>
                        </div>
                        {selectedLead.description && (
                          <div className="py-1">
                            <span className="text-xs text-on-surface-variant block mb-1">Description</span>
                            <span className="text-xs text-on-surface leading-relaxed block">{selectedLead.description}</span>
                          </div>
                        )}
                      </div>

                      {/* Contact & Intelligence Block */}
                      <div className="border border-white/5 bg-surface-container-low rounded-2xl p-5 space-y-4">
                        <h3 className="font-bold text-on-surface text-sm m-0 pb-2 border-b border-white/5 flex items-center gap-2">
                          <span className="material-symbols-outlined text-base">analytics</span>
                          Contact & Intelligence
                        </h3>
                        <div className="py-1 border-b border-white/5">
                          <span className="text-xs text-on-surface-variant block mb-1">Primary Email</span>
                          {hasValidEmail(selectedLead) ? (
                            <span className="text-xs text-on-surface font-semibold flex items-center gap-1.5">
                              <span className="material-symbols-outlined text-emerald-500 text-sm">check_circle</span>
                              {selectedLead.contact_email}
                            </span>
                          ) : (
                            <div className="border border-error-container bg-error-container/10 rounded-2xl p-4 flex items-start gap-3">
                              <span className="material-symbols-outlined text-error text-xl">warning</span>
                              <div>
                                <h4 className="font-bold text-error m-0 text-xs">No Contact Email Detected</h4>
                                <p className="text-on-error-container text-[10px] mt-1 leading-normal m-0">
                                  Our automated scraper was unable to locate a publicly listed email address on this company&apos;s website.
                                </p>
                              </div>
                            </div>
                          )}
                        </div>
                        <div className="py-1">
                          <span className="text-xs text-on-surface-variant block mb-1.5">Social Links</span>
                          {(() => {
                            const socials = parseSocialLinks(selectedLead.social_links);
                            const entries = Object.entries(socials);
                            if (entries.length === 0) return <span className="text-xs text-on-surface font-semibold">None found</span>;
                            return (
                              <div className="flex gap-2 flex-wrap">
                                {entries.map(([platform, url]) => (
                                  <a 
                                    key={platform} 
                                    href={url} 
                                    target="_blank" 
                                    rel="noreferrer" 
                                    className="px-2.5 py-1 bg-surface rounded-full text-[10px] font-bold text-on-surface border border-white/5 hover:border-primary-container/40 transition-all"
                                  >
                                    {platform.charAt(0).toUpperCase() + platform.slice(1)}
                                  </a>
                                ))}
                              </div>
                            );
                          })()}
                        </div>
                      </div>
                    </div>

                    {/* Email Editor Form Panel */}
                    <div className="border border-white/5 bg-surface-container-low rounded-2xl p-5 mt-6 space-y-4">
                      <h3 className="font-bold text-on-surface text-sm m-0 pb-2 border-b border-white/5 flex items-center gap-2">
                        <span className="material-symbols-outlined text-base">drafts</span>
                        Draft Outreach Email
                      </h3>
                      <div className="space-y-4">
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-bold text-on-surface-variant">Subject Line</label>
                          <input
                            type="text"
                            value={subjectEdit}
                            onChange={(e) => setSubjectEdit(e.target.value)}
                            className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-on-surface outline-none focus:border-primary-container/50 transition-all"
                          />
                        </div>
                        <div className="flex flex-col gap-1.5">
                          <label className="text-xs font-bold text-on-surface-variant">Body Text</label>
                          <textarea
                            rows="8"
                            value={bodyEdit}
                            onChange={(e) => setBodyEdit(e.target.value)}
                            className="w-full bg-surface/50 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-on-surface outline-none focus:border-primary-container/50 transition-all font-mono"
                          />
                        </div>
                        {!hasValidEmail(selectedLead) && (
                          <div className="border border-error/25 bg-error/5 rounded-xl p-3.5 flex items-center gap-3">
                            <span className="material-symbols-outlined text-error text-lg">warning</span>
                            <span className="text-[11px] text-error font-medium">Email delivery is unavailable — no verified recipient address was found for this lead.</span>
                          </div>
                        )}
                        <div className="flex flex-wrap gap-4 pt-4 border-t border-white/5 mt-4">
                          <button 
                            className="bg-surface-variant text-on-surface hover:bg-white/10 px-5 py-2 rounded-full font-bold transition-all text-xs border-none cursor-pointer"
                            onClick={handleApprove}
                            disabled={selectedLead.status === 'SENT'}
                          >
                            Save & Approve Draft
                          </button>
                          <button 
                            className="bg-primary-container/10 text-primary-container hover:bg-primary-container/20 px-5 py-2 rounded-full font-bold transition-all text-xs border border-primary-container/20 cursor-pointer"
                            onClick={openEmailPreview}
                            disabled={previewLoading}
                          >
                            {previewLoading ? 'Generating...' : 'Preview HTML'}
                          </button>
                          <button 
                            className="bg-primary-container text-on-primary-container hover:opacity-90 active:scale-95 px-6 py-2.5 rounded-full font-bold transition-all ml-auto text-xs border-none cursor-pointer"
                            onClick={handleSend}
                            disabled={selectedLead.status !== 'APPROVED' || !hasValidEmail(selectedLead)}
                            title={!hasValidEmail(selectedLead) ? 'No verified email address available' : selectedLead.status !== 'APPROVED' ? 'Approve draft first' : 'Send outreach email'}
                          >
                            Send Outreach Email
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Audit Timeline Panel */}
                    <div className="border border-white/5 bg-surface-container-low rounded-2xl p-5 mt-6 space-y-4">
                      <h3 className="font-bold text-on-surface text-sm m-0 pb-2 border-b border-white/5 flex items-center gap-2">
                        <span className="material-symbols-outlined text-base">history</span>
                        Audit Timeline
                      </h3>
                      <div className="space-y-4 relative before:absolute before:left-3 before:top-2 before:bottom-2 before:w-[1px] before:bg-white/10 pt-2">
                        {timelineEvents.map((event, idx) => (
                          <div className="flex gap-4 relative" key={`tl-${idx}`}>
                            <div className="w-6 h-6 rounded-full bg-surface-container-high border border-white/10 flex items-center justify-center z-10 flex-shrink-0">
                              <div className="w-2 h-2 rounded-full bg-primary-container shadow-[0_0_8px_rgba(0,242,254,0.8)]"></div>
                            </div>
                            <div>
                              <p className="text-sm font-bold text-on-surface m-0">{formatEventDescription(event, selectedLead?.company_name)}</p>
                              <p className="text-[10px] text-on-surface-variant mt-1 m-0">{new Date(event.created_at).toLocaleString()}</p>
                            </div>
                          </div>
                        ))}
                        {timelineEvents.length === 0 && (
                          <p className="text-on-surface-variant text-sm m-0">No events found for this lead.</p>
                        )}
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="border border-white/5 bg-surface-container/20 rounded-2xl p-8 text-center">
                    <p className="text-on-surface-variant m-0 text-sm">Select a lead from the sidebar queue to edit and approve emails.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="tab-pane">
            <header className="flex justify-between items-center mb-6 flex-wrap gap-4 text-left">
              <div>
                <h1 className="text-3xl font-extrabold text-on-surface m-0">Outreach Logs</h1>
                <p className="text-on-surface-variant mt-1 m-0">Monitor outreach campaigns, sent emails, and delivery status logs.</p>
              </div>
              <div className="flex items-center gap-3 relative">
                <div className="flex items-center gap-2 border border-white/5 bg-surface-container/60 rounded-full px-4 py-2 text-sm font-bold text-on-surface">
                  <span>{leads.length} Leads</span>
                  <span className="text-emerald-500 flex items-center text-xs font-bold gap-1">
                    <span className="material-symbols-outlined text-sm">trending_up</span>+12 this week
                  </span>
                </div>
                <div className="relative">
                  <button 
                    className="flex items-center gap-2 border border-white/10 bg-surface-container/40 hover:bg-surface-container-high rounded-xl px-4 py-2.5 text-sm font-bold text-on-surface transition-all cursor-pointer"
                    onClick={() => setCampaignDropdownOpen(!campaignDropdownOpen)}
                  >
                    <span className="material-symbols-outlined text-lg text-primary-container">campaign</span>
                    <span>Q3 Tech Outreach Campaign</span>
                    <span className="material-symbols-outlined text-base">expand_more</span>
                  </button>
                  {campaignDropdownOpen && (
                    <div className="border border-white/10 bg-surface-container/90 backdrop-blur-xl absolute top-full right-0 mt-2 rounded-xl z-20 overflow-hidden min-w-[220px] p-1 shadow-2xl">
                      <div className="px-3 py-2 text-[10px] font-bold text-on-surface-variant uppercase tracking-wider">Select Campaign</div>
                      <button className="w-full text-left px-3 py-2 text-xs text-on-surface hover:bg-white/5 rounded-lg border-none bg-transparent cursor-pointer" onClick={() => setCampaignDropdownOpen(false)}>Cold SaaS Leads Campaign</button>
                      <button className="w-full text-left px-3 py-2 text-xs text-on-surface hover:bg-white/5 rounded-lg border-none bg-transparent cursor-pointer" onClick={() => setCampaignDropdownOpen(false)}>Global Enterprise Outreach</button>
                      <button className="w-full text-left px-3 py-2 text-xs text-on-surface hover:bg-white/5 rounded-lg border-none bg-transparent cursor-pointer" onClick={() => setCampaignDropdownOpen(false)}>All Campaigns</button>
                    </div>
                  )}
                </div>
              </div>
            </header>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-6 text-left">
              <div className="border border-white/5 bg-surface-container/40 rounded-2xl p-5 border-l-4 border-l-emerald-500">
                <p className="text-on-surface-variant text-xs font-bold uppercase tracking-wider m-0">Total Sent</p>
                <p className="text-3xl font-bold text-on-surface mt-2 mb-1">{sentCount}</p>
                <div className="flex items-center gap-1.5 text-emerald-500 text-xs font-bold">
                  <span className="material-symbols-outlined text-sm">trending_up</span><span>+12.5% from yesterday</span>
                </div>
              </div>
              <div className="border border-white/5 bg-surface-container/40 rounded-2xl p-5 border-l-4 border-l-primary-container">
                <p className="text-on-surface-variant text-xs font-bold uppercase tracking-wider m-0">Opened</p>
                <p className="text-3xl font-bold text-on-surface mt-2 mb-1">{sentCount > 0 ? '73.8%' : '0%'}</p>
                <div className="flex items-center gap-1.5 text-primary-container text-xs font-bold">
                  <span className="material-symbols-outlined text-sm">visibility</span><span>{sentCount > 0 ? Math.ceil(sentCount * 0.738) : 0} total opens</span>
                </div>
              </div>
              <div className="border border-white/5 bg-surface-container/40 rounded-2xl p-5 border-l-4 border-l-error">
                <p className="text-on-surface-variant text-xs font-bold uppercase tracking-wider m-0">Bounced</p>
                <p className="text-3xl font-bold text-error mt-2 mb-1">{leads.length > 0 ? `${(failedCount / leads.length * 100).toFixed(1)}%` : '0%'}</p>
                <div className="flex items-center gap-1.5 text-error text-xs font-bold">
                  <span className="material-symbols-outlined text-sm">report</span><span>Reputation stable</span>
                </div>
              </div>
              <div className="border border-white/5 bg-surface-container/40 rounded-2xl p-5 border-l-4 border-l-primary-container">
                <p className="text-on-surface-variant text-xs font-bold uppercase tracking-wider m-0">Click Rate</p>
                <p className="text-3xl font-bold text-on-surface mt-2 mb-1">{sentCount > 0 ? '48%' : '0%'}</p>
                <div className="flex items-center gap-1.5 text-primary-container text-xs font-bold">
                  <span className="material-symbols-outlined text-sm">mouse</span><span>{sentCount > 0 ? Math.ceil(sentCount * 0.48) : 0} unique clicks</span>
                </div>
              </div>
            </div>

            <section className="border border-white/5 bg-surface-container/20 rounded-2xl p-6 text-left">
              <div className="flex justify-between items-center flex-wrap gap-4 mb-6">
                <div className="flex gap-2 flex-wrap">
                  {['ALL', 'SENT', 'DELIVERED', 'OPENED', 'BOUNCED'].map((filter) => (
                    <button 
                      key={filter}
                      onClick={() => setLogFilter(filter)}
                      className={`px-4 py-2 rounded-full text-xs font-bold transition-all cursor-pointer border ${logFilter === filter ? 'bg-primary-container text-on-primary-container border-primary-container shadow-[0_0_12px_rgba(0,242,254,0.4)]' : 'bg-surface-container/40 hover:bg-surface-container text-on-surface-variant border-white/5'}`}
                    >
                      {filter.charAt(0) + filter.slice(1).toLowerCase()}
                    </button>
                  ))}
                </div>
                <div className="flex gap-2">
                  <button className="flex items-center gap-1.5 border border-white/10 bg-surface-container/40 hover:bg-surface-container-high rounded-xl px-4 py-2 text-xs font-bold text-on-surface transition-all cursor-pointer">
                    <span className="material-symbols-outlined text-sm">filter_alt</span> Filter
                  </button>
                  <button className="flex items-center gap-1.5 border border-white/10 bg-surface-container/40 hover:bg-surface-container-high rounded-xl px-4 py-2 text-xs font-bold text-on-surface transition-all cursor-pointer">
                    <span className="material-symbols-outlined text-sm">file_download</span> Export
                  </button>
                </div>
              </div>

              <div className="space-y-4">
                {leads.filter(l => l.status === 'SENT').length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-on-surface-variant text-sm m-0">No sent outreach logged yet for Q3 Tech Outreach Campaign.</p>
                  </div>
                ) : (
                  leads.filter(l => l.status === 'SENT').map(l => (
                    <div key={l.id} className="border border-white/5 bg-surface-container/40 rounded-2xl p-5 hover:border-primary-container/20 transition-all duration-300">
                      <div className="flex justify-between items-center mb-4 gap-4 flex-wrap">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-xl bg-primary-container/10 border border-primary-container/20 flex items-center justify-center">
                            <span className="material-symbols-outlined text-primary-container text-xl">corporate_fare</span>
                          </div>
                          <div>
                            <h3 className="font-bold text-on-surface text-sm m-0 flex items-center gap-2 flex-wrap">
                              {l.company_name}
                              <span className="text-xs font-normal text-on-surface-variant">{l.contact_email}</span>
                            </h3>
                            <p className="text-[10px] text-on-surface-variant mt-1 m-0 flex items-center gap-1">
                              <span className="material-symbols-outlined text-[12px]">schedule</span> Sent recently
                            </p>
                          </div>
                        </div>
                        <div>
                          <span className="px-3 py-1 bg-emerald-500/10 text-emerald-500 rounded-full text-[10px] font-bold border border-emerald-500/20 uppercase tracking-wider flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span> SENT
                          </span>
                        </div>
                      </div>
                      <div className="space-y-3">
                        <div>
                          <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-wider m-0">Subject</p>
                          <p className="text-sm font-bold text-on-surface mt-1 m-0">{l.ai_subject}</p>
                        </div>
                        <div className="bg-surface/50 border border-white/5 rounded-xl p-4 font-mono text-xs text-on-surface-variant leading-relaxed white-space-pre-wrap">
                          {l.ai_body}
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t border-white/5 flex gap-4 flex-wrap">
                        <button className="flex items-center gap-1.5 text-xs font-bold text-primary-container bg-transparent border-none cursor-pointer hover:underline">
                          <span className="material-symbols-outlined text-sm">terminal</span> View Raw Delivery Log
                        </button>
                        <button className="flex items-center gap-1.5 text-xs font-bold text-on-surface-variant bg-transparent border-none cursor-pointer hover:underline">
                          <span className="material-symbols-outlined text-sm">replay</span> Resend Email
                        </button>
                        <button className="flex items-center gap-1.5 text-xs font-bold text-on-surface-variant bg-transparent border-none cursor-pointer hover:underline ml-auto">
                          <span className="material-symbols-outlined text-sm">query_stats</span> Analytics Tracking
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </section>
          </div>
        )}
      </main>

      {/* Email Preview Modal */}
      {previewOpen && (
        <div className="fixed inset-0 bg-surface/80 backdrop-blur-md flex items-center justify-center z-50 p-6" onClick={closePreview}>
          <div className="bg-surface-container border border-white/10 rounded-2xl w-full max-w-4xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden text-left" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-center p-6 border-b border-white/5 flex-shrink-0">
              <div>
                <span className="bg-primary-container/10 text-primary-container text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">HTML Preview</span>
                <h2 className="font-bold text-on-surface text-lg m-0 mt-1 truncate max-w-[450px]">
                  {subjectEdit || 'Email Preview'}
                </h2>
                <p className="text-on-surface-variant text-xs m-0 mt-0.5">
                  Exact rendering your recipient will see in their inbox
                </p>
              </div>
              <div className="flex items-center gap-3">
                <button
                  className="flex items-center gap-2 border border-white/10 bg-surface-container/40 hover:bg-surface-container-high rounded-full px-4 py-2 text-xs font-bold text-on-surface transition-all cursor-pointer"
                  onClick={closePreview}
                >
                  <span className="material-symbols-outlined text-sm">edit</span>
                  <span>Edit Email</span>
                </button>
                <button
                  className="bg-primary-container text-on-primary-container hover:opacity-90 active:scale-95 px-5 py-2 rounded-full font-bold transition-all text-xs border-none cursor-pointer"
                  onClick={() => { closePreview(); handleSend(); }}
                  disabled={selectedLead?.status !== 'APPROVED'}
                  title={selectedLead?.status !== 'APPROVED' ? 'Approve draft first' : 'Send this email'}
                >
                  Send Now
                </button>
                <button className="p-1 hover:text-primary-container transition-colors bg-transparent border-none cursor-pointer text-on-surface-variant flex items-center" onClick={closePreview} title="Close preview">
                  <span className="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto flex-1 bg-surface-container-lowest min-h-[400px] flex items-center justify-center">
              {previewLoading ? (
                <div className="text-center">
                  <span className="spinner mb-2"></span>
                  <p className="text-sm text-on-surface-variant m-0">Rendering email template...</p>
                </div>
              ) : (
                <iframe
                  className="w-full h-[400px] border-none bg-white rounded-lg"
                  srcDoc={previewHtml}
                  title="Email HTML Preview"
                  sandbox="allow-same-origin"
                />
              )}
            </div>

            <div className="flex justify-between items-center p-4 border-t border-white/5 bg-surface-container-low text-xs text-on-surface-variant flex-shrink-0 flex-wrap gap-2">
              <div>
                <strong>To:</strong> {selectedLead?.contact_email || 'delivered@resend.dev'}
              </div>
              <div className="flex gap-4">
                <span>
                  <strong>Status:</strong> <span className="text-primary-container font-semibold uppercase">{selectedLead?.status?.replace('_', ' ')}</span>
                </span>
                <span>
                  <strong>Company:</strong> {selectedLead?.company_name}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
