"""Test module for wiring."""

from decimal import Decimal
from typing import Callable

from dependency_injector.wiring import Provide, Provider

from .container import Container
from .service import Service


class TestClass:

    def __init__(self, service: Service = Provide[Container.service]):
        self.service = service


def test_function(service: Service = Provide[Container.service]):
    return service


def test_function_provider(service_provider: Callable[..., Service] = Provider[Container.service]):
    service = service_provider()
    return service


def test_config_value(
        some_value_int: int = Provide[Container.config.a.b.c.as_int()],
        some_value_str: str = Provide[Container.config.a.b.c.as_(str)],
        some_value_decimal: Decimal = Provide[Container.config.a.b.c.as_(Decimal)],
):
    return some_value_int, some_value_str, some_value_decimal


def test_provide_provider(service_provider: Callable[..., Service] = Provider[Container.service.provider]):
    service = service_provider()
    return service


def test_provided_instance(some_value: int = Provide[Container.service.provided.foo['bar'].call()]):
    return some_value


def test_subcontainer_provider(some_value: int = Provide[Container.sub.int_object]):
    return some_value


def test_config_invariant(some_value: int = Provide[Container.config.option[Container.config.switch]]):
    return some_value
