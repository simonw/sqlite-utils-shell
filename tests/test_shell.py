import pytest
from sqlite_utils.plugins import get_plugins
from sqlite_utils_shell import run_sql_shell


def test_plugin_is_installed():
    plugins = get_plugins()
    names = [plugin["name"] for plugin in plugins]
    assert "sqlite-utils-shell" in names


@pytest.mark.parametrize(
    "inputs,expected_outputs",
    (
        (
            ["select 5"],
            [
                "  5\n" "---\n" "  5",
            ],
        ),
        (["select 5 +", "5"], ["  5 +\n    5\n-----\n   10"]),
        (
            [
                "create table foo(id integer primary key)",
                "insert into foo (id) values (5);",
                "insert into foo (id) values (7);",
                "delete from foo;",
            ],
            ["Done", "1 row affected", "1 row affected", "2 rows affected"],
        ),
    ),
)
def test_run_sql_shell(inputs, expected_outputs):
    outputs = []

    def input_(_):
        if inputs:
            s = inputs.pop(0)
            return s
        return "quit"

    def print_(*args):
        outputs.append(" ".join(map(str, args)))

    run_sql_shell(None, input_, print_)

    assert (
        outputs
        == [
            "In-memory database, content will be lost on exit",
            "Type 'exit' to exit.",
        ]
        + expected_outputs
    )
