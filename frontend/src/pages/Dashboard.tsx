import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../api/client'
import { 
  Users, TrendingUp, Mail, Activity, 
  Plus, Search, ArrowRight, Zap, BarChart3 
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

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

const STATUS_COLORS: Record<string, string> = {
  new: '#3B82F6',
  enriched: '#8B5CF6',
  analyzed: '#10B981',
  qualified: '#F59E0B',
  outreach_sent: '#EC4899',
  reply_received: '#6366F1',
  converted: '#14B8A6',
}

const TIER_COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444']

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

  const statusData = stats?.by_status 
    ? Object.entries(stats.by_status).map(([name, value]) => ({ name, value }))
    : []

  const tierData = stats?.by_quality_tier
    ? Object.entries(stats.by_quality_tier).map(([name, value]) => ({ name, value }))
    : []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Overview of your lead generation pipeline</p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="rounded-xl bg-gradient-to-r from-primary-600 to-primary-700 p-6 text-white shadow-lg">
        <div className="md:flex md:items-center md:justify-between">
          <div className="mb-4 md:mb-0">
            <h2 className="text-lg font-semibold">Start Lead Generation</h2>
            <p className="text-primary-100">Find and analyze potential leads</p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              type="text"
              placeholder="What to search (e.g., SaaS companies)"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="rounded-lg border-0 bg-white/20 px-4 py-2.5 text-white placeholder-primary-200 focus:bg-white/30 focus:outline-none focus:ring-2 focus:ring-white/50 w-64"
            />
            <input
              type="text"
              placeholder="Location (optional)"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="rounded-lg border-0 bg-white/20 px-4 py-2.5 text-white placeholder-primary-200 focus:bg-white/30 focus:outline-none focus:ring-2 focus:ring-white/50 w-48"
            />
            <button
              onClick={handleStartPipeline}
              disabled={!query || startingJob}
              className="flex items-center justify-center rounded-lg bg-white px-6 py-2.5 text-primary-700 hover:bg-primary-50 disabled:opacity-50"
            >
              {startingJob ? (
                <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary-700 border-t-transparent" />
              ) : (
                <>
                  <Zap className="mr-2 h-5 w-5" />
                  Start
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Total Leads</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {statsLoading ? '-' : stats?.total || 0}
              </p>
            </div>
            <div className="rounded-full bg-primary-100 p-3">
              <Users className="h-6 w-6 text-primary-600" />
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Avg. Lead Score</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {statsLoading ? '-' : (stats?.average_score || 0).toFixed(1)}
              </p>
            </div>
            <div className="rounded-full bg-green-100 p-3">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Emails Sent</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {statsLoading ? '-' : (stats?.by_status?.outreach_sent || 0)}
              </p>
            </div>
            <div className="rounded-full bg-purple-100 p-3">
              <Mail className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Replies</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {statsLoading ? '-' : (stats?.by_status?.reply_received || 0)}
              </p>
            </div>
            <div className="rounded-full bg-blue-100 p-3">
              <Activity className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Status Distribution */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Lead Status Distribution</h3>
            <BarChart3 className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={statusData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} stroke="#6B7280" />
                <YAxis tick={{ fontSize: 12 }} stroke="#6B7280" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || '#3B82F6'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quality Tiers */}
        <div className="rounded-xl bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Quality Tier Distribution</h3>
            <TrendingUp className="h-5 w-5 text-gray-400" />
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={tierData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {tierData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={TIER_COLORS[index % TIER_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff',
                    border: '1px solid #E5E7EB',
                    borderRadius: '8px'
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 flex justify-center gap-6">
            {tierData.map((item, index) => (
              <div key={item.name} className="flex items-center gap-2">
                <div 
                  className="h-3 w-3 rounded-full" 
                  style={{ backgroundColor: TIER_COLORS[index % TIER_COLORS.length] }}
                />
                <span className="text-sm text-gray-600">
                  {item.name}: {item.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Jobs */}
      <div className="rounded-xl bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Recent Jobs</h3>
          <button className="flex items-center text-sm text-primary-600 hover:text-primary-700">
            View All <ArrowRight className="ml-1 h-4 w-4" />
          </button>
        </div>
        <div className="space-y-4">
          {jobs?.length ? (
            jobs.map((job) => (
              <div key={job.id} className="flex items-center justify-between border-b border-gray-100 pb-4 last:border-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <div className={`h-2 w-2 rounded-full ${
                    job.status === 'completed' ? 'bg-green-500' :
                    job.status === 'running' ? 'bg-blue-500 animate-pulse' :
                    job.status === 'failed' ? 'bg-red-500' : 'bg-gray-400'
                  }`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{job.job_type}</p>
                    <p className="text-xs text-gray-500">{new Date(job.created_at).toLocaleString()}</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  {job.status === 'running' && (
                    <div className="w-24">
                      <div className="h-2 w-full overflow-hidden rounded-full bg-gray-200">
                        <div 
                          className="h-full bg-primary-500 transition-all" 
                          style={{ width: `${job.progress}%` }}
                        />
                      </div>
                      <p className="mt-1 text-xs text-gray-500">{job.progress}%</p>
                    </div>
                  )}
                  <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                    job.status === 'completed' ? 'bg-green-100 text-green-700' :
                    job.status === 'running' ? 'bg-blue-100 text-blue-700' :
                    job.status === 'failed' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {job.status}
                  </span>
                </div>
              </div>
            ))
          ) : (
            <div className="py-8 text-center text-gray-500">
              No jobs yet. Start your first pipeline above!
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
