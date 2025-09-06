DROP TABLE IF EXISTS notices;

CREATE TABLE notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT NOT NULL, -- e.g., 'announcement', 'event', 'urgent' (though is_urgent also exists)
    is_urgent BOOLEAN NOT NULL DEFAULT 0, -- 1 for urgent, 0 for regular
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL, -- Optional expiry date
    event_date DATE NULL,
    event_time TIME NULL,
    event_location TEXT NULL,
    is_active BOOLEAN NOT NULL DEFAULT 1 -- 1 for active, 0 for inactive/draft (admin can toggle)
);