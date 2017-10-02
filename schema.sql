drop table if exists `env`;
CREATE TABLE `env` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(50) COLLATE utf8_bin NOT NULL,
  `dt` datetime NOT NULL,
  `ts` varchar(50) COLLATE utf8_bin NOT NULL,
  `ax` decimal(10,4) DEFAULT NULL,
  `ay` decimal(10,4) DEFAULT NULL,
  `az` decimal(10,4) DEFAULT NULL,
  `light` decimal(10,4) DEFAULT NULL,
  `temp` decimal(10,4) DEFAULT NULL,
  `humi` decimal(10,4) DEFAULT NULL,
  `volts` decimal(10,4) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

drop table if exists `files`;
CREATE TABLE `files` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `uid` varchar(50) COLLATE utf8_bin NOT NULL,
  `dt` datetime NOT NULL,
  `ts` varchar(50) COLLATE utf8_bin NOT NULL,
  `filename` varchar(100) COLLATE utf8_bin DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;