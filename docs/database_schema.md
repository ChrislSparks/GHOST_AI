# Database Schema

Database: SQLite (file: `ghost.db`), managed with SQLAlchemy.
Models are defined in `backend/db/models.py`.
All `created_at` values are filled in automatically by the models and are stored in UTC.

## conversations
| Column     | Type     | Notes                  |
|------------|----------|------------------------|
| id         | integer  | Primary key            |
| title      | string   | Default "New conversation" |
| created_at | datetime |                        |

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
| Column       | Type     | Notes                    |
|--------------|----------|--------------------------|
| id           | integer  | Primary key              |
| message      | string   | Reminder text            |
| remind_at    | datetime | When it should trigger   |
| is_triggered | boolean  | Default false            |
| created_at   | datetime |                          |

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