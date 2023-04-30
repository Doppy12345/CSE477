CREATE TABLE IF NOT EXISTS `tasks` (
`task_id`        int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The task id',
`board_id`            int(11)       NOT NULL 				COMMENT 'FK:The board id',
`title`              varchar(100)  NOT NULL					COMMENT 'My title in this position',
`description`   varchar(500)  NOT NULL                      COMMENT 'My responsibilities in this position',
`state`         int(1)          NOT NULL                      COMMENT 'state of the task',
PRIMARY KEY (`task_id`),
FOREIGN KEY (board_id) REFERENCES boards(board_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Task for a given board";