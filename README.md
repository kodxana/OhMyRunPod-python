# OhMyRunPod

OhMyRunPod is a comprehensive command-line tool designed to facilitate various operations within a Runpod environment. It provides both CLI arguments and an interactive GUI with arrow key navigation for easy pod management.

## Features

- **Interactive GUI**: Beautiful terminal interface with arrow key navigation
- **SSH Setup**: Easily configure SSH for your pod environment with secure password generation
- **Pod Information**: Display detailed information about the pod (RAM, Public IP, GPU count, vCPU count, CUDA versions)
- **Tailscale VPN**: Install and configure Tailscale for secure networking
- **File Transfer**: Multiple file transfer options including croc and SFTP
- **ComfyUI Management**: Complete ComfyUI management system with:
  - Automatic template detection (Aitrepreneur, Standard, Madiator2011's templates)
  - Custom node management via comfy-cli
  - Model downloading with CivitAI and HuggingFace token support
  - ComfyUI-Manager integration
  - Status monitoring and validation

## Installation

To install OhMyRunPod, you can use pip:

```bash
pip install OhMyRunPod
```

## Usage

### Interactive Mode (Recommended)

Simply run OhMyRunPod without any arguments to launch the interactive GUI:

```bash
OhMyRunPod
```

Navigate using arrow keys, Enter to select, and ESC to go back.

### CLI Mode

You can also use specific command-line arguments:

#### Setup SSH
```bash
OhMyRunPod --setup-ssh
```

#### Display Pod Information
```bash
OhMyRunPod --info
```

#### Setup Tailscale
```bash
OhMyRunPod --setup-tailscale
```

#### File Transfer Setup
```bash
OhMyRunPod --file-transfer
```

#### ComfyUI Management
```bash
OhMyRunPod --comfyui
```

## ComfyUI Integration

OhMyRunPod provides comprehensive ComfyUI management through integration with [comfy-cli](https://github.com/Comfy-Org/comfy-cli):

- **Template Detection**: Automatically detects common ComfyUI templates made for Runpod
- **Custom Nodes**: Install, update, and manage custom nodes
- **Model Downloads**: Download models from CivitAI and HuggingFace with token support
- **Manager Integration**: Enable/disable ComfyUI-Manager GUI
- **Status Monitoring**: Check ComfyUI installation status and running processes

## File Transfer Options

- **croc**: Secure file transfer with automatic setup
- **SFTP**: Traditional SFTP server configuration

## Requirements

- Python 3.7+
- Linux environment (designed for RunPod)
- Rich library for terminal UI (automatically installed)

## Contributing

Contributions to OhMyRunPod are welcome! Please feel free to submit pull requests or open issues to discuss proposed changes or report bugs.

## License

This project is licensed under the [GPL-3.0 license](LICENSE).

## Acknowledgements

- **Creator**: Madiator2011
- **ComfyUI Integration**: Powered by [Comfy-Cli](https://github.com/Comfy-Org/comfy-cli)
- Special thanks to everyone who contributed to the development and maintenance of OhMyRunPod.