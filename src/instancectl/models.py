from abc import ABC, abstractmethod
from typing import List, Optional, Dict

from oci.core import ComputeClient

from instancectl.drivers import StorageDriver


class Provider(ABC):
    @abstractmethod
    def get_instance_state(self, instance_id: str) -> str:
        pass

    @abstractmethod
    def perform_instance_action(self, instance_id: str, action: str):
        pass

    @staticmethod
    @abstractmethod
    def get_slug() -> str:
        pass


class OCIProvider(Provider):
    def __init__(self, config: dict) -> None:
        super().__init__()
        self.config = config
        self.compute_client = ComputeClient(self.config)

    def get_instance_state(self, instance_id: str) -> str:
        # todo: validate success
        response = self.compute_client.get_instance(instance_id)
        return response.data.lifecycle_state

    def perform_instance_action(self, instance_id: str, action: str):
        # todo: validate success
        self.compute_client.instance_action(instance_id, action)

    @staticmethod
    def get_slug() -> str:
        return "oci"


class Instance:

    def __init__(self, provider: Provider, instance_id: str) -> None:
        super().__init__()
        self.provider = provider
        self.id = instance_id

    def get_state(self) -> str:
        return self.provider.get_instance_state(self.id)

    def perform_action(self, action: str):
        self.provider.perform_instance_action(self.id, action)

    def to_dict(self) -> dict:
        return {
            "provider": self.provider.get_slug(),
            "id": self.id,
        }


class InstanceFactory:

    def __init__(self, providers: List[Provider]) -> None:
        self._providers = {provider.get_slug(): provider for provider in providers}

    def create(self, obj: dict) -> Instance:
        provider = obj["provider"]
        if provider not in self._providers:
            raise ValueError(f"Unknown provider: {provider}")
        return Instance(self._providers[provider], obj["id"])


class ClickContextObject:

    def __init__(self) -> None:
        self.instances: Dict[str, Instance] = {}
        self.driver: Optional[StorageDriver] = None
        self.instance_factory: Optional[InstanceFactory] = None
        self._is_fully_initialized = False

    @property
    def is_fully_initialized(self):
        return self._is_fully_initialized

    def _ensure_init(self):
        if not self._is_fully_initialized:
            raise ValueError("Object not fully initialized! Run late_init first.")

    def init(self, driver: StorageDriver, instance_factory: InstanceFactory):
        self.driver = driver
        self.instance_factory = instance_factory
        self._is_fully_initialized = True

    def add_instance(self, provider: str, instance_id: str, key: str):
        self._ensure_init()
        if key in self.instances:
            raise ValueError("An instance already exists for the given key.")
        instance = self.instance_factory.create({"provider": provider, "id": instance_id})
        self.instances[key] = instance

    def write_to_storage(self):
        self._ensure_init()
        self.driver.persist({
            "instances": {key: instance.to_dict() for key, instance in self.instances.items()}
        })

    def load_from_storage(self):
        self._ensure_init()
        try:
            obj: dict = self.driver.restore()
            self.instances = {key: self.instance_factory.create(instance_obj)
                              for key, instance_obj in obj.get("instances", {}).items()}
        except FileNotFoundError:
            pass
