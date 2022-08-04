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
@click.option("--provider", "-p", prompt=True)
@click.option("--instance-id", "-i", prompt=True)
@click.pass_context
def add_instance(ctx: Context, provider: str, instance_id: str):
    context = ctx.ensure_object(ClickContextObject)

    context.add_instance(provider, instance_id)
    context.write_to_storage()
    click.echo(f"Added instance {instance_id}")


@instancectl_cmd.command()
@click.pass_context
def list_instances(ctx: Context):
    context = ctx.ensure_object(ClickContextObject)
    for instance in context.instances:
        click.echo(f"{instance.id} ({instance.provider.get_slug()})")


@instancectl_cmd.command()
@click.pass_context
def list_states(ctx: Context):
    context = ctx.ensure_object(ClickContextObject)
    for instance in context.instances:
        details = instance.get_details()
        click.echo(f"{details.display_name}: {details.state}")
