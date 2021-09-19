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


class ApiAttrDefaultTests(TestCase):

    def test_apply_attribute(self):
        expected = "should get this value"

        ss = requests.Session()
        attr = AttrDefault(
            "params", {"test": expected}, ApplyBehavior.UPDATE
        )
        attr.apply(ss, None)

        self.assertEqual(ss.params["test"], expected)


class ApiClientTests(TestCase):

    def test_validation(self):
        try:
            failed = False
            TestExampleClient_ShouldFail()
        except RequiredAttributeError:
            failed = True

        self.assertEqual(failed, True)

    def test_make_new(self):
        try:
            failed, reason = False, None
            inst = TestExampleClient_ShouldPass._make_new()

            if not inst.__class__ is TestExampleClient_ShouldPass:
                raise TypeError(
                    f"_make_new did not return instance "
                    f"of {TestExampleClient_ShouldPass} "
                )
        except Exception as error:
            failed, reason = True, error

        self.assertEqual(failed, False, reason)

    def test_init_session(self):
        inst = TestExampleClient_ShouldPass()
        expected = [0, 1, 2]
        try:
            inst._init_session(headers={"Include-Content": expected})
        except Exception as error:
            failed, reason = True, error
            self.assertEqual(failed, False, reason)

        self.assertEqual(inst.session.headers["Include-Content"], expected)

    def test_instantiation(self):
        try:
            failed, reason = False, None
            TestExampleClient_ShouldPass()
        except Exception as error:
            failed, reason = True, error

        self.assertEqual(failed, False, reason)
