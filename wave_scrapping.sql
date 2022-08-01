-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 01, 2022 at 06:31 AM
-- Server version: 10.4.18-MariaDB
-- PHP Version: 7.3.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `wave_scrapping`
--

-- --------------------------------------------------------

--
-- Table structure for table `scrapping_data`
--

CREATE TABLE `scrapping_data` (
  `id` int(11) NOT NULL,
  `fileName` varchar(200) NOT NULL,
  `web_url` varchar(200) NOT NULL,
  `report_link` varchar(200) NOT NULL,
  `title` varchar(200) NOT NULL,
  `critical_error` varchar(100) NOT NULL,
  `contrast_error` varchar(100) NOT NULL,
  `alerts` varchar(100) NOT NULL,
  `features` varchar(100) NOT NULL,
  `created_at` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `web_url`
--

CREATE TABLE `web_url` (
  `id` int(11) NOT NULL,
  `web_urls` varchar(200) NOT NULL,
  `fileName` varchar(100) NOT NULL,
  `report_generated` varchar(200) NOT NULL,
  `deleted` int(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `scrapping_data`
--
ALTER TABLE `scrapping_data`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `web_url`
--
ALTER TABLE `web_url`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `scrapping_data`
--
ALTER TABLE `scrapping_data`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `web_url`
--
ALTER TABLE `web_url`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
