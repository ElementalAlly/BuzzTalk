CREATE DATABASE buzztalk;
USE buzztalk;

CREATE TABLE IF NOT EXISTS `woodruff` (
  `post_id` int AUTO_INCREMENT NOT NULL,
  `parent_id` int DEFAULT 0,
  `channel` text DEFAULT NULL,
  `username` text DEFAULT NULL,
  `post_time` datetime NOT NULL,
  `title` text DEFAULT NULL,
  `body` text DEFAULT NULL,
   PRIMARY KEY (`post_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `woodruff_channels` (
	`name` varchar(512) NOT NULL UNIQUE,
	`description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS `registry` (
	`username` varchar(512) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;