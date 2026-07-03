import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../api/client'
import { Search, Filter, MoreVertical, Star, Mail, Phone, Globe, ChevronLeft, ChevronRight, Users, X } from 'lucide-react'

interface Contact {
  id: number
  first_name?: string
  last_name?: string
  email?: string
  phone?: string
  title?: string
  is_primary: boolean
}

interface Lead {
  id: number
  company_name?: string
  domain?: string
  status: string
  ai_score?: number
  quality_tier?: string
  city?: string
  country?: string
  phone?: string
  created_at: string
  contacts?: Contact[]
}

interface LeadsResponse {
  leads: Lead[]
  total: number
  skip: number
  limit: number
}

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  new: { bg: 'bg-blue-500/20', text: 'text-blue-400' },
  enriched: { bg: 'bg-purple-500/20', text: 'text-purple-400' },
  analyzed: { bg: 'bg-green-500/20', text: 'text-green-400' },
  qualified: { bg: 'bg-yellow-500/20', text: 'text-yellow-400' },
  rejected: { bg: 'bg-red-500/20', text: 'text-red-400' },
  outreach_sent: { bg: 'bg-pink-500/20', text: 'text-pink-400' },
  reply_received: { bg: 'bg-indigo-500/20', text: 'text-indigo-400' },
  converted: { bg: 'bg-teal-500/20', text: 'text-teal-400' },
}

const TIER_STYLES: Record<string, { bg: string; text: string }> = {
  A: { bg: 'bg-green-500/20', text: 'text-green-400' },
  B: { bg: 'bg-blue-500/20', text: 'text-blue-400' },
  C: { bg: 'bg-yellow-500/20', text: 'text-yellow-400' },
  D: { bg: 'bg-red-500/20', text: 'text-red-400' },
}

