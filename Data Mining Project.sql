CREATE DATABASE ebay_products;

USE ebay_products;

CREATE TABLE `products` (
  `product_id` int PRIMARY KEY AUTO_INCREMENT,
  `product_name` varchar(255),
  `product_price` float,
  `origin_country` varchar(255),
  `shipping_fee` float,
  `product_condition` varchar(255)
);

CREATE TABLE `categories` (
  `product_id` int,
  `category` varchar(255)
);

CREATE TABLE `sellers` (
  `product_id` int,
  `seller_name` varchar(255),
  `pos_feedback_pct` float,
  `seller_feedback_score` int
);

ALTER TABLE `products` ADD FOREIGN KEY (`product_id`) REFERENCES `categories` (`product_id`);

ALTER TABLE `products` ADD FOREIGN KEY (`product_id`) REFERENCES `sellers` (`product_id`);
