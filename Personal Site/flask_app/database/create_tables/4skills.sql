CREATE TABLE IF NOT EXISTS `skills` (
`skill_id`        int(11)       NOT NULL AUTO_INCREMENT	COMMENT 'The skill id',
`name`            varchar(100)  NOT NULL					COMMENT 'The name of the skill',
`skill_level`     int(2)        NOT NULL                    COMMENT 'My level in this skill',

PRIMARY KEY (`skill_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="skills that I posses";