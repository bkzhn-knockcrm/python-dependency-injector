from __future__ import annotations

from pathlib import Path
from typing import (
    Awaitable,
    TypeVar,
    Generic,
    Type,
    Callable as _Callable,
    Any,
    Tuple,
    List as _List,
    Dict as _Dict,
    Optional,
    Union,
    Coroutine as _Coroutine,
    Iterator as _Iterator,
    AsyncIterator as _AsyncIterator,
    Generator as _Generator,
    overload,
)

try:
    import yaml
except ImportError:
    yaml = None

from . import resources


Injection = Any
T = TypeVar('T')


class OverridingContext:
    def __init__(self, overridden: Provider, overriding: Provider): ...
    def __enter__(self) -> Provider: ...
    def __exit__(self, *_: Any) -> None: ...


class Provider(Generic[T]):
    def __init__(self) -> None: ...

    @overload
    def __call__(self, *args: Injection, **kwargs: Injection) -> T: ...
    @overload
    def __call__(self, *args: Injection, **kwargs: Injection) -> Awaitable[T]: ...
    def async_(self, *args: Injection, **kwargs: Injection) -> Awaitable[T]: ...

    def __deepcopy__(self, memo: Optional[_Dict[Any, Any]]) -> Provider: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...
    @property
    def overridden(self) -> Tuple[Provider]: ...
    @property
    def last_overriding(self) -> Optional[Provider]: ...
    def override(self, provider: Union[Provider, Any]) -> OverridingContext: ...
    def reset_last_overriding(self) -> None: ...
    def reset_override(self) -> None: ...
    def delegate(self) -> Provider: ...
    @property
    def provider(self) -> Provider: ...
    @property
    def provided(self) -> ProvidedInstance: ...
    def enable_async_mode(self) -> None: ...
    def disable_async_mode(self) -> None: ...
    def reset_async_mode(self) -> None: ...
    def is_async_mode_enabled(self) -> bool: ...
    def is_async_mode_disabled(self) -> bool: ...
    def is_async_mode_undefined(self) -> bool: ...
    def _copy_overridings(self, copied: Provider, memo: Optional[_Dict[Any, Any]]) -> None: ...


class Object(Provider[T]):
    def __init__(self, provides: T) -> None: ...


class Delegate(Provider[Provider]):
    def __init__(self, provides: Provider) -> None: ...
    @property
    def provides(self) -> Provider: ...


class Dependency(Provider[T]):
    def __init__(self, instance_of: Type[T] = object) -> None: ...
    @property
    def instance_of(self) -> Type[T]: ...
    def provided_by(self, provider: Provider) -> OverridingContext: ...


class ExternalDependency(Dependency[T]): ...


class DependenciesContainer(Object):
    def __init__(self, **dependencies: Provider) -> None: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def providers(self) -> _Dict[str, Provider]: ...


