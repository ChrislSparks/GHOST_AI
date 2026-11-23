# Database Schema

Database: SQLite (file: `ghost.db`), managed with SQLAlchemy.
Models are defined in `backend/db/models.py`.
All `created_at` values are filled in automatically by the models and are stored in UTC.

## conversations
| Column     | Type     | Notes                      |
|------------|----------|----------------------------|
| id         | integer  | Primary key                |
| title      | string   | Default "New conversation" |
| created_at | datetime |                            |

## messages
| Column          | Type     | Notes                                   |
|-----------------|----------|-----------------------------------------|
| id              | integer  | Primary key                             |
| conversation_id | integer  | Foreign key to conversations.id         |
| role            | string   | "user" or "assistant"                   |
| content         | text     | The message text                        |
| input_type      | string   | "voice" or "text"                       |
| created_at      | datetime |                                         |

## reminders
| Column          | Type     | Notes                        |
|-----------------|----------|------------------------------|
| id              | integer  | Primary key                  |
| message         | string   | Reminder text                |
| remind_at       | datetime | When it should trigger (UTC) |
| is_triggered    | boolean  | Scheduler has processed it   |
| is_acknowledged | boolean  | User has dismissed the alert |
| created_at      | datetime | Set when created (UTC)       |

`is_triggered` means the scheduler has processed the reminder. `is_acknowledged` means the user has dismissed it. The frontend's "what is due?" query returns reminders whose time has passed and that are not yet acknowledged, so overdue reminders keep showing until dismissed.

## user_settings
| Column          | Type    | Notes                     |
|-----------------|---------|---------------------------|
| id              | integer | Primary key               |
| display_name    | string  | Default "User"            |
| wake_phrase     | string  | Default "Hey Ghost"       |
| voice_name      | string  | Optional                  |
| speaking_rate   | float   | Default 1.0               |
| response_style  | string  | Default "balanced"        |
| response_length | string  | Default "medium"          |
| save_history    | boolean | Default true              |

## Relationships
- One conversation has many messages. Deleting a conversation deletes its messages.

## Time zones
All datetimes (`created_at`, `remind_at`) are stored in **UTC** as naive datetimes,
because SQLite does not keep time zone information. The frontend converts the user's
local time to UTC before sending it to the API, and converts back for display.
The scheduler compares `remind_at` against the current UTC time.