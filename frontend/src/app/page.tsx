'use client';

import { useQuery } from '@tanstack/react-query';
import { agentsApi, callsApi, costsApi } from '@/lib/api';
import { Phone, Users, DollarSign, Activity, Settings, FileText, CircleHelp } from 'lucide-react';

export default function Dashboard() {
  // Fetch data
  const { data: agents } = useQuery({
    queryKey: ['agents'],
    queryFn: () => agentsApi.list().then(res => res.data),
  });

  const { data: callsData } = useQuery({
    queryKey: ['calls'],
    queryFn: () => callsApi.list({ page: 1, page_size: 5 }).then(res => res.data),
  });

  const { data: costs } = useQuery({
    queryKey: ['costs'],
    queryFn: () => costsApi.getSummary().then(res => res.data),
  });

  const activeAgents = agents?.filter(a => a.is_active).length || 0;
  const totalCalls = callsData?.total || 0;
  const recentCalls = callsData?.items || [];
  const totalCost = costs?.total_cost || 0;

  return (
    <div className="min-h-screen bg-surface-lowest text-on-surface font-body">
      {/* Side Navigation */}
      <aside className="fixed left-0 top-0 h-full w-[280px] bg-surface-lowest/80 backdrop-blur-[20px] border-r border-white/10 shadow-[10px_0_30px_rgba(0,0,0,0.5)] z-60 flex flex-col">
        {/* Brand Header */}
        <div className="p-8">
          <h1 className="text-2xl font-black tracking-tighter text-cyan-glow drop-shadow-[0_0_10px_rgba(0,217,255,0.5)]">
            VoiceAI
          </h1>
          <p className="text-[10px] uppercase tracking-[0.2em] text-white/40 mt-1">
            Orchestrator v2.0
          </p>
        </div>

        {/* Primary CTA */}
        <div className="px-6 mb-8">
          <button className="w-full py-3 px-4 rounded-xl bg-primary-container text-on-primary font-bold text-sm flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(0,217,255,0.4)] hover:scale-[0.98] transition-transform">
            <Phone className="h-4 w-4" />
            New Agent
          </button>
        </div>

        {/* Navigation Links */}
        <nav className="flex-1 px-4 space-y-1">
          <a className="nav-active flex items-center gap-3 px-4 py-3 text-sm" href="#">
            <Activity className="h-5 w-5" />
            Dashboard
          </a>
          <a className="flex items-center gap-3 px-4 py-3 text-white/50 hover:text-white/80 transition-all text-sm hover:bg-white/5" href="/agents">
            <Users className="h-5 w-5" />
            Agents
          </a>
          <a className="flex items-center gap-3 px-4 py-3 text-white/50 hover:text-white/80 transition-all text-sm hover:bg-white/5" href="/calls">
            <Phone className="h-5 w-5" />
            Calls
          </a>
          <a className="flex items-center gap-3 px-4 py-3 text-white/50 hover:text-white/80 transition-all text-sm hover:bg-white/5" href="/transcripts">
            <FileText className="h-5 w-5" />
            Transcripts
          </a>
          <a className="flex items-center gap-3 px-4 py-3 text-white/50 hover:text-white/80 transition-all text-sm hover:bg-white/5" href="/costs">
            <DollarSign className="h-5 w-5" />
            Costs
          </a>
          <a className="flex items-center gap-3 px-4 py-3 text-white/50 hover:text-white/80 transition-all text-sm hover:bg-white/5" href="/settings">
            <Settings className="h-5 w-5" />
            Settings
          </a>
        </nav>

        {/* Footer Links */}
        <div className="p-6 border-t border-white/5 space-y-2">
          <a className="flex items-center gap-3 px-4 py-2 text-white/40 hover:text-white/80 transition-all text-xs" href="#">
            <FileText className="h-4 w-4" />
            Docs
          </a>
          <a className="flex items-center gap-3 px-4 py-2 text-white/40 hover:text-white/80 transition-all text-xs" href="#">
            <CircleHelp className="h-4 w-4" />
            Support
          </a>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-[280px] min-h-screen flex flex-col">
        {/* Top Navigation */}
        <header className="flex justify-between items-center px-8 h-16 w-full sticky top-0 z-50 bg-surface-lowest/40 backdrop-blur-md border-b border-white/5">
          <div className="flex items-center gap-6">
            <span className="text-xs uppercase tracking-widest font-semibold text-white/40">
              Command Center
            </span>
            <nav className="flex gap-4">
              <a className="text-xs uppercase tracking-widest font-semibold text-cyan-glow border-b border-cyan-glow py-5" href="#">
                Network
              </a>
              <a className="text-xs uppercase tracking-widest font-semibold text-white/40 hover:text-cyan-glow transition-colors py-5" href="#">
                Analytics
              </a>
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <input
              className="bg-white/5 border-none rounded-full px-4 py-1.5 text-xs text-white placeholder-white/20 focus:ring-1 focus:ring-cyan-glow w-48 transition-all"
              placeholder="Search systems..."
              type="text"
            />
            <button className="px-4 py-1.5 rounded-full bg-white/5 text-cyan-glow text-xs font-bold border border-cyan-glow/20 hover:bg-cyan-glow/10 transition-all">
              Deploy
            </button>
            <Settings className="h-5 w-5 text-white/40 cursor-pointer hover:text-white transition-all" />
            <Users className="h-5 w-5 text-white/40 cursor-pointer hover:text-white transition-all" />
          </div>
        </header>

        {/* Page Content */}
        <div className="p-8 space-y-6 max-w-7xl mx-auto w-full">
          {/* Hero Section / Voice Visualizer */}
          <section className="glass rounded-3xl p-10 overflow-hidden relative group">
            <div className="absolute top-0 right-0 p-8">
              <div className="flex items-center gap-3">
                <span className="flex h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
                <span className="text-[10px] font-mono uppercase text-white/40 tracking-widest">
                  System Live: 99.98% Uptime
                </span>
              </div>
            </div>

            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-12">
              <div className="space-y-6 max-w-xl">
                <h2 className="text-5xl font-bold text-white leading-tight">
                  Advanced Voice <br />
                  <span className="text-cyan-glow text-glow">Orchestration</span>
                </h2>
                <p className="text-on-surface-variant leading-relaxed">
                  Experience human-like interaction with sub-200ms latency. Your fleet of AI agents is ready to deploy across global nodes.
                </p>
                <div className="flex gap-4">
                  <button className="bg-cyan-glow text-on-primary px-8 py-4 rounded-xl font-bold flex items-center gap-2 hover:scale-[1.02] transition-all shadow-cyan-glow btn-glow">
                    <Phone className="h-5 w-5" />
                    Start Test Call
                  </button>
                  <button className="bg-white/5 border border-white/10 px-8 py-4 rounded-xl font-bold hover:bg-white/10 transition-all">
                    Explore Models
                  </button>
                </div>
              </div>

              {/* Voice Wave Visualizer */}
              <div className="glass rounded-2xl p-8 border-cyan-glow/20 flex flex-col items-center gap-8 relative overflow-hidden">
                <div className="absolute inset-0 bg-cyan-glow/5 blur-3xl rounded-full"></div>
                <div className="voice-wave relative z-10">
                  <div className="voice-bar h-8 animate-bounce" style={{ animationDuration: '1s' }}></div>
                  <div className="voice-bar h-12 animate-bounce" style={{ animationDuration: '1.2s' }}></div>
                  <div className="voice-bar h-16 animate-bounce" style={{ animationDuration: '0.8s' }}></div>
                  <div className="voice-bar h-24 animate-bounce" style={{ animationDuration: '1.1s' }}></div>
                  <div className="voice-bar h-12 animate-bounce" style={{ animationDuration: '0.9s' }}></div>
                  <div className="voice-bar h-20 animate-bounce" style={{ animationDuration: '1.3s' }}></div>
                  <div className="voice-bar h-10 animate-bounce" style={{ animationDuration: '0.7s' }}></div>
                  <div className="voice-bar h-14 animate-bounce" style={{ animationDuration: '1s' }}></div>
                </div>
                <div className="text-center space-y-2 relative z-10">
                  <div className="text-[10px] font-mono uppercase text-cyan-glow tracking-widest">Active Processing</div>
                  <div className="text-xl font-bold text-white">Agent Alpha-7</div>
                </div>
              </div>
            </div>
          </section>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Total Calls Card */}
            <div className="glass p-6 rounded-2xl space-y-4 card-hover border border-white/5">
              <div className="flex justify-between items-start">
                <div className="p-2 rounded-lg bg-white/5 text-cyan-glow">
                  <Phone className="h-5 w-5" />
                </div>
                <span className="text-xs font-mono text-green-400">+12.4%</span>
              </div>
              <div>
                <div className="text-white/40 text-xs uppercase tracking-wider">Total Calls</div>
                <div className="text-3xl font-mono text-white text-glow mt-1">
                  {totalCalls.toLocaleString()}
                </div>
              </div>
              <div className="h-10 flex items-end gap-1">
                <div className="w-full h-4 bg-cyan-glow/20 rounded-sm"></div>
                <div className="w-full h-8 bg-cyan-glow/40 rounded-sm"></div>
                <div className="w-full h-6 bg-cyan-glow/20 rounded-sm"></div>
                <div className="w-full h-10 bg-cyan-glow rounded-sm shadow-[0_0_8px_rgba(0,217,255,0.4)]"></div>
              </div>
            </div>

            {/* Active Agents Card */}
            <div className="glass p-6 rounded-2xl space-y-4 card-hover border border-white/5">
              <div className="flex justify-between items-start">
                <div className="p-2 rounded-lg bg-white/5 text-cyan-glow">
                  <Users className="h-5 w-5" />
                </div>
                <span className="text-xs font-mono text-white/40">Active</span>
              </div>
              <div>
                <div className="text-white/40 text-xs uppercase tracking-wider">Active Agents</div>
                <div className="text-3xl font-mono text-white text-glow mt-1">{activeAgents}</div>
              </div>
              <div className="flex -space-x-2 mt-4">
                <div className="w-8 h-8 rounded-full bg-cyan-glow/20 border-2 border-surface-lowest flex items-center justify-center text-xs text-cyan-glow">
                  A
                </div>
                <div className="w-8 h-8 rounded-full bg-purple-500/20 border-2 border-surface-lowest flex items-center justify-center text-xs text-purple-400">
                  B
                </div>
                <div className="w-8 h-8 rounded-full bg-green-500/20 border-2 border-surface-lowest flex items-center justify-center text-xs text-green-400">
                  C
                </div>
                <div className="w-8 h-8 rounded-full bg-white/5 border-2 border-surface-lowest flex items-center justify-center text-[10px] text-white/40">
                  +{Math.max(0, (agents?.length || 0) - 3)}
                </div>
              </div>
            </div>

            {/* Monthly Cost Card */}
            <div className="glass p-6 rounded-2xl space-y-4 card-hover border border-white/5">
              <div className="flex justify-between items-start">
                <div className="p-2 rounded-lg bg-white/5 text-cyan-glow">
                  <DollarSign className="h-5 w-5" />
                </div>
                <span className="text-xs font-mono text-red-400">-4.2%</span>
              </div>
              <div>
                <div className="text-white/40 text-xs uppercase tracking-wider">Monthly Cost</div>
                <div className="text-3xl font-mono text-white text-glow mt-1">
                  ${totalCost.toFixed(2)}
                </div>
              </div>
              <div className="text-[10px] text-white/20 mt-4">
                Next billing cycle: May 12, 2026
              </div>
            </div>

            {/* Avg Duration Card */}
            <div className="glass p-6 rounded-2xl space-y-4 card-hover border border-white/5">
              <div className="flex justify-between items-start">
                <div className="p-2 rounded-lg bg-white/5 text-cyan-glow">
                  <Activity className="h-5 w-5" />
                </div>
                <span className="text-xs font-mono text-green-400">Optimal</span>
              </div>
              <div>
                <div className="text-white/40 text-xs uppercase tracking-wider">Avg Duration</div>
                <div className="text-3xl font-mono text-white text-glow mt-1">
                  {costs?.avg_duration ? `${Math.round(costs.avg_duration / 60)}m ${Math.round(costs.avg_duration % 60)}s` : '0m 0s'}
                </div>
              </div>
              <div className="w-full bg-white/5 h-1.5 rounded-full mt-4">
                <div className="bg-cyan-glow h-full w-[65%] rounded-full shadow-[0_0_8px_rgba(0,217,255,0.4)]"></div>
              </div>
            </div>
          </div>

          {/* Main Dashboard Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Calls Table */}
            <div className="lg:col-span-2 glass rounded-2xl overflow-hidden">
              <div className="px-8 py-6 flex justify-between items-center border-b border-white/5">
                <h3 className="text-xl font-semibold text-white">Recent Calls</h3>
                <button className="text-xs font-bold text-cyan-glow hover:underline">
                  View All Records
                </button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-white/5 text-[10px] uppercase tracking-widest text-white/40">
                    <tr>
                      <th className="px-8 py-4 font-semibold">Caller</th>
                      <th className="px-8 py-4 font-semibold">Agent Used</th>
                      <th className="px-8 py-4 font-semibold">Duration</th>
                      <th className="px-8 py-4 font-semibold">Status</th>
                      <th className="px-8 py-4 font-semibold">Action</th>
                    </tr>
                  </thead>
                  <tbody className="text-sm">
                    {recentCalls.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-8 py-12 text-center text-white/40">
                          No calls yet. Start a test call to see activity here.
                        </td>
                      </tr>
                    ) : (
                      recentCalls.map((call) => (
                        <tr key={call.id} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                          <td className="px-8 py-5">
                            <div className="font-bold text-white">{call.from_number}</div>
                            <div className="text-xs text-white/40">to {call.to_number}</div>
                          </td>
                          <td className="px-8 py-5">
                            <div className="flex items-center gap-2">
                              <div className="w-6 h-6 rounded-md bg-cyan-glow/10 flex items-center justify-center text-cyan-glow">
                                <Users className="h-3 w-3" />
                              </div>
                              <span className="text-white/80">
                                {agents?.find(a => a.id === call.agent_id)?.name || 'Agent'}
                              </span>
                            </div>
                          </td>
                          <td className="px-8 py-5 font-mono text-white/60">
                            {Math.floor(call.duration / 60)}:{String(call.duration % 60).padStart(2, '0')}
                          </td>
                          <td className="px-8 py-5">
                            <StatusBadge status={call.status} />
                          </td>
                          <td className="px-8 py-5">
                            <button className="text-white/20 hover:text-cyan-glow transition-colors">
                              <Phone className="h-5 w-5" />
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Secondary Widgets */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <div className="glass p-8 rounded-2xl space-y-6">
                <h4 className="text-white font-bold text-sm tracking-widest uppercase">
                  System Maintenance
                </h4>
                <div className="space-y-4">
                  <button className="w-full flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:border-cyan-glow/50 hover:bg-cyan-glow/5 transition-all group">
                    <div className="flex items-center gap-3">
                      <Activity className="h-5 w-5 text-cyan-glow" />
                      <span className="text-sm font-semibold text-white">Deploy Updates</span>
                    </div>
                    <span className="text-white/20 group-hover:text-white transition-colors">
                      →
                    </span>
                  </button>
                  <button className="w-full flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/10 hover:border-cyan-glow/50 hover:bg-cyan-glow/5 transition-all group">
                    <div className="flex items-center gap-3">
                      <DollarSign className="h-5 w-5 text-cyan-glow" />
                      <span className="text-sm font-semibold text-white">Full System Audit</span>
                    </div>
                    <span className="text-white/20 group-hover:text-white transition-colors">
                      →
                    </span>
                  </button>
                </div>
              </div>

              {/* Global Node Health */}
              <div className="glass p-8 rounded-2xl space-y-6 relative overflow-hidden">
                <div className="relative z-10 space-y-4">
                  <h4 className="text-white font-bold text-sm tracking-widest uppercase">
                    Global Node Health
                  </h4>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-white/60">North America (AWS)</span>
                      <span className="text-[10px] text-green-400 font-bold">STABLE</span>
                    </div>
                    <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                      <div className="bg-green-400 h-full w-[98%] shadow-[0_0_5px_rgba(74,222,128,0.5)]"></div>
                    </div>

                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs text-white/60">Europe (GCP)</span>
                      <span className="text-[10px] text-green-400 font-bold">STABLE</span>
                    </div>
                    <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                      <div className="bg-green-400 h-full w-[94%] shadow-[0_0_5px_rgba(74,222,128,0.5)]"></div>
                    </div>

                    <div className="flex justify-between items-center pt-2">
                      <span className="text-xs text-white/60">Asia Pacific (Azure)</span>
                      <span className="text-[10px] text-cyan-glow font-bold">SYNCING</span>
                    </div>
                    <div className="w-full bg-white/5 h-1 rounded-full overflow-hidden">
                      <div className="bg-cyan-glow h-full w-[45%] shadow-[0_0_5px_rgba(0,217,255,0.5)] animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Floating Action Button */}
      <button className="fixed bottom-8 right-8 w-14 h-14 bg-cyan-glow text-on-primary rounded-full flex items-center justify-center shadow-cyan-glow-lg hover:scale-110 transition-transform z-100">
        <Phone className="h-6 w-6" />
      </button>
    </div>
  );
}

// Status Badge Component
function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    completed: 'bg-green-500/10 text-green-400',
    ringing: 'bg-yellow-500/10 text-yellow-400',
    in_progress: 'bg-cyan-glow/10 text-cyan-glow',
    failed: 'bg-red-500/10 text-red-400',
    no_answer: 'bg-gray-500/10 text-gray-400',
    busy: 'bg-orange-500/10 text-orange-400',
  };

  return (
    <span className={`px-2 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider ${styles[status] || styles.failed}`}>
      {status.replace('_', ' ')}
    </span>
  );
}
