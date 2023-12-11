-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 11, 2023 at 09:35 PM
-- Server version: 10.4.27-MariaDB
-- PHP Version: 8.2.0

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `filmweb_test`
--

-- --------------------------------------------------------

--
-- Table structure for table `discord_destinations`
--

CREATE TABLE `discord_destinations` (
  `guild_id` bigint(11) NOT NULL,
  `id_filmweb` varchar(128) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `discord_guilds`
--

CREATE TABLE `discord_guilds` (
  `id` int(11) NOT NULL,
  `guild_id` bigint(11) NOT NULL,
  `channel_id` bigint(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `movies`
--

CREATE TABLE `movies` (
  `id` int(11) NOT NULL,
  `updated_unixtime` int(11) NOT NULL,
  `title` varchar(256) NOT NULL,
  `year` smallint(4) NOT NULL,
  `poster_uri` varchar(128) NOT NULL,
  `community_rate` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `series`
--

CREATE TABLE `series` (
  `id` int(11) NOT NULL,
  `updated_unixtime` int(11) NOT NULL,
  `title` varchar(256) NOT NULL,
  `year` smallint(4) NOT NULL,
  `poster_uri` varchar(128) NOT NULL,
  `community_rate` float NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tasks`
--

CREATE TABLE `tasks` (
  `id_task` int(11) NOT NULL,
  `status` varchar(16) NOT NULL,
  `type` varchar(32) NOT NULL,
  `job` varchar(1024) NOT NULL,
  `unix_timestamp` int(11) NOT NULL,
  `unix_timestamp_last_update` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id_filmweb` varchar(128) NOT NULL,
  `id_discord` bigint(11) NOT NULL,
  `discord_color` varchar(6) NOT NULL DEFAULT 'f7b900'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `watched_movies`
--

CREATE TABLE `watched_movies` (
  `id_watched` int(11) NOT NULL,
  `id_filmweb` varchar(128) NOT NULL,
  `movie_id` int(11) NOT NULL,
  `rate` tinyint(4) NOT NULL,
  `comment` varchar(161) DEFAULT NULL,
  `favourite` tinyint(1) NOT NULL,
  `unix_timestamp` bigint(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `watched_series`
--

CREATE TABLE `watched_series` (
  `id_watched` int(11) NOT NULL,
  `id_filmweb` varchar(128) NOT NULL,
  `series_id` int(11) NOT NULL,
  `rate` tinyint(4) NOT NULL,
  `comment` varchar(161) DEFAULT NULL,
  `favourite` tinyint(1) NOT NULL,
  `unix_timestamp` bigint(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `discord_destinations`
--
ALTER TABLE `discord_destinations`
  ADD KEY `id_filmweb` (`id_filmweb`),
  ADD KEY `guild_id` (`guild_id`);

--
-- Indexes for table `discord_guilds`
--
ALTER TABLE `discord_guilds`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `guild_id` (`guild_id`);

--
-- Indexes for table `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`id`),
  ADD KEY `title` (`title`);

--
-- Indexes for table `series`
--
ALTER TABLE `series`
  ADD PRIMARY KEY (`id`),
  ADD KEY `title` (`title`);

--
-- Indexes for table `tasks`
--
ALTER TABLE `tasks`
  ADD PRIMARY KEY (`id_task`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id_filmweb`),
  ADD UNIQUE KEY `id_discord` (`id_discord`);

--
-- Indexes for table `watched_movies`
--
ALTER TABLE `watched_movies`
  ADD PRIMARY KEY (`id_watched`),
  ADD KEY `id_filmweb` (`id_filmweb`,`movie_id`),
  ADD KEY `movie_id` (`movie_id`);

--
-- Indexes for table `watched_series`
--
ALTER TABLE `watched_series`
  ADD PRIMARY KEY (`id_watched`),
  ADD KEY `id_filmweb` (`id_filmweb`,`series_id`),
  ADD KEY `series_id` (`series_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `discord_guilds`
--
ALTER TABLE `discord_guilds`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tasks`
--
ALTER TABLE `tasks`
  MODIFY `id_task` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `watched_movies`
--
ALTER TABLE `watched_movies`
  MODIFY `id_watched` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `watched_series`
--
ALTER TABLE `watched_series`
  MODIFY `id_watched` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `discord_destinations`
--
ALTER TABLE `discord_destinations`
  ADD CONSTRAINT `discord_destinations_ibfk_1` FOREIGN KEY (`id_filmweb`) REFERENCES `users` (`id_filmweb`) ON DELETE CASCADE,
  ADD CONSTRAINT `discord_destinations_ibfk_2` FOREIGN KEY (`guild_id`) REFERENCES `discord_guilds` (`guild_id`);

--
-- Constraints for table `watched_movies`
--
ALTER TABLE `watched_movies`
  ADD CONSTRAINT `watched_movies_ibfk_1` FOREIGN KEY (`id_filmweb`) REFERENCES `users` (`id_filmweb`) ON DELETE CASCADE,
  ADD CONSTRAINT `watched_movies_ibfk_2` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`);

--
-- Constraints for table `watched_series`
--
ALTER TABLE `watched_series`
  ADD CONSTRAINT `watched_series_ibfk_1` FOREIGN KEY (`id_filmweb`) REFERENCES `users` (`id_filmweb`) ON DELETE CASCADE,
  ADD CONSTRAINT `watched_series_ibfk_2` FOREIGN KEY (`series_id`) REFERENCES `series` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
