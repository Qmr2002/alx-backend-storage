-- Use `IF NOT EXISTS` to prevent errors if the table already exists
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,         -- Define id as integer, auto incrementing, and primary key
    email VARCHAR(255) NOT NULL UNIQUE,       -- Define email as varchar(255), not null, and unique
    name VARCHAR(255),                        -- Define name as varchar(255)
    country ENUM('US', 'CO', 'TN') NOT NULL DEFAULT 'US'  -- Define country as an ENUM with specific values, not null, and defaulting to 'US'
);
