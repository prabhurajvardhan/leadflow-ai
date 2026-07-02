# LeadFlow AI - Database Schema

## Entity Relationship Diagram

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    User     │       │  Workspace  │       │     Job     │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │──┐    │ id (PK)     │──┐    │ id (PK)     │
│ email       │  │    │ name        │  │    │ job_type    │
│ username    │  └───>│ owner_id(FK)│<─┘    │ status      │
│ password    │       │             │       │ workspace_id│
│ is_active   │       └─────────────┘       │ progress    │
└─────────────┘              │              └─────────────┘
       │                     │                     │
       │                     ▼                     │
       │              ┌─────────────┐              │
       │              │    Lead     │              │
       │              ├─────────────┤              │
       │              │ id (PK)     │              │
       │              │ company_name│              │
       │              │ domain      │              │
       │              │ ai_score    │              │
       └─────────────>│ workspace_id│<─────────────┘
                      │ status     │
                      └─────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │   Website   │    │   Contact  │    │ SocialProfile│
   ├─────────────┤    ├─────────────┤    ├─────────────┤
   │ id (PK)     │    │ id (PK)     │    │ id (PK)     │
   │ lead_id(FK) │    │ lead_id(FK) │    │ lead_id(FK) │
   │ url         │    │ email       │    │ platform    │
   │ technologies│    │ name        │    │ url         │
   └─────────────┘    └─────────────┘    └─────────────┘

                      ┌─────────────┐
                      │   AIReport  │
                      ├─────────────┤
                      │ id (PK)     │
                      │ lead_id(FK) │
                      │ summary     │
                      │ pain_points │
                      │ opportunities│
                      │ score       │
                      └─────────────┘
                             │
                             ▼
                 ┌─────────────────────┐
                 │    Campaign         │
                 ├─────────────────────┤
                 │ id (PK)             │
                 │ workspace_id (FK)   │
                 │ name                │
                 │ status              │
                 │ total_leads        │
                 │ sent_count          │
                 └─────────────────────┘
                             │
                             ▼
                 ┌─────────────────────┐
                 │    SentEmail        │
                 ├─────────────────────┤
                 │ id (PK)             │
                 │ campaign_id (FK)    │
                 │ lead_id (FK)        │
                 │ to_email            │
                 │ subject             │
                 │ status              │
                 └─────────────────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
   │ EmailReply  │    │  Followup   │    │ActivityLog │
   ├─────────────┤    ├─────────────┤    ├─────────────┤
   │ id (PK)     │    │ id (PK)     │    │ id (PK)     │
   │ sent_email  │    │ sent_email  │    │ lead_id    │
   │ body        │    │ body        │    │ activity   │
   │ intent      │    │ status      │    │ created_at │
   └─────────────┘    └─────────────┘    └─────────────┘
