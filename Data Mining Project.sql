CREATE TABLE `products` (
  `product_id` int PRIMARY KEY AUTO_INCREMENT,
  `seller_id` int,
  `category_id` int,
  `country_id` int,
  `condition_id` int,
  `product_name` varchar(255),
  `product_price` float,
  `shipping_fee` float,
  `page_number` int
);

CREATE TABLE `categories` (
  `category_id` int PRIMARY KEY AUTO_INCREMENT,
  `category` varchar(255)
);

CREATE TABLE `sellers` (
  `seller_id` int PRIMARY KEY AUTO_INCREMENT,
  `seller_name` varchar(255),
  `seller_feedback_score` int
);

CREATE TABLE `countries` (
  `country_id` int PRIMARY KEY AUTO_INCREMENT,
  `origin_country` varchar(255)
);

CREATE TABLE `conditions` (
  `condition_id` int PRIMARY KEY AUTO_INCREMENT,
  `product_condition` varchar(255)
);

ALTER TABLE `products` ADD FOREIGN KEY (`seller_id`) REFERENCES `sellers` (`seller_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`country_id`) REFERENCES `countries` (`country_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`condition_id`) REFERENCES `conditions` (`condition_id`);
