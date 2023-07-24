import click
import itertools
import readline
import sqlite_utils
from sqlite_utils.utils import sqlite3
import tabulate

MAX_ROWS_TO_RETURN = 100

SQL_KEYWORDS = [
    "select ",
    "from ",
    "where ",
    "insert ",
    "update ",
    "delete ",
    "create ",
    "drop ",
    "begin ",
    "commit ",
    "rollback ",
]


def completer(text, state):
    options = [i for i in SQL_KEYWORDS if i.lower().startswith(text.lower())]
    if state < len(options):
        return options[state]
    else:
        return None


if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
readline.set_completer(completer)


@sqlite_utils.hookimpl
def register_commands(cli):
    @cli.command()
    @click.argument("path", type=click.Path(dir_okay=False, readable=True), required=False)
    def shell(path):
        "Start an interactive SQL shell for this database"
        run_sql_shell(path)


def run_sql_shell(path):
    if path:
        db = sqlite_utils.Database(path)
        print("Attached to {}".format(path))
    else:
        db = sqlite_utils.Database(memory=True)
        print("In-memory database, content will be lost on exit")

    print("Type 'exit' to exit.")

    statement = ""

    prompt = "sqlite-utils> "

    while True:
        line = input(prompt)
        if line:
            readline.add_history(line)

        prompt = "         ...> "

        if line.lower() in ("exit", "quit"):
            break

        statement += "\n" + line

        if sqlite3.complete_statement(statement):
            try:
                statement = statement.strip()
                cursor = db.execute(statement)
                if cursor.description is None:
                    # It was create table / insert / update
                    rowcount = cursor.rowcount
                    if rowcount != -1:
                        print(
                            "{} row{} affected".format(
                                rowcount, "s" if rowcount != 1 else ""
                            )
                        )
                else:
                    headers = [row[0] for row in cursor.description]

                    # Only show first MAX_ROWS_TO_RETURN
                    first_rows = list(cursor.fetchmany(MAX_ROWS_TO_RETURN + 1))
                    has_more = len(first_rows) == MAX_ROWS_TO_RETURN + 1
                    print(
                        tabulate.tabulate(
                            first_rows[:MAX_ROWS_TO_RETURN], headers=headers
                        )
                    )
                    if has_more:
                        print("[ results were truncated ]")

            except sqlite3.Error as e:
                print("An error occurred:", e)

            finally:
                prompt = "sqlite-utils> "

            statement = ""

    db.conn.close()
