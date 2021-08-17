'''
# Terraform CDK docker Provider ~> 2.12

This repo builds and publishes the Terraform docker Provider bindings for [cdktf](https://cdk.tf).

Current build targets are:

* npm
* Pypi
* Nuget
* Maven

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform docker Provider version 1:1. In fact, it always tracks `latest` of `~> 2.12` with every release. If there scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform docker Provider](https://github.com/terraform-providers/terraform-provider-docker)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform docker Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

## projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

## cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/terraform-cdk-providers/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

## provider version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import cdktf
import constructs


class Config(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Config",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/config.html docker_config}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        data: builtins.str,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/config.html docker_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: Base64-url-safe-encoded config data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config.html#data Config#data}
        :param name: User-defined name of the config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config.html#name Config#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ConfigConfig(
            data=data,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Config, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @data.setter
    def data(self, value: builtins.str) -> None:
        jsii.set(self, "data", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ConfigConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "data": "data",
        "name": "name",
    },
)
class ConfigConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        data: builtins.str,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param data: Base64-url-safe-encoded config data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config.html#data Config#data}
        :param name: User-defined name of the config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config.html#name Config#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "data": data,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def data(self) -> builtins.str:
        '''Base64-url-safe-encoded config data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config.html#data Config#data}
        '''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''User-defined name of the config.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/config.html#name Config#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Container(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Container",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/container.html docker_container}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        image: builtins.str,
        name: builtins.str,
        attach: typing.Optional[builtins.bool] = None,
        capabilities: typing.Optional[typing.Sequence["ContainerCapabilities"]] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        cpu_set: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        destroy_grace_seconds: typing.Optional[jsii.Number] = None,
        devices: typing.Optional[typing.Sequence["ContainerDevices"]] = None,
        dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_search: typing.Optional[typing.Sequence[builtins.str]] = None,
        domainname: typing.Optional[builtins.str] = None,
        entrypoint: typing.Optional[typing.Sequence[builtins.str]] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        group_add: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional[typing.Sequence["ContainerHealthcheck"]] = None,
        host: typing.Optional[typing.Sequence["ContainerHost"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        init: typing.Optional[builtins.bool] = None,
        ipc_mode: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence["ContainerLabels"]] = None,
        links: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_driver: typing.Optional[builtins.str] = None,
        log_opts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        logs: typing.Optional[builtins.bool] = None,
        max_retry_count: typing.Optional[jsii.Number] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        mounts: typing.Optional[typing.Sequence["ContainerMounts"]] = None,
        must_run: typing.Optional[builtins.bool] = None,
        network_alias: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        networks_advanced: typing.Optional[typing.Sequence["ContainerNetworksAdvanced"]] = None,
        pid_mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ContainerPorts"]] = None,
        privileged: typing.Optional[builtins.bool] = None,
        publish_all_ports: typing.Optional[builtins.bool] = None,
        read_only: typing.Optional[builtins.bool] = None,
        remove_volumes: typing.Optional[builtins.bool] = None,
        restart: typing.Optional[builtins.str] = None,
        rm: typing.Optional[builtins.bool] = None,
        security_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        start: typing.Optional[builtins.bool] = None,
        stdin_open: typing.Optional[builtins.bool] = None,
        storage_opts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        sysctls: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tmpfs: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tty: typing.Optional[builtins.bool] = None,
        ulimit: typing.Optional[typing.Sequence["ContainerUlimit"]] = None,
        upload: typing.Optional[typing.Sequence["ContainerUpload"]] = None,
        user: typing.Optional[builtins.str] = None,
        userns_mode: typing.Optional[builtins.str] = None,
        volumes: typing.Optional[typing.Sequence["ContainerVolumes"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/container.html docker_container} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param image: The ID of the image to back this container. The easiest way to get this value is to use the ``docker_image`` resource as is shown in the example. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#image Container#image}
        :param name: The name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        :param attach: If ``true`` attach to the container after its creation and waits the end of its execution. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#attach Container#attach}
        :param capabilities: capabilities block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#capabilities Container#capabilities}
        :param command: The command to use to start the container. For example, to run ``/usr/bin/myprogram -f baz.conf`` set the command to be ``["/usr/bin/myprogram","-","baz.con"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#command Container#command}
        :param cpu_set: A comma-separated list or hyphen-separated range of CPUs a container can use, e.g. ``0-1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#cpu_set Container#cpu_set}
        :param cpu_shares: CPU shares (relative weight) for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#cpu_shares Container#cpu_shares}
        :param destroy_grace_seconds: If defined will attempt to stop the container before destroying. Container will be destroyed after ``n`` seconds or on successful stop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#destroy_grace_seconds Container#destroy_grace_seconds}
        :param devices: devices block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#devices Container#devices}
        :param dns: DNS servers to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns Container#dns}
        :param dns_opts: DNS options used by the DNS provider(s), see ``resolv.conf`` documentation for valid list of options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns_opts Container#dns_opts}
        :param dns_search: DNS search domains that are used when bare unqualified hostnames are used inside of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns_search Container#dns_search}
        :param domainname: Domain name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#domainname Container#domainname}
        :param entrypoint: The command to use as the Entrypoint for the container. The Entrypoint allows you to configure a container to run as an executable. For example, to run ``/usr/bin/myprogram`` when starting a container, set the entrypoint to be ``"/usr/bin/myprogra"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#entrypoint Container#entrypoint}
        :param env: Environment variables to set in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#env Container#env}
        :param group_add: Additional groups for the container user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#group_add Container#group_add}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#healthcheck Container#healthcheck}
        :param host: host block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host Container#host}
        :param hostname: Hostname of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#hostname Container#hostname}
        :param init: Configured whether an init process should be injected for this container. If unset this will default to the ``dockerd`` defaults. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#init Container#init}
        :param ipc_mode: IPC sharing mode for the container. Possible values are: ``none``, ``private``, ``shareable``, ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipc_mode Container#ipc_mode}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#labels Container#labels}
        :param links: Set of links for link based connectivity between containers that are running on the same host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#links Container#links}
        :param log_driver: The logging driver to use for the container. Defaults to ``json-file``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#log_driver Container#log_driver}
        :param log_opts: Key/value pairs to use as options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#log_opts Container#log_opts}
        :param logs: Save the container logs (``attach`` must be enabled). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#logs Container#logs}
        :param max_retry_count: The maximum amount of times to an attempt a restart when ``restart`` is set to 'on-failure'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#max_retry_count Container#max_retry_count}
        :param memory: The memory limit for the container in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#memory Container#memory}
        :param memory_swap: The total memory limit (memory + swap) for the container in MBs. This setting may compute to ``-1`` after ``terraform apply`` if the target host doesn't support memory swap, when that is the case docker will use a soft limitation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#memory_swap Container#memory_swap}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#mounts Container#mounts}
        :param must_run: If ``true``, then the Docker container will be kept running. If ``false``, then as long as the container exists, Terraform assumes it is successful. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#must_run Container#must_run}
        :param network_alias: Set an alias for the container in all specified networks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#network_alias Container#network_alias}
        :param network_mode: Network mode of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#network_mode Container#network_mode}
        :param networks: ID of the networks in which the container is. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#networks Container#networks}
        :param networks_advanced: networks_advanced block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#networks_advanced Container#networks_advanced}
        :param pid_mode: he PID (Process) Namespace mode for the container. Either ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#pid_mode Container#pid_mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ports Container#ports}
        :param privileged: If ``true``, the container runs in privileged mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#privileged Container#privileged}
        :param publish_all_ports: Publish all ports of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#publish_all_ports Container#publish_all_ports}
        :param read_only: If ``true``, the container will be started as readonly. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        :param remove_volumes: If ``true``, it will remove anonymous volumes associated with the container. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#remove_volumes Container#remove_volumes}
        :param restart: The restart policy for the container. Must be one of 'no', 'on-failure', 'always', 'unless-stopped'. Defaults to ``no``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#restart Container#restart}
        :param rm: If ``true``, then the container will be automatically removed after his execution. Terraform won't check this container after creation. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#rm Container#rm}
        :param security_opts: List of string values to customize labels for MLS systems, such as SELinux. See https://docs.docker.com/engine/reference/run/#security-configuration. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#security_opts Container#security_opts}
        :param shm_size: Size of ``/dev/shm`` in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#shm_size Container#shm_size}
        :param start: If ``true``, then the Docker container will be started after creation. If ``false``, then the container is only created. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#start Container#start}
        :param stdin_open: If ``true``, keep STDIN open even if not attached (``docker run -i``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#stdin_open Container#stdin_open}
        :param storage_opts: Key/value pairs for the storage driver options, e.g. ``size``: ``120G``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#storage_opts Container#storage_opts}
        :param sysctls: A map of kernel parameters (sysctls) to set in the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#sysctls Container#sysctls}
        :param tmpfs: A map of container directories which should be replaced by ``tmpfs mounts``, and their corresponding mount options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tmpfs Container#tmpfs}
        :param tty: If ``true``, allocate a pseudo-tty (``docker run -t``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tty Container#tty}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ulimit Container#ulimit}
        :param upload: upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#upload Container#upload}
        :param user: User used for run the first process. Format is ``user`` or ``user:group`` which user and group can be passed literraly or by name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#user Container#user}
        :param userns_mode: Sets the usernamespace mode for the container when usernamespace remapping option is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#userns_mode Container#userns_mode}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volumes Container#volumes}
        :param working_dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#working_dir Container#working_dir}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ContainerConfig(
            image=image,
            name=name,
            attach=attach,
            capabilities=capabilities,
            command=command,
            cpu_set=cpu_set,
            cpu_shares=cpu_shares,
            destroy_grace_seconds=destroy_grace_seconds,
            devices=devices,
            dns=dns,
            dns_opts=dns_opts,
            dns_search=dns_search,
            domainname=domainname,
            entrypoint=entrypoint,
            env=env,
            group_add=group_add,
            healthcheck=healthcheck,
            host=host,
            hostname=hostname,
            init=init,
            ipc_mode=ipc_mode,
            labels=labels,
            links=links,
            log_driver=log_driver,
            log_opts=log_opts,
            logs=logs,
            max_retry_count=max_retry_count,
            memory=memory,
            memory_swap=memory_swap,
            mounts=mounts,
            must_run=must_run,
            network_alias=network_alias,
            network_mode=network_mode,
            networks=networks,
            networks_advanced=networks_advanced,
            pid_mode=pid_mode,
            ports=ports,
            privileged=privileged,
            publish_all_ports=publish_all_ports,
            read_only=read_only,
            remove_volumes=remove_volumes,
            restart=restart,
            rm=rm,
            security_opts=security_opts,
            shm_size=shm_size,
            start=start,
            stdin_open=stdin_open,
            storage_opts=storage_opts,
            sysctls=sysctls,
            tmpfs=tmpfs,
            tty=tty,
            ulimit=ulimit,
            upload=upload,
            user=user,
            userns_mode=userns_mode,
            volumes=volumes,
            working_dir=working_dir,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Container, self, [scope, id, config])

    @jsii.member(jsii_name="networkData")
    def network_data(self, index: builtins.str) -> "ContainerNetworkData":
        '''
        :param index: -
        '''
        return typing.cast("ContainerNetworkData", jsii.invoke(self, "networkData", [index]))

    @jsii.member(jsii_name="resetAttach")
    def reset_attach(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttach", []))

    @jsii.member(jsii_name="resetCapabilities")
    def reset_capabilities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCapabilities", []))

    @jsii.member(jsii_name="resetCommand")
    def reset_command(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommand", []))

    @jsii.member(jsii_name="resetCpuSet")
    def reset_cpu_set(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuSet", []))

    @jsii.member(jsii_name="resetCpuShares")
    def reset_cpu_shares(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCpuShares", []))

    @jsii.member(jsii_name="resetDestroyGraceSeconds")
    def reset_destroy_grace_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDestroyGraceSeconds", []))

    @jsii.member(jsii_name="resetDevices")
    def reset_devices(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDevices", []))

    @jsii.member(jsii_name="resetDns")
    def reset_dns(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDns", []))

    @jsii.member(jsii_name="resetDnsOpts")
    def reset_dns_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsOpts", []))

    @jsii.member(jsii_name="resetDnsSearch")
    def reset_dns_search(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsSearch", []))

    @jsii.member(jsii_name="resetDomainname")
    def reset_domainname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainname", []))

    @jsii.member(jsii_name="resetEntrypoint")
    def reset_entrypoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEntrypoint", []))

    @jsii.member(jsii_name="resetEnv")
    def reset_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnv", []))

    @jsii.member(jsii_name="resetGroupAdd")
    def reset_group_add(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupAdd", []))

    @jsii.member(jsii_name="resetHealthcheck")
    def reset_healthcheck(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthcheck", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetHostname")
    def reset_hostname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHostname", []))

    @jsii.member(jsii_name="resetInit")
    def reset_init(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInit", []))

    @jsii.member(jsii_name="resetIpcMode")
    def reset_ipc_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpcMode", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetLinks")
    def reset_links(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLinks", []))

    @jsii.member(jsii_name="resetLogDriver")
    def reset_log_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogDriver", []))

    @jsii.member(jsii_name="resetLogOpts")
    def reset_log_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogOpts", []))

    @jsii.member(jsii_name="resetLogs")
    def reset_logs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogs", []))

    @jsii.member(jsii_name="resetMaxRetryCount")
    def reset_max_retry_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxRetryCount", []))

    @jsii.member(jsii_name="resetMemory")
    def reset_memory(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemory", []))

    @jsii.member(jsii_name="resetMemorySwap")
    def reset_memory_swap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMemorySwap", []))

    @jsii.member(jsii_name="resetMounts")
    def reset_mounts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMounts", []))

    @jsii.member(jsii_name="resetMustRun")
    def reset_must_run(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMustRun", []))

    @jsii.member(jsii_name="resetNetworkAlias")
    def reset_network_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkAlias", []))

    @jsii.member(jsii_name="resetNetworkMode")
    def reset_network_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkMode", []))

    @jsii.member(jsii_name="resetNetworks")
    def reset_networks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworks", []))

    @jsii.member(jsii_name="resetNetworksAdvanced")
    def reset_networks_advanced(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworksAdvanced", []))

    @jsii.member(jsii_name="resetPidMode")
    def reset_pid_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPidMode", []))

    @jsii.member(jsii_name="resetPorts")
    def reset_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPorts", []))

    @jsii.member(jsii_name="resetPrivileged")
    def reset_privileged(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivileged", []))

    @jsii.member(jsii_name="resetPublishAllPorts")
    def reset_publish_all_ports(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublishAllPorts", []))

    @jsii.member(jsii_name="resetReadOnly")
    def reset_read_only(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnly", []))

    @jsii.member(jsii_name="resetRemoveVolumes")
    def reset_remove_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRemoveVolumes", []))

    @jsii.member(jsii_name="resetRestart")
    def reset_restart(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestart", []))

    @jsii.member(jsii_name="resetRm")
    def reset_rm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRm", []))

    @jsii.member(jsii_name="resetSecurityOpts")
    def reset_security_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurityOpts", []))

    @jsii.member(jsii_name="resetShmSize")
    def reset_shm_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShmSize", []))

    @jsii.member(jsii_name="resetStart")
    def reset_start(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStart", []))

    @jsii.member(jsii_name="resetStdinOpen")
    def reset_stdin_open(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStdinOpen", []))

    @jsii.member(jsii_name="resetStorageOpts")
    def reset_storage_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageOpts", []))

    @jsii.member(jsii_name="resetSysctls")
    def reset_sysctls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSysctls", []))

    @jsii.member(jsii_name="resetTmpfs")
    def reset_tmpfs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTmpfs", []))

    @jsii.member(jsii_name="resetTty")
    def reset_tty(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTty", []))

    @jsii.member(jsii_name="resetUlimit")
    def reset_ulimit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUlimit", []))

    @jsii.member(jsii_name="resetUpload")
    def reset_upload(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpload", []))

    @jsii.member(jsii_name="resetUser")
    def reset_user(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUser", []))

    @jsii.member(jsii_name="resetUsernsMode")
    def reset_userns_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsernsMode", []))

    @jsii.member(jsii_name="resetVolumes")
    def reset_volumes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVolumes", []))

    @jsii.member(jsii_name="resetWorkingDir")
    def reset_working_dir(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkingDir", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="bridge")
    def bridge(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bridge"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="containerLogs")
    def container_logs(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerLogs"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="exitCode")
    def exit_code(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "exitCode"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "imageInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipPrefixLength")
    def ip_prefix_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipPrefixLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachInput")
    def attach_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "attachInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilitiesInput")
    def capabilities_input(
        self,
    ) -> typing.Optional[typing.List["ContainerCapabilities"]]:
        return typing.cast(typing.Optional[typing.List["ContainerCapabilities"]], jsii.get(self, "capabilitiesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commandInput")
    def command_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "commandInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSetInput")
    def cpu_set_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cpuSetInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSharesInput")
    def cpu_shares_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cpuSharesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroyGraceSecondsInput")
    def destroy_grace_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "destroyGraceSecondsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="devicesInput")
    def devices_input(self) -> typing.Optional[typing.List["ContainerDevices"]]:
        return typing.cast(typing.Optional[typing.List["ContainerDevices"]], jsii.get(self, "devicesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsInput")
    def dns_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsOptsInput")
    def dns_opts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsSearchInput")
    def dns_search_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsSearchInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainnameInput")
    def domainname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "domainnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entrypointInput")
    def entrypoint_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "entrypointInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envInput")
    def env_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "envInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupAddInput")
    def group_add_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "groupAddInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheckInput")
    def healthcheck_input(self) -> typing.Optional[typing.List["ContainerHealthcheck"]]:
        return typing.cast(typing.Optional[typing.List["ContainerHealthcheck"]], jsii.get(self, "healthcheckInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[typing.List["ContainerHost"]]:
        return typing.cast(typing.Optional[typing.List["ContainerHost"]], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="initInput")
    def init_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "initInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipcModeInput")
    def ipc_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipcModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["ContainerLabels"]]:
        return typing.cast(typing.Optional[typing.List["ContainerLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="linksInput")
    def links_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "linksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDriverInput")
    def log_driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logDriverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logOptsInput")
    def log_opts_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "logOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logsInput")
    def logs_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "logsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetryCountInput")
    def max_retry_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxRetryCountInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memoryInput")
    def memory_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memoryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySwapInput")
    def memory_swap_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "memorySwapInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountsInput")
    def mounts_input(self) -> typing.Optional[typing.List["ContainerMounts"]]:
        return typing.cast(typing.Optional[typing.List["ContainerMounts"]], jsii.get(self, "mountsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mustRunInput")
    def must_run_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "mustRunInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkAliasInput")
    def network_alias_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networkAliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkModeInput")
    def network_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksAdvancedInput")
    def networks_advanced_input(
        self,
    ) -> typing.Optional[typing.List["ContainerNetworksAdvanced"]]:
        return typing.cast(typing.Optional[typing.List["ContainerNetworksAdvanced"]], jsii.get(self, "networksAdvancedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksInput")
    def networks_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "networksInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pidModeInput")
    def pid_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pidModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="portsInput")
    def ports_input(self) -> typing.Optional[typing.List["ContainerPorts"]]:
        return typing.cast(typing.Optional[typing.List["ContainerPorts"]], jsii.get(self, "portsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privilegedInput")
    def privileged_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "privilegedInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishAllPortsInput")
    def publish_all_ports_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "publishAllPortsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnlyInput")
    def read_only_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "readOnlyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removeVolumesInput")
    def remove_volumes_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "removeVolumesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restartInput")
    def restart_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "restartInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rmInput")
    def rm_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "rmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityOptsInput")
    def security_opts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "securityOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shmSizeInput")
    def shm_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "shmSizeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="startInput")
    def start_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "startInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stdinOpenInput")
    def stdin_open_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "stdinOpenInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageOptsInput")
    def storage_opts_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "storageOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sysctlsInput")
    def sysctls_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "sysctlsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tmpfsInput")
    def tmpfs_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tmpfsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ttyInput")
    def tty_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "ttyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ulimitInput")
    def ulimit_input(self) -> typing.Optional[typing.List["ContainerUlimit"]]:
        return typing.cast(typing.Optional[typing.List["ContainerUlimit"]], jsii.get(self, "ulimitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uploadInput")
    def upload_input(self) -> typing.Optional[typing.List["ContainerUpload"]]:
        return typing.cast(typing.Optional[typing.List["ContainerUpload"]], jsii.get(self, "uploadInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="userInput")
    def user_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernsModeInput")
    def userns_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernsModeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumesInput")
    def volumes_input(self) -> typing.Optional[typing.List["ContainerVolumes"]]:
        return typing.cast(typing.Optional[typing.List["ContainerVolumes"]], jsii.get(self, "volumesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDirInput")
    def working_dir_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "workingDirInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attach")
    def attach(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "attach"))

    @attach.setter
    def attach(self, value: builtins.bool) -> None:
        jsii.set(self, "attach", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="capabilities")
    def capabilities(self) -> typing.List["ContainerCapabilities"]:
        return typing.cast(typing.List["ContainerCapabilities"], jsii.get(self, "capabilities"))

    @capabilities.setter
    def capabilities(self, value: typing.List["ContainerCapabilities"]) -> None:
        jsii.set(self, "capabilities", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="command")
    def command(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "command"))

    @command.setter
    def command(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "command", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuSet")
    def cpu_set(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cpuSet"))

    @cpu_set.setter
    def cpu_set(self, value: builtins.str) -> None:
        jsii.set(self, "cpuSet", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="cpuShares")
    def cpu_shares(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpuShares"))

    @cpu_shares.setter
    def cpu_shares(self, value: jsii.Number) -> None:
        jsii.set(self, "cpuShares", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="destroyGraceSeconds")
    def destroy_grace_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "destroyGraceSeconds"))

    @destroy_grace_seconds.setter
    def destroy_grace_seconds(self, value: jsii.Number) -> None:
        jsii.set(self, "destroyGraceSeconds", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="devices")
    def devices(self) -> typing.List["ContainerDevices"]:
        return typing.cast(typing.List["ContainerDevices"], jsii.get(self, "devices"))

    @devices.setter
    def devices(self, value: typing.List["ContainerDevices"]) -> None:
        jsii.set(self, "devices", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dns")
    def dns(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dns"))

    @dns.setter
    def dns(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dns", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsOpts")
    def dns_opts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsOpts"))

    @dns_opts.setter
    def dns_opts(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsSearch")
    def dns_search(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsSearch"))

    @dns_search.setter
    def dns_search(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsSearch", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="domainname")
    def domainname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "domainname"))

    @domainname.setter
    def domainname(self, value: builtins.str) -> None:
        jsii.set(self, "domainname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="entrypoint")
    def entrypoint(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "entrypoint"))

    @entrypoint.setter
    def entrypoint(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "entrypoint", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "env"))

    @env.setter
    def env(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "env", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="groupAdd")
    def group_add(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "groupAdd"))

    @group_add.setter
    def group_add(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "groupAdd", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="healthcheck")
    def healthcheck(self) -> typing.List["ContainerHealthcheck"]:
        return typing.cast(typing.List["ContainerHealthcheck"], jsii.get(self, "healthcheck"))

    @healthcheck.setter
    def healthcheck(self, value: typing.List["ContainerHealthcheck"]) -> None:
        jsii.set(self, "healthcheck", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> typing.List["ContainerHost"]:
        return typing.cast(typing.List["ContainerHost"], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.List["ContainerHost"]) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        jsii.set(self, "hostname", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        jsii.set(self, "image", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="init")
    def init(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "init"))

    @init.setter
    def init(self, value: builtins.bool) -> None:
        jsii.set(self, "init", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipcMode")
    def ipc_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipcMode"))

    @ipc_mode.setter
    def ipc_mode(self, value: builtins.str) -> None:
        jsii.set(self, "ipcMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["ContainerLabels"]:
        return typing.cast(typing.List["ContainerLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["ContainerLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="links")
    def links(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "links"))

    @links.setter
    def links(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "links", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logDriver")
    def log_driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logDriver"))

    @log_driver.setter
    def log_driver(self, value: builtins.str) -> None:
        jsii.set(self, "logDriver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logOpts")
    def log_opts(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "logOpts"))

    @log_opts.setter
    def log_opts(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "logOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="logs")
    def logs(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "logs"))

    @logs.setter
    def logs(self, value: builtins.bool) -> None:
        jsii.set(self, "logs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="maxRetryCount")
    def max_retry_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxRetryCount"))

    @max_retry_count.setter
    def max_retry_count(self, value: jsii.Number) -> None:
        jsii.set(self, "maxRetryCount", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @memory.setter
    def memory(self, value: jsii.Number) -> None:
        jsii.set(self, "memory", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="memorySwap")
    def memory_swap(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memorySwap"))

    @memory_swap.setter
    def memory_swap(self, value: jsii.Number) -> None:
        jsii.set(self, "memorySwap", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mounts")
    def mounts(self) -> typing.List["ContainerMounts"]:
        return typing.cast(typing.List["ContainerMounts"], jsii.get(self, "mounts"))

    @mounts.setter
    def mounts(self, value: typing.List["ContainerMounts"]) -> None:
        jsii.set(self, "mounts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mustRun")
    def must_run(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "mustRun"))

    @must_run.setter
    def must_run(self, value: builtins.bool) -> None:
        jsii.set(self, "mustRun", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkAlias")
    def network_alias(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networkAlias"))

    @network_alias.setter
    def network_alias(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "networkAlias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkMode")
    def network_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkMode"))

    @network_mode.setter
    def network_mode(self, value: builtins.str) -> None:
        jsii.set(self, "networkMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networks")
    def networks(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "networks"))

    @networks.setter
    def networks(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "networks", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networksAdvanced")
    def networks_advanced(self) -> typing.List["ContainerNetworksAdvanced"]:
        return typing.cast(typing.List["ContainerNetworksAdvanced"], jsii.get(self, "networksAdvanced"))

    @networks_advanced.setter
    def networks_advanced(
        self,
        value: typing.List["ContainerNetworksAdvanced"],
    ) -> None:
        jsii.set(self, "networksAdvanced", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pidMode")
    def pid_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pidMode"))

    @pid_mode.setter
    def pid_mode(self, value: builtins.str) -> None:
        jsii.set(self, "pidMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ports")
    def ports(self) -> typing.List["ContainerPorts"]:
        return typing.cast(typing.List["ContainerPorts"], jsii.get(self, "ports"))

    @ports.setter
    def ports(self, value: typing.List["ContainerPorts"]) -> None:
        jsii.set(self, "ports", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privileged")
    def privileged(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "privileged"))

    @privileged.setter
    def privileged(self, value: builtins.bool) -> None:
        jsii.set(self, "privileged", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publishAllPorts")
    def publish_all_ports(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "publishAllPorts"))

    @publish_all_ports.setter
    def publish_all_ports(self, value: builtins.bool) -> None:
        jsii.set(self, "publishAllPorts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readOnly")
    def read_only(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "readOnly"))

    @read_only.setter
    def read_only(self, value: builtins.bool) -> None:
        jsii.set(self, "readOnly", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="removeVolumes")
    def remove_volumes(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "removeVolumes"))

    @remove_volumes.setter
    def remove_volumes(self, value: builtins.bool) -> None:
        jsii.set(self, "removeVolumes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="restart")
    def restart(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "restart"))

    @restart.setter
    def restart(self, value: builtins.str) -> None:
        jsii.set(self, "restart", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rm")
    def rm(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "rm"))

    @rm.setter
    def rm(self, value: builtins.bool) -> None:
        jsii.set(self, "rm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="securityOpts")
    def security_opts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "securityOpts"))

    @security_opts.setter
    def security_opts(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "securityOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="shmSize")
    def shm_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "shmSize"))

    @shm_size.setter
    def shm_size(self, value: jsii.Number) -> None:
        jsii.set(self, "shmSize", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="start")
    def start(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "start"))

    @start.setter
    def start(self, value: builtins.bool) -> None:
        jsii.set(self, "start", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="stdinOpen")
    def stdin_open(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "stdinOpen"))

    @stdin_open.setter
    def stdin_open(self, value: builtins.bool) -> None:
        jsii.set(self, "stdinOpen", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="storageOpts")
    def storage_opts(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "storageOpts"))

    @storage_opts.setter
    def storage_opts(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "storageOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sysctls")
    def sysctls(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "sysctls"))

    @sysctls.setter
    def sysctls(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "sysctls", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tmpfs")
    def tmpfs(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tmpfs"))

    @tmpfs.setter
    def tmpfs(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "tmpfs", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="tty")
    def tty(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "tty"))

    @tty.setter
    def tty(self, value: builtins.bool) -> None:
        jsii.set(self, "tty", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ulimit")
    def ulimit(self) -> typing.List["ContainerUlimit"]:
        return typing.cast(typing.List["ContainerUlimit"], jsii.get(self, "ulimit"))

    @ulimit.setter
    def ulimit(self, value: typing.List["ContainerUlimit"]) -> None:
        jsii.set(self, "ulimit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="upload")
    def upload(self) -> typing.List["ContainerUpload"]:
        return typing.cast(typing.List["ContainerUpload"], jsii.get(self, "upload"))

    @upload.setter
    def upload(self, value: typing.List["ContainerUpload"]) -> None:
        jsii.set(self, "upload", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="user")
    def user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "user"))

    @user.setter
    def user(self, value: builtins.str) -> None:
        jsii.set(self, "user", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="usernsMode")
    def userns_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "usernsMode"))

    @userns_mode.setter
    def userns_mode(self, value: builtins.str) -> None:
        jsii.set(self, "usernsMode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="volumes")
    def volumes(self) -> typing.List["ContainerVolumes"]:
        return typing.cast(typing.List["ContainerVolumes"], jsii.get(self, "volumes"))

    @volumes.setter
    def volumes(self, value: typing.List["ContainerVolumes"]) -> None:
        jsii.set(self, "volumes", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="workingDir")
    def working_dir(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "workingDir"))

    @working_dir.setter
    def working_dir(self, value: builtins.str) -> None:
        jsii.set(self, "workingDir", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerCapabilities",
    jsii_struct_bases=[],
    name_mapping={"add": "add", "drop": "drop"},
)
class ContainerCapabilities:
    def __init__(
        self,
        *,
        add: typing.Optional[typing.Sequence[builtins.str]] = None,
        drop: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param add: List of linux capabilities to add. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#add Container#add}
        :param drop: List of linux capabilities to drop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#drop Container#drop}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if add is not None:
            self._values["add"] = add
        if drop is not None:
            self._values["drop"] = drop

    @builtins.property
    def add(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of linux capabilities to add.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#add Container#add}
        '''
        result = self._values.get("add")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def drop(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of linux capabilities to drop.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#drop Container#drop}
        '''
        result = self._values.get("drop")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerCapabilities(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "image": "image",
        "name": "name",
        "attach": "attach",
        "capabilities": "capabilities",
        "command": "command",
        "cpu_set": "cpuSet",
        "cpu_shares": "cpuShares",
        "destroy_grace_seconds": "destroyGraceSeconds",
        "devices": "devices",
        "dns": "dns",
        "dns_opts": "dnsOpts",
        "dns_search": "dnsSearch",
        "domainname": "domainname",
        "entrypoint": "entrypoint",
        "env": "env",
        "group_add": "groupAdd",
        "healthcheck": "healthcheck",
        "host": "host",
        "hostname": "hostname",
        "init": "init",
        "ipc_mode": "ipcMode",
        "labels": "labels",
        "links": "links",
        "log_driver": "logDriver",
        "log_opts": "logOpts",
        "logs": "logs",
        "max_retry_count": "maxRetryCount",
        "memory": "memory",
        "memory_swap": "memorySwap",
        "mounts": "mounts",
        "must_run": "mustRun",
        "network_alias": "networkAlias",
        "network_mode": "networkMode",
        "networks": "networks",
        "networks_advanced": "networksAdvanced",
        "pid_mode": "pidMode",
        "ports": "ports",
        "privileged": "privileged",
        "publish_all_ports": "publishAllPorts",
        "read_only": "readOnly",
        "remove_volumes": "removeVolumes",
        "restart": "restart",
        "rm": "rm",
        "security_opts": "securityOpts",
        "shm_size": "shmSize",
        "start": "start",
        "stdin_open": "stdinOpen",
        "storage_opts": "storageOpts",
        "sysctls": "sysctls",
        "tmpfs": "tmpfs",
        "tty": "tty",
        "ulimit": "ulimit",
        "upload": "upload",
        "user": "user",
        "userns_mode": "usernsMode",
        "volumes": "volumes",
        "working_dir": "workingDir",
    },
)
class ContainerConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        image: builtins.str,
        name: builtins.str,
        attach: typing.Optional[builtins.bool] = None,
        capabilities: typing.Optional[typing.Sequence[ContainerCapabilities]] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        cpu_set: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        destroy_grace_seconds: typing.Optional[jsii.Number] = None,
        devices: typing.Optional[typing.Sequence["ContainerDevices"]] = None,
        dns: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        dns_search: typing.Optional[typing.Sequence[builtins.str]] = None,
        domainname: typing.Optional[builtins.str] = None,
        entrypoint: typing.Optional[typing.Sequence[builtins.str]] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        group_add: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional[typing.Sequence["ContainerHealthcheck"]] = None,
        host: typing.Optional[typing.Sequence["ContainerHost"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        init: typing.Optional[builtins.bool] = None,
        ipc_mode: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence["ContainerLabels"]] = None,
        links: typing.Optional[typing.Sequence[builtins.str]] = None,
        log_driver: typing.Optional[builtins.str] = None,
        log_opts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        logs: typing.Optional[builtins.bool] = None,
        max_retry_count: typing.Optional[jsii.Number] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        mounts: typing.Optional[typing.Sequence["ContainerMounts"]] = None,
        must_run: typing.Optional[builtins.bool] = None,
        network_alias: typing.Optional[typing.Sequence[builtins.str]] = None,
        network_mode: typing.Optional[builtins.str] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        networks_advanced: typing.Optional[typing.Sequence["ContainerNetworksAdvanced"]] = None,
        pid_mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ContainerPorts"]] = None,
        privileged: typing.Optional[builtins.bool] = None,
        publish_all_ports: typing.Optional[builtins.bool] = None,
        read_only: typing.Optional[builtins.bool] = None,
        remove_volumes: typing.Optional[builtins.bool] = None,
        restart: typing.Optional[builtins.str] = None,
        rm: typing.Optional[builtins.bool] = None,
        security_opts: typing.Optional[typing.Sequence[builtins.str]] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        start: typing.Optional[builtins.bool] = None,
        stdin_open: typing.Optional[builtins.bool] = None,
        storage_opts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        sysctls: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tmpfs: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        tty: typing.Optional[builtins.bool] = None,
        ulimit: typing.Optional[typing.Sequence["ContainerUlimit"]] = None,
        upload: typing.Optional[typing.Sequence["ContainerUpload"]] = None,
        user: typing.Optional[builtins.str] = None,
        userns_mode: typing.Optional[builtins.str] = None,
        volumes: typing.Optional[typing.Sequence["ContainerVolumes"]] = None,
        working_dir: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param image: The ID of the image to back this container. The easiest way to get this value is to use the ``docker_image`` resource as is shown in the example. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#image Container#image}
        :param name: The name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        :param attach: If ``true`` attach to the container after its creation and waits the end of its execution. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#attach Container#attach}
        :param capabilities: capabilities block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#capabilities Container#capabilities}
        :param command: The command to use to start the container. For example, to run ``/usr/bin/myprogram -f baz.conf`` set the command to be ``["/usr/bin/myprogram","-","baz.con"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#command Container#command}
        :param cpu_set: A comma-separated list or hyphen-separated range of CPUs a container can use, e.g. ``0-1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#cpu_set Container#cpu_set}
        :param cpu_shares: CPU shares (relative weight) for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#cpu_shares Container#cpu_shares}
        :param destroy_grace_seconds: If defined will attempt to stop the container before destroying. Container will be destroyed after ``n`` seconds or on successful stop. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#destroy_grace_seconds Container#destroy_grace_seconds}
        :param devices: devices block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#devices Container#devices}
        :param dns: DNS servers to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns Container#dns}
        :param dns_opts: DNS options used by the DNS provider(s), see ``resolv.conf`` documentation for valid list of options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns_opts Container#dns_opts}
        :param dns_search: DNS search domains that are used when bare unqualified hostnames are used inside of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns_search Container#dns_search}
        :param domainname: Domain name of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#domainname Container#domainname}
        :param entrypoint: The command to use as the Entrypoint for the container. The Entrypoint allows you to configure a container to run as an executable. For example, to run ``/usr/bin/myprogram`` when starting a container, set the entrypoint to be ``"/usr/bin/myprogra"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#entrypoint Container#entrypoint}
        :param env: Environment variables to set in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#env Container#env}
        :param group_add: Additional groups for the container user. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#group_add Container#group_add}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#healthcheck Container#healthcheck}
        :param host: host block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host Container#host}
        :param hostname: Hostname of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#hostname Container#hostname}
        :param init: Configured whether an init process should be injected for this container. If unset this will default to the ``dockerd`` defaults. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#init Container#init}
        :param ipc_mode: IPC sharing mode for the container. Possible values are: ``none``, ``private``, ``shareable``, ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipc_mode Container#ipc_mode}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#labels Container#labels}
        :param links: Set of links for link based connectivity between containers that are running on the same host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#links Container#links}
        :param log_driver: The logging driver to use for the container. Defaults to ``json-file``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#log_driver Container#log_driver}
        :param log_opts: Key/value pairs to use as options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#log_opts Container#log_opts}
        :param logs: Save the container logs (``attach`` must be enabled). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#logs Container#logs}
        :param max_retry_count: The maximum amount of times to an attempt a restart when ``restart`` is set to 'on-failure'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#max_retry_count Container#max_retry_count}
        :param memory: The memory limit for the container in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#memory Container#memory}
        :param memory_swap: The total memory limit (memory + swap) for the container in MBs. This setting may compute to ``-1`` after ``terraform apply`` if the target host doesn't support memory swap, when that is the case docker will use a soft limitation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#memory_swap Container#memory_swap}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#mounts Container#mounts}
        :param must_run: If ``true``, then the Docker container will be kept running. If ``false``, then as long as the container exists, Terraform assumes it is successful. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#must_run Container#must_run}
        :param network_alias: Set an alias for the container in all specified networks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#network_alias Container#network_alias}
        :param network_mode: Network mode of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#network_mode Container#network_mode}
        :param networks: ID of the networks in which the container is. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#networks Container#networks}
        :param networks_advanced: networks_advanced block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#networks_advanced Container#networks_advanced}
        :param pid_mode: he PID (Process) Namespace mode for the container. Either ``container:<name|id>`` or ``host``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#pid_mode Container#pid_mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ports Container#ports}
        :param privileged: If ``true``, the container runs in privileged mode. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#privileged Container#privileged}
        :param publish_all_ports: Publish all ports of the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#publish_all_ports Container#publish_all_ports}
        :param read_only: If ``true``, the container will be started as readonly. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        :param remove_volumes: If ``true``, it will remove anonymous volumes associated with the container. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#remove_volumes Container#remove_volumes}
        :param restart: The restart policy for the container. Must be one of 'no', 'on-failure', 'always', 'unless-stopped'. Defaults to ``no``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#restart Container#restart}
        :param rm: If ``true``, then the container will be automatically removed after his execution. Terraform won't check this container after creation. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#rm Container#rm}
        :param security_opts: List of string values to customize labels for MLS systems, such as SELinux. See https://docs.docker.com/engine/reference/run/#security-configuration. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#security_opts Container#security_opts}
        :param shm_size: Size of ``/dev/shm`` in MBs. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#shm_size Container#shm_size}
        :param start: If ``true``, then the Docker container will be started after creation. If ``false``, then the container is only created. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#start Container#start}
        :param stdin_open: If ``true``, keep STDIN open even if not attached (``docker run -i``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#stdin_open Container#stdin_open}
        :param storage_opts: Key/value pairs for the storage driver options, e.g. ``size``: ``120G``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#storage_opts Container#storage_opts}
        :param sysctls: A map of kernel parameters (sysctls) to set in the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#sysctls Container#sysctls}
        :param tmpfs: A map of container directories which should be replaced by ``tmpfs mounts``, and their corresponding mount options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tmpfs Container#tmpfs}
        :param tty: If ``true``, allocate a pseudo-tty (``docker run -t``). Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tty Container#tty}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ulimit Container#ulimit}
        :param upload: upload block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#upload Container#upload}
        :param user: User used for run the first process. Format is ``user`` or ``user:group`` which user and group can be passed literraly or by name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#user Container#user}
        :param userns_mode: Sets the usernamespace mode for the container when usernamespace remapping option is enabled. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#userns_mode Container#userns_mode}
        :param volumes: volumes block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volumes Container#volumes}
        :param working_dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#working_dir Container#working_dir}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if attach is not None:
            self._values["attach"] = attach
        if capabilities is not None:
            self._values["capabilities"] = capabilities
        if command is not None:
            self._values["command"] = command
        if cpu_set is not None:
            self._values["cpu_set"] = cpu_set
        if cpu_shares is not None:
            self._values["cpu_shares"] = cpu_shares
        if destroy_grace_seconds is not None:
            self._values["destroy_grace_seconds"] = destroy_grace_seconds
        if devices is not None:
            self._values["devices"] = devices
        if dns is not None:
            self._values["dns"] = dns
        if dns_opts is not None:
            self._values["dns_opts"] = dns_opts
        if dns_search is not None:
            self._values["dns_search"] = dns_search
        if domainname is not None:
            self._values["domainname"] = domainname
        if entrypoint is not None:
            self._values["entrypoint"] = entrypoint
        if env is not None:
            self._values["env"] = env
        if group_add is not None:
            self._values["group_add"] = group_add
        if healthcheck is not None:
            self._values["healthcheck"] = healthcheck
        if host is not None:
            self._values["host"] = host
        if hostname is not None:
            self._values["hostname"] = hostname
        if init is not None:
            self._values["init"] = init
        if ipc_mode is not None:
            self._values["ipc_mode"] = ipc_mode
        if labels is not None:
            self._values["labels"] = labels
        if links is not None:
            self._values["links"] = links
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if log_opts is not None:
            self._values["log_opts"] = log_opts
        if logs is not None:
            self._values["logs"] = logs
        if max_retry_count is not None:
            self._values["max_retry_count"] = max_retry_count
        if memory is not None:
            self._values["memory"] = memory
        if memory_swap is not None:
            self._values["memory_swap"] = memory_swap
        if mounts is not None:
            self._values["mounts"] = mounts
        if must_run is not None:
            self._values["must_run"] = must_run
        if network_alias is not None:
            self._values["network_alias"] = network_alias
        if network_mode is not None:
            self._values["network_mode"] = network_mode
        if networks is not None:
            self._values["networks"] = networks
        if networks_advanced is not None:
            self._values["networks_advanced"] = networks_advanced
        if pid_mode is not None:
            self._values["pid_mode"] = pid_mode
        if ports is not None:
            self._values["ports"] = ports
        if privileged is not None:
            self._values["privileged"] = privileged
        if publish_all_ports is not None:
            self._values["publish_all_ports"] = publish_all_ports
        if read_only is not None:
            self._values["read_only"] = read_only
        if remove_volumes is not None:
            self._values["remove_volumes"] = remove_volumes
        if restart is not None:
            self._values["restart"] = restart
        if rm is not None:
            self._values["rm"] = rm
        if security_opts is not None:
            self._values["security_opts"] = security_opts
        if shm_size is not None:
            self._values["shm_size"] = shm_size
        if start is not None:
            self._values["start"] = start
        if stdin_open is not None:
            self._values["stdin_open"] = stdin_open
        if storage_opts is not None:
            self._values["storage_opts"] = storage_opts
        if sysctls is not None:
            self._values["sysctls"] = sysctls
        if tmpfs is not None:
            self._values["tmpfs"] = tmpfs
        if tty is not None:
            self._values["tty"] = tty
        if ulimit is not None:
            self._values["ulimit"] = ulimit
        if upload is not None:
            self._values["upload"] = upload
        if user is not None:
            self._values["user"] = user
        if userns_mode is not None:
            self._values["userns_mode"] = userns_mode
        if volumes is not None:
            self._values["volumes"] = volumes
        if working_dir is not None:
            self._values["working_dir"] = working_dir

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def image(self) -> builtins.str:
        '''The ID of the image to back this container.

        The easiest way to get this value is to use the ``docker_image`` resource as is shown in the example.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#image Container#image}
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attach(self) -> typing.Optional[builtins.bool]:
        '''If ``true`` attach to the container after its creation and waits the end of its execution. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#attach Container#attach}
        '''
        result = self._values.get("attach")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def capabilities(self) -> typing.Optional[typing.List[ContainerCapabilities]]:
        '''capabilities block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#capabilities Container#capabilities}
        '''
        result = self._values.get("capabilities")
        return typing.cast(typing.Optional[typing.List[ContainerCapabilities]], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command to use to start the container.

        For example, to run ``/usr/bin/myprogram -f baz.conf`` set the command to be ``["/usr/bin/myprogram","-","baz.con"]``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#command Container#command}
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cpu_set(self) -> typing.Optional[builtins.str]:
        '''A comma-separated list or hyphen-separated range of CPUs a container can use, e.g. ``0-1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#cpu_set Container#cpu_set}
        '''
        result = self._values.get("cpu_set")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_shares(self) -> typing.Optional[jsii.Number]:
        '''CPU shares (relative weight) for the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#cpu_shares Container#cpu_shares}
        '''
        result = self._values.get("cpu_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def destroy_grace_seconds(self) -> typing.Optional[jsii.Number]:
        '''If defined will attempt to stop the container before destroying.

        Container will be destroyed after ``n`` seconds or on successful stop.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#destroy_grace_seconds Container#destroy_grace_seconds}
        '''
        result = self._values.get("destroy_grace_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def devices(self) -> typing.Optional[typing.List["ContainerDevices"]]:
        '''devices block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#devices Container#devices}
        '''
        result = self._values.get("devices")
        return typing.cast(typing.Optional[typing.List["ContainerDevices"]], result)

    @builtins.property
    def dns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''DNS servers to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns Container#dns}
        '''
        result = self._values.get("dns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_opts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''DNS options used by the DNS provider(s), see ``resolv.conf`` documentation for valid list of options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns_opts Container#dns_opts}
        '''
        result = self._values.get("dns_opts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def dns_search(self) -> typing.Optional[typing.List[builtins.str]]:
        '''DNS search domains that are used when bare unqualified hostnames are used inside of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#dns_search Container#dns_search}
        '''
        result = self._values.get("dns_search")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def domainname(self) -> typing.Optional[builtins.str]:
        '''Domain name of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#domainname Container#domainname}
        '''
        result = self._values.get("domainname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def entrypoint(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command to use as the Entrypoint for the container.

        The Entrypoint allows you to configure a container to run as an executable. For example, to run ``/usr/bin/myprogram`` when starting a container, set the entrypoint to be ``"/usr/bin/myprogra"]``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#entrypoint Container#entrypoint}
        '''
        result = self._values.get("entrypoint")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Environment variables to set in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#env Container#env}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def group_add(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Additional groups for the container user.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#group_add Container#group_add}
        '''
        result = self._values.get("group_add")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def healthcheck(self) -> typing.Optional[typing.List["ContainerHealthcheck"]]:
        '''healthcheck block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#healthcheck Container#healthcheck}
        '''
        result = self._values.get("healthcheck")
        return typing.cast(typing.Optional[typing.List["ContainerHealthcheck"]], result)

    @builtins.property
    def host(self) -> typing.Optional[typing.List["ContainerHost"]]:
        '''host block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host Container#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[typing.List["ContainerHost"]], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''Hostname of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#hostname Container#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def init(self) -> typing.Optional[builtins.bool]:
        '''Configured whether an init process should be injected for this container.

        If unset this will default to the ``dockerd`` defaults.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#init Container#init}
        '''
        result = self._values.get("init")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ipc_mode(self) -> typing.Optional[builtins.str]:
        '''IPC sharing mode for the container. Possible values are: ``none``, ``private``, ``shareable``, ``container:<name|id>`` or ``host``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipc_mode Container#ipc_mode}
        '''
        result = self._values.get("ipc_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["ContainerLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#labels Container#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ContainerLabels"]], result)

    @builtins.property
    def links(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set of links for link based connectivity between containers that are running on the same host.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#links Container#links}
        '''
        result = self._values.get("links")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def log_driver(self) -> typing.Optional[builtins.str]:
        '''The logging driver to use for the container. Defaults to ``json-file``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#log_driver Container#log_driver}
        '''
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_opts(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key/value pairs to use as options for the logging driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#log_opts Container#log_opts}
        '''
        result = self._values.get("log_opts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def logs(self) -> typing.Optional[builtins.bool]:
        '''Save the container logs (``attach`` must be enabled). Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#logs Container#logs}
        '''
        result = self._values.get("logs")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def max_retry_count(self) -> typing.Optional[jsii.Number]:
        '''The maximum amount of times to an attempt a restart when ``restart`` is set to 'on-failure'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#max_retry_count Container#max_retry_count}
        '''
        result = self._values.get("max_retry_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''The memory limit for the container in MBs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#memory Container#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_swap(self) -> typing.Optional[jsii.Number]:
        '''The total memory limit (memory + swap) for the container in MBs.

        This setting may compute to ``-1`` after ``terraform apply`` if the target host doesn't support memory swap, when that is the case docker will use a soft limitation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#memory_swap Container#memory_swap}
        '''
        result = self._values.get("memory_swap")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mounts(self) -> typing.Optional[typing.List["ContainerMounts"]]:
        '''mounts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#mounts Container#mounts}
        '''
        result = self._values.get("mounts")
        return typing.cast(typing.Optional[typing.List["ContainerMounts"]], result)

    @builtins.property
    def must_run(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, then the Docker container will be kept running.

        If ``false``, then as long as the container exists, Terraform assumes it is successful. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#must_run Container#must_run}
        '''
        result = self._values.get("must_run")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def network_alias(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Set an alias for the container in all specified networks.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#network_alias Container#network_alias}
        '''
        result = self._values.get("network_alias")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def network_mode(self) -> typing.Optional[builtins.str]:
        '''Network mode of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#network_mode Container#network_mode}
        '''
        result = self._values.get("network_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def networks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''ID of the networks in which the container is.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#networks Container#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def networks_advanced(
        self,
    ) -> typing.Optional[typing.List["ContainerNetworksAdvanced"]]:
        '''networks_advanced block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#networks_advanced Container#networks_advanced}
        '''
        result = self._values.get("networks_advanced")
        return typing.cast(typing.Optional[typing.List["ContainerNetworksAdvanced"]], result)

    @builtins.property
    def pid_mode(self) -> typing.Optional[builtins.str]:
        '''he PID (Process) Namespace mode for the container. Either ``container:<name|id>`` or ``host``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#pid_mode Container#pid_mode}
        '''
        result = self._values.get("pid_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List["ContainerPorts"]]:
        '''ports block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ports Container#ports}
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List["ContainerPorts"]], result)

    @builtins.property
    def privileged(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, the container runs in privileged mode.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#privileged Container#privileged}
        '''
        result = self._values.get("privileged")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def publish_all_ports(self) -> typing.Optional[builtins.bool]:
        '''Publish all ports of the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#publish_all_ports Container#publish_all_ports}
        '''
        result = self._values.get("publish_all_ports")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, the container will be started as readonly. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def remove_volumes(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, it will remove anonymous volumes associated with the container. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#remove_volumes Container#remove_volumes}
        '''
        result = self._values.get("remove_volumes")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def restart(self) -> typing.Optional[builtins.str]:
        '''The restart policy for the container. Must be one of 'no', 'on-failure', 'always', 'unless-stopped'. Defaults to ``no``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#restart Container#restart}
        '''
        result = self._values.get("restart")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rm(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, then the container will be automatically removed after his execution.

        Terraform won't check this container after creation. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#rm Container#rm}
        '''
        result = self._values.get("rm")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_opts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of string values to customize labels for MLS systems, such as SELinux. See https://docs.docker.com/engine/reference/run/#security-configuration.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#security_opts Container#security_opts}
        '''
        result = self._values.get("security_opts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def shm_size(self) -> typing.Optional[jsii.Number]:
        '''Size of ``/dev/shm`` in MBs.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#shm_size Container#shm_size}
        '''
        result = self._values.get("shm_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, then the Docker container will be started after creation.

        If ``false``, then the container is only created. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#start Container#start}
        '''
        result = self._values.get("start")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def stdin_open(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, keep STDIN open even if not attached (``docker run -i``). Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#stdin_open Container#stdin_open}
        '''
        result = self._values.get("stdin_open")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def storage_opts(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Key/value pairs for the storage driver options, e.g. ``size``: ``120G``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#storage_opts Container#storage_opts}
        '''
        result = self._values.get("storage_opts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def sysctls(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of kernel parameters (sysctls) to set in the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#sysctls Container#sysctls}
        '''
        result = self._values.get("sysctls")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tmpfs(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A map of container directories which should be replaced by ``tmpfs mounts``, and their corresponding mount options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tmpfs Container#tmpfs}
        '''
        result = self._values.get("tmpfs")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def tty(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, allocate a pseudo-tty (``docker run -t``). Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tty Container#tty}
        '''
        result = self._values.get("tty")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ulimit(self) -> typing.Optional[typing.List["ContainerUlimit"]]:
        '''ulimit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ulimit Container#ulimit}
        '''
        result = self._values.get("ulimit")
        return typing.cast(typing.Optional[typing.List["ContainerUlimit"]], result)

    @builtins.property
    def upload(self) -> typing.Optional[typing.List["ContainerUpload"]]:
        '''upload block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#upload Container#upload}
        '''
        result = self._values.get("upload")
        return typing.cast(typing.Optional[typing.List["ContainerUpload"]], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''User used for run the first process.

        Format is ``user`` or ``user:group`` which user and group can be passed literraly or by name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#user Container#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def userns_mode(self) -> typing.Optional[builtins.str]:
        '''Sets the usernamespace mode for the container when usernamespace remapping option is enabled.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#userns_mode Container#userns_mode}
        '''
        result = self._values.get("userns_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def volumes(self) -> typing.Optional[typing.List["ContainerVolumes"]]:
        '''volumes block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volumes Container#volumes}
        '''
        result = self._values.get("volumes")
        return typing.cast(typing.Optional[typing.List["ContainerVolumes"]], result)

    @builtins.property
    def working_dir(self) -> typing.Optional[builtins.str]:
        '''The working directory for commands to run in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#working_dir Container#working_dir}
        '''
        result = self._values.get("working_dir")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerDevices",
    jsii_struct_bases=[],
    name_mapping={
        "host_path": "hostPath",
        "container_path": "containerPath",
        "permissions": "permissions",
    },
)
class ContainerDevices:
    def __init__(
        self,
        *,
        host_path: builtins.str,
        container_path: typing.Optional[builtins.str] = None,
        permissions: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_path: The path on the host where the device is located. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host_path Container#host_path}
        :param container_path: The path in the container where the device will be bound. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#container_path Container#container_path}
        :param permissions: The cgroup permissions given to the container to access the device. Defaults to ``rwm``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#permissions Container#permissions}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host_path": host_path,
        }
        if container_path is not None:
            self._values["container_path"] = container_path
        if permissions is not None:
            self._values["permissions"] = permissions

    @builtins.property
    def host_path(self) -> builtins.str:
        '''The path on the host where the device is located.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host_path Container#host_path}
        '''
        result = self._values.get("host_path")
        assert result is not None, "Required property 'host_path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def container_path(self) -> typing.Optional[builtins.str]:
        '''The path in the container where the device will be bound.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#container_path Container#container_path}
        '''
        result = self._values.get("container_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def permissions(self) -> typing.Optional[builtins.str]:
        '''The cgroup permissions given to the container to access the device. Defaults to ``rwm``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#permissions Container#permissions}
        '''
        result = self._values.get("permissions")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerDevices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerHealthcheck",
    jsii_struct_bases=[],
    name_mapping={
        "test": "test",
        "interval": "interval",
        "retries": "retries",
        "start_period": "startPeriod",
        "timeout": "timeout",
    },
)
class ContainerHealthcheck:
    def __init__(
        self,
        *,
        test: typing.Sequence[builtins.str],
        interval: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        start_period: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param test: Command to run to check health. For example, to run ``curl -f localhost/health`` set the command to be ``["CMD", "curl", "-f", "localhost/health"]``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#test Container#test}
        :param interval: Time between running the check (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#interval Container#interval}
        :param retries: Consecutive failures needed to report unhealthy. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#retries Container#retries}
        :param start_period: Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#start_period Container#start_period}
        :param timeout: Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#timeout Container#timeout}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "test": test,
        }
        if interval is not None:
            self._values["interval"] = interval
        if retries is not None:
            self._values["retries"] = retries
        if start_period is not None:
            self._values["start_period"] = start_period
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def test(self) -> typing.List[builtins.str]:
        '''Command to run to check health.

        For example, to run ``curl -f localhost/health`` set the command to be ``["CMD", "curl", "-f", "localhost/health"]``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#test Container#test}
        '''
        result = self._values.get("test")
        assert result is not None, "Required property 'test' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Time between running the check (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#interval Container#interval}
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''Consecutive failures needed to report unhealthy. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#retries Container#retries}
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_period(self) -> typing.Optional[builtins.str]:
        '''Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#start_period Container#start_period}
        '''
        result = self._values.get("start_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#timeout Container#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerHealthcheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerHost",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "ip": "ip"},
)
class ContainerHost:
    def __init__(self, *, host: builtins.str, ip: builtins.str) -> None:
        '''
        :param host: Hostname to add. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host Container#host}
        :param ip: IP address this hostname should resolve to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ip Container#ip}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host": host,
            "ip": ip,
        }

    @builtins.property
    def host(self) -> builtins.str:
        '''Hostname to add.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host Container#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip(self) -> builtins.str:
        '''IP address this hostname should resolve to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ip Container#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerHost(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ContainerLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#label Container#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#value Container#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#label Container#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#value Container#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMounts",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "type": "type",
        "bind_options": "bindOptions",
        "read_only": "readOnly",
        "source": "source",
        "tmpfs_options": "tmpfsOptions",
        "volume_options": "volumeOptions",
    },
)
class ContainerMounts:
    def __init__(
        self,
        *,
        target: builtins.str,
        type: builtins.str,
        bind_options: typing.Optional[typing.Sequence["ContainerMountsBindOptions"]] = None,
        read_only: typing.Optional[builtins.bool] = None,
        source: typing.Optional[builtins.str] = None,
        tmpfs_options: typing.Optional[typing.Sequence["ContainerMountsTmpfsOptions"]] = None,
        volume_options: typing.Optional[typing.Sequence["ContainerMountsVolumeOptions"]] = None,
    ) -> None:
        '''
        :param target: Container path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#target Container#target}
        :param type: The mount type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#type Container#type}
        :param bind_options: bind_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#bind_options Container#bind_options}
        :param read_only: Whether the mount should be read-only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        :param source: Mount source (e.g. a volume name, a host path). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#source Container#source}
        :param tmpfs_options: tmpfs_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tmpfs_options Container#tmpfs_options}
        :param volume_options: volume_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volume_options Container#volume_options}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
            "type": type,
        }
        if bind_options is not None:
            self._values["bind_options"] = bind_options
        if read_only is not None:
            self._values["read_only"] = read_only
        if source is not None:
            self._values["source"] = source
        if tmpfs_options is not None:
            self._values["tmpfs_options"] = tmpfs_options
        if volume_options is not None:
            self._values["volume_options"] = volume_options

    @builtins.property
    def target(self) -> builtins.str:
        '''Container path.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#target Container#target}
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The mount type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#type Container#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_options(
        self,
    ) -> typing.Optional[typing.List["ContainerMountsBindOptions"]]:
        '''bind_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#bind_options Container#bind_options}
        '''
        result = self._values.get("bind_options")
        return typing.cast(typing.Optional[typing.List["ContainerMountsBindOptions"]], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''Whether the mount should be read-only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Mount source (e.g. a volume name, a host path).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#source Container#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tmpfs_options(
        self,
    ) -> typing.Optional[typing.List["ContainerMountsTmpfsOptions"]]:
        '''tmpfs_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#tmpfs_options Container#tmpfs_options}
        '''
        result = self._values.get("tmpfs_options")
        return typing.cast(typing.Optional[typing.List["ContainerMountsTmpfsOptions"]], result)

    @builtins.property
    def volume_options(
        self,
    ) -> typing.Optional[typing.List["ContainerMountsVolumeOptions"]]:
        '''volume_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volume_options Container#volume_options}
        '''
        result = self._values.get("volume_options")
        return typing.cast(typing.Optional[typing.List["ContainerMountsVolumeOptions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMounts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsBindOptions",
    jsii_struct_bases=[],
    name_mapping={"propagation": "propagation"},
)
class ContainerMountsBindOptions:
    def __init__(self, *, propagation: typing.Optional[builtins.str] = None) -> None:
        '''
        :param propagation: A propagation mode with the value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#propagation Container#propagation}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if propagation is not None:
            self._values["propagation"] = propagation

    @builtins.property
    def propagation(self) -> typing.Optional[builtins.str]:
        '''A propagation mode with the value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#propagation Container#propagation}
        '''
        result = self._values.get("propagation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsTmpfsOptions",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "size_bytes": "sizeBytes"},
)
class ContainerMountsTmpfsOptions:
    def __init__(
        self,
        *,
        mode: typing.Optional[jsii.Number] = None,
        size_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The permission mode for the tmpfs mount in an integer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#mode Container#mode}
        :param size_bytes: The size for the tmpfs mount in bytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#size_bytes Container#size_bytes}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if size_bytes is not None:
            self._values["size_bytes"] = size_bytes

    @builtins.property
    def mode(self) -> typing.Optional[jsii.Number]:
        '''The permission mode for the tmpfs mount in an integer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#mode Container#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def size_bytes(self) -> typing.Optional[jsii.Number]:
        '''The size for the tmpfs mount in bytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#size_bytes Container#size_bytes}
        '''
        result = self._values.get("size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsTmpfsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsVolumeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "driver_name": "driverName",
        "driver_options": "driverOptions",
        "labels": "labels",
        "no_copy": "noCopy",
    },
)
class ContainerMountsVolumeOptions:
    def __init__(
        self,
        *,
        driver_name: typing.Optional[builtins.str] = None,
        driver_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        labels: typing.Optional[typing.Sequence["ContainerMountsVolumeOptionsLabels"]] = None,
        no_copy: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param driver_name: Name of the driver to use to create the volume. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#driver_name Container#driver_name}
        :param driver_options: key/value map of driver specific options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#driver_options Container#driver_options}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#labels Container#labels}
        :param no_copy: Populate volume with data from the target. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#no_copy Container#no_copy}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if driver_name is not None:
            self._values["driver_name"] = driver_name
        if driver_options is not None:
            self._values["driver_options"] = driver_options
        if labels is not None:
            self._values["labels"] = labels
        if no_copy is not None:
            self._values["no_copy"] = no_copy

    @builtins.property
    def driver_name(self) -> typing.Optional[builtins.str]:
        '''Name of the driver to use to create the volume.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#driver_name Container#driver_name}
        '''
        result = self._values.get("driver_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''key/value map of driver specific options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#driver_options Container#driver_options}
        '''
        result = self._values.get("driver_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.List["ContainerMountsVolumeOptionsLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#labels Container#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ContainerMountsVolumeOptionsLabels"]], result)

    @builtins.property
    def no_copy(self) -> typing.Optional[builtins.bool]:
        '''Populate volume with data from the target.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#no_copy Container#no_copy}
        '''
        result = self._values.get("no_copy")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsVolumeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerMountsVolumeOptionsLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ContainerMountsVolumeOptionsLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#label Container#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#value Container#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#label Container#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#value Container#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerMountsVolumeOptionsLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ContainerNetworkData(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.ContainerNetworkData",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(ContainerNetworkData, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalIpv6Address")
    def global_ipv6_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "globalIpv6Address"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="globalIpv6PrefixLength")
    def global_ipv6_prefix_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "globalIpv6PrefixLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddress")
    def ip_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipPrefixLength")
    def ip_prefix_length(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ipPrefixLength"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6Gateway")
    def ipv6_gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6Gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="networkName")
    def network_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkName"))


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerNetworksAdvanced",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "aliases": "aliases",
        "ipv4_address": "ipv4Address",
        "ipv6_address": "ipv6Address",
    },
)
class ContainerNetworksAdvanced:
    def __init__(
        self,
        *,
        name: builtins.str,
        aliases: typing.Optional[typing.Sequence[builtins.str]] = None,
        ipv4_address: typing.Optional[builtins.str] = None,
        ipv6_address: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: The name of the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        :param aliases: The network aliases of the container in the specific network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#aliases Container#aliases}
        :param ipv4_address: The IPV4 address of the container in the specific network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipv4_address Container#ipv4_address}
        :param ipv6_address: The IPV6 address of the container in the specific network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipv6_address Container#ipv6_address}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if aliases is not None:
            self._values["aliases"] = aliases
        if ipv4_address is not None:
            self._values["ipv4_address"] = ipv4_address
        if ipv6_address is not None:
            self._values["ipv6_address"] = ipv6_address

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aliases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The network aliases of the container in the specific network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#aliases Container#aliases}
        '''
        result = self._values.get("aliases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ipv4_address(self) -> typing.Optional[builtins.str]:
        '''The IPV4 address of the container in the specific network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipv4_address Container#ipv4_address}
        '''
        result = self._values.get("ipv4_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6_address(self) -> typing.Optional[builtins.str]:
        '''The IPV6 address of the container in the specific network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ipv6_address Container#ipv6_address}
        '''
        result = self._values.get("ipv6_address")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerNetworksAdvanced(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerPorts",
    jsii_struct_bases=[],
    name_mapping={
        "internal": "internal",
        "external": "external",
        "ip": "ip",
        "protocol": "protocol",
    },
)
class ContainerPorts:
    def __init__(
        self,
        *,
        internal: jsii.Number,
        external: typing.Optional[jsii.Number] = None,
        ip: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param internal: Port within the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#internal Container#internal}
        :param external: Port exposed out of the container. If not given a free random port ``>= 32768`` will be used. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#external Container#external}
        :param ip: IP address/mask that can access this port. Defaults to ``0.0.0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ip Container#ip}
        :param protocol: Protocol that can be used over this port. Defaults to ``tcp``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#protocol Container#protocol}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "internal": internal,
        }
        if external is not None:
            self._values["external"] = external
        if ip is not None:
            self._values["ip"] = ip
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def internal(self) -> jsii.Number:
        '''Port within the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#internal Container#internal}
        '''
        result = self._values.get("internal")
        assert result is not None, "Required property 'internal' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def external(self) -> typing.Optional[jsii.Number]:
        '''Port exposed out of the container. If not given a free random port ``>= 32768`` will be used.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#external Container#external}
        '''
        result = self._values.get("external")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip(self) -> typing.Optional[builtins.str]:
        '''IP address/mask that can access this port. Defaults to ``0.0.0.0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#ip Container#ip}
        '''
        result = self._values.get("ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Protocol that can be used over this port. Defaults to ``tcp``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#protocol Container#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerUlimit",
    jsii_struct_bases=[],
    name_mapping={"hard": "hard", "name": "name", "soft": "soft"},
)
class ContainerUlimit:
    def __init__(
        self,
        *,
        hard: jsii.Number,
        name: builtins.str,
        soft: jsii.Number,
    ) -> None:
        '''
        :param hard: The hard limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#hard Container#hard}
        :param name: The name of the ulimit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        :param soft: The soft limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#soft Container#soft}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hard": hard,
            "name": name,
            "soft": soft,
        }

    @builtins.property
    def hard(self) -> jsii.Number:
        '''The hard limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#hard Container#hard}
        '''
        result = self._values.get("hard")
        assert result is not None, "Required property 'hard' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the ulimit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#name Container#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def soft(self) -> jsii.Number:
        '''The soft limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#soft Container#soft}
        '''
        result = self._values.get("soft")
        assert result is not None, "Required property 'soft' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerUlimit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerUpload",
    jsii_struct_bases=[],
    name_mapping={
        "file": "file",
        "content": "content",
        "content_base64": "contentBase64",
        "executable": "executable",
        "source": "source",
        "source_hash": "sourceHash",
    },
)
class ContainerUpload:
    def __init__(
        self,
        *,
        file: builtins.str,
        content: typing.Optional[builtins.str] = None,
        content_base64: typing.Optional[builtins.str] = None,
        executable: typing.Optional[builtins.bool] = None,
        source: typing.Optional[builtins.str] = None,
        source_hash: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file: Path to the file in the container where is upload goes to. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#file Container#file}
        :param content: Literal string value to use as the object content, which will be uploaded as UTF-8-encoded text. Conflicts with ``content_base64`` & ``source`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#content Container#content}
        :param content_base64: Base64-encoded data that will be decoded and uploaded as raw bytes for the object content. This allows safely uploading non-UTF8 binary data, but is recommended only for larger binary content such as the result of the ``base64encode`` interpolation function. See `here <https://github.com/terraform-providers/terraform-provider-docker/issues/48#issuecomment-374174588>`_ for the reason. Conflicts with ``content`` & ``source`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#content_base64 Container#content_base64}
        :param executable: If ``true``, the file will be uploaded with user executable permission. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#executable Container#executable}
        :param source: A filename that references a file which will be uploaded as the object content. This allows for large file uploads that do not get stored in state. Conflicts with ``content`` & ``content_base64`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#source Container#source}
        :param source_hash: If using ``source``, this will force an update if the file content has updated but the filename has not. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#source_hash Container#source_hash}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file": file,
        }
        if content is not None:
            self._values["content"] = content
        if content_base64 is not None:
            self._values["content_base64"] = content_base64
        if executable is not None:
            self._values["executable"] = executable
        if source is not None:
            self._values["source"] = source
        if source_hash is not None:
            self._values["source_hash"] = source_hash

    @builtins.property
    def file(self) -> builtins.str:
        '''Path to the file in the container where is upload goes to.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#file Container#file}
        '''
        result = self._values.get("file")
        assert result is not None, "Required property 'file' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''Literal string value to use as the object content, which will be uploaded as UTF-8-encoded text.

        Conflicts with ``content_base64`` & ``source``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#content Container#content}
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def content_base64(self) -> typing.Optional[builtins.str]:
        '''Base64-encoded data that will be decoded and uploaded as raw bytes for the object content.

        This allows safely uploading non-UTF8 binary data, but is recommended only for larger binary content such as the result of the ``base64encode`` interpolation function. See `here <https://github.com/terraform-providers/terraform-provider-docker/issues/48#issuecomment-374174588>`_ for the reason. Conflicts with ``content`` & ``source``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#content_base64 Container#content_base64}
        '''
        result = self._values.get("content_base64")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def executable(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, the file will be uploaded with user executable permission. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#executable Container#executable}
        '''
        result = self._values.get("executable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''A filename that references a file which will be uploaded as the object content.

        This allows for large file uploads that do not get stored in state. Conflicts with ``content`` & ``content_base64``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#source Container#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_hash(self) -> typing.Optional[builtins.str]:
        '''If using ``source``, this will force an update if the file content has updated but the filename has not.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#source_hash Container#source_hash}
        '''
        result = self._values.get("source_hash")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerUpload(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ContainerVolumes",
    jsii_struct_bases=[],
    name_mapping={
        "container_path": "containerPath",
        "from_container": "fromContainer",
        "host_path": "hostPath",
        "read_only": "readOnly",
        "volume_name": "volumeName",
    },
)
class ContainerVolumes:
    def __init__(
        self,
        *,
        container_path: typing.Optional[builtins.str] = None,
        from_container: typing.Optional[builtins.str] = None,
        host_path: typing.Optional[builtins.str] = None,
        read_only: typing.Optional[builtins.bool] = None,
        volume_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param container_path: The path in the container where the volume will be mounted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#container_path Container#container_path}
        :param from_container: The container where the volume is coming from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#from_container Container#from_container}
        :param host_path: The path on the host where the volume is coming from. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host_path Container#host_path}
        :param read_only: If ``true``, this volume will be readonly. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        :param volume_name: The name of the docker volume which should be mounted. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volume_name Container#volume_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if container_path is not None:
            self._values["container_path"] = container_path
        if from_container is not None:
            self._values["from_container"] = from_container
        if host_path is not None:
            self._values["host_path"] = host_path
        if read_only is not None:
            self._values["read_only"] = read_only
        if volume_name is not None:
            self._values["volume_name"] = volume_name

    @builtins.property
    def container_path(self) -> typing.Optional[builtins.str]:
        '''The path in the container where the volume will be mounted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#container_path Container#container_path}
        '''
        result = self._values.get("container_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def from_container(self) -> typing.Optional[builtins.str]:
        '''The container where the volume is coming from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#from_container Container#from_container}
        '''
        result = self._values.get("from_container")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host_path(self) -> typing.Optional[builtins.str]:
        '''The path on the host where the volume is coming from.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#host_path Container#host_path}
        '''
        result = self._values.get("host_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, this volume will be readonly. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#read_only Container#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def volume_name(self) -> typing.Optional[builtins.str]:
        '''The name of the docker volume which should be mounted.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/container.html#volume_name Container#volume_name}
        '''
        result = self._values.get("volume_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ContainerVolumes(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerImage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/image.html docker_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/image.html docker_image} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/image.html#name DataDockerImage#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerImageConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataDockerImage, self, [scope, id, config])

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoDigest")
    def repo_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoDigest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataDockerImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/image.html#name DataDockerImage#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Docker image, including any tags or SHA256 repo digests.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/image.html#name DataDockerImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerNetwork(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerNetwork",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/network.html docker_network}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/network.html docker_network} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/network.html#name DataDockerNetwork#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerNetworkConfig(
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataDockerNetwork, self, [scope, id, config])

    @jsii.member(jsii_name="ipamConfig")
    def ipam_config(self, index: builtins.str) -> "DataDockerNetworkIpamConfig":
        '''
        :param index: -
        '''
        return typing.cast("DataDockerNetworkIpamConfig", jsii.invoke(self, "ipamConfig", [index]))

    @jsii.member(jsii_name="options")
    def options(self, key: builtins.str) -> builtins.str:
        '''
        :param key: -
        '''
        return typing.cast(builtins.str, jsii.invoke(self, "options", [key]))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driver")
    def driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driver"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internal")
    def internal(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "internal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerNetworkConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
    },
)
class DataDockerNetworkConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/network.html#name DataDockerNetwork#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Docker network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/network.html#name DataDockerNetwork#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerNetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerNetworkIpamConfig(
    cdktf.ComplexComputedList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerNetworkIpamConfig",
):
    def __init__(
        self,
        terraform_resource: cdktf.ITerraformResource,
        terraform_attribute: builtins.str,
        complex_computed_list_index: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: -
        :param terraform_attribute: -
        :param complex_computed_list_index: -

        :stability: experimental
        '''
        jsii.create(DataDockerNetworkIpamConfig, self, [terraform_resource, terraform_attribute, complex_computed_list_index])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auxAddress")
    def aux_address(self) -> typing.Any:
        return typing.cast(typing.Any, jsii.get(self, "auxAddress"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="gateway")
    def gateway(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gateway"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipRange")
    def ip_range(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipRange"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subnet")
    def subnet(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subnet"))


class DataDockerPlugin(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerPlugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/plugin.html docker_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/plugin.html docker_plugin} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: The alias of the Docker plugin. If the tag is omitted, ``:latest`` is complemented to the attribute value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin.html#alias DataDockerPlugin#alias}
        :param id: The ID of the plugin, which has precedence over the ``alias`` of both are given. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin.html#id DataDockerPlugin#id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerPluginConfig(
            alias=alias,
            id=id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataDockerPlugin, self, [scope, id_, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enabled"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "env"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantAllPermissions")
    def grant_all_permissions(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "grantAllPermissions"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginReference")
    def plugin_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerPluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "alias": "alias",
        "id": "id",
    },
)
class DataDockerPluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        alias: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param alias: The alias of the Docker plugin. If the tag is omitted, ``:latest`` is complemented to the attribute value. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin.html#alias DataDockerPlugin#alias}
        :param id: The ID of the plugin, which has precedence over the ``alias`` of both are given. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin.html#id DataDockerPlugin#id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if alias is not None:
            self._values["alias"] = alias
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''The alias of the Docker plugin. If the tag is omitted, ``:latest`` is complemented to the attribute value.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin.html#alias DataDockerPlugin#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''The ID of the plugin, which has precedence over the ``alias`` of both are given.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/plugin.html#id DataDockerPlugin#id}
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerPluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDockerRegistryImage(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DataDockerRegistryImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html docker_registry_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        insecure_skip_verify: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html docker_registry_image} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image, including any tags. e.g. ``alpine:latest``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html#name DataDockerRegistryImage#name}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html#insecure_skip_verify DataDockerRegistryImage#insecure_skip_verify}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataDockerRegistryImageConfig(
            name=name,
            insecure_skip_verify=insecure_skip_verify,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(DataDockerRegistryImage, self, [scope, id, config])

    @jsii.member(jsii_name="resetInsecureSkipVerify")
    def reset_insecure_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureSkipVerify", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha256Digest")
    def sha256_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha256Digest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerifyInput")
    def insecure_skip_verify_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "insecureSkipVerifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerify")
    def insecure_skip_verify(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "insecureSkipVerify"))

    @insecure_skip_verify.setter
    def insecure_skip_verify(self, value: builtins.bool) -> None:
        jsii.set(self, "insecureSkipVerify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DataDockerRegistryImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "insecure_skip_verify": "insecureSkipVerify",
    },
)
class DataDockerRegistryImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        insecure_skip_verify: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image, including any tags. e.g. ``alpine:latest``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html#name DataDockerRegistryImage#name}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html#insecure_skip_verify DataDockerRegistryImage#insecure_skip_verify}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if insecure_skip_verify is not None:
            self._values["insecure_skip_verify"] = insecure_skip_verify

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Docker image, including any tags. e.g. ``alpine:latest``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html#name DataDockerRegistryImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def insecure_skip_verify(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/d/registry_image.html#insecure_skip_verify DataDockerRegistryImage#insecure_skip_verify}
        '''
        result = self._values.get("insecure_skip_verify")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDockerRegistryImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DockerProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.DockerProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker docker}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        ca_material: typing.Optional[builtins.str] = None,
        cert_material: typing.Optional[builtins.str] = None,
        cert_path: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        key_material: typing.Optional[builtins.str] = None,
        registry_auth: typing.Optional[typing.Sequence["DockerProviderRegistryAuth"]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker docker} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#alias DockerProvider#alias}
        :param ca_material: PEM-encoded content of Docker host CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#ca_material DockerProvider#ca_material}
        :param cert_material: PEM-encoded content of Docker client certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_material DockerProvider#cert_material}
        :param cert_path: Path to directory with Docker TLS config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_path DockerProvider#cert_path}
        :param host: The Docker daemon address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#host DockerProvider#host}
        :param key_material: PEM-encoded content of Docker client private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#key_material DockerProvider#key_material}
        :param registry_auth: registry_auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#registry_auth DockerProvider#registry_auth}
        '''
        config = DockerProviderConfig(
            alias=alias,
            ca_material=ca_material,
            cert_material=cert_material,
            cert_path=cert_path,
            host=host,
            key_material=key_material,
            registry_auth=registry_auth,
        )

        jsii.create(DockerProvider, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetCaMaterial")
    def reset_ca_material(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaMaterial", []))

    @jsii.member(jsii_name="resetCertMaterial")
    def reset_cert_material(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertMaterial", []))

    @jsii.member(jsii_name="resetCertPath")
    def reset_cert_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertPath", []))

    @jsii.member(jsii_name="resetHost")
    def reset_host(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHost", []))

    @jsii.member(jsii_name="resetKeyMaterial")
    def reset_key_material(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyMaterial", []))

    @jsii.member(jsii_name="resetRegistryAuth")
    def reset_registry_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegistryAuth", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caMaterialInput")
    def ca_material_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caMaterialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certMaterialInput")
    def cert_material_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certMaterialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPathInput")
    def cert_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPathInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="hostInput")
    def host_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyMaterialInput")
    def key_material_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyMaterialInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registryAuthInput")
    def registry_auth_input(
        self,
    ) -> typing.Optional[typing.List["DockerProviderRegistryAuth"]]:
        return typing.cast(typing.Optional[typing.List["DockerProviderRegistryAuth"]], jsii.get(self, "registryAuthInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caMaterial")
    def ca_material(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caMaterial"))

    @ca_material.setter
    def ca_material(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "caMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certMaterial")
    def cert_material(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certMaterial"))

    @cert_material.setter
    def cert_material(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPath")
    def cert_path(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certPath"))

    @cert_path.setter
    def cert_path(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "certPath", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="host")
    def host(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "host"))

    @host.setter
    def host(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "host", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyMaterial")
    def key_material(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyMaterial"))

    @key_material.setter
    def key_material(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "keyMaterial", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="registryAuth")
    def registry_auth(
        self,
    ) -> typing.Optional[typing.List["DockerProviderRegistryAuth"]]:
        return typing.cast(typing.Optional[typing.List["DockerProviderRegistryAuth"]], jsii.get(self, "registryAuth"))

    @registry_auth.setter
    def registry_auth(
        self,
        value: typing.Optional[typing.List["DockerProviderRegistryAuth"]],
    ) -> None:
        jsii.set(self, "registryAuth", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DockerProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "ca_material": "caMaterial",
        "cert_material": "certMaterial",
        "cert_path": "certPath",
        "host": "host",
        "key_material": "keyMaterial",
        "registry_auth": "registryAuth",
    },
)
class DockerProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        ca_material: typing.Optional[builtins.str] = None,
        cert_material: typing.Optional[builtins.str] = None,
        cert_path: typing.Optional[builtins.str] = None,
        host: typing.Optional[builtins.str] = None,
        key_material: typing.Optional[builtins.str] = None,
        registry_auth: typing.Optional[typing.Sequence["DockerProviderRegistryAuth"]] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#alias DockerProvider#alias}
        :param ca_material: PEM-encoded content of Docker host CA certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#ca_material DockerProvider#ca_material}
        :param cert_material: PEM-encoded content of Docker client certificate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_material DockerProvider#cert_material}
        :param cert_path: Path to directory with Docker TLS config. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_path DockerProvider#cert_path}
        :param host: The Docker daemon address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#host DockerProvider#host}
        :param key_material: PEM-encoded content of Docker client private key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#key_material DockerProvider#key_material}
        :param registry_auth: registry_auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#registry_auth DockerProvider#registry_auth}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if ca_material is not None:
            self._values["ca_material"] = ca_material
        if cert_material is not None:
            self._values["cert_material"] = cert_material
        if cert_path is not None:
            self._values["cert_path"] = cert_path
        if host is not None:
            self._values["host"] = host
        if key_material is not None:
            self._values["key_material"] = key_material
        if registry_auth is not None:
            self._values["registry_auth"] = registry_auth

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#alias DockerProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_material(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded content of Docker host CA certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#ca_material DockerProvider#ca_material}
        '''
        result = self._values.get("ca_material")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_material(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded content of Docker client certificate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_material DockerProvider#cert_material}
        '''
        result = self._values.get("cert_material")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cert_path(self) -> typing.Optional[builtins.str]:
        '''Path to directory with Docker TLS config.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#cert_path DockerProvider#cert_path}
        '''
        result = self._values.get("cert_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def host(self) -> typing.Optional[builtins.str]:
        '''The Docker daemon address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#host DockerProvider#host}
        '''
        result = self._values.get("host")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_material(self) -> typing.Optional[builtins.str]:
        '''PEM-encoded content of Docker client private key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#key_material DockerProvider#key_material}
        '''
        result = self._values.get("key_material")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_auth(
        self,
    ) -> typing.Optional[typing.List["DockerProviderRegistryAuth"]]:
        '''registry_auth block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#registry_auth DockerProvider#registry_auth}
        '''
        result = self._values.get("registry_auth")
        return typing.cast(typing.Optional[typing.List["DockerProviderRegistryAuth"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.DockerProviderRegistryAuth",
    jsii_struct_bases=[],
    name_mapping={
        "address": "address",
        "config_file": "configFile",
        "config_file_content": "configFileContent",
        "password": "password",
        "username": "username",
    },
)
class DockerProviderRegistryAuth:
    def __init__(
        self,
        *,
        address: builtins.str,
        config_file: typing.Optional[builtins.str] = None,
        config_file_content: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param address: Address of the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#address DockerProvider#address}
        :param config_file: Path to docker json file for registry auth. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file DockerProvider#config_file}
        :param config_file_content: Plain content of the docker json file for registry auth. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file_content DockerProvider#config_file_content}
        :param password: Password for the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#password DockerProvider#password}
        :param username: Username for the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#username DockerProvider#username}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "address": address,
        }
        if config_file is not None:
            self._values["config_file"] = config_file
        if config_file_content is not None:
            self._values["config_file_content"] = config_file_content
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def address(self) -> builtins.str:
        '''Address of the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#address DockerProvider#address}
        '''
        result = self._values.get("address")
        assert result is not None, "Required property 'address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_file(self) -> typing.Optional[builtins.str]:
        '''Path to docker json file for registry auth.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file DockerProvider#config_file}
        '''
        result = self._values.get("config_file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_file_content(self) -> typing.Optional[builtins.str]:
        '''Plain content of the docker json file for registry auth.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#config_file_content DockerProvider#config_file_content}
        '''
        result = self._values.get("config_file_content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Password for the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#password DockerProvider#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Username for the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker#username DockerProvider#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DockerProviderRegistryAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Image(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Image",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/image.html docker_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        build_attribute: typing.Optional[typing.Sequence["ImageBuild"]] = None,
        force_remove: typing.Optional[builtins.bool] = None,
        keep_locally: typing.Optional[builtins.bool] = None,
        pull_trigger: typing.Optional[builtins.str] = None,
        pull_triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/image.html docker_image} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#name Image#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#build Image#build}
        :param force_remove: If true, then the image is removed forcibly when the resource is destroyed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#force_remove Image#force_remove}
        :param keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#keep_locally Image#keep_locally}
        :param pull_trigger: A value which cause an image pull when changed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#pull_trigger Image#pull_trigger}
        :param pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the `docker_registry_image <../data-sources/registry_image.md>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#pull_triggers Image#pull_triggers}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ImageConfig(
            name=name,
            build_attribute=build_attribute,
            force_remove=force_remove,
            keep_locally=keep_locally,
            pull_trigger=pull_trigger,
            pull_triggers=pull_triggers,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Image, self, [scope, id, config])

    @jsii.member(jsii_name="resetBuildAttribute")
    def reset_build_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildAttribute", []))

    @jsii.member(jsii_name="resetForceRemove")
    def reset_force_remove(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceRemove", []))

    @jsii.member(jsii_name="resetKeepLocally")
    def reset_keep_locally(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepLocally", []))

    @jsii.member(jsii_name="resetPullTrigger")
    def reset_pull_trigger(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullTrigger", []))

    @jsii.member(jsii_name="resetPullTriggers")
    def reset_pull_triggers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPullTriggers", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="latest")
    def latest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "latest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="output")
    def output(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "output"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="repoDigest")
    def repo_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "repoDigest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttributeInput")
    def build_attribute_input(self) -> typing.Optional[typing.List["ImageBuild"]]:
        return typing.cast(typing.Optional[typing.List["ImageBuild"]], jsii.get(self, "buildAttributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemoveInput")
    def force_remove_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "forceRemoveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepLocallyInput")
    def keep_locally_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "keepLocallyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTriggerInput")
    def pull_trigger_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pullTriggerInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTriggersInput")
    def pull_triggers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "pullTriggersInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttribute")
    def build_attribute(self) -> typing.List["ImageBuild"]:
        return typing.cast(typing.List["ImageBuild"], jsii.get(self, "buildAttribute"))

    @build_attribute.setter
    def build_attribute(self, value: typing.List["ImageBuild"]) -> None:
        jsii.set(self, "buildAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceRemove")
    def force_remove(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "forceRemove"))

    @force_remove.setter
    def force_remove(self, value: builtins.bool) -> None:
        jsii.set(self, "forceRemove", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepLocally")
    def keep_locally(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "keepLocally"))

    @keep_locally.setter
    def keep_locally(self, value: builtins.bool) -> None:
        jsii.set(self, "keepLocally", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTrigger")
    def pull_trigger(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pullTrigger"))

    @pull_trigger.setter
    def pull_trigger(self, value: builtins.str) -> None:
        jsii.set(self, "pullTrigger", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pullTriggers")
    def pull_triggers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "pullTriggers"))

    @pull_triggers.setter
    def pull_triggers(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "pullTriggers", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ImageBuild",
    jsii_struct_bases=[],
    name_mapping={
        "path": "path",
        "build_arg": "buildArg",
        "dockerfile": "dockerfile",
        "force_remove": "forceRemove",
        "label": "label",
        "no_cache": "noCache",
        "remove": "remove",
        "tag": "tag",
        "target": "target",
    },
)
class ImageBuild:
    def __init__(
        self,
        *,
        path: builtins.str,
        build_arg: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        force_remove: typing.Optional[builtins.bool] = None,
        label: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        no_cache: typing.Optional[builtins.bool] = None,
        remove: typing.Optional[builtins.bool] = None,
        tag: typing.Optional[typing.Sequence[builtins.str]] = None,
        target: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param path: Context path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#path Image#path}
        :param build_arg: Set build-time variables. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#build_arg Image#build_arg}
        :param dockerfile: Name of the Dockerfile. Defaults to ``Dockerfile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#dockerfile Image#dockerfile}
        :param force_remove: Always remove intermediate containers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#force_remove Image#force_remove}
        :param label: Set metadata for an image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#label Image#label}
        :param no_cache: Do not use cache when building the image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#no_cache Image#no_cache}
        :param remove: Remove intermediate containers after a successful build. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#remove Image#remove}
        :param tag: Name and optionally a tag in the 'name:tag' format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#tag Image#tag}
        :param target: Set the target build stage to build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#target Image#target}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "path": path,
        }
        if build_arg is not None:
            self._values["build_arg"] = build_arg
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if force_remove is not None:
            self._values["force_remove"] = force_remove
        if label is not None:
            self._values["label"] = label
        if no_cache is not None:
            self._values["no_cache"] = no_cache
        if remove is not None:
            self._values["remove"] = remove
        if tag is not None:
            self._values["tag"] = tag
        if target is not None:
            self._values["target"] = target

    @builtins.property
    def path(self) -> builtins.str:
        '''Context path.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#path Image#path}
        '''
        result = self._values.get("path")
        assert result is not None, "Required property 'path' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_arg(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Set build-time variables.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#build_arg Image#build_arg}
        '''
        result = self._values.get("build_arg")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''Name of the Dockerfile. Defaults to ``Dockerfile``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#dockerfile Image#dockerfile}
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def force_remove(self) -> typing.Optional[builtins.bool]:
        '''Always remove intermediate containers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#force_remove Image#force_remove}
        '''
        result = self._values.get("force_remove")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def label(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Set metadata for an image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#label Image#label}
        '''
        result = self._values.get("label")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def no_cache(self) -> typing.Optional[builtins.bool]:
        '''Do not use cache when building the image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#no_cache Image#no_cache}
        '''
        result = self._values.get("no_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def remove(self) -> typing.Optional[builtins.bool]:
        '''Remove intermediate containers after a successful build. Defaults to  ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#remove Image#remove}
        '''
        result = self._values.get("remove")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tag(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Name and optionally a tag in the 'name:tag' format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#tag Image#tag}
        '''
        result = self._values.get("tag")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Set the target build stage to build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#target Image#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageBuild(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "build_attribute": "buildAttribute",
        "force_remove": "forceRemove",
        "keep_locally": "keepLocally",
        "pull_trigger": "pullTrigger",
        "pull_triggers": "pullTriggers",
    },
)
class ImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        build_attribute: typing.Optional[typing.Sequence[ImageBuild]] = None,
        force_remove: typing.Optional[builtins.bool] = None,
        keep_locally: typing.Optional[builtins.bool] = None,
        pull_trigger: typing.Optional[builtins.str] = None,
        pull_triggers: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image, including any tags or SHA256 repo digests. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#name Image#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#build Image#build}
        :param force_remove: If true, then the image is removed forcibly when the resource is destroyed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#force_remove Image#force_remove}
        :param keep_locally: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker local storage on destroy operation. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#keep_locally Image#keep_locally}
        :param pull_trigger: A value which cause an image pull when changed. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#pull_trigger Image#pull_trigger}
        :param pull_triggers: List of values which cause an image pull when changed. This is used to store the image digest from the registry when using the `docker_registry_image <../data-sources/registry_image.md>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#pull_triggers Image#pull_triggers}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if build_attribute is not None:
            self._values["build_attribute"] = build_attribute
        if force_remove is not None:
            self._values["force_remove"] = force_remove
        if keep_locally is not None:
            self._values["keep_locally"] = keep_locally
        if pull_trigger is not None:
            self._values["pull_trigger"] = pull_trigger
        if pull_triggers is not None:
            self._values["pull_triggers"] = pull_triggers

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Docker image, including any tags or SHA256 repo digests.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#name Image#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_attribute(self) -> typing.Optional[typing.List[ImageBuild]]:
        '''build block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#build Image#build}
        '''
        result = self._values.get("build_attribute")
        return typing.cast(typing.Optional[typing.List[ImageBuild]], result)

    @builtins.property
    def force_remove(self) -> typing.Optional[builtins.bool]:
        '''If true, then the image is removed forcibly when the resource is destroyed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#force_remove Image#force_remove}
        '''
        result = self._values.get("force_remove")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def keep_locally(self) -> typing.Optional[builtins.bool]:
        '''If true, then the Docker image won't be deleted on destroy operation.

        If this is false, it will delete the image from the docker local storage on destroy operation.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#keep_locally Image#keep_locally}
        '''
        result = self._values.get("keep_locally")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def pull_trigger(self) -> typing.Optional[builtins.str]:
        '''A value which cause an image pull when changed.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#pull_trigger Image#pull_trigger}
        '''
        result = self._values.get("pull_trigger")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_triggers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of values which cause an image pull when changed.

        This is used to store the image digest from the registry when using the `docker_registry_image <../data-sources/registry_image.md>`_.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/image.html#pull_triggers Image#pull_triggers}
        '''
        result = self._values.get("pull_triggers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Network(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Network",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/network.html docker_network}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        attachable: typing.Optional[builtins.bool] = None,
        check_duplicate: typing.Optional[builtins.bool] = None,
        driver: typing.Optional[builtins.str] = None,
        ingress: typing.Optional[builtins.bool] = None,
        internal: typing.Optional[builtins.bool] = None,
        ipam_config: typing.Optional[typing.Sequence["NetworkIpamConfig"]] = None,
        ipam_driver: typing.Optional[builtins.str] = None,
        ipv6: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence["NetworkLabels"]] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/network.html docker_network} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#name Network#name}
        :param attachable: Enable manual container attachment to the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#attachable Network#attachable}
        :param check_duplicate: Requests daemon to check for networks with same name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#check_duplicate Network#check_duplicate}
        :param driver: The driver of the Docker network. Possible values are ``bridge``, ``host``, ``overlay``, ``macvlan``. See `network docs <https://docs.docker.com/network/#network-drivers>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#driver Network#driver}
        :param ingress: Create swarm routing-mesh network. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ingress Network#ingress}
        :param internal: Whether the network is internal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#internal Network#internal}
        :param ipam_config: ipam_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipam_config Network#ipam_config}
        :param ipam_driver: Driver used by the custom IP scheme of the network. Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipam_driver Network#ipam_driver}
        :param ipv6: Enable IPv6 networking. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipv6 Network#ipv6}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#labels Network#labels}
        :param options: Only available with bridge networks. See `bridge options docs <https://docs.docker.com/engine/reference/commandline/network_create/#bridge-driver-options>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#options Network#options}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = NetworkConfig(
            name=name,
            attachable=attachable,
            check_duplicate=check_duplicate,
            driver=driver,
            ingress=ingress,
            internal=internal,
            ipam_config=ipam_config,
            ipam_driver=ipam_driver,
            ipv6=ipv6,
            labels=labels,
            options=options,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Network, self, [scope, id, config])

    @jsii.member(jsii_name="resetAttachable")
    def reset_attachable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAttachable", []))

    @jsii.member(jsii_name="resetCheckDuplicate")
    def reset_check_duplicate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckDuplicate", []))

    @jsii.member(jsii_name="resetDriver")
    def reset_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriver", []))

    @jsii.member(jsii_name="resetIngress")
    def reset_ingress(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIngress", []))

    @jsii.member(jsii_name="resetInternal")
    def reset_internal(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternal", []))

    @jsii.member(jsii_name="resetIpamConfig")
    def reset_ipam_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpamConfig", []))

    @jsii.member(jsii_name="resetIpamDriver")
    def reset_ipam_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpamDriver", []))

    @jsii.member(jsii_name="resetIpv6")
    def reset_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="scope")
    def scope(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scope"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachableInput")
    def attachable_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "attachableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkDuplicateInput")
    def check_duplicate_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "checkDuplicateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverInput")
    def driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingressInput")
    def ingress_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "ingressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalInput")
    def internal_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "internalInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamConfigInput")
    def ipam_config_input(self) -> typing.Optional[typing.List["NetworkIpamConfig"]]:
        return typing.cast(typing.Optional[typing.List["NetworkIpamConfig"]], jsii.get(self, "ipamConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamDriverInput")
    def ipam_driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ipamDriverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "ipv6Input"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["NetworkLabels"]]:
        return typing.cast(typing.Optional[typing.List["NetworkLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "optionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="attachable")
    def attachable(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "attachable"))

    @attachable.setter
    def attachable(self, value: builtins.bool) -> None:
        jsii.set(self, "attachable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="checkDuplicate")
    def check_duplicate(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "checkDuplicate"))

    @check_duplicate.setter
    def check_duplicate(self, value: builtins.bool) -> None:
        jsii.set(self, "checkDuplicate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driver")
    def driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driver"))

    @driver.setter
    def driver(self, value: builtins.str) -> None:
        jsii.set(self, "driver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ingress")
    def ingress(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "ingress"))

    @ingress.setter
    def ingress(self, value: builtins.bool) -> None:
        jsii.set(self, "ingress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internal")
    def internal(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "internal"))

    @internal.setter
    def internal(self, value: builtins.bool) -> None:
        jsii.set(self, "internal", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamConfig")
    def ipam_config(self) -> typing.List["NetworkIpamConfig"]:
        return typing.cast(typing.List["NetworkIpamConfig"], jsii.get(self, "ipamConfig"))

    @ipam_config.setter
    def ipam_config(self, value: typing.List["NetworkIpamConfig"]) -> None:
        jsii.set(self, "ipamConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipamDriver")
    def ipam_driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipamDriver"))

    @ipam_driver.setter
    def ipam_driver(self, value: builtins.str) -> None:
        jsii.set(self, "ipamDriver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "ipv6"))

    @ipv6.setter
    def ipv6(self, value: builtins.bool) -> None:
        jsii.set(self, "ipv6", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["NetworkLabels"]:
        return typing.cast(typing.List["NetworkLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["NetworkLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="options")
    def options(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "options"))

    @options.setter
    def options(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "options", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.NetworkConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "attachable": "attachable",
        "check_duplicate": "checkDuplicate",
        "driver": "driver",
        "ingress": "ingress",
        "internal": "internal",
        "ipam_config": "ipamConfig",
        "ipam_driver": "ipamDriver",
        "ipv6": "ipv6",
        "labels": "labels",
        "options": "options",
    },
)
class NetworkConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        attachable: typing.Optional[builtins.bool] = None,
        check_duplicate: typing.Optional[builtins.bool] = None,
        driver: typing.Optional[builtins.str] = None,
        ingress: typing.Optional[builtins.bool] = None,
        internal: typing.Optional[builtins.bool] = None,
        ipam_config: typing.Optional[typing.Sequence["NetworkIpamConfig"]] = None,
        ipam_driver: typing.Optional[builtins.str] = None,
        ipv6: typing.Optional[builtins.bool] = None,
        labels: typing.Optional[typing.Sequence["NetworkLabels"]] = None,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#name Network#name}
        :param attachable: Enable manual container attachment to the network. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#attachable Network#attachable}
        :param check_duplicate: Requests daemon to check for networks with same name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#check_duplicate Network#check_duplicate}
        :param driver: The driver of the Docker network. Possible values are ``bridge``, ``host``, ``overlay``, ``macvlan``. See `network docs <https://docs.docker.com/network/#network-drivers>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#driver Network#driver}
        :param ingress: Create swarm routing-mesh network. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ingress Network#ingress}
        :param internal: Whether the network is internal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#internal Network#internal}
        :param ipam_config: ipam_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipam_config Network#ipam_config}
        :param ipam_driver: Driver used by the custom IP scheme of the network. Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipam_driver Network#ipam_driver}
        :param ipv6: Enable IPv6 networking. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipv6 Network#ipv6}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#labels Network#labels}
        :param options: Only available with bridge networks. See `bridge options docs <https://docs.docker.com/engine/reference/commandline/network_create/#bridge-driver-options>`_ for more details. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#options Network#options}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if attachable is not None:
            self._values["attachable"] = attachable
        if check_duplicate is not None:
            self._values["check_duplicate"] = check_duplicate
        if driver is not None:
            self._values["driver"] = driver
        if ingress is not None:
            self._values["ingress"] = ingress
        if internal is not None:
            self._values["internal"] = internal
        if ipam_config is not None:
            self._values["ipam_config"] = ipam_config
        if ipam_driver is not None:
            self._values["ipam_driver"] = ipam_driver
        if ipv6 is not None:
            self._values["ipv6"] = ipv6
        if labels is not None:
            self._values["labels"] = labels
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Docker network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#name Network#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def attachable(self) -> typing.Optional[builtins.bool]:
        '''Enable manual container attachment to the network.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#attachable Network#attachable}
        '''
        result = self._values.get("attachable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def check_duplicate(self) -> typing.Optional[builtins.bool]:
        '''Requests daemon to check for networks with same name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#check_duplicate Network#check_duplicate}
        '''
        result = self._values.get("check_duplicate")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def driver(self) -> typing.Optional[builtins.str]:
        '''The driver of the Docker network. Possible values are ``bridge``, ``host``, ``overlay``, ``macvlan``. See `network docs <https://docs.docker.com/network/#network-drivers>`_ for more details.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#driver Network#driver}
        '''
        result = self._values.get("driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ingress(self) -> typing.Optional[builtins.bool]:
        '''Create swarm routing-mesh network. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ingress Network#ingress}
        '''
        result = self._values.get("ingress")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def internal(self) -> typing.Optional[builtins.bool]:
        '''Whether the network is internal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#internal Network#internal}
        '''
        result = self._values.get("internal")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def ipam_config(self) -> typing.Optional[typing.List["NetworkIpamConfig"]]:
        '''ipam_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipam_config Network#ipam_config}
        '''
        result = self._values.get("ipam_config")
        return typing.cast(typing.Optional[typing.List["NetworkIpamConfig"]], result)

    @builtins.property
    def ipam_driver(self) -> typing.Optional[builtins.str]:
        '''Driver used by the custom IP scheme of the network. Defaults to ``default``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipam_driver Network#ipam_driver}
        '''
        result = self._values.get("ipam_driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ipv6(self) -> typing.Optional[builtins.bool]:
        '''Enable IPv6 networking. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ipv6 Network#ipv6}
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["NetworkLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#labels Network#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["NetworkLabels"]], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Only available with bridge networks. See `bridge options docs <https://docs.docker.com/engine/reference/commandline/network_create/#bridge-driver-options>`_ for more details.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#options Network#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.NetworkIpamConfig",
    jsii_struct_bases=[],
    name_mapping={
        "aux_address": "auxAddress",
        "gateway": "gateway",
        "ip_range": "ipRange",
        "subnet": "subnet",
    },
)
class NetworkIpamConfig:
    def __init__(
        self,
        *,
        aux_address: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        gateway: typing.Optional[builtins.str] = None,
        ip_range: typing.Optional[builtins.str] = None,
        subnet: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param aux_address: Auxiliary IPv4 or IPv6 addresses used by Network driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#aux_address Network#aux_address}
        :param gateway: The IP address of the gateway. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#gateway Network#gateway}
        :param ip_range: The ip range in CIDR form. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ip_range Network#ip_range}
        :param subnet: The subnet in CIDR form. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#subnet Network#subnet}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if aux_address is not None:
            self._values["aux_address"] = aux_address
        if gateway is not None:
            self._values["gateway"] = gateway
        if ip_range is not None:
            self._values["ip_range"] = ip_range
        if subnet is not None:
            self._values["subnet"] = subnet

    @builtins.property
    def aux_address(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Auxiliary IPv4 or IPv6 addresses used by Network driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#aux_address Network#aux_address}
        '''
        result = self._values.get("aux_address")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def gateway(self) -> typing.Optional[builtins.str]:
        '''The IP address of the gateway.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#gateway Network#gateway}
        '''
        result = self._values.get("gateway")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ip_range(self) -> typing.Optional[builtins.str]:
        '''The ip range in CIDR form.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#ip_range Network#ip_range}
        '''
        result = self._values.get("ip_range")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subnet(self) -> typing.Optional[builtins.str]:
        '''The subnet in CIDR form.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#subnet Network#subnet}
        '''
        result = self._values.get("subnet")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkIpamConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.NetworkLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class NetworkLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#label Network#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#value Network#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#label Network#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/network.html#value Network#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Plugin(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Plugin",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/plugin.html docker_plugin}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_timeout: typing.Optional[jsii.Number] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_destroy: typing.Optional[builtins.bool] = None,
        force_disable: typing.Optional[builtins.bool] = None,
        grant_all_permissions: typing.Optional[builtins.bool] = None,
        grant_permissions: typing.Optional[typing.Sequence["PluginGrantPermissions"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/plugin.html docker_plugin} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docker Plugin name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#name Plugin#name}
        :param alias: Docker Plugin alias. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#alias Plugin#alias}
        :param enabled: If ``true`` the plugin is enabled. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#enabled Plugin#enabled}
        :param enable_timeout: HTTP client timeout to enable the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#enable_timeout Plugin#enable_timeout}
        :param env: The environment variables in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#env Plugin#env}
        :param force_destroy: If true, then the plugin is destroyed forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#force_destroy Plugin#force_destroy}
        :param force_disable: If true, then the plugin is disabled forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#force_disable Plugin#force_disable}
        :param grant_all_permissions: If true, grant all permissions necessary to run the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#grant_all_permissions Plugin#grant_all_permissions}
        :param grant_permissions: grant_permissions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#grant_permissions Plugin#grant_permissions}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PluginConfig(
            name=name,
            alias=alias,
            enabled=enabled,
            enable_timeout=enable_timeout,
            env=env,
            force_destroy=force_destroy,
            force_disable=force_disable,
            grant_all_permissions=grant_all_permissions,
            grant_permissions=grant_permissions,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Plugin, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetEnableTimeout")
    def reset_enable_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableTimeout", []))

    @jsii.member(jsii_name="resetEnv")
    def reset_env(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnv", []))

    @jsii.member(jsii_name="resetForceDestroy")
    def reset_force_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDestroy", []))

    @jsii.member(jsii_name="resetForceDisable")
    def reset_force_disable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForceDisable", []))

    @jsii.member(jsii_name="resetGrantAllPermissions")
    def reset_grant_all_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrantAllPermissions", []))

    @jsii.member(jsii_name="resetGrantPermissions")
    def reset_grant_permissions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGrantPermissions", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="pluginReference")
    def plugin_reference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pluginReference"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "enabledInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTimeoutInput")
    def enable_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "enableTimeoutInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="envInput")
    def env_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "envInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroyInput")
    def force_destroy_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "forceDestroyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDisableInput")
    def force_disable_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "forceDisableInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantAllPermissionsInput")
    def grant_all_permissions_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "grantAllPermissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPermissionsInput")
    def grant_permissions_input(
        self,
    ) -> typing.Optional[typing.List["PluginGrantPermissions"]]:
        return typing.cast(typing.Optional[typing.List["PluginGrantPermissions"]], jsii.get(self, "grantPermissionsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: builtins.str) -> None:
        jsii.set(self, "alias", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(self, value: builtins.bool) -> None:
        jsii.set(self, "enabled", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="enableTimeout")
    def enable_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "enableTimeout"))

    @enable_timeout.setter
    def enable_timeout(self, value: jsii.Number) -> None:
        jsii.set(self, "enableTimeout", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="env")
    def env(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "env"))

    @env.setter
    def env(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "env", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDestroy")
    def force_destroy(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "forceDestroy"))

    @force_destroy.setter
    def force_destroy(self, value: builtins.bool) -> None:
        jsii.set(self, "forceDestroy", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="forceDisable")
    def force_disable(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "forceDisable"))

    @force_disable.setter
    def force_disable(self, value: builtins.bool) -> None:
        jsii.set(self, "forceDisable", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantAllPermissions")
    def grant_all_permissions(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "grantAllPermissions"))

    @grant_all_permissions.setter
    def grant_all_permissions(self, value: builtins.bool) -> None:
        jsii.set(self, "grantAllPermissions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="grantPermissions")
    def grant_permissions(self) -> typing.List["PluginGrantPermissions"]:
        return typing.cast(typing.List["PluginGrantPermissions"], jsii.get(self, "grantPermissions"))

    @grant_permissions.setter
    def grant_permissions(self, value: typing.List["PluginGrantPermissions"]) -> None:
        jsii.set(self, "grantPermissions", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.PluginConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "alias": "alias",
        "enabled": "enabled",
        "enable_timeout": "enableTimeout",
        "env": "env",
        "force_destroy": "forceDestroy",
        "force_disable": "forceDisable",
        "grant_all_permissions": "grantAllPermissions",
        "grant_permissions": "grantPermissions",
    },
)
class PluginConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        alias: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[builtins.bool] = None,
        enable_timeout: typing.Optional[jsii.Number] = None,
        env: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_destroy: typing.Optional[builtins.bool] = None,
        force_disable: typing.Optional[builtins.bool] = None,
        grant_all_permissions: typing.Optional[builtins.bool] = None,
        grant_permissions: typing.Optional[typing.Sequence["PluginGrantPermissions"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Docker Plugin name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#name Plugin#name}
        :param alias: Docker Plugin alias. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#alias Plugin#alias}
        :param enabled: If ``true`` the plugin is enabled. Defaults to ``true``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#enabled Plugin#enabled}
        :param enable_timeout: HTTP client timeout to enable the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#enable_timeout Plugin#enable_timeout}
        :param env: The environment variables in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#env Plugin#env}
        :param force_destroy: If true, then the plugin is destroyed forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#force_destroy Plugin#force_destroy}
        :param force_disable: If true, then the plugin is disabled forcibly. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#force_disable Plugin#force_disable}
        :param grant_all_permissions: If true, grant all permissions necessary to run the plugin. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#grant_all_permissions Plugin#grant_all_permissions}
        :param grant_permissions: grant_permissions block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#grant_permissions Plugin#grant_permissions}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if alias is not None:
            self._values["alias"] = alias
        if enabled is not None:
            self._values["enabled"] = enabled
        if enable_timeout is not None:
            self._values["enable_timeout"] = enable_timeout
        if env is not None:
            self._values["env"] = env
        if force_destroy is not None:
            self._values["force_destroy"] = force_destroy
        if force_disable is not None:
            self._values["force_disable"] = force_disable
        if grant_all_permissions is not None:
            self._values["grant_all_permissions"] = grant_all_permissions
        if grant_permissions is not None:
            self._values["grant_permissions"] = grant_permissions

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docker Plugin name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#name Plugin#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Docker Plugin alias.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#alias Plugin#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(self) -> typing.Optional[builtins.bool]:
        '''If ``true`` the plugin is enabled. Defaults to ``true``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#enabled Plugin#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_timeout(self) -> typing.Optional[jsii.Number]:
        '''HTTP client timeout to enable the plugin.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#enable_timeout Plugin#enable_timeout}
        '''
        result = self._values.get("enable_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The environment variables in the form of ``KEY=VALUE``, e.g. ``DEBUG=0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#env Plugin#env}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def force_destroy(self) -> typing.Optional[builtins.bool]:
        '''If true, then the plugin is destroyed forcibly.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#force_destroy Plugin#force_destroy}
        '''
        result = self._values.get("force_destroy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def force_disable(self) -> typing.Optional[builtins.bool]:
        '''If true, then the plugin is disabled forcibly.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#force_disable Plugin#force_disable}
        '''
        result = self._values.get("force_disable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def grant_all_permissions(self) -> typing.Optional[builtins.bool]:
        '''If true, grant all permissions necessary to run the plugin.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#grant_all_permissions Plugin#grant_all_permissions}
        '''
        result = self._values.get("grant_all_permissions")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def grant_permissions(
        self,
    ) -> typing.Optional[typing.List["PluginGrantPermissions"]]:
        '''grant_permissions block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#grant_permissions Plugin#grant_permissions}
        '''
        result = self._values.get("grant_permissions")
        return typing.cast(typing.Optional[typing.List["PluginGrantPermissions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.PluginGrantPermissions",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class PluginGrantPermissions:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param name: The name of the permission. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#name Plugin#name}
        :param value: The value of the permission. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#value Plugin#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the permission.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#name Plugin#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> typing.List[builtins.str]:
        '''The value of the permission.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/plugin.html#value Plugin#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PluginGrantPermissions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RegistryImage(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.RegistryImage",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html docker_registry_image}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        build_attribute: typing.Optional[typing.Sequence["RegistryImageBuild"]] = None,
        insecure_skip_verify: typing.Optional[builtins.bool] = None,
        keep_remotely: typing.Optional[builtins.bool] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html docker_registry_image} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: The name of the Docker image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#name RegistryImage#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build RegistryImage#build}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#insecure_skip_verify RegistryImage#insecure_skip_verify}
        :param keep_remotely: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker registry on destroy operation. Defaults to ``false`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#keep_remotely RegistryImage#keep_remotely}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = RegistryImageConfig(
            name=name,
            build_attribute=build_attribute,
            insecure_skip_verify=insecure_skip_verify,
            keep_remotely=keep_remotely,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(RegistryImage, self, [scope, id, config])

    @jsii.member(jsii_name="resetBuildAttribute")
    def reset_build_attribute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBuildAttribute", []))

    @jsii.member(jsii_name="resetInsecureSkipVerify")
    def reset_insecure_skip_verify(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInsecureSkipVerify", []))

    @jsii.member(jsii_name="resetKeepRemotely")
    def reset_keep_remotely(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeepRemotely", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha256Digest")
    def sha256_digest(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha256Digest"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttributeInput")
    def build_attribute_input(
        self,
    ) -> typing.Optional[typing.List["RegistryImageBuild"]]:
        return typing.cast(typing.Optional[typing.List["RegistryImageBuild"]], jsii.get(self, "buildAttributeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerifyInput")
    def insecure_skip_verify_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "insecureSkipVerifyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepRemotelyInput")
    def keep_remotely_input(self) -> typing.Optional[builtins.bool]:
        return typing.cast(typing.Optional[builtins.bool], jsii.get(self, "keepRemotelyInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="buildAttribute")
    def build_attribute(self) -> typing.List["RegistryImageBuild"]:
        return typing.cast(typing.List["RegistryImageBuild"], jsii.get(self, "buildAttribute"))

    @build_attribute.setter
    def build_attribute(self, value: typing.List["RegistryImageBuild"]) -> None:
        jsii.set(self, "buildAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="insecureSkipVerify")
    def insecure_skip_verify(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "insecureSkipVerify"))

    @insecure_skip_verify.setter
    def insecure_skip_verify(self, value: builtins.bool) -> None:
        jsii.set(self, "insecureSkipVerify", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keepRemotely")
    def keep_remotely(self) -> builtins.bool:
        return typing.cast(builtins.bool, jsii.get(self, "keepRemotely"))

    @keep_remotely.setter
    def keep_remotely(self, value: builtins.bool) -> None:
        jsii.set(self, "keepRemotely", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageBuild",
    jsii_struct_bases=[],
    name_mapping={
        "context": "context",
        "auth_config": "authConfig",
        "build_args": "buildArgs",
        "build_id": "buildId",
        "cache_from": "cacheFrom",
        "cgroup_parent": "cgroupParent",
        "cpu_period": "cpuPeriod",
        "cpu_quota": "cpuQuota",
        "cpu_set_cpus": "cpuSetCpus",
        "cpu_set_mems": "cpuSetMems",
        "cpu_shares": "cpuShares",
        "dockerfile": "dockerfile",
        "extra_hosts": "extraHosts",
        "force_remove": "forceRemove",
        "isolation": "isolation",
        "labels": "labels",
        "memory": "memory",
        "memory_swap": "memorySwap",
        "network_mode": "networkMode",
        "no_cache": "noCache",
        "platform": "platform",
        "pull_parent": "pullParent",
        "remote_context": "remoteContext",
        "remove": "remove",
        "security_opt": "securityOpt",
        "session_id": "sessionId",
        "shm_size": "shmSize",
        "squash": "squash",
        "suppress_output": "suppressOutput",
        "target": "target",
        "ulimit": "ulimit",
        "version": "version",
    },
)
class RegistryImageBuild:
    def __init__(
        self,
        *,
        context: builtins.str,
        auth_config: typing.Optional[typing.Sequence["RegistryImageBuildAuthConfig"]] = None,
        build_args: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        build_id: typing.Optional[builtins.str] = None,
        cache_from: typing.Optional[typing.Sequence[builtins.str]] = None,
        cgroup_parent: typing.Optional[builtins.str] = None,
        cpu_period: typing.Optional[jsii.Number] = None,
        cpu_quota: typing.Optional[jsii.Number] = None,
        cpu_set_cpus: typing.Optional[builtins.str] = None,
        cpu_set_mems: typing.Optional[builtins.str] = None,
        cpu_shares: typing.Optional[jsii.Number] = None,
        dockerfile: typing.Optional[builtins.str] = None,
        extra_hosts: typing.Optional[typing.Sequence[builtins.str]] = None,
        force_remove: typing.Optional[builtins.bool] = None,
        isolation: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        memory: typing.Optional[jsii.Number] = None,
        memory_swap: typing.Optional[jsii.Number] = None,
        network_mode: typing.Optional[builtins.str] = None,
        no_cache: typing.Optional[builtins.bool] = None,
        platform: typing.Optional[builtins.str] = None,
        pull_parent: typing.Optional[builtins.bool] = None,
        remote_context: typing.Optional[builtins.str] = None,
        remove: typing.Optional[builtins.bool] = None,
        security_opt: typing.Optional[typing.Sequence[builtins.str]] = None,
        session_id: typing.Optional[builtins.str] = None,
        shm_size: typing.Optional[jsii.Number] = None,
        squash: typing.Optional[builtins.bool] = None,
        suppress_output: typing.Optional[builtins.bool] = None,
        target: typing.Optional[builtins.str] = None,
        ulimit: typing.Optional[typing.Sequence["RegistryImageBuildUlimit"]] = None,
        version: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param context: The absolute path to the context folder. You can use the helper function '${path.cwd}/context-dir'. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#context RegistryImage#context}
        :param auth_config: auth_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#auth_config RegistryImage#auth_config}
        :param build_args: Pairs for build-time variables in the form TODO. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build_args RegistryImage#build_args}
        :param build_id: BuildID is an optional identifier that can be passed together with the build request. The. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build_id RegistryImage#build_id}
        :param cache_from: Images to consider as cache sources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cache_from RegistryImage#cache_from}
        :param cgroup_parent: Optional parent cgroup for the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cgroup_parent RegistryImage#cgroup_parent}
        :param cpu_period: The length of a CPU period in microseconds. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_period RegistryImage#cpu_period}
        :param cpu_quota: Microseconds of CPU time that the container can get in a CPU period. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_quota RegistryImage#cpu_quota}
        :param cpu_set_cpus: CPUs in which to allow execution (e.g., ``0-3``, ``0``, ``1``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_set_cpus RegistryImage#cpu_set_cpus}
        :param cpu_set_mems: MEMs in which to allow execution (``0-3``, ``0``, ``1``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_set_mems RegistryImage#cpu_set_mems}
        :param cpu_shares: CPU shares (relative weight). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_shares RegistryImage#cpu_shares}
        :param dockerfile: Dockerfile file. Defaults to ``Dockerfile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#dockerfile RegistryImage#dockerfile}
        :param extra_hosts: A list of hostnames/IP mappings to add to the container’s /etc/hosts file. Specified in the form ["hostname:IP"]. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#extra_hosts RegistryImage#extra_hosts}
        :param force_remove: Always remove intermediate containers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#force_remove RegistryImage#force_remove}
        :param isolation: Isolation represents the isolation technology of a container. The supported values are. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#isolation RegistryImage#isolation}
        :param labels: User-defined key/value metadata. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#labels RegistryImage#labels}
        :param memory: Set memory limit for build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#memory RegistryImage#memory}
        :param memory_swap: Total memory (memory + swap), -1 to enable unlimited swap. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#memory_swap RegistryImage#memory_swap}
        :param network_mode: Set the networking mode for the RUN instructions during build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#network_mode RegistryImage#network_mode}
        :param no_cache: Do not use the cache when building the image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#no_cache RegistryImage#no_cache}
        :param platform: Set platform if server is multi-platform capable. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#platform RegistryImage#platform}
        :param pull_parent: Attempt to pull the image even if an older image exists locally. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#pull_parent RegistryImage#pull_parent}
        :param remote_context: A Git repository URI or HTTP/HTTPS context URI. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#remote_context RegistryImage#remote_context}
        :param remove: Remove intermediate containers after a successful build (default behavior). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#remove RegistryImage#remove}
        :param security_opt: The security options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#security_opt RegistryImage#security_opt}
        :param session_id: Set an ID for the build session. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#session_id RegistryImage#session_id}
        :param shm_size: Size of /dev/shm in bytes. The size must be greater than 0. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#shm_size RegistryImage#shm_size}
        :param squash: If true the new layers are squashed into a new image with a single new layer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#squash RegistryImage#squash}
        :param suppress_output: Suppress the build output and print image ID on success. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#suppress_output RegistryImage#suppress_output}
        :param target: Set the target build stage to build. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#target RegistryImage#target}
        :param ulimit: ulimit block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#ulimit RegistryImage#ulimit}
        :param version: Version of the unerlying builder to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#version RegistryImage#version}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "context": context,
        }
        if auth_config is not None:
            self._values["auth_config"] = auth_config
        if build_args is not None:
            self._values["build_args"] = build_args
        if build_id is not None:
            self._values["build_id"] = build_id
        if cache_from is not None:
            self._values["cache_from"] = cache_from
        if cgroup_parent is not None:
            self._values["cgroup_parent"] = cgroup_parent
        if cpu_period is not None:
            self._values["cpu_period"] = cpu_period
        if cpu_quota is not None:
            self._values["cpu_quota"] = cpu_quota
        if cpu_set_cpus is not None:
            self._values["cpu_set_cpus"] = cpu_set_cpus
        if cpu_set_mems is not None:
            self._values["cpu_set_mems"] = cpu_set_mems
        if cpu_shares is not None:
            self._values["cpu_shares"] = cpu_shares
        if dockerfile is not None:
            self._values["dockerfile"] = dockerfile
        if extra_hosts is not None:
            self._values["extra_hosts"] = extra_hosts
        if force_remove is not None:
            self._values["force_remove"] = force_remove
        if isolation is not None:
            self._values["isolation"] = isolation
        if labels is not None:
            self._values["labels"] = labels
        if memory is not None:
            self._values["memory"] = memory
        if memory_swap is not None:
            self._values["memory_swap"] = memory_swap
        if network_mode is not None:
            self._values["network_mode"] = network_mode
        if no_cache is not None:
            self._values["no_cache"] = no_cache
        if platform is not None:
            self._values["platform"] = platform
        if pull_parent is not None:
            self._values["pull_parent"] = pull_parent
        if remote_context is not None:
            self._values["remote_context"] = remote_context
        if remove is not None:
            self._values["remove"] = remove
        if security_opt is not None:
            self._values["security_opt"] = security_opt
        if session_id is not None:
            self._values["session_id"] = session_id
        if shm_size is not None:
            self._values["shm_size"] = shm_size
        if squash is not None:
            self._values["squash"] = squash
        if suppress_output is not None:
            self._values["suppress_output"] = suppress_output
        if target is not None:
            self._values["target"] = target
        if ulimit is not None:
            self._values["ulimit"] = ulimit
        if version is not None:
            self._values["version"] = version

    @builtins.property
    def context(self) -> builtins.str:
        '''The absolute path to the context folder. You can use the helper function '${path.cwd}/context-dir'.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#context RegistryImage#context}
        '''
        result = self._values.get("context")
        assert result is not None, "Required property 'context' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth_config(
        self,
    ) -> typing.Optional[typing.List["RegistryImageBuildAuthConfig"]]:
        '''auth_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#auth_config RegistryImage#auth_config}
        '''
        result = self._values.get("auth_config")
        return typing.cast(typing.Optional[typing.List["RegistryImageBuildAuthConfig"]], result)

    @builtins.property
    def build_args(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Pairs for build-time variables in the form TODO.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build_args RegistryImage#build_args}
        '''
        result = self._values.get("build_args")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def build_id(self) -> typing.Optional[builtins.str]:
        '''BuildID is an optional identifier that can be passed together with the build request. The.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build_id RegistryImage#build_id}
        '''
        result = self._values.get("build_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cache_from(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Images to consider as cache sources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cache_from RegistryImage#cache_from}
        '''
        result = self._values.get("cache_from")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def cgroup_parent(self) -> typing.Optional[builtins.str]:
        '''Optional parent cgroup for the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cgroup_parent RegistryImage#cgroup_parent}
        '''
        result = self._values.get("cgroup_parent")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_period(self) -> typing.Optional[jsii.Number]:
        '''The length of a CPU period in microseconds.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_period RegistryImage#cpu_period}
        '''
        result = self._values.get("cpu_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_quota(self) -> typing.Optional[jsii.Number]:
        '''Microseconds of CPU time that the container can get in a CPU period.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_quota RegistryImage#cpu_quota}
        '''
        result = self._values.get("cpu_quota")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cpu_set_cpus(self) -> typing.Optional[builtins.str]:
        '''CPUs in which to allow execution (e.g., ``0-3``, ``0``, ``1``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_set_cpus RegistryImage#cpu_set_cpus}
        '''
        result = self._values.get("cpu_set_cpus")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_set_mems(self) -> typing.Optional[builtins.str]:
        '''MEMs in which to allow execution (``0-3``, ``0``, ``1``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_set_mems RegistryImage#cpu_set_mems}
        '''
        result = self._values.get("cpu_set_mems")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cpu_shares(self) -> typing.Optional[jsii.Number]:
        '''CPU shares (relative weight).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#cpu_shares RegistryImage#cpu_shares}
        '''
        result = self._values.get("cpu_shares")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def dockerfile(self) -> typing.Optional[builtins.str]:
        '''Dockerfile file. Defaults to ``Dockerfile``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#dockerfile RegistryImage#dockerfile}
        '''
        result = self._values.get("dockerfile")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def extra_hosts(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of hostnames/IP mappings to add to the container’s /etc/hosts file. Specified in the form ["hostname:IP"].

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#extra_hosts RegistryImage#extra_hosts}
        '''
        result = self._values.get("extra_hosts")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def force_remove(self) -> typing.Optional[builtins.bool]:
        '''Always remove intermediate containers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#force_remove RegistryImage#force_remove}
        '''
        result = self._values.get("force_remove")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def isolation(self) -> typing.Optional[builtins.str]:
        '''Isolation represents the isolation technology of a container. The supported values are.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#isolation RegistryImage#isolation}
        '''
        result = self._values.get("isolation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''User-defined key/value metadata.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#labels RegistryImage#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def memory(self) -> typing.Optional[jsii.Number]:
        '''Set memory limit for build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#memory RegistryImage#memory}
        '''
        result = self._values.get("memory")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def memory_swap(self) -> typing.Optional[jsii.Number]:
        '''Total memory (memory + swap), -1 to enable unlimited swap.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#memory_swap RegistryImage#memory_swap}
        '''
        result = self._values.get("memory_swap")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def network_mode(self) -> typing.Optional[builtins.str]:
        '''Set the networking mode for the RUN instructions during build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#network_mode RegistryImage#network_mode}
        '''
        result = self._values.get("network_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_cache(self) -> typing.Optional[builtins.bool]:
        '''Do not use the cache when building the image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#no_cache RegistryImage#no_cache}
        '''
        result = self._values.get("no_cache")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def platform(self) -> typing.Optional[builtins.str]:
        '''Set platform if server is multi-platform capable.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#platform RegistryImage#platform}
        '''
        result = self._values.get("platform")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pull_parent(self) -> typing.Optional[builtins.bool]:
        '''Attempt to pull the image even if an older image exists locally.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#pull_parent RegistryImage#pull_parent}
        '''
        result = self._values.get("pull_parent")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def remote_context(self) -> typing.Optional[builtins.str]:
        '''A Git repository URI or HTTP/HTTPS context URI.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#remote_context RegistryImage#remote_context}
        '''
        result = self._values.get("remote_context")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def remove(self) -> typing.Optional[builtins.bool]:
        '''Remove intermediate containers after a successful build (default behavior).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#remove RegistryImage#remove}
        '''
        result = self._values.get("remove")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def security_opt(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The security options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#security_opt RegistryImage#security_opt}
        '''
        result = self._values.get("security_opt")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def session_id(self) -> typing.Optional[builtins.str]:
        '''Set an ID for the build session.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#session_id RegistryImage#session_id}
        '''
        result = self._values.get("session_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shm_size(self) -> typing.Optional[jsii.Number]:
        '''Size of /dev/shm in bytes. The size must be greater than 0.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#shm_size RegistryImage#shm_size}
        '''
        result = self._values.get("shm_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def squash(self) -> typing.Optional[builtins.bool]:
        '''If true the new layers are squashed into a new image with a single new layer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#squash RegistryImage#squash}
        '''
        result = self._values.get("squash")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def suppress_output(self) -> typing.Optional[builtins.bool]:
        '''Suppress the build output and print image ID on success.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#suppress_output RegistryImage#suppress_output}
        '''
        result = self._values.get("suppress_output")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def target(self) -> typing.Optional[builtins.str]:
        '''Set the target build stage to build.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#target RegistryImage#target}
        '''
        result = self._values.get("target")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ulimit(self) -> typing.Optional[typing.List["RegistryImageBuildUlimit"]]:
        '''ulimit block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#ulimit RegistryImage#ulimit}
        '''
        result = self._values.get("ulimit")
        return typing.cast(typing.Optional[typing.List["RegistryImageBuildUlimit"]], result)

    @builtins.property
    def version(self) -> typing.Optional[builtins.str]:
        '''Version of the unerlying builder to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#version RegistryImage#version}
        '''
        result = self._values.get("version")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageBuild(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageBuildAuthConfig",
    jsii_struct_bases=[],
    name_mapping={
        "host_name": "hostName",
        "auth": "auth",
        "email": "email",
        "identity_token": "identityToken",
        "password": "password",
        "registry_token": "registryToken",
        "server_address": "serverAddress",
        "user_name": "userName",
    },
)
class RegistryImageBuildAuthConfig:
    def __init__(
        self,
        *,
        host_name: builtins.str,
        auth: typing.Optional[builtins.str] = None,
        email: typing.Optional[builtins.str] = None,
        identity_token: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        registry_token: typing.Optional[builtins.str] = None,
        server_address: typing.Optional[builtins.str] = None,
        user_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param host_name: hostname of the registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#host_name RegistryImage#host_name}
        :param auth: the auth token. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#auth RegistryImage#auth}
        :param email: the user emal. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#email RegistryImage#email}
        :param identity_token: the identity token. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#identity_token RegistryImage#identity_token}
        :param password: the registry password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#password RegistryImage#password}
        :param registry_token: the registry token. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#registry_token RegistryImage#registry_token}
        :param server_address: the server address. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#server_address RegistryImage#server_address}
        :param user_name: the registry user name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#user_name RegistryImage#user_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host_name": host_name,
        }
        if auth is not None:
            self._values["auth"] = auth
        if email is not None:
            self._values["email"] = email
        if identity_token is not None:
            self._values["identity_token"] = identity_token
        if password is not None:
            self._values["password"] = password
        if registry_token is not None:
            self._values["registry_token"] = registry_token
        if server_address is not None:
            self._values["server_address"] = server_address
        if user_name is not None:
            self._values["user_name"] = user_name

    @builtins.property
    def host_name(self) -> builtins.str:
        '''hostname of the registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#host_name RegistryImage#host_name}
        '''
        result = self._values.get("host_name")
        assert result is not None, "Required property 'host_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auth(self) -> typing.Optional[builtins.str]:
        '''the auth token.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#auth RegistryImage#auth}
        '''
        result = self._values.get("auth")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email(self) -> typing.Optional[builtins.str]:
        '''the user emal.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#email RegistryImage#email}
        '''
        result = self._values.get("email")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_token(self) -> typing.Optional[builtins.str]:
        '''the identity token.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#identity_token RegistryImage#identity_token}
        '''
        result = self._values.get("identity_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''the registry password.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#password RegistryImage#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry_token(self) -> typing.Optional[builtins.str]:
        '''the registry token.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#registry_token RegistryImage#registry_token}
        '''
        result = self._values.get("registry_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def server_address(self) -> typing.Optional[builtins.str]:
        '''the server address.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#server_address RegistryImage#server_address}
        '''
        result = self._values.get("server_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_name(self) -> typing.Optional[builtins.str]:
        '''the registry user name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#user_name RegistryImage#user_name}
        '''
        result = self._values.get("user_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageBuildAuthConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageBuildUlimit",
    jsii_struct_bases=[],
    name_mapping={"hard": "hard", "name": "name", "soft": "soft"},
)
class RegistryImageBuildUlimit:
    def __init__(
        self,
        *,
        hard: jsii.Number,
        name: builtins.str,
        soft: jsii.Number,
    ) -> None:
        '''
        :param hard: soft limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#hard RegistryImage#hard}
        :param name: type of ulimit, e.g. ``nofile``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#name RegistryImage#name}
        :param soft: hard limit. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#soft RegistryImage#soft}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "hard": hard,
            "name": name,
            "soft": soft,
        }

    @builtins.property
    def hard(self) -> jsii.Number:
        '''soft limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#hard RegistryImage#hard}
        '''
        result = self._values.get("hard")
        assert result is not None, "Required property 'hard' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''type of ulimit, e.g. ``nofile``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#name RegistryImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def soft(self) -> jsii.Number:
        '''hard limit.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#soft RegistryImage#soft}
        '''
        result = self._values.get("soft")
        assert result is not None, "Required property 'soft' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageBuildUlimit(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.RegistryImageConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "build_attribute": "buildAttribute",
        "insecure_skip_verify": "insecureSkipVerify",
        "keep_remotely": "keepRemotely",
    },
)
class RegistryImageConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        build_attribute: typing.Optional[typing.Sequence[RegistryImageBuild]] = None,
        insecure_skip_verify: typing.Optional[builtins.bool] = None,
        keep_remotely: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: The name of the Docker image. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#name RegistryImage#name}
        :param build_attribute: build block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build RegistryImage#build}
        :param insecure_skip_verify: If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#insecure_skip_verify RegistryImage#insecure_skip_verify}
        :param keep_remotely: If true, then the Docker image won't be deleted on destroy operation. If this is false, it will delete the image from the docker registry on destroy operation. Defaults to ``false`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#keep_remotely RegistryImage#keep_remotely}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if build_attribute is not None:
            self._values["build_attribute"] = build_attribute
        if insecure_skip_verify is not None:
            self._values["insecure_skip_verify"] = insecure_skip_verify
        if keep_remotely is not None:
            self._values["keep_remotely"] = keep_remotely

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Docker image.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#name RegistryImage#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def build_attribute(self) -> typing.Optional[typing.List[RegistryImageBuild]]:
        '''build block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#build RegistryImage#build}
        '''
        result = self._values.get("build_attribute")
        return typing.cast(typing.Optional[typing.List[RegistryImageBuild]], result)

    @builtins.property
    def insecure_skip_verify(self) -> typing.Optional[builtins.bool]:
        '''If ``true``, the verification of TLS certificates of the server/registry is disabled. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#insecure_skip_verify RegistryImage#insecure_skip_verify}
        '''
        result = self._values.get("insecure_skip_verify")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def keep_remotely(self) -> typing.Optional[builtins.bool]:
        '''If true, then the Docker image won't be deleted on destroy operation.

        If this is false, it will delete the image from the docker registry on destroy operation. Defaults to ``false``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/registry_image.html#keep_remotely RegistryImage#keep_remotely}
        '''
        result = self._values.get("keep_remotely")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistryImageConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Secret(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Secret",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/secret.html docker_secret}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        data: builtins.str,
        name: builtins.str,
        labels: typing.Optional[typing.Sequence["SecretLabels"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/secret.html docker_secret} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param data: Base64-url-safe-encoded secret data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#data Secret#data}
        :param name: User-defined name of the secret. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#name Secret#name}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#labels Secret#labels}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SecretConfig(
            data=data,
            name=name,
            labels=labels,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Secret, self, [scope, id, config])

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dataInput")
    def data_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dataInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["SecretLabels"]]:
        return typing.cast(typing.Optional[typing.List["SecretLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="data")
    def data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "data"))

    @data.setter
    def data(self, value: builtins.str) -> None:
        jsii.set(self, "data", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["SecretLabels"]:
        return typing.cast(typing.List["SecretLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["SecretLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.SecretConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "data": "data",
        "name": "name",
        "labels": "labels",
    },
)
class SecretConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        data: builtins.str,
        name: builtins.str,
        labels: typing.Optional[typing.Sequence["SecretLabels"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param data: Base64-url-safe-encoded secret data. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#data Secret#data}
        :param name: User-defined name of the secret. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#name Secret#name}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#labels Secret#labels}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "data": data,
            "name": name,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if labels is not None:
            self._values["labels"] = labels

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def data(self) -> builtins.str:
        '''Base64-url-safe-encoded secret data.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#data Secret#data}
        '''
        result = self._values.get("data")
        assert result is not None, "Required property 'data' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''User-defined name of the secret.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#name Secret#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["SecretLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#labels Secret#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["SecretLabels"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.SecretLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class SecretLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#label Secret#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#value Secret#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#label Secret#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/secret.html#value Secret#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SecretLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Service(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Service",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/service.html docker_service}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        task_spec: typing.Sequence["ServiceTaskSpec"],
        auth: typing.Optional[typing.Sequence["ServiceAuth"]] = None,
        converge_config: typing.Optional[typing.Sequence["ServiceConvergeConfig"]] = None,
        endpoint_spec: typing.Optional[typing.Sequence["ServiceEndpointSpec"]] = None,
        labels: typing.Optional[typing.Sequence["ServiceLabels"]] = None,
        mode: typing.Optional[typing.Sequence["ServiceMode"]] = None,
        rollback_config: typing.Optional[typing.Sequence["ServiceRollbackConfig"]] = None,
        update_config: typing.Optional[typing.Sequence["ServiceUpdateConfig"]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/service.html docker_service} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Name of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        :param task_spec: task_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#task_spec Service#task_spec}
        :param auth: auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#auth Service#auth}
        :param converge_config: converge_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#converge_config Service#converge_config}
        :param endpoint_spec: endpoint_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#endpoint_spec Service#endpoint_spec}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        :param mode: mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        :param rollback_config: rollback_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#rollback_config Service#rollback_config}
        :param update_config: update_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#update_config Service#update_config}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = ServiceConfig(
            name=name,
            task_spec=task_spec,
            auth=auth,
            converge_config=converge_config,
            endpoint_spec=endpoint_spec,
            labels=labels,
            mode=mode,
            rollback_config=rollback_config,
            update_config=update_config,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Service, self, [scope, id, config])

    @jsii.member(jsii_name="resetAuth")
    def reset_auth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuth", []))

    @jsii.member(jsii_name="resetConvergeConfig")
    def reset_converge_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConvergeConfig", []))

    @jsii.member(jsii_name="resetEndpointSpec")
    def reset_endpoint_spec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndpointSpec", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetRollbackConfig")
    def reset_rollback_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRollbackConfig", []))

    @jsii.member(jsii_name="resetUpdateConfig")
    def reset_update_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateConfig", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskSpecInput")
    def task_spec_input(self) -> typing.List["ServiceTaskSpec"]:
        return typing.cast(typing.List["ServiceTaskSpec"], jsii.get(self, "taskSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="authInput")
    def auth_input(self) -> typing.Optional[typing.List["ServiceAuth"]]:
        return typing.cast(typing.Optional[typing.List["ServiceAuth"]], jsii.get(self, "authInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="convergeConfigInput")
    def converge_config_input(
        self,
    ) -> typing.Optional[typing.List["ServiceConvergeConfig"]]:
        return typing.cast(typing.Optional[typing.List["ServiceConvergeConfig"]], jsii.get(self, "convergeConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointSpecInput")
    def endpoint_spec_input(
        self,
    ) -> typing.Optional[typing.List["ServiceEndpointSpec"]]:
        return typing.cast(typing.Optional[typing.List["ServiceEndpointSpec"]], jsii.get(self, "endpointSpecInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["ServiceLabels"]]:
        return typing.cast(typing.Optional[typing.List["ServiceLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[typing.List["ServiceMode"]]:
        return typing.cast(typing.Optional[typing.List["ServiceMode"]], jsii.get(self, "modeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rollbackConfigInput")
    def rollback_config_input(
        self,
    ) -> typing.Optional[typing.List["ServiceRollbackConfig"]]:
        return typing.cast(typing.Optional[typing.List["ServiceRollbackConfig"]], jsii.get(self, "rollbackConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateConfigInput")
    def update_config_input(
        self,
    ) -> typing.Optional[typing.List["ServiceUpdateConfig"]]:
        return typing.cast(typing.Optional[typing.List["ServiceUpdateConfig"]], jsii.get(self, "updateConfigInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="auth")
    def auth(self) -> typing.List["ServiceAuth"]:
        return typing.cast(typing.List["ServiceAuth"], jsii.get(self, "auth"))

    @auth.setter
    def auth(self, value: typing.List["ServiceAuth"]) -> None:
        jsii.set(self, "auth", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="convergeConfig")
    def converge_config(self) -> typing.List["ServiceConvergeConfig"]:
        return typing.cast(typing.List["ServiceConvergeConfig"], jsii.get(self, "convergeConfig"))

    @converge_config.setter
    def converge_config(self, value: typing.List["ServiceConvergeConfig"]) -> None:
        jsii.set(self, "convergeConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="endpointSpec")
    def endpoint_spec(self) -> typing.List["ServiceEndpointSpec"]:
        return typing.cast(typing.List["ServiceEndpointSpec"], jsii.get(self, "endpointSpec"))

    @endpoint_spec.setter
    def endpoint_spec(self, value: typing.List["ServiceEndpointSpec"]) -> None:
        jsii.set(self, "endpointSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["ServiceLabels"]:
        return typing.cast(typing.List["ServiceLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["ServiceLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mode")
    def mode(self) -> typing.List["ServiceMode"]:
        return typing.cast(typing.List["ServiceMode"], jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: typing.List["ServiceMode"]) -> None:
        jsii.set(self, "mode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rollbackConfig")
    def rollback_config(self) -> typing.List["ServiceRollbackConfig"]:
        return typing.cast(typing.List["ServiceRollbackConfig"], jsii.get(self, "rollbackConfig"))

    @rollback_config.setter
    def rollback_config(self, value: typing.List["ServiceRollbackConfig"]) -> None:
        jsii.set(self, "rollbackConfig", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="taskSpec")
    def task_spec(self) -> typing.List["ServiceTaskSpec"]:
        return typing.cast(typing.List["ServiceTaskSpec"], jsii.get(self, "taskSpec"))

    @task_spec.setter
    def task_spec(self, value: typing.List["ServiceTaskSpec"]) -> None:
        jsii.set(self, "taskSpec", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="updateConfig")
    def update_config(self) -> typing.List["ServiceUpdateConfig"]:
        return typing.cast(typing.List["ServiceUpdateConfig"], jsii.get(self, "updateConfig"))

    @update_config.setter
    def update_config(self, value: typing.List["ServiceUpdateConfig"]) -> None:
        jsii.set(self, "updateConfig", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceAuth",
    jsii_struct_bases=[],
    name_mapping={
        "server_address": "serverAddress",
        "password": "password",
        "username": "username",
    },
)
class ServiceAuth:
    def __init__(
        self,
        *,
        server_address: builtins.str,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param server_address: The address of the server for the authentication. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#server_address Service#server_address}
        :param password: The password. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#password Service#password}
        :param username: The username. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#username Service#username}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "server_address": server_address,
        }
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def server_address(self) -> builtins.str:
        '''The address of the server for the authentication.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#server_address Service#server_address}
        '''
        result = self._values.get("server_address")
        assert result is not None, "Required property 'server_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''The password.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#password Service#password}
        '''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''The username.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#username Service#username}
        '''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceAuth(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "name": "name",
        "task_spec": "taskSpec",
        "auth": "auth",
        "converge_config": "convergeConfig",
        "endpoint_spec": "endpointSpec",
        "labels": "labels",
        "mode": "mode",
        "rollback_config": "rollbackConfig",
        "update_config": "updateConfig",
    },
)
class ServiceConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        name: builtins.str,
        task_spec: typing.Sequence["ServiceTaskSpec"],
        auth: typing.Optional[typing.Sequence[ServiceAuth]] = None,
        converge_config: typing.Optional[typing.Sequence["ServiceConvergeConfig"]] = None,
        endpoint_spec: typing.Optional[typing.Sequence["ServiceEndpointSpec"]] = None,
        labels: typing.Optional[typing.Sequence["ServiceLabels"]] = None,
        mode: typing.Optional[typing.Sequence["ServiceMode"]] = None,
        rollback_config: typing.Optional[typing.Sequence["ServiceRollbackConfig"]] = None,
        update_config: typing.Optional[typing.Sequence["ServiceUpdateConfig"]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param name: Name of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        :param task_spec: task_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#task_spec Service#task_spec}
        :param auth: auth block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#auth Service#auth}
        :param converge_config: converge_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#converge_config Service#converge_config}
        :param endpoint_spec: endpoint_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#endpoint_spec Service#endpoint_spec}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        :param mode: mode block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        :param rollback_config: rollback_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#rollback_config Service#rollback_config}
        :param update_config: update_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#update_config Service#update_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
            "task_spec": task_spec,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if auth is not None:
            self._values["auth"] = auth
        if converge_config is not None:
            self._values["converge_config"] = converge_config
        if endpoint_spec is not None:
            self._values["endpoint_spec"] = endpoint_spec
        if labels is not None:
            self._values["labels"] = labels
        if mode is not None:
            self._values["mode"] = mode
        if rollback_config is not None:
            self._values["rollback_config"] = rollback_config
        if update_config is not None:
            self._values["update_config"] = update_config

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def task_spec(self) -> typing.List["ServiceTaskSpec"]:
        '''task_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#task_spec Service#task_spec}
        '''
        result = self._values.get("task_spec")
        assert result is not None, "Required property 'task_spec' is missing"
        return typing.cast(typing.List["ServiceTaskSpec"], result)

    @builtins.property
    def auth(self) -> typing.Optional[typing.List[ServiceAuth]]:
        '''auth block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#auth Service#auth}
        '''
        result = self._values.get("auth")
        return typing.cast(typing.Optional[typing.List[ServiceAuth]], result)

    @builtins.property
    def converge_config(self) -> typing.Optional[typing.List["ServiceConvergeConfig"]]:
        '''converge_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#converge_config Service#converge_config}
        '''
        result = self._values.get("converge_config")
        return typing.cast(typing.Optional[typing.List["ServiceConvergeConfig"]], result)

    @builtins.property
    def endpoint_spec(self) -> typing.Optional[typing.List["ServiceEndpointSpec"]]:
        '''endpoint_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#endpoint_spec Service#endpoint_spec}
        '''
        result = self._values.get("endpoint_spec")
        return typing.cast(typing.Optional[typing.List["ServiceEndpointSpec"]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["ServiceLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ServiceLabels"]], result)

    @builtins.property
    def mode(self) -> typing.Optional[typing.List["ServiceMode"]]:
        '''mode block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[typing.List["ServiceMode"]], result)

    @builtins.property
    def rollback_config(self) -> typing.Optional[typing.List["ServiceRollbackConfig"]]:
        '''rollback_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#rollback_config Service#rollback_config}
        '''
        result = self._values.get("rollback_config")
        return typing.cast(typing.Optional[typing.List["ServiceRollbackConfig"]], result)

    @builtins.property
    def update_config(self) -> typing.Optional[typing.List["ServiceUpdateConfig"]]:
        '''update_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#update_config Service#update_config}
        '''
        result = self._values.get("update_config")
        return typing.cast(typing.Optional[typing.List["ServiceUpdateConfig"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceConvergeConfig",
    jsii_struct_bases=[],
    name_mapping={"delay": "delay", "timeout": "timeout"},
)
class ServiceConvergeConfig:
    def __init__(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param delay: The interval to check if the desired state is reached (ms|s). Defaults to ``7s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        :param timeout: The timeout of the service to reach the desired state (s|m). Defaults to ``3m``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#timeout Service#timeout}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delay is not None:
            self._values["delay"] = delay
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''The interval to check if the desired state is reached (ms|s). Defaults to ``7s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''The timeout of the service to reach the desired state (s|m). Defaults to ``3m``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#timeout Service#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceConvergeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceEndpointSpec",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "ports": "ports"},
)
class ServiceEndpointSpec:
    def __init__(
        self,
        *,
        mode: typing.Optional[builtins.str] = None,
        ports: typing.Optional[typing.Sequence["ServiceEndpointSpecPorts"]] = None,
    ) -> None:
        '''
        :param mode: The mode of resolution to use for internal load balancing between tasks. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        :param ports: ports block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#ports Service#ports}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if ports is not None:
            self._values["ports"] = ports

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''The mode of resolution to use for internal load balancing between tasks.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ports(self) -> typing.Optional[typing.List["ServiceEndpointSpecPorts"]]:
        '''ports block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#ports Service#ports}
        '''
        result = self._values.get("ports")
        return typing.cast(typing.Optional[typing.List["ServiceEndpointSpecPorts"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEndpointSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceEndpointSpecPorts",
    jsii_struct_bases=[],
    name_mapping={
        "target_port": "targetPort",
        "name": "name",
        "protocol": "protocol",
        "published_port": "publishedPort",
        "publish_mode": "publishMode",
    },
)
class ServiceEndpointSpecPorts:
    def __init__(
        self,
        *,
        target_port: jsii.Number,
        name: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        published_port: typing.Optional[jsii.Number] = None,
        publish_mode: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param target_port: The port inside the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#target_port Service#target_port}
        :param name: A random name for the port. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        :param protocol: Rrepresents the protocol of a port: 'tcp', 'udp' or 'sctp'. Defaults to ``tcp``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#protocol Service#protocol}
        :param published_port: The port on the swarm hosts. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#published_port Service#published_port}
        :param publish_mode: Represents the mode in which the port is to be published: 'ingress' or 'host'. Defaults to ``ingress``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#publish_mode Service#publish_mode}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target_port": target_port,
        }
        if name is not None:
            self._values["name"] = name
        if protocol is not None:
            self._values["protocol"] = protocol
        if published_port is not None:
            self._values["published_port"] = published_port
        if publish_mode is not None:
            self._values["publish_mode"] = publish_mode

    @builtins.property
    def target_port(self) -> jsii.Number:
        '''The port inside the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#target_port Service#target_port}
        '''
        result = self._values.get("target_port")
        assert result is not None, "Required property 'target_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''A random name for the port.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Rrepresents the protocol of a port: 'tcp', 'udp' or 'sctp'. Defaults to ``tcp``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#protocol Service#protocol}
        '''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def published_port(self) -> typing.Optional[jsii.Number]:
        '''The port on the swarm hosts.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#published_port Service#published_port}
        '''
        result = self._values.get("published_port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def publish_mode(self) -> typing.Optional[builtins.str]:
        '''Represents the mode in which the port is to be published: 'ingress' or 'host'. Defaults to ``ingress``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#publish_mode Service#publish_mode}
        '''
        result = self._values.get("publish_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceEndpointSpecPorts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ServiceLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#label Service#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#value Service#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#label Service#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#value Service#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceMode",
    jsii_struct_bases=[],
    name_mapping={"global_": "global", "replicated": "replicated"},
)
class ServiceMode:
    def __init__(
        self,
        *,
        global_: typing.Optional[builtins.bool] = None,
        replicated: typing.Optional[typing.Sequence["ServiceModeReplicated"]] = None,
    ) -> None:
        '''
        :param global_: The global service mode. Defaults to ``false``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#global Service#global}
        :param replicated: replicated block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#replicated Service#replicated}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if global_ is not None:
            self._values["global_"] = global_
        if replicated is not None:
            self._values["replicated"] = replicated

    @builtins.property
    def global_(self) -> typing.Optional[builtins.bool]:
        '''The global service mode. Defaults to ``false``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#global Service#global}
        '''
        result = self._values.get("global_")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def replicated(self) -> typing.Optional[typing.List["ServiceModeReplicated"]]:
        '''replicated block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#replicated Service#replicated}
        '''
        result = self._values.get("replicated")
        return typing.cast(typing.Optional[typing.List["ServiceModeReplicated"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceMode(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceModeReplicated",
    jsii_struct_bases=[],
    name_mapping={"replicas": "replicas"},
)
class ServiceModeReplicated:
    def __init__(self, *, replicas: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param replicas: The amount of replicas of the service. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#replicas Service#replicas}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if replicas is not None:
            self._values["replicas"] = replicas

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        '''The amount of replicas of the service. Defaults to ``1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#replicas Service#replicas}
        '''
        result = self._values.get("replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceModeReplicated(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceRollbackConfig",
    jsii_struct_bases=[],
    name_mapping={
        "delay": "delay",
        "failure_action": "failureAction",
        "max_failure_ratio": "maxFailureRatio",
        "monitor": "monitor",
        "order": "order",
        "parallelism": "parallelism",
    },
)
class ServiceRollbackConfig:
    def __init__(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        failure_action: typing.Optional[builtins.str] = None,
        max_failure_ratio: typing.Optional[builtins.str] = None,
        monitor: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        parallelism: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param delay: Delay between task rollbacks (ns|us|ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        :param failure_action: Action on rollback failure: pause | continue. Defaults to ``pause``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#failure_action Service#failure_action}
        :param max_failure_ratio: Failure rate to tolerate during a rollback. Defaults to ``0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_failure_ratio Service#max_failure_ratio}
        :param monitor: Duration after each task rollback to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#monitor Service#monitor}
        :param order: Rollback order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#order Service#order}
        :param parallelism: Maximum number of tasks to be rollbacked in one iteration. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#parallelism Service#parallelism}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delay is not None:
            self._values["delay"] = delay
        if failure_action is not None:
            self._values["failure_action"] = failure_action
        if max_failure_ratio is not None:
            self._values["max_failure_ratio"] = max_failure_ratio
        if monitor is not None:
            self._values["monitor"] = monitor
        if order is not None:
            self._values["order"] = order
        if parallelism is not None:
            self._values["parallelism"] = parallelism

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''Delay between task rollbacks (ns|us|ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failure_action(self) -> typing.Optional[builtins.str]:
        '''Action on rollback failure: pause | continue. Defaults to ``pause``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#failure_action Service#failure_action}
        '''
        result = self._values.get("failure_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_failure_ratio(self) -> typing.Optional[builtins.str]:
        '''Failure rate to tolerate during a rollback. Defaults to ``0.0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_failure_ratio Service#max_failure_ratio}
        '''
        result = self._values.get("max_failure_ratio")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitor(self) -> typing.Optional[builtins.str]:
        '''Duration after each task rollback to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#monitor Service#monitor}
        '''
        result = self._values.get("monitor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Rollback order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#order Service#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parallelism(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of tasks to be rollbacked in one iteration. Defaults to ``1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#parallelism Service#parallelism}
        '''
        result = self._values.get("parallelism")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceRollbackConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpec",
    jsii_struct_bases=[],
    name_mapping={
        "container_spec": "containerSpec",
        "force_update": "forceUpdate",
        "log_driver": "logDriver",
        "networks": "networks",
        "placement": "placement",
        "resources": "resources",
        "restart_policy": "restartPolicy",
        "runtime": "runtime",
    },
)
class ServiceTaskSpec:
    def __init__(
        self,
        *,
        container_spec: typing.Sequence["ServiceTaskSpecContainerSpec"],
        force_update: typing.Optional[jsii.Number] = None,
        log_driver: typing.Optional[typing.Sequence["ServiceTaskSpecLogDriver"]] = None,
        networks: typing.Optional[typing.Sequence[builtins.str]] = None,
        placement: typing.Optional[typing.Sequence["ServiceTaskSpecPlacement"]] = None,
        resources: typing.Optional[typing.Sequence["ServiceTaskSpecResources"]] = None,
        restart_policy: typing.Optional[typing.Sequence["ServiceTaskSpecRestartPolicy"]] = None,
        runtime: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param container_spec: container_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#container_spec Service#container_spec}
        :param force_update: A counter that triggers an update even if no relevant parameters have been changed. See the `spec <https://github.com/docker/swarmkit/blob/master/api/specs.proto#L126>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#force_update Service#force_update}
        :param log_driver: log_driver block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#log_driver Service#log_driver}
        :param networks: Ids of the networks in which the container will be put in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#networks Service#networks}
        :param placement: placement block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#placement Service#placement}
        :param resources: resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#resources Service#resources}
        :param restart_policy: restart_policy block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#restart_policy Service#restart_policy}
        :param runtime: Runtime is the type of runtime specified for the task executor. See the `types <https://github.com/moby/moby/blob/master/api/types/swarm/runtime.go>`_. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#runtime Service#runtime}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "container_spec": container_spec,
        }
        if force_update is not None:
            self._values["force_update"] = force_update
        if log_driver is not None:
            self._values["log_driver"] = log_driver
        if networks is not None:
            self._values["networks"] = networks
        if placement is not None:
            self._values["placement"] = placement
        if resources is not None:
            self._values["resources"] = resources
        if restart_policy is not None:
            self._values["restart_policy"] = restart_policy
        if runtime is not None:
            self._values["runtime"] = runtime

    @builtins.property
    def container_spec(self) -> typing.List["ServiceTaskSpecContainerSpec"]:
        '''container_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#container_spec Service#container_spec}
        '''
        result = self._values.get("container_spec")
        assert result is not None, "Required property 'container_spec' is missing"
        return typing.cast(typing.List["ServiceTaskSpecContainerSpec"], result)

    @builtins.property
    def force_update(self) -> typing.Optional[jsii.Number]:
        '''A counter that triggers an update even if no relevant parameters have been changed. See the `spec <https://github.com/docker/swarmkit/blob/master/api/specs.proto#L126>`_.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#force_update Service#force_update}
        '''
        result = self._values.get("force_update")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_driver(self) -> typing.Optional[typing.List["ServiceTaskSpecLogDriver"]]:
        '''log_driver block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#log_driver Service#log_driver}
        '''
        result = self._values.get("log_driver")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecLogDriver"]], result)

    @builtins.property
    def networks(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Ids of the networks in which the  container will be put in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#networks Service#networks}
        '''
        result = self._values.get("networks")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def placement(self) -> typing.Optional[typing.List["ServiceTaskSpecPlacement"]]:
        '''placement block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#placement Service#placement}
        '''
        result = self._values.get("placement")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecPlacement"]], result)

    @builtins.property
    def resources(self) -> typing.Optional[typing.List["ServiceTaskSpecResources"]]:
        '''resources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#resources Service#resources}
        '''
        result = self._values.get("resources")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecResources"]], result)

    @builtins.property
    def restart_policy(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecRestartPolicy"]]:
        '''restart_policy block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#restart_policy Service#restart_policy}
        '''
        result = self._values.get("restart_policy")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecRestartPolicy"]], result)

    @builtins.property
    def runtime(self) -> typing.Optional[builtins.str]:
        '''Runtime is the type of runtime specified for the task executor. See the `types <https://github.com/moby/moby/blob/master/api/types/swarm/runtime.go>`_.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#runtime Service#runtime}
        '''
        result = self._values.get("runtime")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpec",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "args": "args",
        "command": "command",
        "configs": "configs",
        "dir": "dir",
        "dns_config": "dnsConfig",
        "env": "env",
        "groups": "groups",
        "healthcheck": "healthcheck",
        "hostname": "hostname",
        "hosts": "hosts",
        "isolation": "isolation",
        "labels": "labels",
        "mounts": "mounts",
        "privileges": "privileges",
        "read_only": "readOnly",
        "secrets": "secrets",
        "stop_grace_period": "stopGracePeriod",
        "stop_signal": "stopSignal",
        "user": "user",
    },
)
class ServiceTaskSpecContainerSpec:
    def __init__(
        self,
        *,
        image: builtins.str,
        args: typing.Optional[typing.Sequence[builtins.str]] = None,
        command: typing.Optional[typing.Sequence[builtins.str]] = None,
        configs: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecConfigs"]] = None,
        dir: typing.Optional[builtins.str] = None,
        dns_config: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecDnsConfig"]] = None,
        env: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        groups: typing.Optional[typing.Sequence[builtins.str]] = None,
        healthcheck: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecHealthcheck"]] = None,
        hostname: typing.Optional[builtins.str] = None,
        hosts: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecHosts"]] = None,
        isolation: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecLabels"]] = None,
        mounts: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMounts"]] = None,
        privileges: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecPrivileges"]] = None,
        read_only: typing.Optional[builtins.bool] = None,
        secrets: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecSecrets"]] = None,
        stop_grace_period: typing.Optional[builtins.str] = None,
        stop_signal: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param image: The image name to use for the containers of the service, like ``nginx:1.17.6``. Also use the data-source or resource of ``docker_image`` with the ``repo_digest`` or ``docker_registry_image`` with the ``name`` attribute for this, as shown in the examples. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#image Service#image}
        :param args: Arguments to the command. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#args Service#args}
        :param command: The command/entrypoint to be run in the image. According to the `docker cli <https://github.com/docker/cli/blob/v20.10.7/cli/command/service/opts.go#L705>`_ the override of the entrypoint is also passed to the ``command`` property and there is no ``entrypoint`` attribute in the ``ContainerSpec`` of the service. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#command Service#command}
        :param configs: configs block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#configs Service#configs}
        :param dir: The working directory for commands to run in. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#dir Service#dir}
        :param dns_config: dns_config block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#dns_config Service#dns_config}
        :param env: A list of environment variables in the form VAR="value". Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#env Service#env}
        :param groups: A list of additional groups that the container process will run as. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#groups Service#groups}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#healthcheck Service#healthcheck}
        :param hostname: The hostname to use for the container, as a valid RFC 1123 hostname. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#hostname Service#hostname}
        :param hosts: hosts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#hosts Service#hosts}
        :param isolation: Isolation technology of the containers running the service. (Windows only). Defaults to ``default``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#isolation Service#isolation}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        :param mounts: mounts block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mounts Service#mounts}
        :param privileges: privileges block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#privileges Service#privileges}
        :param read_only: Mount the container's root filesystem as read only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#read_only Service#read_only}
        :param secrets: secrets block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#secrets Service#secrets}
        :param stop_grace_period: Amount of time to wait for the container to terminate before forcefully removing it (ms|s|m|h). If not specified or '0s' the destroy will not check if all tasks/containers of the service terminate. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#stop_grace_period Service#stop_grace_period}
        :param stop_signal: Signal to stop the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#stop_signal Service#stop_signal}
        :param user: The user inside the container. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#user Service#user}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "image": image,
        }
        if args is not None:
            self._values["args"] = args
        if command is not None:
            self._values["command"] = command
        if configs is not None:
            self._values["configs"] = configs
        if dir is not None:
            self._values["dir"] = dir
        if dns_config is not None:
            self._values["dns_config"] = dns_config
        if env is not None:
            self._values["env"] = env
        if groups is not None:
            self._values["groups"] = groups
        if healthcheck is not None:
            self._values["healthcheck"] = healthcheck
        if hostname is not None:
            self._values["hostname"] = hostname
        if hosts is not None:
            self._values["hosts"] = hosts
        if isolation is not None:
            self._values["isolation"] = isolation
        if labels is not None:
            self._values["labels"] = labels
        if mounts is not None:
            self._values["mounts"] = mounts
        if privileges is not None:
            self._values["privileges"] = privileges
        if read_only is not None:
            self._values["read_only"] = read_only
        if secrets is not None:
            self._values["secrets"] = secrets
        if stop_grace_period is not None:
            self._values["stop_grace_period"] = stop_grace_period
        if stop_signal is not None:
            self._values["stop_signal"] = stop_signal
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def image(self) -> builtins.str:
        '''The image name to use for the containers of the service, like ``nginx:1.17.6``. Also use the data-source or resource of ``docker_image`` with the ``repo_digest`` or ``docker_registry_image`` with the ``name`` attribute for this, as shown in the examples.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#image Service#image}
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Arguments to the command.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#args Service#args}
        '''
        result = self._values.get("args")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def command(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The command/entrypoint to be run in the image.

        According to the `docker cli <https://github.com/docker/cli/blob/v20.10.7/cli/command/service/opts.go#L705>`_ the override of the entrypoint is also passed to the ``command`` property and there is no ``entrypoint`` attribute in the ``ContainerSpec`` of the service.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#command Service#command}
        '''
        result = self._values.get("command")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def configs(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecConfigs"]]:
        '''configs block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#configs Service#configs}
        '''
        result = self._values.get("configs")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecConfigs"]], result)

    @builtins.property
    def dir(self) -> typing.Optional[builtins.str]:
        '''The working directory for commands to run in.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#dir Service#dir}
        '''
        result = self._values.get("dir")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_config(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecDnsConfig"]]:
        '''dns_config block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#dns_config Service#dns_config}
        '''
        result = self._values.get("dns_config")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecDnsConfig"]], result)

    @builtins.property
    def env(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''A list of environment variables in the form VAR="value".

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#env Service#env}
        '''
        result = self._values.get("env")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def groups(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of additional groups that the container process will run as.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#groups Service#groups}
        '''
        result = self._values.get("groups")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def healthcheck(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecHealthcheck"]]:
        '''healthcheck block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#healthcheck Service#healthcheck}
        '''
        result = self._values.get("healthcheck")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecHealthcheck"]], result)

    @builtins.property
    def hostname(self) -> typing.Optional[builtins.str]:
        '''The hostname to use for the container, as a valid RFC 1123 hostname.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#hostname Service#hostname}
        '''
        result = self._values.get("hostname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def hosts(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecHosts"]]:
        '''hosts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#hosts Service#hosts}
        '''
        result = self._values.get("hosts")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecHosts"]], result)

    @builtins.property
    def isolation(self) -> typing.Optional[builtins.str]:
        '''Isolation technology of the containers running the service. (Windows only). Defaults to ``default``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#isolation Service#isolation}
        '''
        result = self._values.get("isolation")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecLabels"]], result)

    @builtins.property
    def mounts(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMounts"]]:
        '''mounts block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mounts Service#mounts}
        '''
        result = self._values.get("mounts")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMounts"]], result)

    @builtins.property
    def privileges(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecPrivileges"]]:
        '''privileges block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#privileges Service#privileges}
        '''
        result = self._values.get("privileges")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecPrivileges"]], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''Mount the container's root filesystem as read only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#read_only Service#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def secrets(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecSecrets"]]:
        '''secrets block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#secrets Service#secrets}
        '''
        result = self._values.get("secrets")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecSecrets"]], result)

    @builtins.property
    def stop_grace_period(self) -> typing.Optional[builtins.str]:
        '''Amount of time to wait for the container to terminate before forcefully removing it (ms|s|m|h).

        If not specified or '0s' the destroy will not check if all tasks/containers of the service terminate.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#stop_grace_period Service#stop_grace_period}
        '''
        result = self._values.get("stop_grace_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stop_signal(self) -> typing.Optional[builtins.str]:
        '''Signal to stop the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#stop_signal Service#stop_signal}
        '''
        result = self._values.get("stop_signal")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''The user inside the container.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#user Service#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecConfigs",
    jsii_struct_bases=[],
    name_mapping={
        "config_id": "configId",
        "file_name": "fileName",
        "config_name": "configName",
        "file_gid": "fileGid",
        "file_mode": "fileMode",
        "file_uid": "fileUid",
    },
)
class ServiceTaskSpecContainerSpecConfigs:
    def __init__(
        self,
        *,
        config_id: builtins.str,
        file_name: builtins.str,
        config_name: typing.Optional[builtins.str] = None,
        file_gid: typing.Optional[builtins.str] = None,
        file_mode: typing.Optional[jsii.Number] = None,
        file_uid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_id: ID of the specific config that we're referencing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#config_id Service#config_id}
        :param file_name: Represents the final filename in the filesystem. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_name Service#file_name}
        :param config_name: Name of the config that this references, but this is just provided for lookup/display purposes. The config in the reference will be identified by its ID Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#config_name Service#config_name}
        :param file_gid: Represents the file GID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_gid Service#file_gid}
        :param file_mode: Represents represents the FileMode of the file. Defaults to ``0o444``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_mode Service#file_mode}
        :param file_uid: Represents the file UID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_uid Service#file_uid}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "config_id": config_id,
            "file_name": file_name,
        }
        if config_name is not None:
            self._values["config_name"] = config_name
        if file_gid is not None:
            self._values["file_gid"] = file_gid
        if file_mode is not None:
            self._values["file_mode"] = file_mode
        if file_uid is not None:
            self._values["file_uid"] = file_uid

    @builtins.property
    def config_id(self) -> builtins.str:
        '''ID of the specific config that we're referencing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#config_id Service#config_id}
        '''
        result = self._values.get("config_id")
        assert result is not None, "Required property 'config_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_name(self) -> builtins.str:
        '''Represents the final filename in the filesystem.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_name Service#file_name}
        '''
        result = self._values.get("file_name")
        assert result is not None, "Required property 'file_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_name(self) -> typing.Optional[builtins.str]:
        '''Name of the config that this references, but this is just provided for lookup/display purposes.

        The config in the reference will be identified by its ID

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#config_name Service#config_name}
        '''
        result = self._values.get("config_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_gid(self) -> typing.Optional[builtins.str]:
        '''Represents the file GID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_gid Service#file_gid}
        '''
        result = self._values.get("file_gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_mode(self) -> typing.Optional[jsii.Number]:
        '''Represents represents the FileMode of the file. Defaults to ``0o444``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_mode Service#file_mode}
        '''
        result = self._values.get("file_mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def file_uid(self) -> typing.Optional[builtins.str]:
        '''Represents the file UID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_uid Service#file_uid}
        '''
        result = self._values.get("file_uid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecConfigs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecDnsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "nameservers": "nameservers",
        "options": "options",
        "search": "search",
    },
)
class ServiceTaskSpecContainerSpecDnsConfig:
    def __init__(
        self,
        *,
        nameservers: typing.Sequence[builtins.str],
        options: typing.Optional[typing.Sequence[builtins.str]] = None,
        search: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param nameservers: The IP addresses of the name servers. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#nameservers Service#nameservers}
        :param options: A list of internal resolver variables to be modified (e.g., debug, ndots:3, etc.). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#options Service#options}
        :param search: A search list for host-name lookup. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#search Service#search}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "nameservers": nameservers,
        }
        if options is not None:
            self._values["options"] = options
        if search is not None:
            self._values["search"] = search

    @builtins.property
    def nameservers(self) -> typing.List[builtins.str]:
        '''The IP addresses of the name servers.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#nameservers Service#nameservers}
        '''
        result = self._values.get("nameservers")
        assert result is not None, "Required property 'nameservers' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def options(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A list of internal resolver variables to be modified (e.g., debug, ndots:3, etc.).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#options Service#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def search(self) -> typing.Optional[typing.List[builtins.str]]:
        '''A search list for host-name lookup.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#search Service#search}
        '''
        result = self._values.get("search")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecDnsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecHealthcheck",
    jsii_struct_bases=[],
    name_mapping={
        "test": "test",
        "interval": "interval",
        "retries": "retries",
        "start_period": "startPeriod",
        "timeout": "timeout",
    },
)
class ServiceTaskSpecContainerSpecHealthcheck:
    def __init__(
        self,
        *,
        test: typing.Sequence[builtins.str],
        interval: typing.Optional[builtins.str] = None,
        retries: typing.Optional[jsii.Number] = None,
        start_period: typing.Optional[builtins.str] = None,
        timeout: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param test: The test to perform as list. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#test Service#test}
        :param interval: Time between running the check (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#interval Service#interval}
        :param retries: Consecutive failures needed to report unhealthy. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#retries Service#retries}
        :param start_period: Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#start_period Service#start_period}
        :param timeout: Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#timeout Service#timeout}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "test": test,
        }
        if interval is not None:
            self._values["interval"] = interval
        if retries is not None:
            self._values["retries"] = retries
        if start_period is not None:
            self._values["start_period"] = start_period
        if timeout is not None:
            self._values["timeout"] = timeout

    @builtins.property
    def test(self) -> typing.List[builtins.str]:
        '''The test to perform as list.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#test Service#test}
        '''
        result = self._values.get("test")
        assert result is not None, "Required property 'test' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def interval(self) -> typing.Optional[builtins.str]:
        '''Time between running the check (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#interval Service#interval}
        '''
        result = self._values.get("interval")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retries(self) -> typing.Optional[jsii.Number]:
        '''Consecutive failures needed to report unhealthy. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#retries Service#retries}
        '''
        result = self._values.get("retries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_period(self) -> typing.Optional[builtins.str]:
        '''Start period for the container to initialize before counting retries towards unstable (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#start_period Service#start_period}
        '''
        result = self._values.get("start_period")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeout(self) -> typing.Optional[builtins.str]:
        '''Maximum time to allow one check to run (ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#timeout Service#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecHealthcheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecHosts",
    jsii_struct_bases=[],
    name_mapping={"host": "host", "ip": "ip"},
)
class ServiceTaskSpecContainerSpecHosts:
    def __init__(self, *, host: builtins.str, ip: builtins.str) -> None:
        '''
        :param host: The name of the host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#host Service#host}
        :param ip: The ip of the host. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#ip Service#ip}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "host": host,
            "ip": ip,
        }

    @builtins.property
    def host(self) -> builtins.str:
        '''The name of the host.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#host Service#host}
        '''
        result = self._values.get("host")
        assert result is not None, "Required property 'host' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ip(self) -> builtins.str:
        '''The ip of the host.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#ip Service#ip}
        '''
        result = self._values.get("ip")
        assert result is not None, "Required property 'ip' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecHosts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ServiceTaskSpecContainerSpecLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#label Service#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#value Service#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#label Service#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#value Service#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMounts",
    jsii_struct_bases=[],
    name_mapping={
        "target": "target",
        "type": "type",
        "bind_options": "bindOptions",
        "read_only": "readOnly",
        "source": "source",
        "tmpfs_options": "tmpfsOptions",
        "volume_options": "volumeOptions",
    },
)
class ServiceTaskSpecContainerSpecMounts:
    def __init__(
        self,
        *,
        target: builtins.str,
        type: builtins.str,
        bind_options: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMountsBindOptions"]] = None,
        read_only: typing.Optional[builtins.bool] = None,
        source: typing.Optional[builtins.str] = None,
        tmpfs_options: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMountsTmpfsOptions"]] = None,
        volume_options: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMountsVolumeOptions"]] = None,
    ) -> None:
        '''
        :param target: Container path. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#target Service#target}
        :param type: The mount type. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#type Service#type}
        :param bind_options: bind_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#bind_options Service#bind_options}
        :param read_only: Whether the mount should be read-only. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#read_only Service#read_only}
        :param source: Mount source (e.g. a volume name, a host path). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#source Service#source}
        :param tmpfs_options: tmpfs_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#tmpfs_options Service#tmpfs_options}
        :param volume_options: volume_options block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#volume_options Service#volume_options}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "target": target,
            "type": type,
        }
        if bind_options is not None:
            self._values["bind_options"] = bind_options
        if read_only is not None:
            self._values["read_only"] = read_only
        if source is not None:
            self._values["source"] = source
        if tmpfs_options is not None:
            self._values["tmpfs_options"] = tmpfs_options
        if volume_options is not None:
            self._values["volume_options"] = volume_options

    @builtins.property
    def target(self) -> builtins.str:
        '''Container path.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#target Service#target}
        '''
        result = self._values.get("target")
        assert result is not None, "Required property 'target' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''The mount type.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#type Service#type}
        '''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_options(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsBindOptions"]]:
        '''bind_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#bind_options Service#bind_options}
        '''
        result = self._values.get("bind_options")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsBindOptions"]], result)

    @builtins.property
    def read_only(self) -> typing.Optional[builtins.bool]:
        '''Whether the mount should be read-only.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#read_only Service#read_only}
        '''
        result = self._values.get("read_only")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def source(self) -> typing.Optional[builtins.str]:
        '''Mount source (e.g. a volume name, a host path).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#source Service#source}
        '''
        result = self._values.get("source")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tmpfs_options(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsTmpfsOptions"]]:
        '''tmpfs_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#tmpfs_options Service#tmpfs_options}
        '''
        result = self._values.get("tmpfs_options")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsTmpfsOptions"]], result)

    @builtins.property
    def volume_options(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsVolumeOptions"]]:
        '''volume_options block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#volume_options Service#volume_options}
        '''
        result = self._values.get("volume_options")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsVolumeOptions"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMounts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsBindOptions",
    jsii_struct_bases=[],
    name_mapping={"propagation": "propagation"},
)
class ServiceTaskSpecContainerSpecMountsBindOptions:
    def __init__(self, *, propagation: typing.Optional[builtins.str] = None) -> None:
        '''
        :param propagation: Bind propagation refers to whether or not mounts created within a given bind-mount or named volume can be propagated to replicas of that mount. See the `docs <https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation>`_ for details. Defaults to ``rprivate`` Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#propagation Service#propagation}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if propagation is not None:
            self._values["propagation"] = propagation

    @builtins.property
    def propagation(self) -> typing.Optional[builtins.str]:
        '''Bind propagation refers to whether or not mounts created within a given bind-mount or named volume can be propagated to replicas of that mount.

        See the `docs <https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation>`_ for details. Defaults to ``rprivate``

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#propagation Service#propagation}
        '''
        result = self._values.get("propagation")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsBindOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsTmpfsOptions",
    jsii_struct_bases=[],
    name_mapping={"mode": "mode", "size_bytes": "sizeBytes"},
)
class ServiceTaskSpecContainerSpecMountsTmpfsOptions:
    def __init__(
        self,
        *,
        mode: typing.Optional[jsii.Number] = None,
        size_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param mode: The permission mode for the tmpfs mount in an integer. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        :param size_bytes: The size for the tmpfs mount in bytes. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#size_bytes Service#size_bytes}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if mode is not None:
            self._values["mode"] = mode
        if size_bytes is not None:
            self._values["size_bytes"] = size_bytes

    @builtins.property
    def mode(self) -> typing.Optional[jsii.Number]:
        '''The permission mode for the tmpfs mount in an integer.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#mode Service#mode}
        '''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def size_bytes(self) -> typing.Optional[jsii.Number]:
        '''The size for the tmpfs mount in bytes.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#size_bytes Service#size_bytes}
        '''
        result = self._values.get("size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsTmpfsOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsVolumeOptions",
    jsii_struct_bases=[],
    name_mapping={
        "driver_name": "driverName",
        "driver_options": "driverOptions",
        "labels": "labels",
        "no_copy": "noCopy",
    },
)
class ServiceTaskSpecContainerSpecMountsVolumeOptions:
    def __init__(
        self,
        *,
        driver_name: typing.Optional[builtins.str] = None,
        driver_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        labels: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels"]] = None,
        no_copy: typing.Optional[builtins.bool] = None,
    ) -> None:
        '''
        :param driver_name: Name of the driver to use to create the volume. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#driver_name Service#driver_name}
        :param driver_options: key/value map of driver specific options. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#driver_options Service#driver_options}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        :param no_copy: Populate volume with data from the target. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#no_copy Service#no_copy}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if driver_name is not None:
            self._values["driver_name"] = driver_name
        if driver_options is not None:
            self._values["driver_options"] = driver_options
        if labels is not None:
            self._values["labels"] = labels
        if no_copy is not None:
            self._values["no_copy"] = no_copy

    @builtins.property
    def driver_name(self) -> typing.Optional[builtins.str]:
        '''Name of the driver to use to create the volume.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#driver_name Service#driver_name}
        '''
        result = self._values.get("driver_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''key/value map of driver specific options.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#driver_options Service#driver_options}
        '''
        result = self._values.get("driver_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#labels Service#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels"]], result)

    @builtins.property
    def no_copy(self) -> typing.Optional[builtins.bool]:
        '''Populate volume with data from the target.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#no_copy Service#no_copy}
        '''
        result = self._values.get("no_copy")
        return typing.cast(typing.Optional[builtins.bool], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsVolumeOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#label Service#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#value Service#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#label Service#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#value Service#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivileges",
    jsii_struct_bases=[],
    name_mapping={
        "credential_spec": "credentialSpec",
        "se_linux_context": "seLinuxContext",
    },
)
class ServiceTaskSpecContainerSpecPrivileges:
    def __init__(
        self,
        *,
        credential_spec: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"]] = None,
        se_linux_context: typing.Optional[typing.Sequence["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"]] = None,
    ) -> None:
        '''
        :param credential_spec: credential_spec block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#credential_spec Service#credential_spec}
        :param se_linux_context: se_linux_context block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#se_linux_context Service#se_linux_context}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if credential_spec is not None:
            self._values["credential_spec"] = credential_spec
        if se_linux_context is not None:
            self._values["se_linux_context"] = se_linux_context

    @builtins.property
    def credential_spec(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"]]:
        '''credential_spec block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#credential_spec Service#credential_spec}
        '''
        result = self._values.get("credential_spec")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecPrivilegesCredentialSpec"]], result)

    @builtins.property
    def se_linux_context(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"]]:
        '''se_linux_context block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#se_linux_context Service#se_linux_context}
        '''
        result = self._values.get("se_linux_context")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecPrivileges(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesCredentialSpec",
    jsii_struct_bases=[],
    name_mapping={"file": "file", "registry": "registry"},
)
class ServiceTaskSpecContainerSpecPrivilegesCredentialSpec:
    def __init__(
        self,
        *,
        file: typing.Optional[builtins.str] = None,
        registry: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file: Load credential spec from this file. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file Service#file}
        :param registry: Load credential spec from this value in the Windows registry. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#registry Service#registry}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if file is not None:
            self._values["file"] = file
        if registry is not None:
            self._values["registry"] = registry

    @builtins.property
    def file(self) -> typing.Optional[builtins.str]:
        '''Load credential spec from this file.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file Service#file}
        '''
        result = self._values.get("file")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def registry(self) -> typing.Optional[builtins.str]:
        '''Load credential spec from this value in the Windows registry.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#registry Service#registry}
        '''
        result = self._values.get("registry")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecPrivilegesCredentialSpec(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext",
    jsii_struct_bases=[],
    name_mapping={
        "disable": "disable",
        "level": "level",
        "role": "role",
        "type": "type",
        "user": "user",
    },
)
class ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext:
    def __init__(
        self,
        *,
        disable: typing.Optional[builtins.bool] = None,
        level: typing.Optional[builtins.str] = None,
        role: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        user: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param disable: Disable SELinux. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#disable Service#disable}
        :param level: SELinux level label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#level Service#level}
        :param role: SELinux role label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#role Service#role}
        :param type: SELinux type label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#type Service#type}
        :param user: SELinux user label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#user Service#user}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if disable is not None:
            self._values["disable"] = disable
        if level is not None:
            self._values["level"] = level
        if role is not None:
            self._values["role"] = role
        if type is not None:
            self._values["type"] = type
        if user is not None:
            self._values["user"] = user

    @builtins.property
    def disable(self) -> typing.Optional[builtins.bool]:
        '''Disable SELinux.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#disable Service#disable}
        '''
        result = self._values.get("disable")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def level(self) -> typing.Optional[builtins.str]:
        '''SELinux level label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#level Service#level}
        '''
        result = self._values.get("level")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role(self) -> typing.Optional[builtins.str]:
        '''SELinux role label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#role Service#role}
        '''
        result = self._values.get("role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''SELinux type label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#type Service#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user(self) -> typing.Optional[builtins.str]:
        '''SELinux user label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#user Service#user}
        '''
        result = self._values.get("user")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecContainerSpecSecrets",
    jsii_struct_bases=[],
    name_mapping={
        "file_name": "fileName",
        "secret_id": "secretId",
        "file_gid": "fileGid",
        "file_mode": "fileMode",
        "file_uid": "fileUid",
        "secret_name": "secretName",
    },
)
class ServiceTaskSpecContainerSpecSecrets:
    def __init__(
        self,
        *,
        file_name: builtins.str,
        secret_id: builtins.str,
        file_gid: typing.Optional[builtins.str] = None,
        file_mode: typing.Optional[jsii.Number] = None,
        file_uid: typing.Optional[builtins.str] = None,
        secret_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param file_name: Represents the final filename in the filesystem. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_name Service#file_name}
        :param secret_id: ID of the specific secret that we're referencing. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#secret_id Service#secret_id}
        :param file_gid: Represents the file GID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_gid Service#file_gid}
        :param file_mode: Represents represents the FileMode of the file. Defaults to ``0o444``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_mode Service#file_mode}
        :param file_uid: Represents the file UID. Defaults to ``0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_uid Service#file_uid}
        :param secret_name: Name of the secret that this references, but this is just provided for lookup/display purposes. The config in the reference will be identified by its ID Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#secret_name Service#secret_name}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "file_name": file_name,
            "secret_id": secret_id,
        }
        if file_gid is not None:
            self._values["file_gid"] = file_gid
        if file_mode is not None:
            self._values["file_mode"] = file_mode
        if file_uid is not None:
            self._values["file_uid"] = file_uid
        if secret_name is not None:
            self._values["secret_name"] = secret_name

    @builtins.property
    def file_name(self) -> builtins.str:
        '''Represents the final filename in the filesystem.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_name Service#file_name}
        '''
        result = self._values.get("file_name")
        assert result is not None, "Required property 'file_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def secret_id(self) -> builtins.str:
        '''ID of the specific secret that we're referencing.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#secret_id Service#secret_id}
        '''
        result = self._values.get("secret_id")
        assert result is not None, "Required property 'secret_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def file_gid(self) -> typing.Optional[builtins.str]:
        '''Represents the file GID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_gid Service#file_gid}
        '''
        result = self._values.get("file_gid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_mode(self) -> typing.Optional[jsii.Number]:
        '''Represents represents the FileMode of the file. Defaults to ``0o444``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_mode Service#file_mode}
        '''
        result = self._values.get("file_mode")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def file_uid(self) -> typing.Optional[builtins.str]:
        '''Represents the file UID. Defaults to ``0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#file_uid Service#file_uid}
        '''
        result = self._values.get("file_uid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''Name of the secret that this references, but this is just provided for lookup/display purposes.

        The config in the reference will be identified by its ID

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#secret_name Service#secret_name}
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecContainerSpecSecrets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecLogDriver",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "options": "options"},
)
class ServiceTaskSpecLogDriver:
    def __init__(
        self,
        *,
        name: builtins.str,
        options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param name: The logging driver to use. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        :param options: The options for the logging driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#options Service#options}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if options is not None:
            self._values["options"] = options

    @builtins.property
    def name(self) -> builtins.str:
        '''The logging driver to use.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#name Service#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def options(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''The options for the logging driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#options Service#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecLogDriver(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecPlacement",
    jsii_struct_bases=[],
    name_mapping={
        "constraints": "constraints",
        "max_replicas": "maxReplicas",
        "platforms": "platforms",
        "prefs": "prefs",
    },
)
class ServiceTaskSpecPlacement:
    def __init__(
        self,
        *,
        constraints: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_replicas: typing.Optional[jsii.Number] = None,
        platforms: typing.Optional[typing.Sequence["ServiceTaskSpecPlacementPlatforms"]] = None,
        prefs: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param constraints: An array of constraints. e.g.: ``node.role==manager``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#constraints Service#constraints}
        :param max_replicas: Maximum number of replicas for per node (default value is ``0``, which is unlimited). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_replicas Service#max_replicas}
        :param platforms: platforms block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#platforms Service#platforms}
        :param prefs: Preferences provide a way to make the scheduler aware of factors such as topology. They are provided in order from highest to lowest precedence, e.g.: spread=node.role.manager Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#prefs Service#prefs}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if constraints is not None:
            self._values["constraints"] = constraints
        if max_replicas is not None:
            self._values["max_replicas"] = max_replicas
        if platforms is not None:
            self._values["platforms"] = platforms
        if prefs is not None:
            self._values["prefs"] = prefs

    @builtins.property
    def constraints(self) -> typing.Optional[typing.List[builtins.str]]:
        '''An array of constraints. e.g.: ``node.role==manager``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#constraints Service#constraints}
        '''
        result = self._values.get("constraints")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_replicas(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of replicas for per node (default value is ``0``, which is unlimited).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_replicas Service#max_replicas}
        '''
        result = self._values.get("max_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def platforms(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecPlacementPlatforms"]]:
        '''platforms block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#platforms Service#platforms}
        '''
        result = self._values.get("platforms")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecPlacementPlatforms"]], result)

    @builtins.property
    def prefs(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Preferences provide a way to make the scheduler aware of factors such as topology.

        They are provided in order from highest to lowest precedence, e.g.: spread=node.role.manager

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#prefs Service#prefs}
        '''
        result = self._values.get("prefs")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecPlacement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecPlacementPlatforms",
    jsii_struct_bases=[],
    name_mapping={"architecture": "architecture", "os": "os"},
)
class ServiceTaskSpecPlacementPlatforms:
    def __init__(self, *, architecture: builtins.str, os: builtins.str) -> None:
        '''
        :param architecture: The architecture, e.g. ``amd64``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#architecture Service#architecture}
        :param os: The operation system, e.g. ``linux``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#os Service#os}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "architecture": architecture,
            "os": os,
        }

    @builtins.property
    def architecture(self) -> builtins.str:
        '''The architecture, e.g. ``amd64``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#architecture Service#architecture}
        '''
        result = self._values.get("architecture")
        assert result is not None, "Required property 'architecture' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def os(self) -> builtins.str:
        '''The operation system, e.g. ``linux``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#os Service#os}
        '''
        result = self._values.get("os")
        assert result is not None, "Required property 'os' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecPlacementPlatforms(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResources",
    jsii_struct_bases=[],
    name_mapping={"limits": "limits", "reservation": "reservation"},
)
class ServiceTaskSpecResources:
    def __init__(
        self,
        *,
        limits: typing.Optional[typing.Sequence["ServiceTaskSpecResourcesLimits"]] = None,
        reservation: typing.Optional[typing.Sequence["ServiceTaskSpecResourcesReservation"]] = None,
    ) -> None:
        '''
        :param limits: limits block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#limits Service#limits}
        :param reservation: reservation block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#reservation Service#reservation}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if limits is not None:
            self._values["limits"] = limits
        if reservation is not None:
            self._values["reservation"] = reservation

    @builtins.property
    def limits(self) -> typing.Optional[typing.List["ServiceTaskSpecResourcesLimits"]]:
        '''limits block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#limits Service#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecResourcesLimits"]], result)

    @builtins.property
    def reservation(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecResourcesReservation"]]:
        '''reservation block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#reservation Service#reservation}
        '''
        result = self._values.get("reservation")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecResourcesReservation"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesLimits",
    jsii_struct_bases=[],
    name_mapping={"memory_bytes": "memoryBytes", "nano_cpus": "nanoCpus"},
)
class ServiceTaskSpecResourcesLimits:
    def __init__(
        self,
        *,
        memory_bytes: typing.Optional[jsii.Number] = None,
        nano_cpus: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param memory_bytes: The amounf of memory in bytes the container allocates. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#memory_bytes Service#memory_bytes}
        :param nano_cpus: CPU shares in units of ``1/1e9`` (or ``10^-9``) of the CPU. Should be at least 1000000. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#nano_cpus Service#nano_cpus}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if memory_bytes is not None:
            self._values["memory_bytes"] = memory_bytes
        if nano_cpus is not None:
            self._values["nano_cpus"] = nano_cpus

    @builtins.property
    def memory_bytes(self) -> typing.Optional[jsii.Number]:
        '''The amounf of memory in bytes the container allocates.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#memory_bytes Service#memory_bytes}
        '''
        result = self._values.get("memory_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nano_cpus(self) -> typing.Optional[jsii.Number]:
        '''CPU shares in units of ``1/1e9`` (or ``10^-9``) of the CPU. Should be at least 1000000.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#nano_cpus Service#nano_cpus}
        '''
        result = self._values.get("nano_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResourcesLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesReservation",
    jsii_struct_bases=[],
    name_mapping={
        "generic_resources": "genericResources",
        "memory_bytes": "memoryBytes",
        "nano_cpus": "nanoCpus",
    },
)
class ServiceTaskSpecResourcesReservation:
    def __init__(
        self,
        *,
        generic_resources: typing.Optional[typing.Sequence["ServiceTaskSpecResourcesReservationGenericResources"]] = None,
        memory_bytes: typing.Optional[jsii.Number] = None,
        nano_cpus: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param generic_resources: generic_resources block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#generic_resources Service#generic_resources}
        :param memory_bytes: The amounf of memory in bytes the container allocates. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#memory_bytes Service#memory_bytes}
        :param nano_cpus: CPU shares in units of 1/1e9 (or 10^-9) of the CPU. Should be at least 1000000. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#nano_cpus Service#nano_cpus}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if generic_resources is not None:
            self._values["generic_resources"] = generic_resources
        if memory_bytes is not None:
            self._values["memory_bytes"] = memory_bytes
        if nano_cpus is not None:
            self._values["nano_cpus"] = nano_cpus

    @builtins.property
    def generic_resources(
        self,
    ) -> typing.Optional[typing.List["ServiceTaskSpecResourcesReservationGenericResources"]]:
        '''generic_resources block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#generic_resources Service#generic_resources}
        '''
        result = self._values.get("generic_resources")
        return typing.cast(typing.Optional[typing.List["ServiceTaskSpecResourcesReservationGenericResources"]], result)

    @builtins.property
    def memory_bytes(self) -> typing.Optional[jsii.Number]:
        '''The amounf of memory in bytes the container allocates.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#memory_bytes Service#memory_bytes}
        '''
        result = self._values.get("memory_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def nano_cpus(self) -> typing.Optional[jsii.Number]:
        '''CPU shares in units of 1/1e9 (or 10^-9) of the CPU. Should be at least 1000000.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#nano_cpus Service#nano_cpus}
        '''
        result = self._values.get("nano_cpus")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResourcesReservation(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecResourcesReservationGenericResources",
    jsii_struct_bases=[],
    name_mapping={
        "discrete_resources_spec": "discreteResourcesSpec",
        "named_resources_spec": "namedResourcesSpec",
    },
)
class ServiceTaskSpecResourcesReservationGenericResources:
    def __init__(
        self,
        *,
        discrete_resources_spec: typing.Optional[typing.Sequence[builtins.str]] = None,
        named_resources_spec: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param discrete_resources_spec: The Integer resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#discrete_resources_spec Service#discrete_resources_spec}
        :param named_resources_spec: The String resources. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#named_resources_spec Service#named_resources_spec}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if discrete_resources_spec is not None:
            self._values["discrete_resources_spec"] = discrete_resources_spec
        if named_resources_spec is not None:
            self._values["named_resources_spec"] = named_resources_spec

    @builtins.property
    def discrete_resources_spec(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The Integer resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#discrete_resources_spec Service#discrete_resources_spec}
        '''
        result = self._values.get("discrete_resources_spec")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def named_resources_spec(self) -> typing.Optional[typing.List[builtins.str]]:
        '''The String resources.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#named_resources_spec Service#named_resources_spec}
        '''
        result = self._values.get("named_resources_spec")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecResourcesReservationGenericResources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceTaskSpecRestartPolicy",
    jsii_struct_bases=[],
    name_mapping={
        "condition": "condition",
        "delay": "delay",
        "max_attempts": "maxAttempts",
        "window": "window",
    },
)
class ServiceTaskSpecRestartPolicy:
    def __init__(
        self,
        *,
        condition: typing.Optional[builtins.str] = None,
        delay: typing.Optional[builtins.str] = None,
        max_attempts: typing.Optional[jsii.Number] = None,
        window: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param condition: Condition for restart. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#condition Service#condition}
        :param delay: Delay between restart attempts (ms|s|m|h). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        :param max_attempts: Maximum attempts to restart a given container before giving up (default value is ``0``, which is ignored). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_attempts Service#max_attempts}
        :param window: The time window used to evaluate the restart policy (default value is ``0``, which is unbounded) (ms|s|m|h). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#window Service#window}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if condition is not None:
            self._values["condition"] = condition
        if delay is not None:
            self._values["delay"] = delay
        if max_attempts is not None:
            self._values["max_attempts"] = max_attempts
        if window is not None:
            self._values["window"] = window

    @builtins.property
    def condition(self) -> typing.Optional[builtins.str]:
        '''Condition for restart.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#condition Service#condition}
        '''
        result = self._values.get("condition")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''Delay between restart attempts (ms|s|m|h).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_attempts(self) -> typing.Optional[jsii.Number]:
        '''Maximum attempts to restart a given container before giving up (default value is ``0``, which is ignored).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_attempts Service#max_attempts}
        '''
        result = self._values.get("max_attempts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def window(self) -> typing.Optional[builtins.str]:
        '''The time window used to evaluate the restart policy (default value is ``0``, which is unbounded) (ms|s|m|h).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#window Service#window}
        '''
        result = self._values.get("window")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceTaskSpecRestartPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.ServiceUpdateConfig",
    jsii_struct_bases=[],
    name_mapping={
        "delay": "delay",
        "failure_action": "failureAction",
        "max_failure_ratio": "maxFailureRatio",
        "monitor": "monitor",
        "order": "order",
        "parallelism": "parallelism",
    },
)
class ServiceUpdateConfig:
    def __init__(
        self,
        *,
        delay: typing.Optional[builtins.str] = None,
        failure_action: typing.Optional[builtins.str] = None,
        max_failure_ratio: typing.Optional[builtins.str] = None,
        monitor: typing.Optional[builtins.str] = None,
        order: typing.Optional[builtins.str] = None,
        parallelism: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param delay: Delay between task updates (ns|us|ms|s|m|h). Defaults to ``0s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        :param failure_action: Action on update failure: pause | continue | rollback. Defaults to ``pause``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#failure_action Service#failure_action}
        :param max_failure_ratio: Failure rate to tolerate during an update. Defaults to ``0.0``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_failure_ratio Service#max_failure_ratio}
        :param monitor: Duration after each task update to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#monitor Service#monitor}
        :param order: Update order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#order Service#order}
        :param parallelism: Maximum number of tasks to be updated in one iteration. Defaults to ``1``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#parallelism Service#parallelism}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if delay is not None:
            self._values["delay"] = delay
        if failure_action is not None:
            self._values["failure_action"] = failure_action
        if max_failure_ratio is not None:
            self._values["max_failure_ratio"] = max_failure_ratio
        if monitor is not None:
            self._values["monitor"] = monitor
        if order is not None:
            self._values["order"] = order
        if parallelism is not None:
            self._values["parallelism"] = parallelism

    @builtins.property
    def delay(self) -> typing.Optional[builtins.str]:
        '''Delay between task updates (ns|us|ms|s|m|h). Defaults to ``0s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#delay Service#delay}
        '''
        result = self._values.get("delay")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def failure_action(self) -> typing.Optional[builtins.str]:
        '''Action on update failure: pause | continue | rollback. Defaults to ``pause``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#failure_action Service#failure_action}
        '''
        result = self._values.get("failure_action")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_failure_ratio(self) -> typing.Optional[builtins.str]:
        '''Failure rate to tolerate during an update. Defaults to ``0.0``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#max_failure_ratio Service#max_failure_ratio}
        '''
        result = self._values.get("max_failure_ratio")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def monitor(self) -> typing.Optional[builtins.str]:
        '''Duration after each task update to monitor for failure (ns|us|ms|s|m|h). Defaults to ``5s``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#monitor Service#monitor}
        '''
        result = self._values.get("monitor")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def order(self) -> typing.Optional[builtins.str]:
        '''Update order: either 'stop-first' or 'start-first'. Defaults to ``stop-first``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#order Service#order}
        '''
        result = self._values.get("order")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parallelism(self) -> typing.Optional[jsii.Number]:
        '''Maximum number of tasks to be updated in one iteration. Defaults to ``1``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/service.html#parallelism Service#parallelism}
        '''
        result = self._values.get("parallelism")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ServiceUpdateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Volume(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-docker.Volume",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/docker/r/volume.html docker_volume}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        driver: typing.Optional[builtins.str] = None,
        driver_opts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        labels: typing.Optional[typing.Sequence["VolumeLabels"]] = None,
        name: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/docker/r/volume.html docker_volume} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param driver: Driver type for the volume. Defaults to ``local``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#driver Volume#driver}
        :param driver_opts: Options specific to the driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#driver_opts Volume#driver_opts}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#labels Volume#labels}
        :param name: The name of the Docker volume (will be generated if not provided). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#name Volume#name}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = VolumeConfig(
            driver=driver,
            driver_opts=driver_opts,
            labels=labels,
            name=name,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(Volume, self, [scope, id, config])

    @jsii.member(jsii_name="resetDriver")
    def reset_driver(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriver", []))

    @jsii.member(jsii_name="resetDriverOpts")
    def reset_driver_opts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDriverOpts", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="mountpoint")
    def mountpoint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mountpoint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverInput")
    def driver_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "driverInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOptsInput")
    def driver_opts_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "driverOptsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labelsInput")
    def labels_input(self) -> typing.Optional[typing.List["VolumeLabels"]]:
        return typing.cast(typing.Optional[typing.List["VolumeLabels"]], jsii.get(self, "labelsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driver")
    def driver(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "driver"))

    @driver.setter
    def driver(self, value: builtins.str) -> None:
        jsii.set(self, "driver", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="driverOpts")
    def driver_opts(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "driverOpts"))

    @driver_opts.setter
    def driver_opts(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        jsii.set(self, "driverOpts", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="labels")
    def labels(self) -> typing.List["VolumeLabels"]:
        return typing.cast(typing.List["VolumeLabels"], jsii.get(self, "labels"))

    @labels.setter
    def labels(self, value: typing.List["VolumeLabels"]) -> None:
        jsii.set(self, "labels", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        jsii.set(self, "name", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.VolumeConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "driver": "driver",
        "driver_opts": "driverOpts",
        "labels": "labels",
        "name": "name",
    },
)
class VolumeConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        driver: typing.Optional[builtins.str] = None,
        driver_opts: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        labels: typing.Optional[typing.Sequence["VolumeLabels"]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param driver: Driver type for the volume. Defaults to ``local``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#driver Volume#driver}
        :param driver_opts: Options specific to the driver. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#driver_opts Volume#driver_opts}
        :param labels: labels block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#labels Volume#labels}
        :param name: The name of the Docker volume (will be generated if not provided). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#name Volume#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if driver is not None:
            self._values["driver"] = driver
        if driver_opts is not None:
            self._values["driver_opts"] = driver_opts
        if labels is not None:
            self._values["labels"] = labels
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def driver(self) -> typing.Optional[builtins.str]:
        '''Driver type for the volume. Defaults to ``local``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#driver Volume#driver}
        '''
        result = self._values.get("driver")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def driver_opts(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Options specific to the driver.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#driver_opts Volume#driver_opts}
        '''
        result = self._values.get("driver_opts")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def labels(self) -> typing.Optional[typing.List["VolumeLabels"]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#labels Volume#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.List["VolumeLabels"]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''The name of the Docker volume (will be generated if not provided).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#name Volume#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VolumeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-docker.VolumeLabels",
    jsii_struct_bases=[],
    name_mapping={"label": "label", "value": "value"},
)
class VolumeLabels:
    def __init__(self, *, label: builtins.str, value: builtins.str) -> None:
        '''
        :param label: Name of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#label Volume#label}
        :param value: Value of the label. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#value Volume#value}
        '''
        self._values: typing.Dict[str, typing.Any] = {
            "label": label,
            "value": value,
        }

    @builtins.property
    def label(self) -> builtins.str:
        '''Name of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#label Volume#label}
        '''
        result = self._values.get("label")
        assert result is not None, "Required property 'label' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Value of the label.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/docker/r/volume.html#value Volume#value}
        '''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "VolumeLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "Config",
    "ConfigConfig",
    "Container",
    "ContainerCapabilities",
    "ContainerConfig",
    "ContainerDevices",
    "ContainerHealthcheck",
    "ContainerHost",
    "ContainerLabels",
    "ContainerMounts",
    "ContainerMountsBindOptions",
    "ContainerMountsTmpfsOptions",
    "ContainerMountsVolumeOptions",
    "ContainerMountsVolumeOptionsLabels",
    "ContainerNetworkData",
    "ContainerNetworksAdvanced",
    "ContainerPorts",
    "ContainerUlimit",
    "ContainerUpload",
    "ContainerVolumes",
    "DataDockerImage",
    "DataDockerImageConfig",
    "DataDockerNetwork",
    "DataDockerNetworkConfig",
    "DataDockerNetworkIpamConfig",
    "DataDockerPlugin",
    "DataDockerPluginConfig",
    "DataDockerRegistryImage",
    "DataDockerRegistryImageConfig",
    "DockerProvider",
    "DockerProviderConfig",
    "DockerProviderRegistryAuth",
    "Image",
    "ImageBuild",
    "ImageConfig",
    "Network",
    "NetworkConfig",
    "NetworkIpamConfig",
    "NetworkLabels",
    "Plugin",
    "PluginConfig",
    "PluginGrantPermissions",
    "RegistryImage",
    "RegistryImageBuild",
    "RegistryImageBuildAuthConfig",
    "RegistryImageBuildUlimit",
    "RegistryImageConfig",
    "Secret",
    "SecretConfig",
    "SecretLabels",
    "Service",
    "ServiceAuth",
    "ServiceConfig",
    "ServiceConvergeConfig",
    "ServiceEndpointSpec",
    "ServiceEndpointSpecPorts",
    "ServiceLabels",
    "ServiceMode",
    "ServiceModeReplicated",
    "ServiceRollbackConfig",
    "ServiceTaskSpec",
    "ServiceTaskSpecContainerSpec",
    "ServiceTaskSpecContainerSpecConfigs",
    "ServiceTaskSpecContainerSpecDnsConfig",
    "ServiceTaskSpecContainerSpecHealthcheck",
    "ServiceTaskSpecContainerSpecHosts",
    "ServiceTaskSpecContainerSpecLabels",
    "ServiceTaskSpecContainerSpecMounts",
    "ServiceTaskSpecContainerSpecMountsBindOptions",
    "ServiceTaskSpecContainerSpecMountsTmpfsOptions",
    "ServiceTaskSpecContainerSpecMountsVolumeOptions",
    "ServiceTaskSpecContainerSpecMountsVolumeOptionsLabels",
    "ServiceTaskSpecContainerSpecPrivileges",
    "ServiceTaskSpecContainerSpecPrivilegesCredentialSpec",
    "ServiceTaskSpecContainerSpecPrivilegesSeLinuxContext",
    "ServiceTaskSpecContainerSpecSecrets",
    "ServiceTaskSpecLogDriver",
    "ServiceTaskSpecPlacement",
    "ServiceTaskSpecPlacementPlatforms",
    "ServiceTaskSpecResources",
    "ServiceTaskSpecResourcesLimits",
    "ServiceTaskSpecResourcesReservation",
    "ServiceTaskSpecResourcesReservationGenericResources",
    "ServiceTaskSpecRestartPolicy",
    "ServiceUpdateConfig",
    "Volume",
    "VolumeConfig",
    "VolumeLabels",
]

publication.publish()
