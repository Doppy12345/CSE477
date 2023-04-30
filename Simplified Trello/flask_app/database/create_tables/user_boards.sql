CREATE TABLE IF NOT EXISTS `user_boards` (
`user_board_id`    int(11)           NOT NULL AUTO_INCREMENT	COMMENT 'The user_board id',
`board_id`         int(11)           NOT NULL 			        COMMENT 'FK:The board id',
`user_id`          int(11)           NOT NULL 			        COMMENT 'FK:The user id',

PRIMARY KEY (`user_board_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id),
FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="boards pertaining to certain users";