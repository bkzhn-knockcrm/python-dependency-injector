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
    Iterable as _Iterable,
    Iterator as _Iterator,
    AsyncIterator as _AsyncIterator,
    Generator as _Generator,
    overload,
)

try:
    import yaml
except ImportError:
    yaml = None

try:
    import pydantic
except ImportError:
    pydantic = None

from . import resources


Injection = Any
ProviderParent = Union['Provider', Any]
T = TypeVar('T')
TT = TypeVar('TT')
P = TypeVar('P', bound='Provider')
BS = TypeVar('BS', bound='BaseSingleton')


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
    def override(self, provider: Union[Provider, Any]) -> OverridingContext[P]: ...
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
    @property
    def related(self) -> _Iterator[Provider]: ...
    def traverse(self, types: Optional[_Iterable[Type[TT]]] = None) -> _Iterator[TT]: ...
    def _copy_overridings(self, copied: Provider, memo: Optional[_Dict[Any, Any]]) -> None: ...


class Object(Provider[T]):
    def __init__(self, provides: Optional[T] = None) -> None: ...
    def provides(self) -> Optional[T]: ...
    def set_provides(self, provides: Optional[T]) -> Object: ...


class Self(Provider[T]):
    def __init__(self, container: Optional[T] = None) -> None: ...
    def set_container(self, container: T) -> None: ...
    def set_alt_names(self, alt_names: _Iterable[Any]) -> None: ...
    @property
    def alt_names(self) -> Tuple[Any]: ...


class Delegate(Provider[Provider]):
    def __init__(self, provides: Optional[Provider] = None) -> None: ...
    @property
    def provides(self) -> Optional[Provider]: ...
    def set_provides(self, provides: Optional[Provider]) -> Delegate: ...


class Dependency(Provider[T]):
    def __init__(self, instance_of: Type[T] = object, default: Optional[Union[Provider, Any]] = None) -> None: ...
    def __getattr__(self, name: str) -> Any: ...

    @property
    def instance_of(self) -> Type[T]: ...
    def set_instance_of(self, instance_of: Type[T]) -> Dependency[T]: ...

    @property
    def default(self) -> Provider[T]: ...
    def set_default(self, default: Optional[Union[Provider, Any]]) -> Dependency[T]: ...

    @property
    def is_defined(self) -> bool: ...
    def provided_by(self, provider: Provider) -> OverridingContext[P]: ...
    @property
    def parent(self) -> Optional[ProviderParent]: ...
    @property
    def parent_name(self) -> Optional[str]: ...
    def assign_parent(self, parent: ProviderParent) -> None: ...


class ExternalDependency(Dependency[T]): ...


class DependenciesContainer(Object):
    def __init__(self, **dependencies: Provider) -> None: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def providers(self) -> _Dict[str, Provider]: ...
    def resolve_provider_name(self, provider: Provider) -> str: ...
    @property
    def parent(self) -> Optional[ProviderParent]: ...
    @property
    def parent_name(self) -> Optional[str]: ...
    def assign_parent(self, parent: ProviderParent) -> None: ...


