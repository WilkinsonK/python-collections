from unittest import TestCase

from collection.apiclient import *


class TestExampleClient_ShouldPass(BaseApiClient):
    """
    This api client should pass validation because
    root_url and max_timeout do not rely on default
    values.
    """

    root_url = "https://www.google.com"
    max_timeout = (5.0, 10.0)


class TestExampleClient_ShouldFail(BaseApiClient):
    """
    This api client should fail validation because
    root_url and max_timeout are not set in the
    class definition.
    """
    pass


class ApiClientTests(TestCase):

    def test_validation(self):
        try:
            failed = False
            TestExampleClient_ShouldFail()
        except RequiredAttributeError:
            failed = True

        self.assertEqual(failed, True)

    def test_instantiation(self):
        try:
            failed, reason = False, None
            TestExampleClient_ShouldPass()
        except Exception as error:
            failed, reason = True, error

        self.assertEqual(failed, False, reason)


class ApiAttrDefaultTests(TestCase):

    def test_apply_attribute(self):
        expected = "should get this value"

        ss = requests.Session()
        attr = AttrDefault(
            "params", {"test": expected}, ApplyBehavior.UPDATE
        )
        attr.apply(ss, None)

        self.assertEqual(ss.params["test"], expected)
