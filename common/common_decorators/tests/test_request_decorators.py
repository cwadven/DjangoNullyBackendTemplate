from common.common_decorators.request_decorators import (
    mandatories,
    optionals,
)
from common.common_exceptions.exceptions import (
    CodeInvalidateException,
    MissingMandatoryParameterException,
)
from django.http import HttpRequest
from django.test import TestCase


@mandatories('param1', 'param2')
def my_mandatories_view_function(request, m):
    return m


class MyMandatoriesViewClass:
    @mandatories('param1', 'param2')
    def my_method(self, request, m):
        return m


class TestMandatoriesDecorator(TestCase):

    def test_decorator_applied_to_function(self):
        # Given: Create a request
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'param1': 'value1', 'param2': 'value2'}

        # When: Call the decorated function with mandatory parameters
        response = my_mandatories_view_function(request)

        # Then: Ensure the function executes and returns the expected result
        self.assertEqual(response, {'param1': 'value1', 'param2': 'value2'})

        # When: Call the decorated function with missing mandatory parameter
        request.GET = {'param1': 'value1'}
        with self.assertRaises(MissingMandatoryParameterException) as e:
            my_mandatories_view_function(request)

        self.assertEqual(e.exception.default_detail, '입력값을 다시 확인해주세요.')
        self.assertEqual(e.exception.default_code, 'missing-mandatory-parameter')
        self.assertEqual(e.exception.errors, {'param2': ['param2 입력값을 확인해주세요.']})

    def test_decorator_applied_to_class_method(self):
        # Given: Create a request
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'param1': 'value1', 'param2': 'value2'}

        # When: Instantiate the class and call the decorated method with mandatory parameters
        view_instance = MyMandatoriesViewClass()
        response = view_instance.my_method(request)

        # Then: Ensure the method executes and returns the expected result
        self.assertEqual(response, {'param1': 'value1', 'param2': 'value2'})

        # When: Instantiate the class and call the decorated method with missing mandatory parameter
        request.GET = {'param1': 'value1'}
        with self.assertRaises(MissingMandatoryParameterException) as e:
            view_instance.my_method(request)

        self.assertEqual(e.exception.default_detail, '입력값을 다시 확인해주세요.')
        self.assertEqual(e.exception.default_code, 'missing-mandatory-parameter')
        self.assertEqual(e.exception.errors, {'param2': ['param2 입력값을 확인해주세요.']})

    def test_decorator_without_request_argument(self):
        # When: Call the decorator without a request argument (should raise CodeInvalidateException)
        @mandatories('param1', 'param2')
        def invalid_function():
            pass

        with self.assertRaises(CodeInvalidateException):
            invalid_function()

        class InvalidViewClass:
            @mandatories('param1', 'param2')
            def method(self):
                pass
        # When: Apply the decorator to a class without request arguments (should raise CodeInvalidateException)
        with self.assertRaises(CodeInvalidateException):
            InvalidViewClass().method()


@optionals({'param1': 'default_value1', 'param2': 'default_value2'})
def my_optional_view_function(request, o):
    return o


class MyOptionalViewClass:
    @optionals({'param1': 'default_value1', 'param2': 'default_value2'})
    def my_method(self, request, o):
        return o


class TestOptionalsDecorator(TestCase):

    def test_decorator_applied_to_function(self):
        # Given: Create a request
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'param1': 'value1'}

        # When: Call the decorated function with an optional parameter and a provided value
        response = my_optional_view_function(request)

        # Then: Ensure the function executes and returns the expected result
        self.assertEqual(response, {'param1': 'value1', 'param2': 'default_value2'})

        # When: Call the decorated function with an optional parameter and no provided value
        request.GET = {}
        response = my_optional_view_function(request)

        # Then: Ensure the function executes and returns the default value
        self.assertEqual(response, {'param1': 'default_value1', 'param2': 'default_value2'})

    def test_decorator_applied_to_class_method(self):
        # Given: Create a request
        request = HttpRequest()
        request.method = 'GET'
        request.GET = {'param1': 'value1'}

        # When: Instantiate the class and call the decorated method with an optional parameter and a provided value
        view_instance = MyOptionalViewClass()
        response = view_instance.my_method(request)

        # Then: Ensure the method executes and returns the expected result
        self.assertEqual(response, {'param1': 'value1', 'param2': 'default_value2'})

        # When: Instantiate the class and call the decorated method with an optional parameter and no provided value
        request.GET = {}
        response = view_instance.my_method(request)

        # Then: Ensure the method executes and returns the default value
        self.assertEqual(response, {'param1': 'default_value1', 'param2': 'default_value2'})

    def test_decorator_without_request_argument(self):
        # When: Call the decorator without a request argument (should raise CodeInvalidateException)
        @optionals({'param1': 'default_value1', 'param2': 'default_value2'})
        def invalid_function():
            pass

        with self.assertRaises(CodeInvalidateException):
            invalid_function()

        # When: Apply the decorator to a class without request arguments (should raise CodeInvalidateException)
        @optionals({'param1': 'default_value1', 'param2': 'default_value2'})
        class InvalidViewClass:
            def method(self):
                pass

        with self.assertRaises(CodeInvalidateException):
            InvalidViewClass().method()
