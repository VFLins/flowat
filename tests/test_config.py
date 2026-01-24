from flowat import config


def get_test_parser():
    return config.get_parser(filename="test")


class TestConfigList(config._ConfigList):
    __test__ = False
    def __init__(self):
        super().__init__(
            parser_factory=get_test_parser,
            section="test",
            key="something",
            default=["a", "beautiful", "list"]
        )


try:
    # when calling `get` before any `set`, should retrieve the default value
    assert TestConfigList.get() == ["a", "beautiful", "list"]

    # section 'test' should exist after first use of TestConfigList
    parser = get_test_parser()
    assert parser.has_section("test")

    # test if string was removed with `rm`
    TestConfigList.rm("a")
    assert TestConfigList.get() == ["beautiful", "list"]
finally:
    # test cleanup
    if parser._config_file.is_file():
        parser._config_file.unlink()
