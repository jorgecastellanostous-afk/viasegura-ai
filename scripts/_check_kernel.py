import jupyter_client, json
specs = jupyter_client.kernelspec.KernelSpecManager().get_all_specs()
for name, spec in specs.items():
    print(f"Kernel: {name}")
    argv = spec["spec"]["argv"]
    print(f"  argv[0]: {argv[0]}")
    print(f"  display_name: {spec['spec']['display_name']}")