class Callable(Provider[T]):
    def __init__(self, provides: Optional[_Callable[..., T]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def provides(self) -> Optional[T]: ...
    def set_provides(self, provides: Optional[_Callable[..., T]]) -> Callable[T]: ...
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
    def override(self, provider: Callable) -> OverridingContext[P]: ...


class CallableDelegate(Delegate):
    def __init__(self, callable: Callable) -> None: ...


class Coroutine(Callable[T]): ...


class DelegatedCoroutine(Coroutine[T]): ...


class AbstractCoroutine(Coroutine[T]):
    def override(self, provider: Coroutine) -> OverridingContext[P]: ...


class CoroutineDelegate(Delegate):
    def __init__(self, coroutine: Coroutine) -> None: ...


class ConfigurationOption(Provider[Any]):
    UNDEFINED: object
    def __init__(self, name: Tuple[str], root: Configuration) -> None: ...
    def __enter__(self) -> ConfigurationOption: ...
    def __exit__(self, *exc_info: Any) -> None: ...
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
    def from_ini(self, filepath: Union[Path, str], required: bool = False) -> None: ...
    def from_yaml(self, filepath: Union[Path, str], required: bool = False, loader: Optional[Any]=None) -> None: ...
    def from_pydantic(self, settings: PydanticSettings, required: bool = False, **kwargs: Any) -> None: ...
    def from_dict(self, options: _Dict[str, Any], required: bool = False) -> None: ...
    def from_env(self, name: str, default: Optional[Any] = None, required: bool = False) -> None: ...


class TypedConfigurationOption(Callable[T]):
    @property
    def option(self) -> ConfigurationOption: ...


class Configuration(Object[Any]):
    DEFAULT_NAME: str = 'config'
    def __init__(self, name: str = DEFAULT_NAME, default: Optional[Any] = None, *, strict: bool = False) -> None: ...
    def __enter__(self) -> Configuration : ...
    def __exit__(self, *exc_info: Any) -> None: ...
    def __getattr__(self, item: str) -> ConfigurationOption: ...
    def __getitem__(self, item: Union[str, Provider]) -> ConfigurationOption: ...

    def get_name(self) -> str: ...
    def set_name(self, name: str) -> Configuration: ...

    def get_default(self) -> _Dict[Any, Any]: ...
    def set_default(self, default: _Dict[Any, Any]): ...

    def get_strict(self) -> bool: ...
    def set_strict(self, strict: bool) -> Configuration: ...

    def get_children(self) -> _Dict[str, ConfigurationOption]: ...
    def set_children(self, children: _Dict[str, ConfigurationOption) -> Configuration: ...

    def get(self, selector: str) -> Any: ...
    def set(self, selector: str, value: Any) -> OverridingContext[P]: ...
    def reset_cache(self) -> None: ...
    def update(self, value: Any) -> None: ...
    def from_ini(self, filepath: Union[Path, str], required: bool = False) -> None: ...
    def from_yaml(self, filepath: Union[Path, str], required: bool = False, loader: Optional[Any]=None) -> None: ...
    def from_pydantic(self, settings: PydanticSettings, required: bool = False, **kwargs: Any) -> None: ...
    def from_dict(self, options: _Dict[str, Any], required: bool = False) -> None: ...
    def from_env(self, name: str, default: Optional[Any] = None, required: bool = False) -> None: ...


class Factory(Provider[T]):
    provided_type: Optional[Type]
    def __init__(self, provides: Optional[_Callable[..., T]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def cls(self) -> T: ...
    @property
    def provides(self) -> T: ...
    def set_provides(self, provides: Optional[_Callable[..., T]]) -> Factory[T]: ...
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
    def override(self, provider: Factory) -> OverridingContext[P]: ...


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
    def set_factories(self, **factories: Factory) -> FactoryAggregate: ...


class BaseSingleton(Provider[T]):
    provided_type = Optional[Type]
    def __init__(self, provides: Optional[_Callable[..., T]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def cls(self) -> T: ...
    @property
    def provides(self) -> T: ...
    def set_provides(self, provides: Optional[_Callable[..., T]]) -> BaseSingleton[T]: ...
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
    def reset(self) -> SingletonResetContext[BS]: ...
    def full_reset(self) -> SingletonFullResetContext[BS]: ...


class Singleton(BaseSingleton[T]): ...


class DelegatedSingleton(Singleton[T]): ...


class ThreadSafeSingleton(Singleton[T]): ...


class DelegatedThreadSafeSingleton(ThreadSafeSingleton[T]): ...


class ThreadLocalSingleton(BaseSingleton[T]): ...


class DelegatedThreadLocalSingleton(ThreadLocalSingleton[T]): ...


class AbstractSingleton(BaseSingleton[T]):
    def override(self, provider: BaseSingleton) -> OverridingContext[P]: ...


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
    def __init__(self, provides: Optional[Type[resources.Resource[T]]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, provides: Optional[Type[resources.AsyncResource[T]]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, provides: Optional[_Callable[..., _Iterator[T]]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, provides: Optional[_Callable[..., _AsyncIterator[T]]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, provides: Optional[_Callable[..., _Coroutine[Injection, Injection, T]]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @overload
    def __init__(self, provides: Optional[_Callable[..., T]] = None, *args: Injection, **kwargs: Injection) -> None: ...
    @property
    def provides(self) -> Optional[_Callable[..., Any]]: ...
    def set_provides(self, provides: Optional[Any]) -> Resource[T]: ...
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
    def __init__(self, container_cls: Type[T], container: Optional[T] = None, **overriding_providers: Union[Provider, Any]) -> None: ...
    def __getattr__(self, name: str) -> Provider: ...
    @property
    def container(self) -> T: ...
    def resolve_provider_name(self, provider: Provider) -> str: ...
    @property
    def parent(self) -> Optional[ProviderParent]: ...
    @property
    def parent_name(self) -> Optional[str]: ...
    def assign_parent(self, parent: ProviderParent) -> None: ...


class Selector(Provider[Any]):
    def __init__(self, selector: Optional[_Callable[..., Any]] = None, **providers: Provider): ...
    def __getattr__(self, name: str) -> Provider: ...

    @property
    def selector(self) -> Optional[_Callable[..., Any]]: ...
    def set_selector(self, selector: Optional[_Callable[..., Any]]) -> Selector: ...

    @property
    def providers(self) -> _Dict[str, Provider]: ...
    def set_providers(self, **providers: Provider) -> Selector: ...


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


class OverridingContext(Generic[T]):
    def __init__(self, overridden: Provider, overriding: Provider): ...
    def __enter__(self) -> T: ...
    def __exit__(self, *_: Any) -> None: ...


class BaseSingletonResetContext(Generic[T]):
    def __init__(self, provider: T): ...
    def __enter__(self) -> T: ...
    def __exit__(self, *_: Any) -> None: ...


class SingletonResetContext(BaseSingletonResetContext):
    ...


class SingletonFullResetContext(BaseSingletonResetContext):
    ...


CHILD_PROVIDERS: Tuple[Provider]


def is_provider(instance: Any) -> bool: ...


def ensure_is_provider(instance: Any) -> Provider: ...


def is_delegated(instance: Any) -> bool: ...


def represent_provider(provider: Provider, provides: Any) -> str: ...


def deepcopy(instance: Any, memo: Optional[_Dict[Any, Any]] = None): Any: ...


def merge_dicts(dict1: _Dict[Any, Any], dict2: _Dict[Any, Any]) -> _Dict[Any, Any]: ...


def traverse(*providers: Provider, types: Optional[_Iterable[Type]]=None) -> _Iterator[Provider]: ...


if yaml:
    class YamlLoader(yaml.SafeLoader): ...
else:
    class YamlLoader: ...

if pydantic:
    PydanticSettings = pydantic.BaseSettings
else:
    PydanticSettings = Any
