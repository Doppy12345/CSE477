CREATE TABLE IF NOT EXISTS `boards` (
`board_id`        int(11)       NOT NULL AUTO_INCREMENT 	COMMENT 'Board id',
`name`           varchar(100)  NOT NULL                	COMMENT 'Name of the project this board is associated with',

PRIMARY KEY  (`board_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="Kanban Boards";