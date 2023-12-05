def pytest_addoption(parser):
    parser.addoption(
        "--answer_path",
        action="append",
        default=[],
        help="URL of answer key",
    )

    parser.addoption(
        "--files",
        action="append",
        default=[],
        help="List of file names to be graded."
    )

    parser.addoption(
        "--cols",
        action="append",
        default=[],
        help="List of columns to check"
    )


def pytest_generate_tests(metafunc):
    if "answer_path" in metafunc.fixturenames:
        metafunc.parametrize(
            "answer_path", metafunc.config.getoption("answer_path"))

    if "files" in metafunc.fixturenames:
        metafunc.parametrize(
            "files", metafunc.config.getoption("files"))

    if "cols" in metafunc.fixturenames:
        metafunc.parametrize(
            "cols", metafunc.config.getoption("cols"))
