import { useState } from 'react'
import { Plus, Mail, Users, Play, Pause, BarChart3, Send, TrendingUp, Eye, MessageCircle } from 'lucide-react'

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

export default function Campaigns() {
  const [showCreateModal, setShowCreateModal] = useState(false)

  const stats = [
    { 
      label: 'Total Sent', 
      value: campaigns.reduce((acc, c) => acc + c.sent_count, 0),
      icon: Send,
      gradient: 'from-blue-600/20 to-blue-500/10',
      iconBg: 'bg-blue-500/20',
      iconColor: 'text-blue-400'
    },
    { 
      label: 'Open Rate', 
      value: '0%',
      icon: Eye,
      gradient: 'from-purple-600/20 to-purple-500/10',
      iconBg: 'bg-purple-500/20',
      iconColor: 'text-purple-400'
    },
    { 
      label: 'Reply Rate', 
      value: '0%',
      icon: MessageCircle,
      gradient: 'from-green-600/20 to-green-500/10',
      iconBg: 'bg-green-500/20',
      iconColor: 'text-green-400'
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Campaigns</h1>
          <p className="text-gray-400 mt-1">Manage your email outreach campaigns</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 font-medium hover:opacity-90 transition-opacity"
        >
          <Plus className="w-5 h-5" />
          New Campaign
        </button>
      </div>

      {/* Stats */}
      <div className="grid gap-6 md:grid-cols-3">
        {stats.map((stat, i) => (
          <div 
            key={i}
            className={`relative overflow-hidden rounded-2xl bg-gradient-to-br ${stat.gradient} border border-white/10 p-6`}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`w-12 h-12 rounded-xl ${stat.iconBg} flex items-center justify-center`}>
                <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
              </div>
            </div>
            <div className="text-3xl font-bold text-white mb-1">{stat.value}</div>
            <div className="text-sm text-gray-400">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Campaigns */}
      {campaigns.length > 0 ? (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {campaigns.map((campaign) => (
            <div
              key={campaign.id}
              className="group rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 hover:border-purple-500/50 transition-all p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="font-semibold text-lg">{campaign.name}</h3>
                  <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-medium ${
                    campaign.status === 'running' ? 'bg-green-500/20 text-green-400' :
                    campaign.status === 'draft' ? 'bg-gray-500/20 text-gray-400' :
                    campaign.status === 'completed' ? 'bg-blue-500/20 text-blue-400' :
                    'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {campaign.status}
                  </span>
                </div>
                <div className="flex gap-2">
                  {campaign.status === 'draft' && (
                    <button className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors">
                      <Play className="w-4 h-4" />
                    </button>
                  )}
                  {campaign.status === 'running' && (
                    <button className="p-2 rounded-lg bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 transition-colors">
                      <Pause className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-500">Sent</p>
                  <p className="text-lg font-semibold text-white">
                    {campaign.sent_count} <span className="text-sm font-normal text-gray-500">/ {campaign.total_leads}</span>
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Open Rate</p>
                  <p className="text-lg font-semibold text-white">
                    {campaign.sent_count > 0 ? ((campaign.opened_count / campaign.sent_count) * 100).toFixed(1) : 0}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Reply Rate</p>
                  <p className="text-lg font-semibold text-white">
                    {campaign.sent_count > 0 ? ((campaign.replied_count / campaign.sent_count) * 100).toFixed(1) : 0}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Created</p>
                  <p className="text-sm text-gray-400">{new Date(campaign.created_at).toLocaleDateString()}</p>
                </div>
              </div>

              <div className="flex gap-2">
                <button className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:border-purple-500/50 transition-all text-sm">
                  <Mail className="w-4 h-4" />
                  Emails
                </button>
                <button className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg border border-white/10 text-gray-400 hover:text-white hover:border-purple-500/50 transition-all text-sm">
                  <BarChart3 className="w-4 h-4" />
                  Analytics
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="rounded-2xl bg-gradient-to-br from-white/5 to-transparent border border-white/10 p-16 text-center">
          <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 flex items-center justify-center mb-6">
            <Send className="w-10 h-10 text-purple-400" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No campaigns yet</h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Create your first email campaign to start reaching out to leads and growing your business.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 font-medium hover:opacity-90 transition-opacity"
          >
            <Plus className="w-5 h-5" />
            Create Campaign
          </button>
        </div>
      )}
    </div>
  )
}