export default function Leads() {
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const [tierFilter, setTierFilter] = useState<string | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const limit = 20

  const { data, isLoading } = useQuery<LeadsResponse>({
    queryKey: ['leads', page, search, statusFilter, tierFilter],
    queryFn: async () => {
      const params = new URLSearchParams({
        skip: String(page * limit),
        limit: String(limit),
      })
      if (statusFilter) params.append('status', statusFilter)
      if (tierFilter) params.append('quality_tier', tierFilter)
      
      if (search) {
        const response = await api.get(`/workspaces/1/leads/search?q=${search}`)
        return { leads: response.data.leads, total: response.data.total, skip: page * limit, limit }
      }
      
      const response = await api.get(`/workspaces/1/leads?${params}`)
      return response.data
    },
  })

  const totalPages = data ? Math.ceil(data.total / limit) : 0

  const clearFilters = () => {
    setStatusFilter(null)
    setTierFilter(null)
    setSearch('')
    setPage(0)
  }

  const hasActiveFilters = statusFilter || tierFilter || search

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Leads</h1>
          <p className="text-gray-400 mt-1">
            {data?.total || 0} leads in your workspace
          </p>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search leads by company, domain..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            className="w-full rounded-xl border border-white/10 bg-white/5 px-4 py-3 pl-12 text-white placeholder-gray-500 focus:border-purple-500/50 focus:bg-white/10 focus:outline-none transition-all"
          />
        </div>
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={`flex items-center gap-2 px-4 py-3 rounded-xl border transition-all ${
            hasActiveFilters 
              ? 'border-purple-500/50 bg-purple-500/10 text-purple-400' 
              : 'border-white/10 bg-white/5 text-gray-400 hover:text-white'
          }`}
        >
          <Filter className="w-5 h-5" />
          Filters
          {hasActiveFilters && (
            <span className="w-2 h-2 rounded-full bg-purple-500" />
          )}
        </button>
      </div>

      {/* Filter Panel */}
      {showFilters && (
        <div className="flex flex-wrap gap-4 p-4 rounded-xl bg-white/5 border border-white/10">
          <select
            value={statusFilter || ''}
            onChange={(e) => { setStatusFilter(e.target.value || null); setPage(0); }}
            className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="">All Statuses</option>
            <option value="new">New</option>
            <option value="enriched">Enriched</option>
            <option value="analyzed">Analyzed</option>
            <option value="qualified">Qualified</option>
            <option value="outreach_sent">Outreach Sent</option>
            <option value="reply_received">Reply Received</option>
          </select>
          <select
            value={tierFilter || ''}
            onChange={(e) => { setTierFilter(e.target.value || null); setPage(0); }}
            className="rounded-lg border border-white/10 bg-white/5 px-4 py-2 text-sm text-white focus:border-purple-500/50 focus:outline-none"
          >
            <option value="">All Tiers</option>
            <option value="A">Tier A</option>
            <option value="B">Tier B</option>
            <option value="C">Tier C</option>
            <option value="D">Tier D</option>
          </select>
          {hasActiveFilters && (
            <button
              onClick={clearFilters}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm text-gray-400 hover:text-white transition-colors"
            >
              <X className="w-4 h-4" />
              Clear filters
            </button>
          )}
        </div>
      )}

      {/* Leads Table */}
      <div className="rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
                  Company
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
                  Contact
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
                  Score
                </th>
                <th className="px-6 py-4 text-left text-xs font-medium uppercase tracking-wider text-gray-400">
                  Status
                </th>
                <th className="px-6 py-4 text-right text-xs font-medium uppercase tracking-wider text-gray-400">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 5 }).map((_, j) => (
                      <td key={j} className="px-6 py-4">
                        <div className="h-4 w-24 rounded bg-white/5 animate-pulse" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : data?.leads.length ? (
                data.leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center text-purple-400 font-bold">
                          {lead.company_name?.[0]?.toUpperCase() || '?'}
                        </div>
                        <div>
                          <p className="font-medium text-white">{lead.company_name || 'Unknown'}</p>
                          <div className="flex items-center gap-1 text-sm text-gray-500">
                            <Globe className="w-3 h-3" />
                            {lead.domain || 'No domain'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {lead.contacts?.[0] ? (
                        <div>
                          <p className="text-sm text-white">
                            {lead.contacts[0].first_name} {lead.contacts[0].last_name}
                          </p>
                          <p className="text-xs text-gray-500">{lead.contacts[0].title || 'No title'}</p>
                          <div className="flex gap-2 mt-1">
                            {lead.contacts[0].email && (
                              <a href={`mailto:${lead.contacts[0].email}`} className="text-gray-500 hover:text-purple-400 transition-colors">
                                <Mail className="w-4 h-4" />
                              </a>
                            )}
                            {lead.contacts[0].phone && (
                              <a href={`tel:${lead.contacts[0].phone}`} className="text-gray-500 hover:text-purple-400 transition-colors">
                                <Phone className="w-4 h-4" />
                              </a>
                            )}
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">No contact</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {lead.ai_score !== null && lead.ai_score !== undefined ? (
                        <div className="flex items-center gap-3">
                          <div className="flex items-center gap-1">
                            <Star className={`w-4 h-4 ${lead.ai_score >= 80 ? 'text-yellow-400 fill-yellow-400' : 'text-gray-500'}`} />
                            <span className="font-medium">{lead.ai_score.toFixed(0)}</span>
                          </div>
                          {lead.quality_tier && (
                            <span className={`px-2 py-0.5 rounded text-xs font-medium ${TIER_STYLES[lead.quality_tier]?.bg} ${TIER_STYLES[lead.quality_tier]?.text}`}>
                              Tier {lead.quality_tier}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${STATUS_STYLES[lead.status]?.bg} ${STATUS_STYLES[lead.status]?.text}`}>
                        {lead.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 rounded-lg text-gray-500 hover:text-white hover:bg-white/10 transition-colors">
                        <MoreVertical className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <Users className="w-12 h-12 mx-auto mb-3 text-gray-600" />
>
                    <p className="text-gray-500">No leads found</p>
                    <p className="text-sm text-gray-600 mt-1">Start a pipeline to collect leads</p>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-white/10">
            <p className="text-sm text-gray-400">
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, data?.total || 0)} of {data?.total || 0}
            </p>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="p-2 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:border-purple-500/50 disabled:opacity-50 transition-all"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <span className="px-4 py-2 rounded-lg bg-purple-500/20 text-purple-400 text-sm font-medium">
                {page + 1} / {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="p-2 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:border-purple-500/50 disabled:opacity-50 transition-all"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
