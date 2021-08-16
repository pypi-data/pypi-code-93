from simple_ddl_parser import DDLParser


ddl = """
CREATE TABLE IF NOT EXISTS `shema`.table
(
    field_1        BIGINT,
    `partition`   STRING,
);
"""
parse_result = DDLParser(ddl).run(output_mode="hql")
print(parse_result)
