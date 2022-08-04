import click
from click import Context
from oci.config import from_file as oci_config_from_file

from instancectl.drivers import FileSystemDriver
from instancectl.models import ClickContextObject, InstanceFactory, OCIProvider


@click.group()
@click.pass_context
def instancectl_cmd(ctx: Context):
    driver = FileSystemDriver("~/.instancectl")
    oci_config = oci_config_from_file()
    instance_factory = InstanceFactory([OCIProvider(oci_config)])

    context = ctx.ensure_object(ClickContextObject)
    context.init(driver, instance_factory)
    context.load_from_storage()


@instancectl_cmd.command()
@click.pass_context
@click.option("--provider", "-p", prompt=True)
@click.option("--instance-id", "-i", prompt="Instance ID")
@click.option("--key", "-k", prompt=True)
def add_instance(ctx: Context, provider: str, instance_id: str, key: str):
    context = ctx.ensure_object(ClickContextObject)

    context.add_instance(provider, instance_id, key)
    context.write_to_storage()
    click.echo(f"Added instance {instance_id}")


@instancectl_cmd.command()
@click.pass_context
def list_instances(ctx: Context):
    context = ctx.ensure_object(ClickContextObject)
    for key, instance in context.instances.items():
        click.echo(f"{key} ({instance.provider.get_slug()}, {instance.id})")


@instancectl_cmd.command()
@click.pass_context
def list_states(ctx: Context):
    context = ctx.ensure_object(ClickContextObject)
    for key, instance in context.instances.items():
        click.echo(f"{key}: {instance.get_state()}")


@instancectl_cmd.command()
@click.pass_context
@click.option("--key", "-k", prompt=True)
@click.option("--action", "-a", prompt=True)
def perform_action(ctx: Context, key: str, action: str):
    context = ctx.ensure_object(ClickContextObject)
    if key not in context.instances:
        click.echo("Key not found :(")
        return
    context.instances[key].perform_action(action)
    click.echo(f"Action {action} performed.")
