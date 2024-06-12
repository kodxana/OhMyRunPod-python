
# OhMyRunPod

OhMyRunPod is a command-line tool designed to facilitate various operations within a pod environment. It provides functionalities such as setting up SSH and displaying pod information and more things to be added.

## Features

- **SSH Setup**: Easily configure SSH for your pod environment.
- **Pod Information**: Display detailed information about the pod, such as RAM, Public IP, GPU count, vCPU count, and CUDA versions.

## Installation

To install OhMyRunPod, you can use pip:

\```bash
pip install OhMyRunPod
\```

## Usage

After installation, you can run OhMyRunPod using the following commands:

### Setup SSH

To set up SSH:

\```bash
OhMyRunPod --setup-ssh
\```

This command will configure SSH for your pod based on the environment settings.

### Display Pod Information

To display information about your pod:

\```bash
OhMyRunPod --info
\```

This command will show detailed information about the pod, including hardware resources and software versions.

## Contributing

Contributions to OhMyRunPod are welcome! Please feel free to submit pull requests or open issues to discuss proposed changes or report bugs.

## License

This project is licensed under the [GPL-3.0 license](LICENSE).

## Acknowledgements

Special thanks to everyone who contributed to the development and maintenance of OhMyRunPod.
