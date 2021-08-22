import argparse

cli = argparse.ArgumentParser()

cli.add_argument("--sql_username", type=str, default="")
cli.add_argument("--sql_password", type=str, default="")
cli.add_argument("--sql_server", type=str, default="localhost")
cli.add_argument("--sql_port", type=int, default=3306)
cli.add_argument("--sql_database", type=str, default="")

cli.add_argument("--smtp_hostname", type=str, default="localhost")
cli.add_argument("--smtp_port", type=int, default=25)
cli.add_argument("--smtp_email", type=str, default="")

cli.add_argument("--mongo_server", type=str, default="localhost")
cli.add_argument("--mongo_port", type=int, default=27017)

args = vars(cli.parse_args())

MONGO_SETTINGS = {
    "host": args["mongo_server"],
    "port": args["mongo_port"]
}

SQL_CONNECTION = "mysql://{}:{}@{}:{}/{}?charset=utf8mb4".format(
    args["sql_username"],
    args["sql_password"],
    args["sql_server"],
    args["sql_port"],
    args["sql_database"]
)

SMTP_SETTINGS = {
    "host": args["smtp_hostname"],
    "port": args["smtp_port"],
    "email": args["smtp_email"]
}
