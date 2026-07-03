import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../api/client'
import { 
  Users, TrendingUp, Mail, Activity, 
  Plus, Search, ArrowRight, Zap, BarChart3, 
  Target, Globe, Sparkles, Play, Pause
} from 'lucide-react'

interface LeadStats {
  total: number
  by_status: Record<string, number>
  by_quality_tier: Record<string, number>
  average_score: number
}

interface Job {
  id: number
  job_type: string
  status: string
  progress: number
  created_at: string
}

export default function Dashboard() {
  const [query, setQuery] = useState('')
  const [location, setLocation] = useState('')
  const [startingJob, setStartingJob] = useState(false)

  const { data: stats, isLoading: statsLoading } = useQuery<LeadStats>({
    queryKey: ['lead-stats'],
    queryFn: async () => {
      const response = await api.get('/workspaces/1/leads/stats')
      return response.data
    },
  })

  const { data: jobs } = useQuery<Job[]>({
    queryKey: ['jobs'],
    queryFn: async () => {
      const response = await api.get('/workspaces/1/jobs?limit=5')
      return response.data
    },
  })

  const handleStartPipeline = async () => {
    if (!query) return
    
    setStartingJob(true)
    try {
      await api.post('/workspaces/1/jobs/', {
        job_type: 'full_pipeline',
        query,
        location,
        max_leads: 100,
      })
      setQuery('')
      setLocation('')
    } catch (error) {
      console.error('Failed to start job:', error)
    } finally {
      setStartingJob(false)
    }
  }

  const statCards = [
    { 
      label: 'Total Leads', 
      value: stats?.total || 0, 
      icon: Users, 
      gradient: 'from-purple-600/20 to-purple-500/10',
      iconBg: 'bg-purple-500/20',
      iconColor: 'text-purple-400'
    },
    { 
      label: 'Avg. Score', 
      value: stats?.average_score?.toFixed(1) || '0', 
      icon: Target, 
      gradient: 'from-green-600/20 to-green-500/10',
      iconBg: 'bg-green-500/20',
      iconColor: 'text-green-400'
    },
    { 
      label: 'Emails Sent', 
      value: stats?.by_status?.outreach_sent || 0, 
      icon: Mail, 
      gradient: 'from-blue-600/20 to-blue-500/10',
      iconBg: 'bg-blue-500/20',
      iconColor: 'text-blue-400'
    },
    { 
      label: 'Replies', 
      value: stats?.by_status?.reply_received || 0, 
      icon: Activity, 
      gradient: 'from-amber-600/20 to-amber-500/10',
      iconBg: 'bg-amber-500/20',
      iconColor: 'text-amber-400'
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-gray-400 mt-1">Overview of your lead generation pipeline</p>
        </div>
      </div>

      {/* Lead Generation CTA */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-purple-600/20 via-blue-600/20 to-purple-600/20 border border-purple-500/30 p-8">
        <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-0 w-48 h-48 bg-blue-500/10 rounded-full blur-3xl" />
        
        <div className="relative">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">Start Lead Generation</h2>
              <p className="text-gray-400 text-sm">Powered by AI • Free with OpenStreetMap</p>
            </div>
          </div>
          
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex flex-col sm:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  placeholder="What to search (e.g., SaaS companies)"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 pl-12 text-white placeholder-gray-500 focus:border-purple-500/50 focus:bg-white/10 focus:outline-none transition-all"
                />
              </div>
              <div className="relative sm:w-48">
                <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  placeholder="Location (optional)"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 pl-12 text-white placeholder-gray-500 focus:border-purple-500/50 focus:bg-white/10 focus:outline-none transition-all"
                />
              </div>
            </div>
            <button
              onClick={handleStartPipeline}
              disabled={!query || startingJob}
              className="flex items-center justify-center gap-2 px-8 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 font-semibold hover:opacity-90 disabled:opacity-50 transition-all"
            >
              {startingJob ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Start Pipeline
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, i) => (
          <div 
            key={i}
            className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${stat.gradient} border border-white/10 p-6`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl ${stat.iconBg} flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">
              {statsLoading ? (
                <div className="w-16 h-8 bg-white/10 rounded animate-pulse" />
              ) : stat.value}
            </div>
            <div className="text-sm text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Status Distribution */}
        <div className="rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">Lead Status</h3>
            <BarChart3 className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-4">
            {Object.entries(stats?.by_status || {}).slice(0, 5).map(([status, count]) => (
              <div key={status} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-purple-500" />
                  <span className="text-sm text-gray-300 capitalize">{status.replace(/_/g, ' ')}</span>
                </div>
                <span className="font-medium text-white">{count as number}</span>
              </div>
            ))}
            {(!stats?.by_status || Object.keys(stats.by_status).length === 0) && (
              <div className="text-center py-8 text-gray-500">
                No leads yet. Start a pipeline to collect leads.
              </div>
            )}
          </div>
        </div>

        {/* Quality Distribution */}
        <div className="rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-semibold">Quality Tiers</h3>
            <TrendingUp className="w-5 h-5 text-gray-500" />
          </div>
          <div className="space-y-4">
            {['A', 'B', 'C', 'D'].map((tier, i) => {
              const count = stats?.by_quality_tier?.[tier] || 0
              const colors = ['text-green-400', 'text-blue-400', 'text-yellow-400', 'text-red-400']
              const bgColors = ['bg-green-500', 'bg-blue-500', 'bg-yellow-500', 'bg-red-500']
              const percentages = stats?.total ? (count / stats.total * 100) : 0
              
              return (
                <div key={tier} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className={colors[i]}>Tier {tier}</span>
                    <span className="text-gray-400">{count} leads</span>
                  </div>
                  <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${bgColors[i]} rounded-full transition-all`}
                      style={{ width: `${percentages}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Recent Jobs</h3>
          <button className="text-sm text-purple-400 hover:text-purple-300 flex items-center gap-1">
            View All <ArrowRight className="w-4 h-4" />
          </button>
        </div>
        
        <div className="space-y-4">
          {jobs && jobs.length > 0 ? (
            jobs.map((job) => (
              <div key={job.id} className="flex items-center justify-between p-4 rounded-xl bg-white/5 border border-white/5">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
                    job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    job.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                    job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {job.status === 'completed' ? <Activity className="w-5 h-5" /> :
                     job.status === 'running' ? <Play className="w-5 h-5" /> :
                     job.status === 'failed' ? <Pause className="w-5 h-5" /> :
                     <Search className="w-5 h-5" />}
                  </div>
                  <div>
                    <p className="font-medium text-white">{job.job_type.replace(/_/g, ' ')}</p>
                    <p className="text-xs text-gray-500">{new Date(job.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  {job.status === 'running' && (
                    <div className="w-24">
                      <div className="h-2 w-full bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all" 
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1 text-right">{job.progress}%</p>
                    </div>
                  )}
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    job.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    job.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                    job.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {job.status}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              <Search className="w-12 h-12 mx-auto mb-3 text-gray-600" />
>
              No jobs yet. Start your first pipeline above!
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