```

## Tables

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | |
| avatar_url | VARCHAR(500) | |
| is_active | BOOLEAN | DEFAULT TRUE |
| is_superuser | BOOLEAN | DEFAULT FALSE |
| email_verified | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT NOW() |
| last_login | TIMESTAMP | |

### workspaces
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | UNIQUE, NOT NULL |
| description | TEXT | |
| owner_id | INTEGER | FK -> users.id |
| settings | JSON | DEFAULT {} |
| created_at | TIMESTAMP | DEFAULT NOW() |

### jobs
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| job_type | VARCHAR(50) | NOT NULL |
| status | VARCHAR(20) | DEFAULT 'pending' |
| workspace_id | INTEGER | FK -> workspaces.id |
| params | JSON | DEFAULT {} |
| result | JSON | DEFAULT {} |
| error_message | TEXT | |
| progress | INTEGER | DEFAULT 0 |
| started_at | TIMESTAMP | |
| completed_at | TIMESTAMP | |
| created_at | TIMESTAMP | DEFAULT NOW() |

### leads
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| workspace_id | INTEGER | FK -> workspaces.id |
| name | VARCHAR(255) | |
| company_name | VARCHAR(255) | INDEX |
| domain | VARCHAR(255) | INDEX |
| description | TEXT | |
| address | TEXT | |
| city | VARCHAR(100) | |
| state | VARCHAR(100) | |
| country | VARCHAR(100) | |
| postal_code | VARCHAR(20) | |
| phone | VARCHAR(50) | |
| linkedin_url | VARCHAR(500) | |
| status | VARCHAR(20) | DEFAULT 'new' |
| ai_score | FLOAT | |
| quality_tier | VARCHAR(20) | |
| source | VARCHAR(50) | |
| source_data | JSON | DEFAULT {} |
| created_at | TIMESTAMP | DEFAULT NOW() |

### websites
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| lead_id | INTEGER | FK -> leads.id, UNIQUE |
| url | VARCHAR(500) | NOT NULL |
| title | VARCHAR(500) | |
| description | TEXT | |
| technologies | JSON | DEFAULT [] |
| meta_description | TEXT | |
| page_count | INTEGER | DEFAULT 0 |
| crawl_status | VARCHAR(20) | DEFAULT 'pending' |
| last_crawled | TIMESTAMP | |

### contacts
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| lead_id | INTEGER | FK -> leads.id |
| first_name | VARCHAR(100) | |
| last_name | VARCHAR(100) | |
| email | VARCHAR(255) | INDEX |
| phone | VARCHAR(50) | |
| title | VARCHAR(255) | |
| linkedin_url | VARCHAR(500) | |
| is_primary | BOOLEAN | DEFAULT FALSE |
| is_verified | BOOLEAN | DEFAULT FALSE |

### social_profiles
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| lead_id | INTEGER | FK -> leads.id |
| platform | VARCHAR(50) | NOT NULL |
| url | VARCHAR(500) | NOT NULL |
| UNIQUE(lead_id, platform) | | |

### ai_reports
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| lead_id | INTEGER | FK -> leads.id, UNIQUE |
| summary | TEXT | |
| pain_points | JSON | DEFAULT [] |
| opportunities | JSON | DEFAULT [] |
| recommendations | JSON | DEFAULT [] |
| score_breakdown | JSON | DEFAULT {} |
| quality_tier | VARCHAR(10) | |
| industry | VARCHAR(100) | |
| personalization_hints | JSON | DEFAULT {} |
| ai_provider | VARCHAR(50) | |
| ai_model | VARCHAR(100) | |
| created_at | TIMESTAMP | DEFAULT NOW() |

### campaigns
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| workspace_id | INTEGER | FK -> workspaces.id |
| name | VARCHAR(255) | NOT NULL |
| subject | VARCHAR(500) | |
| email_body | TEXT | |
| status | VARCHAR(20) | DEFAULT 'draft' |
| scheduled_at | TIMESTAMP | |
| total_leads | INTEGER | DEFAULT 0 |
| sent_count | INTEGER | DEFAULT 0 |
| opened_count | INTEGER | DEFAULT 0 |
| replied_count | INTEGER | DEFAULT 0 |
| created_at | TIMESTAMP | DEFAULT NOW() |

### sent_emails
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| campaign_id | INTEGER | FK -> campaigns.id |
| lead_id | INTEGER | FK -> leads.id |
| contact_id | INTEGER | FK -> contacts.id |
| to_email | VARCHAR(255) | NOT NULL |
| subject | VARCHAR(500) | |
| body | TEXT | |
| status | VARCHAR(20) | DEFAULT 'pending' |
| tracking_id | VARCHAR(100) | UNIQUE |
| message_id | VARCHAR(500) | |
| sent_at | TIMESTAMP | |
| delivered_at | TIMESTAMP | |
| opened_at | TIMESTAMP | |
| replied_at | TIMESTAMP | |
| created_at | TIMESTAMP | DEFAULT NOW() |

### email_replies
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| sent_email_id | INTEGER | FK -> sent_emails.id |
| from_email | VARCHAR(255) | NOT NULL |
| subject | VARCHAR(500) | |
| body | TEXT | |
| intent | VARCHAR(50) | |
| sentiment | VARCHAR(20) | |
| summary | TEXT | |
| is_processed | BOOLEAN | DEFAULT FALSE |
| received_at | TIMESTAMP | |

### followups
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| sent_email_id | INTEGER | FK -> sent_emails.id |
| sequence_number | INTEGER | NOT NULL |
| scheduled_at | TIMESTAMP | |
| sent_at | TIMESTAMP | |
| subject | VARCHAR(500) | |
| body | TEXT | |
| status | VARCHAR(20) | DEFAULT 'pending' |

### activity_logs
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| lead_id | INTEGER | FK -> leads.id |
| workspace_id | INTEGER | FK -> workspaces.id |
| user_id | INTEGER | FK -> users.id |
| activity_type | VARCHAR(50) | NOT NULL |
| description | TEXT | |
| extra_data | JSON | DEFAULT {} |
| created_at | TIMESTAMP | DEFAULT NOW() |

### refresh_tokens
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY |
| token | VARCHAR(500) | UNIQUE, NOT NULL |
| user_id | INTEGER | FK -> users.id |
| expires_at | TIMESTAMP | NOT NULL |
| revoked | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | DEFAULT NOW() |
