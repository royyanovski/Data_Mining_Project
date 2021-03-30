CREATE TABLE `products` (
  `product_id` int PRIMARY KEY AUTO_INCREMENT,
  `seller_id` int,
  `category_id` int,
  `country_id` int,
  `condition_id` int,
  `product_name` varchar(255) UNIQUE,
  `product_price` float,
  `shipping_fee` float,
  `page_number` int
);

CREATE TABLE `categories` (
  `category_id` int PRIMARY KEY AUTO_INCREMENT,
  `category` varchar(255) UNIQUE
);

CREATE TABLE `sellers` (
  `seller_id` int PRIMARY KEY AUTO_INCREMENT,
  `seller_name` varchar(255) UNIQUE,
  `seller_feedback_score` int
);

CREATE TABLE `countries` (
  `country_id` int PRIMARY KEY AUTO_INCREMENT,
  `origin_country` varchar(255) UNIQUE
);

CREATE TABLE `conditions` (
  `condition_id` int PRIMARY KEY AUTO_INCREMENT,
  `product_condition` varchar(255) UNIQUE
);

CREATE TABLE `currency` (
  `product_id` int,
  `Israeli_Shekel_ILS` float,
  `US_Dollar_USD` float,
  `EU_Euro_EUR` float,
  `GB_Pound_GBP` float,
  `China_Yoan_CNY` float,
  `Russia_Ruble_RUB` float
);

ALTER TABLE `products` ADD FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`seller_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`condition_id`) REFERENCES `conditions` (`condition_id`);

ALTER TABLE `currency` ADD FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);
