import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import api from '../api/client'
import { Search, Filter, MoreVertical, Star, Mail, Phone, Globe, ChevronLeft, ChevronRight } from 'lucide-react'

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
  website?: { url?: string; technologies?: string[] }
  ai_report?: { summary?: string; industry?: string }
}

interface LeadsResponse {
  leads: Lead[]
  total: number
  skip: number
  limit: number
}

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  new: { bg: 'bg-blue-100', text: 'text-blue-700' },
  enriched: { bg: 'bg-purple-100', text: 'text-purple-700' },
  analyzed: { bg: 'bg-green-100', text: 'text-green-700' },
  qualified: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
  rejected: { bg: 'bg-red-100', text: 'text-red-700' },
  outreach_sent: { bg: 'bg-pink-100', text: 'text-pink-700' },
  reply_received: { bg: 'bg-indigo-100', text: 'text-indigo-700' },
  converted: { bg: 'bg-teal-100', text: 'text-teal-700' },
}

const TIER_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  A: { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
  B: { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  C: { bg: 'bg-yellow-50', text: 'text-yellow-700', border: 'border-yellow-200' },
  D: { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200' },
}

export default function Leads() {
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string | null>(null)
  const [tierFilter, setTierFilter] = useState<string | null>(null)
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Leads</h1>
          <p className="mt-1 text-sm text-gray-500">
            {data?.total || 0} total leads in your workspace
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4 rounded-xl bg-white p-4 shadow-sm md:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search leads..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(0); }}
            className="w-full rounded-lg border border-gray-300 py-2 pl-10 pr-4 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div className="flex gap-2">
          <select
            value={statusFilter || ''}
            onChange={(e) => { setStatusFilter(e.target.value || null); setPage(0); }}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
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
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Tiers</option>
            <option value="A">Tier A</option>
            <option value="B">Tier B</option>
            <option value="C">Tier C</option>
            <option value="D">Tier D</option>
          </select>
        </div>
      </div>

      {/* Leads Table */}
      <div className="rounded-xl bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Company
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Contact
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">
                  Industry
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-gray-500">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {isLoading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 6 }).map((_, j) => (
                      <td key={j} className="px-6 py-4">
                        <div className="h-4 w-24 animate-pulse rounded bg-gray-200" />
                      </td>
                    ))}
                  </tr>
                ))
              ) : data?.leads.length ? (
                data.leads.map((lead) => (
                  <tr key={lead.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{lead.company_name || 'Unknown'}</p>
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Globe className="h-3 w-3" />
                          {lead.domain || 'No domain'}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      {lead.contacts?.[0] ? (
                        <div>
                          <p className="text-sm text-gray-900">
                            {lead.contacts[0].first_name} {lead.contacts[0].last_name}
                          </p>
                          <p className="text-xs text-gray-500">{lead.contacts[0].title || 'No title'}</p>
                          <div className="mt-1 flex gap-2">
                            {lead.contacts[0].email && (
                              <a href={`mailto:${lead.contacts[0].email}`} className="text-gray-400 hover:text-primary-600">
                                <Mail className="h-4 w-4" />
                              </a>
                            )}
                            {lead.contacts[0].phone && (
                              <a href={`tel:${lead.contacts[0].phone}`} className="text-gray-400 hover:text-primary-600">
                                <Phone className="h-4 w-4" />
                              </a>
                            )}
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">No contact</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {lead.ai_score !== null && lead.ai_score !== undefined ? (
                        <div className="flex items-center gap-2">
                          <div className="flex items-center">
                            <Star className={`h-4 w-4 ${lead.ai_score >= 80 ? 'text-yellow-500' : 'text-gray-300'}`} />
                            <span className="ml-1 font-medium">{lead.ai_score.toFixed(0)}</span>
                          </div>
                          {lead.quality_tier && (
                            <span className={`rounded border px-2 py-0.5 text-xs font-medium ${TIER_STYLES[lead.quality_tier]?.bg || 'bg-gray-50'} ${TIER_STYLES[lead.quality_tier]?.text || 'text-gray-700'} ${TIER_STYLES[lead.quality_tier]?.border || 'border-gray-200'}`}>
                              Tier {lead.quality_tier}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[lead.status]?.bg || 'bg-gray-100'} ${STATUS_STYLES[lead.status]?.text || 'text-gray-700'}`}>
                        {lead.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-sm text-gray-600">
                        {lead.ai_report?.industry || '-'}
                      </p>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
                        <MoreVertical className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                    No leads found. Start a pipeline to collect leads.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between border-t border-gray-200 px-6 py-3">
            <p className="text-sm text-gray-700">
              Showing {page * limit + 1} to {Math.min((page + 1) * limit, data?.total || 0)} of {data?.total || 0} results
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(p => Math.max(0, p - 1))}
                disabled={page === 0}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="rounded-lg bg-primary-50 px-3 py-1.5 text-sm font-medium text-primary-700">
                {page + 1} / {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages - 1, p + 1))}
                disabled={page >= totalPages - 1}
                className="rounded-lg border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
