from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from oci.core import ComputeClient
from oci.core.models import Instance as OCIInstance

from instancectl.drivers import StorageDriver


@dataclass
class InstanceDetails:
    display_name: str
    state: str


class Provider(ABC):
    @abstractmethod
    def get_instance_details(self, instance_id: str) -> InstanceDetails:
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

    def get_instance_details(self, instance_id: str) -> InstanceDetails:
        oci_instance: OCIInstance = self.compute_client.get_instance(instance_id).data
        return InstanceDetails(display_name=oci_instance.display_name, state=oci_instance.lifecycle_state)

    @staticmethod
    def get_slug() -> str:
        return "oci"


class Instance:

    def __init__(self, provider: Provider, instance_id: str) -> None:
        super().__init__()
        self.provider = provider
        self.id = instance_id

    def get_details(self) -> InstanceDetails:
        return self.provider.get_instance_details(self.id)

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
        self.instances: List[Instance] = []
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

    def add_instance(self, provider: str, instance_id: str):
        self._ensure_init()
        self.instances.append(self.instance_factory.create({"provider": provider, "id": instance_id}))

    def write_to_storage(self):
        self._ensure_init()
        self.driver.persist({
            "instances": [instance.to_dict() for instance in self.instances]
        })

    def load_from_storage(self):
        self._ensure_init()
        try:
            obj: dict = self.driver.restore()
            self.instances = [self.instance_factory.create(instance_obj) for instance_obj in obj.get("instances", [])]
        except FileNotFoundError:
            pass
