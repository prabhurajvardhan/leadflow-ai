import { useState } from 'react'
import { Plus, Mail, Users, Play, Pause, BarChart3, Send } from 'lucide-react'

interface Campaign {
  id: number
  name: string
  status: string
  total_leads: number
  sent_count: number
  opened_count: number
  replied_count: number
  created_at: string
}

const campaigns: Campaign[] = []

const STATUS_STYLES: Record<string, { bg: string; text: string }> = {
  draft: { bg: 'bg-gray-100', text: 'text-gray-700' },
  scheduled: { bg: 'bg-blue-100', text: 'text-blue-700' },
  running: { bg: 'bg-green-100', text: 'text-green-700' },
  paused: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
  completed: { bg: 'bg-purple-100', text: 'text-purple-700' },
  failed: { bg: 'bg-red-100', text: 'text-red-700' },
}

export default function Campaigns() {
  const [showCreateModal, setShowCreateModal] = useState(false)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="mt-1 text-sm text-gray-500">Manage your email outreach campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="mt-4 flex items-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 md:mt-0"
        >
          <Plus className="mr-2 h-4 w-4" />
          New Campaign
        </button>
      </div>

      {/* Campaigns Grid */}
      {campaigns.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="rounded-xl bg-white p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                  <span className={`mt-2 inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[campaign.status]?.bg} ${STATUS_STYLES[campaign.status]?.text}`}>
                    {campaign.status}
                  </span>
                </div>
                <div className="flex gap-2">
                  {campaign.status === 'draft' && (
                    <button className="rounded p-1 text-green-600 hover:bg-green-50">
                      <Play className="h-5 w-5" />
                    </button>
                  )}
                  {campaign.status === 'running' && (
                    <button className="rounded p-1 text-yellow-600 hover:bg-yellow-50">
                      <Pause className="h-5 w-5" />
                    </button>
                  )}
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-gray-500">Sent</p>
                  <p className="mt-1 text-lg font-semibold text-gray-900">
                    {campaign.sent_count} <span className="text-sm font-normal text-gray-400">/ {campaign.total_leads}</span>
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Open Rate</p>
                  <p className="mt-1 text-lg font-semibold text-gray-900">
                    {campaign.sent_count > 0 ? ((campaign.opened_count / campaign.sent_count) * 100).toFixed(1) : 0}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Reply Rate</p>
                  <p className="mt-1 text-lg font-semibold text-gray-900">
                    {campaign.sent_count > 0 ? ((campaign.replied_count / campaign.sent_count) * 100).toFixed(1) : 0}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Created</p>
                  <p className="mt-1 text-sm text-gray-600">
                    {new Date(campaign.created_at).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div className="mt-4 flex gap-2">
                <button className="flex flex-1 items-center justify-center rounded-lg border border-gray-300 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                  <Mail className="mr-2 h-4 w-4" />
                  View Emails
                </button>
                <button className="flex flex-1 items-center justify-center rounded-lg border border-gray-300 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
                  <BarChart3 className="mr-2 h-4 w-4" />
                  Analytics
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-xl bg-white py-16 text-center shadow-sm">
          <div className="mx-auto h-16 w-16 rounded-full bg-gray-100 p-4">
            <Send className="h-8 w-8 text-gray-400" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">No campaigns yet</h3>
          <p className="mt-2 text-sm text-gray-500">
            Create your first email campaign to start reaching out to leads
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="mt-6 inline-flex items-center rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            <Plus className="mr-2 h-4 w-4" />
            Create Campaign
          </button>
        </div>
      )}

      {/* Quick Stats */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-blue-100">Total Sent</p>
              <p className="mt-2 text-3xl font-bold">0</p>
            </div>
            <div className="rounded-full bg-white/20 p-3">
              <Send className="h-6 w-6" />
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-green-500 to-green-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-green-100">Avg Open Rate</p>
              <p className="mt-2 text-3xl font-bold">0%</p>
            </div>
            <div className="rounded-full bg-white/20 p-3">
              <Mail className="h-6 w-6" />
            </div>
          </div>
        </div>

        <div className="rounded-xl bg-gradient-to-br from-purple-500 to-purple-600 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-purple-100">Total Replies</p>
              <p className="mt-2 text-3xl font-bold">0</p>
            </div>
            <div className="rounded-full bg-white/20 p-3">
              <Users className="h-6 w-6" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
