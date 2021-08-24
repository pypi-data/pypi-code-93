CLI_COMMANDS_HELP = {
    'parameter': {
        'add': """Add a parameter to a context, or update a parameter if it is already existing in the context.\n
                ** Tips: 1) If the parameter is inherited from the parent contexts, it will be overriden in the context. 2) Multiple parameters may be added at once using the '--input' option.\n
                KEY: The identifier of the parameter to be added. It may also be provided using the '--key' option.\n
                VALUE: The value for the parameter. If the parameter is already existing in the context, the value will be updated to the new one. It may also be provided using the '--value' option.\n
                """,
        'list': """Return the list of owned/inherited parameters in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden parameters only, use the '--uninherited' option. This will return only the context specific parameters.
                """,
        'get': """Return the current value of a parameter.\n
                ** Tips: 1) The parameter may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the parameter. It may also be provided using the '--key' option.\n
                """,
        'edit': """Edit the current value of a parameter.\n
                ** Tips: 1) The parameter may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the parameter. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a parameter from a context.\n
                ** Tips: 1) The inherited parameters cannot be deleted. The context must be the owner of the parameter or a not found error will be returned. 2) Multiple parameters may be deleted at once using the '--input' option.\n         
                KEY: The identifier of the parameter to be deleted. It may also be provided using the '--key' option.\n
                """,
        'history': """Return the revision history of parameter.\n
                ** Tips: 1) The parameter may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the parameter. It may also be provided using the '--key' option.\n
                """,
    },
    'secret': {
        'add': """Add a secret to a context, or update a secret if it is already existing in the context.\n
                ** Tips: 1) If the secret is inherited from the parent contexts, it will be overriden in the context. 2) Multiple secrets may be added at once using the '--input' option.\n
                KEY: The identifier of the secret to be added. It may also be provided using the '--key' option.\n
                VALUE: The value for the secret. If the secret is already existing in the context, the value will be updated to the new one. It may also be provided using the '--value' option.\n
                """,
        'list': """Return the list of owned/inherited secrets in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden secrets only, use the '--uninherited' option. This will return only the context specific secrets.
                """,
        'get': """Return the current value of a secret.\n
                ** Tips: 1) The secret may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'edit': """Edit the current value of a secret.\n
                ** Tips: 1) The secret may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a secret from a context.\n
                ** Tips: 1) The inherited secrets cannot be deleted. The context must be the owner of the secret or a not found error will be returned. 2) Multiple secrets may be deleted at once using the '--input' option.\n         
                KEY: The identifier of the secret to be deleted. It may also be provided using the '--key' option.\n
                """,
        'history': """Return the revision history of secret.\n
                ** Tips: 1) The secret may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,

    },
    'template': {
        'add': """Add a template to a context, or update the contents if it is already existing in the context.\n
                ** Tips: 1) If the template is inherited from the parent contexts, it will be overriden in the context. 2) Multiple templates may be added recursively from a directory.\n
                KEY: The identifier of the template to be added. It may also be provided using the '--key' option.\n
                """,
        'list': """Return the list of templates in a context.\n
                ** Tips: 1) To limit the list to the owned/overriden templates only, use the '--uninherited' option. This will return only the context specific templates.
                """,
        'get': """Return the contents of a template.\n
                ** Tips: 1) The template may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'edit': """Edit the contents of a template.\n
                ** Tips: 1) The template may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the secret. It may also be provided using the '--key' option.\n
                """,
        'delete': """Delete a template from a context.\n
                ** Tips: 1) The inherited template cannot be deleted. The context must be the owner of the secret or a not found error will be returned. 2) Multiple templates may be deleted at once using the '--input' option.\n
                KEY: The identifier of the template to be deleted. It may also be provided using the '--key' option.\n
                """,
        'history': """Return the revision history of template.\n
                ** Tips: 1) The template may be inherited from the parent contexts or owned by the given context.\n
                KEY: The identifier of the template. It may also be provided using the '--key' option.\n
                """,
        'render': """Render templates in a context.\n
                    """,
        },
    'config': {
        'get': """Get DSO application configuration.\n
                ** Tips: 1) Use --local or --global to get local or global configuration only.\n
                KEY: The key of the configuration
                """,
        'set': """Set DSO application configuration.\n
                ** Tips: 1) Use --local or --global to get local or global configuration only.\n
                KEY: The key of the configuration. It may also be provided using the '--key' option.\n
                VALUE: The value for the configuration. It may also be provided using the '--value' option.\n
                """,
        'delete': """Get DSO application configuration.\n
                ** Tips: 1) Use --local or --global to get local or global configuration only.\n
                KEY: The key of the configuration
                """,
        'init': """Initialize DSO configuration for the working directory.\n
                ** Tips: 1) Use --input to load connfiguration from a file.\n
                The option '--working-dir' can be used to specify a different working directory than the current directory where dso is running in.\n
                """,
    },
    'network': {
        'layout_subnet_plan': """Layout subnet plan.\n
                """,

    }
}

CLI_COMMANDS_SHORT_HELP = {
    'version': "Display versions.",
    'parameter': {
        'list': "List parameters available to the application.",
        'add': "Add/Update one or multiple parameters to the application.",
        'get': "Get the value of a parameter.",
        'edit': "Edit the value of a parameter.",
        'delete': "Delete one or multiple parameters from the application.",
        'history': "Get the revision history of a parameter.",
    },
    'secret': {
        'list': "List secrets available to the application.",
        'add': "Add/Update one or multiple secrets to the application.",
        'get': "Get the value of a secret.",
        'edit': "Edit the value of a secret.",
        'delete': "Delete one or multiple secrets from the application.",
        'history': "Get the revision history of a secret.",
    },
    'template': {
        'list': "List templates available to the application.",
        'add': "Add/Update a template to the application.",
        'get': "Get the contents of a template.",
        'edit': "Edit the contents of a template.",
        'delete': "Delete one or multiple templates from the application.",
        'history': "Get the revision history of a template.",
        'render': "Render templates using parameters in a context.",
    },
    'package': {
        'list': "List packages built for the application.",
        'create': "Create a build package for the application.",
        'get': "Download an application build package.",
        'delete': "Delete a build package from the application.",
    },
    'release': {
        'list': "List deployment releases for the application.",
        'create': "Create a deployment release for the application.",
        'get': "Download an application deployment release.",
        'delete': "Delete a deployment release from the application.",
    },
    'config': {
        'get': "Get DSO application configuration(s).",
        'set': "Set the DSO application configuration(s).",
        'delete': "Delete a DSO application configuration.",
        'init': "Initialize DSO configuration for the working directory.",
    },
    'network': {
        'layout_subnet_plan': "Layout subnet plan group.",

    }

}
CLI_PARAMETERS_HELP = {
    'common': {
        'working_dir': "Path to a (local) directory where the DSO application configuration resides. By default, the current working directory will be used if the option is not provided.",
        'verbosity' : "Specify the logging verbosity, where 0 is for logging critical fatal errors only, 1 also logs error messages, 2 also logs warnings, 3 also logs information messages, 4 also logs debug messages, and finally 5 logs everything.",
        'stage' : "Target a specific stage using the stage identifier, which is combination of a name and an optional number, where name must conform to ^([a-zA-Z][a-zA-Z0-9]+)$ regex expression. If no /<number> is specified, the default environment (/0) in the given context will be targeted.",
        'input' : "Path to a (local) file defining the input data. Use '-' to read from the shell pipe or stdin. Use '--format' to specify the format if needed.",
        'format': "Specify the format of the output or the input if mixed with the '--input' option.",
        'config': "Comma separated list of key/value pairs to temporarily override the current DSO application configurations. It takes effect only while executing the command and does not have any lasting effect on the DSO application configuration or subsequent command executions.",
        'query': "Customize output using JMESPath query language.",
        'query_all': "Include all the available fields in the ouput.",
        'global_scope': "Use the global context.",
        'project_scope': "Use the project context.",
        'scope': "Select the context scope.",
        'filter': "Use a regex pattern to filter result by the provider.",

    },
    'parameter': {
        'key': "The key of the parameter. See KEY argument for more details.",
        'value': "The value for the parameter. See VALUE argument for more details.",
        'query_values': "Include parameter values in the output.",
        'uninherited': "Select only parameters which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'revision': "The revision ID whose value to be fetched.",
        'history': "Get the revision history of the parameter.",

    },
    'secret': {
        'key': "The key of the secret",
        'value': "The value for the secret",
        'decrypt': "Decrypt the secret value.",
        'query_values': "Include secret values in the output.",
        'uninherited': "Select only secrets which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'revision': "The revision ID whose value to be fetched.",
        'history': "Get the revision history of the secret.",
    },
    'template': {
        'type': "Type of the template. Use 'resource' for templates needed at the provision time when provisioning resources required by the application to run such as SQS queus, SNS topics, and CI/CD piplines.\nUse 'package' for templates needed at the build time when generating a package.\nUse 'release' for templates needed at the deploy time when generating a release." ,
        'key': "The key of the template",
        'limit': "Limit templates to be rendered.",
        'render_path': "Path (relative to the root of the DSO application) where rendered template will be placed at.",
        'query_render_path': "Include the template render paths in the output.",
        'input' : "Path to a local file containing the template content.",
        'recursive' : "Add files recursively.",
        'uninherited': "Select only templates which are specific to the gievn context, i.e. not inherited from the parent contexts.",
        'include_contents': "Include template contenets in the output. ",
        'history': "Get the revision history of the template.",

    },
    'config': {
        'key': "The key of the configuration",
        'value': 'Value for the configuration key',
        'input' : "Path to a local (yaml) file inputing the configuration. Use '-' to read from the shell pipe or stdin.",
        'local': "Select the local DSO configurations, i.e. existing in the working directory.",
        'global': "Select the global DSO configurations, i.e. user-wide configuration.",
        'init_local': "Explicitly override inherited configurations locally. If mixed with '-i' / '--input' option, it will casue the local configuration to be merged with the provided input configuration.",
        'setup': "Run a setup wizard to assist configuring the DSO application.",

    },
    'network': {
        'subnet_layout_mode': "Select the subnet plan layout mode.",
    
    }


}


CLI_MESSAGES = {
    'MissingOption': "Missing option {0}.",
    'MissingArgument': "Missing argument {0}.",
    'ArgumentsOnlyOneProvided': "Only one of the following arguments/options may be provided: {0}",
    'ArgumentsAtLeastOneProvided': "At least one of the following arguments/options must be provided: {0}",
    'ArgumentsAllProvided': "All of the following arguments/options must be provide: {0}",
    'ArgumentsNoneProvided': "The following arguments/options cannot be provided: {0}",
    'ArgumentsNotAllProvided': "The following arguments/options cannot be provided together: {0}",
    'ArgumentsOnlyOneProvidedBecause': "Since {0} provided, only one of the following arguments/options may be provided: {1}",
    'ArgumentsAtLeastOneProvidedBecause': "Since {0} provided, at least one of the following arguments/options must also be provided: {1}",
    'ArgumentsAllProvidedBecause': "Since {0} provided, all of the following arguments/options must also be provide: {1}",
    'ArgumentsNoneProvidedBecause': "Since {0} provided, the following arguments/options cannot be provided: {1}",
    'ArgumentsNotAllProvidedBecasue': "Since {0} provided, the following arguments/options may be provided together: {1}",
    'TryHelpWithCommand': "Try '{0} --help' for more details.",
    'TryHelp': "Try the command with '-h' / '--help' option for more details.",
    'InvalidFileFormat': "Invalid file, not conforming to the expected '{0}' format.",
    'EnteredSecretValuesNotMatched': "Entered values for the secret did not macth.",
    'RenderPathNotReleative': "Render path '{0}' is not releative to the application root directory.",
    # 'InvalidRenderPath': "'{0}' is not a valid render path.",
    'InvalidRenderPathExistingDir': "'{0}' is not a valid render path because it is an existing directory.",
    'InvalidFilter': "Invalid regex pattern for filter: {0}",
    'NoChanegeDetectedAfterEditing': "No change detected after editing.",
    'ParameterNotFound': "Parameter '{0}' not found in the given context: project={1}, application={2}, stage={3}",
    'SecretNotFound': "Secret '{0}' not found in the given context: project={1}, application={2}, stage={3}",
    'TemplateNotFound': "Template '{0}' not found in the given context: project={1}, application={2}, stage={3}",
}
