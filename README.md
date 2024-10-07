# Proxmox Management Tool

This Python-based GUI tool enables the management of Linux Containers (LXC) and Virtual Machines (VM) on a Proxmox server. It provides an easy-to-use interface for viewing the status of LXCs and VMs, and for performing basic actions like starting, shutting down, or stopping instances.

## Features
- **Login Interface:** Users can input Proxmox server details to establish a connection (Node name, IP address, Username, Token ID, Token Value).
- **Status Display:** List view displaying the status of all LXCs and VMs on the connected server.
- **Administration Functions:** Start, shut down, or stop LXCs and VMs directly from the GUI.

## Requirements
- Python 3.x
- PySimpleGUI
- proxmoxer
- urllib3

Install the required packages using:

```bash
pip install PySimpleGUI proxmoxer urllib3
```

## Usage

- Run the program and enter the connection details for the Proxmox server.
- Upon successful connection, the status of all LXCs and VMs will be displayed.
- Use the buttons to refresh the status or perform administrative tasks like starting, shutting down, or stopping.

## Project Information

This program was developed as an exam project for the "Skriptsprachen" module at the University of Applied Sciences Südwestfalen.

## Warnings

The program disables the verification of the Proxmox server's HTTPS certificate (using urllib3.disable_warnings). This is insecure and should not be used in a production environment. For production use, install a valid certificate and enable certificate verification.
