from sqlalchemy import create_engine
from data_grid_text_reader.data_grid_text_reader import DataGridTextReader
from data_grid_text_reader.assert_equal_lists import assert_equal


def test_without_data_grid_text_reader():
    with create_engine('sqlite://').connect() as connection:
        connection.execute("""
        CREATE TABLE sales_by_day (
            sale_date DATE,
            units_sold INT,
            gross_sales DOUBLE
        );""")

        connection.execute("""
        INSERT INTO sales_by_day
        (sale_date, units_sold, gross_sales) VALUES
        ('2019-01-01', 10, 100),
        ('2019-01-02', 20, 200),
        ('2019-01-08', 80, 800);""")

        actual_rows = [dict(row) for row in connection.execute("""
        SELECT  CAST(STRFTIME('%W', sale_date) AS INT) + 1 AS week_of_year,
                AVG(units_sold) AS avg_units_sold,
                SUM(gross_sales) AS gross_sales
        FROM    sales_by_day
        GROUP BY 1
        ORDER BY 1
        """)]

        assert 2 == len(actual_rows)  # Number of rows
        assert 3 == len(actual_rows[0])  # Number of columns
        assert 1 == actual_rows[0]['week_of_year']
        assert 15 == actual_rows[0]['avg_units_sold']
        assert 300 == actual_rows[0]['gross_sales']
        assert 2 == actual_rows[1]['week_of_year']
        assert 80 == actual_rows[1]['avg_units_sold']
        assert 800 == actual_rows[1]['gross_sales']


def test_using_data_grid_text_reader():
    with create_engine('sqlite://').connect() as connection:
        reader = DataGridTextReader()
        reader.save_as_table('sales_by_day', """
        +----------+----------+-----------+
        |sale_date |units_sold|gross_sales|
        [date      |int       |double     |
        +----------+----------+-----------+
        |2019-01-01|10        |100        |
        |2019-01-02|20        |200        |
        |2019-01-08|80        |800        |
        +----------+----------+-----------+
        """, connection)

        actual_rows = [dict(row) for row in connection.execute("""
        SELECT  CAST(STRFTIME('%W', sale_date) AS INT) + 1 AS week_of_year,
                AVG(units_sold) AS avg_units_sold,
                SUM(gross_sales) AS gross_sales
        FROM    sales_by_day
        GROUP BY 1
        ORDER BY 1
        """)]

        expected_rows = reader.data_grid_text_to_list("""
        +------------+--------------+-----------+
        |week_of_year|avg_units_sold|gross_sales|
        [int         |int           |double     |
        +------------+--------------+-----------+
        |1           |15            |300        |
        |2           |80            |800        |
        +------------+--------------+-----------+
        """)
        assert_equal(expected_rows, actual_rows)
