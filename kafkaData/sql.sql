DROP TABLE IF EXISTS `sgyy_device_module_section`;
create table `sgyy_device_module_section`
(
    id                           int          not null auto_increment comment '主键id',
    sgyy_device_info_id          int          null comment '三供一业设备id',
    sgyy_device_module_id        int          null comment '三供一业设备模块id',
    module_type_id               int          null comment '模块类型id',
    section_type                 int          null comment '阙值类型：正常阈值、隐患阈值、故障阈值、告警阈值',
    section_rule                 int          null comment '阙值规则：等于、不等于、区间、大于、小于、大于等于、小于等于',
    rule_max                     varchar(255) null comment '上限',
    rule_min                     varchar(255) null comment '下限',
    created_at                   datetime     not null comment '创建时间',
    updated_at                   datetime     null comment '修改时间',
    deleted_at                   datetime     null comment '删除时间',
    primary key (id) using btree
)ENGINE = InnoDB AUTO_INCREMENT = 1
 CHARACTER SET = utf8mb4
 COLLATE = utf8mb4_general_ci
 COMMENT = '三供一业设备模块阈值表';