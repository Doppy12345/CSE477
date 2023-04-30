CREATE TABLE IF NOT EXISTS `experiences` (
`exp_id`            int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The experience id',
`position_id`        int(11)       NOT NULL 			    COMMENT 'FK:The position id',
`name`               varchar(100)  NOT NULL					COMMENT 'The name of this experience',
`description`        varchar(500)  NOT NULL                 COMMENT 'The description of this experience',
`hyperlink`          varchar(200)                           COMMENT 'My description if the experience',
`start_date`         date                                   COMMENT 'My start date for this experience',
`end_date`           date          DEFAULT NULL             COMMENT 'The end date for this experience',
PRIMARY KEY (`exp_id`),
FOREIGN KEY (position_id) REFERENCES positions(position_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="experiences I have had in certain positions";