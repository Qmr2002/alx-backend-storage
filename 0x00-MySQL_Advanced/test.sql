#!/bin/bash

# Drop the users table if it exists
mysql -uroot -pyour_pass holberton <<EOF
DROP TABLE IF EXISTS users;
EOF

# Create the users table
mysql -uroot -pyour_pass holberton <<EOF
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(255),
    country ENUM('US', 'CO', 'TN') NOT NULL DEFAULT 'US'
);
EOF

# Insert data into the users table
mysql -uroot -pyour_pass holberton <<EOF
INSERT INTO users (email, name, country) VALUES ("bob@dylan.com", "Bob", "US");
EOF
