CREATE TABLE IF NOT EXISTS `exp_skills` (
`exp_skill_id`    int(11)           NOT NULL AUTO_INCREMENT	COMMENT 'The exp_skill id',
`skill_id`        int(11)           NOT NULL 			        COMMENT 'FK:The skill id',
`exp_id`          int(11)           NOT NULL 			        COMMENT 'FK:The experience id',

PRIMARY KEY (`exp_skill_id`),
FOREIGN KEY (skill_id) REFERENCES skills(skill_id),
FOREIGN KEY (exp_id) REFERENCES experiences(exp_id)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COMMENT="skills pertaining to certain experiences";