class Callable(Provider[T]):
    def __init__(self, provides: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def provides(self) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Callable[T]: ...
    def set_args(self, *args: Injection) -> Callable[T]: ...
    def clear_args(self) -> Callable[T]: ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Callable[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> Callable[T]: ...
    def clear_kwargs(self) -> Callable[T]: ...


class DelegatedCallable(Callable[T]): ...


class AbstractCallable(Callable[T]):
    def override(self, provider: Callable) -> OverridingContext: ...


class CallableDelegate(Delegate):
    def __init__(self, callable: Callable) -> None: ...


class Coroutine(Callable[T]): ...


class DelegatedCoroutine(Coroutine[T]): ...


class AbstractCoroutine(Coroutine[T]):
    def override(self, provider: Coroutine) -> OverridingContext: ...


class CoroutineDelegate(Delegate):
    def __init__(self, coroutine: Coroutine) -> None: ...


class ConfigurationOption(Provider[Any]):
    UNDEFINED: object
    def __init__(self, name: Tuple[str], root: Configuration) -> None: ...
    def __getattr__(self, item: str) -> ConfigurationOption: ...
    def __getitem__(self, item: Union[str, Provider]) -> ConfigurationOption: ...
    @property
    def root(self) -> Configuration: ...
    def get_name(self) -> str: ...
    def get_name_segments(self) -> Tuple[Union[str, Provider]]: ...
    def as_int(self) -> TypedConfigurationOption[int]: ...
    def as_float(self) -> TypedConfigurationOption[float]: ...
    def as_(self, callback: _Callable[..., T], *args: Injection, **kwargs: Injection) -> TypedConfigurationOption[T]: ...
    def required(self) -> ConfigurationOption: ...
    def is_required(self) -> bool: ...
    def update(self, value: Any) -> None: ...
    def from_ini(self, filepath: Union[Path, str]) -> None: ...
    def from_yaml(self, filepath: Union[Path, str], loader: Optional[Any]=None) -> None: ...
    def from_dict(self, options: _Dict[str, Any]) -> None: ...
    def from_env(self, name: str, default: Optional[Any] = None) -> None: ...


class TypedConfigurationOption(Callable[T]):
    @property
    def option(self) -> ConfigurationOption: ...


class Configuration(Object[Any]):
    DEFAULT_NAME: str = 'config'
    def __init__(self, name: str = DEFAULT_NAME, default: Optional[Any] = None, *, strict: bool = False) -> None: ...
    def __getattr__(self, item: str) -> ConfigurationOption: ...
    def __getitem__(self, item: Union[str, Provider]) -> ConfigurationOption: ...
    def get_name(self) -> str: ...
    def get(self, selector: str) -> Any: ...
    def set(self, selector: str, value: Any) -> OverridingContext: ...
    def reset_cache(self) -> None: ...
    def update(self, value: Any) -> None: ...
    def from_ini(self, filepath: Union[Path, str]) -> None: ...
    def from_yaml(self, filepath: Union[Path, str], loader: Optional[Any]=None) -> None: ...
    def from_dict(self, options: _Dict[str, Any]) -> None: ...
    def from_env(self, name: str, default: Optional[Any] = None) -> None: ...


class Factory(Provider[T]):
    provided_type: Optional[Type]
    def __init__(self, provides: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def cls(self) -> T: ...
    @property
    def provides(self) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Factory[T]: ...
    def set_args(self, *args: Injection) -> Factory[T]: ...
    def clear_args(self) -> Factory[T]: ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Factory[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> Factory[T]: ...
    def clear_kwargs(self) -> Factory[T]: ...
    @property
    def attributes(self) -> _Dict[Any, Injection]: ...
    def add_attributes(self, **kwargs: Injection) -> Factory[T]: ...
    def set_attributes(self, **kwargs: Injection) -> Factory[T]: ...
    def clear_attributes(self) -> Factory[T]: ...


class DelegatedFactory(Factory[T]): ...


class AbstractFactory(Factory[T]):
    def override(self, provider: Factory) -> OverridingContext: ...


class FactoryDelegate(Delegate):
    def __init__(self, factory: Factory): ...


class FactoryAggregate(Provider):
    def __init__(self, **factories: Factory): ...
    def __getattr__(self, factory_name: str) -> Factory: ...

    @overload
    def __call__(self, factory_name: str, *args: Injection, **kwargs: Injection) -> Any: ...
    @overload
    def __call__(self, factory_name: str, *args: Injection, **kwargs: Injection) -> Awaitable[Any]: ...
    def async_(self, factory_name: str, *args: Injection, **kwargs: Injection) -> Awaitable[Any]: ...

    @property
    def factories(self) -> _Dict[str, Factory]: ...


class BaseSingleton(Provider[T]):
    provided_type = Optional[Type]
    def __init__(self, provides: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def cls(self) -> T: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> BaseSingleton[T]: ...
    def set_args(self, *args: Injection) -> BaseSingleton[T]: ...
    def clear_args(self) -> BaseSingleton[T]: ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> BaseSingleton[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> BaseSingleton[T]: ...
    def clear_kwargs(self) -> BaseSingleton[T]: ...
    @property
    def attributes(self) -> _Dict[Any, Injection]: ...
    def add_attributes(self, **kwargs: Injection) -> BaseSingleton[T]: ...
    def set_attributes(self, **kwargs: Injection) -> BaseSingleton[T]: ...
    def clear_attributes(self) -> BaseSingleton[T]: ...
    def reset(self) -> None: ...


class Singleton(BaseSingleton[T]): ...


class DelegatedSingleton(Singleton[T]): ...


class ThreadSafeSingleton(Singleton[T]): ...


class DelegatedThreadSafeSingleton(ThreadSafeSingleton[T]): ...


class ThreadLocalSingleton(BaseSingleton[T]): ...


class DelegatedThreadLocalSingleton(ThreadLocalSingleton[T]): ...


class AbstractSingleton(BaseSingleton[T]):
    def override(self, provider: BaseSingleton) -> OverridingContext: ...


class SingletonDelegate(Delegate):
    def __init__(self, factory: BaseSingleton): ...


class List(Provider[_List]):
    def __init__(self, *args: Injection): ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> List[T]: ...
    def set_args(self, *args: Injection) -> List[T]: ...
    def clear_args(self) -> List[T]: ...


class Dict(Provider[_Dict]):
    def __init__(self, dict_: Optional[_Dict[Any, Injection]] = None, **kwargs: Injection): ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, dict_: Optional[_Dict[Any, Injection]] = None, **kwargs: Injection) -> Dict: ...
    def set_kwargs(self, dict_: Optional[_Dict[Any, Injection]] = None, **kwargs: Injection) -> Dict: ...
    def clear_kwargs(self) -> Dict: ...


class Resource(Provider[T]):
    @overload
    def __init__(self, initializer: Type[resources.Resource[T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: Type[resources.AsyncResource[T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: _Callable[..., _Iterator[T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: _Callable[..., _AsyncIterator[T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: _Callable[..., _Coroutine[Injection, Injection, T]], *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, initializer: _Callable[..., T], *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def args(self) -> Tuple[Injection]: ...
    def add_args(self, *args: Injection) -> Resource[T]: ...
    def set_args(self, *args: Injection) -> Resource[T]: ...
    def clear_args(self) -> Resource[T]: ...
    @property
    def kwargs(self) -> _Dict[Any, Injection]: ...
    def add_kwargs(self, **kwargs: Injection) -> Resource[T]: ...
    def set_kwargs(self, **kwargs: Injection) -> Resource[T]: ...
    def clear_kwargs(self) -> Resource[T]: ...
    @property
    def initialized(self) -> bool: ...
    def init(self) -> Optional[Awaitable[T]]: ...
    def shutdown(self) -> Optional[Awaitable]: ...


class Container(Provider[T]):
    def __init__(self, container_cls: Type[T], container: Optional[T] = None, **overriding_providers: Provider) -> None: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def container(self) -> T: ...


class Selector(Provider[Any]):
    def __init__(self, selector: _Callable[..., Any], **providers: Provider): ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def providers(self) -> _Dict[str, Provider]: ...


class ProvidedInstanceFluentInterface:
    def __getattr__(self, item: Any) -> AttributeGetter: ...
    def __getitem__(self, item: Any) -> ItemGetter: ...
    def call(self, *args: Injection, **kwargs: Injection) -> MethodCaller: ...


class ProvidedInstance(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider) -> None: ...


class AttributeGetter(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider, attribute: str) -> None: ...


class ItemGetter(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider, item: str) -> None: ...


class MethodCaller(Provider, ProvidedInstanceFluentInterface):
    def __init__(self, provider: Provider, *args: Injection, **kwargs: Injection) -> None: ...


def is_provider(instance: Any) -> bool: ...


def ensure_is_provider(instance: Any) -> Provider: ...


def is_delegated(instance: Any) -> bool: ...


def represent_provider(provider: Provider, provides: Any) -> str: ...


def deepcopy(instance: Any, memo: Optional[_Dict[Any, Any]] = None): Any: ...


def merge_dicts(dict1: _Dict[Any, Any], dict2: _Dict[Any, Any]) -> _Dict[Any, Any]: ...


if yaml:
    class YamlLoader(yaml.SafeLoader): ...
else:
    class YamlLoader: ...
