# Plugin permissions

Pumpkin plugins run in a WASM sandbox, meaning that they don't by default have permission to access anything on the host system. This is great for safety/security, but limits plugin functionality quite a bit. For this reason it is possible for plugins to request access to specific server resources through the permissions list.

When a plugin is first added to the server, or when a plugin is updated, the server will prompt the server admin in the console with a list of the permissions the plugin requests and ask for a single `y` or `n`. The admin either approves everything the plugin asked for, or denies it (which then prevents the plugin from loading). The answer is remembered until the plugin file or its permission list changes. Server owners can also pre-approve or block individual permissions, per plugin or globally, without being asked: see [Plugin loading & server configuration](./plugin-configuration.md).

> [!NOTE]
> All permission groups **besides `sys.info.*`** control access to official `wasi:*` extensions. These are usually implemented by the language natively and Pumpkin doesn't re-expose an API for them. For example to use the `fs.read.data` permission to read a file, you should use your language's native file reading API (like `fs::read()` in Rust or `open()` in Python)

## File system permissions

### `fs.read.data` { data-since=0.1 }

Allows a plugin to read data in the plugin's dedicated data folder. On disk this folder is `./plugins/data/<plugin_name>` relative to the server's working directory, but the plugin never sees that path. It runs inside a sandbox where the folder is mounted as `data`, and `context.get_data_folder()` returns that sandbox path (the string `data`), which is what you should open with your language's file API. This permission applies to sub-directories as well.

### `fs.write.data` { data-since=0.1 }

Allows a plugin to write data in the plugin's dedicated data folder (the same folder as above, see `fs.read.data`). This permission also implies `fs.read.data`, so a plugin that writes doesn't need to ask for both. It applies to sub-directories as well.

## HTTP

### `http.outbound` { data-since=0.1 }

This permission allows the plugin to access the `wasi:http` extension and make outbound http requests. Note: This permission is separate from the `network.*` group which instead allows access to the more powerful `wasi:socket` extension.

## Networking permissions

All the permissions listed below control access level to the `wasi:socket` API.

How they combine, since the names suggest more overlap than there is: `network.tcp` allows both connecting and binding for TCP, and `network.udp` does the same for UDP. `network.outbound` allows TCP and UDP *connections* to anywhere but does not allow binding or listening. `network.loopback` doesn't grant anything on its own, it restricts whatever else the plugin was granted to loopback addresses. A plugin that also wants DNS needs `network.dns` on top of any of these.

### `network.dns` { data-since=0.1 }

Allows plugin to perform DNS resolution (required if you plan on sending requests to servers by domain name instead of IP)

### `network.tcp` { data-since=0.1 }

Allows working with TCP requests

#### `network.tcp.connect` { data-since=0.1 }

Permission for plugin to behave as a TCP client and connect to an existing TCP server

#### `network.tcp.bind` { data-since=0.1 }

Permission for plugin to behave as a TCP server and accept client connections

### `network.udp` { data-since=0.1 }

Allows working with UDP requests

#### `network.udp.connect` { data-since=0.1 }

Permission for plugin to behave as a UDP client and connect to an existing TCP server

#### `network.udp.bind` { data-since=0.1 }

Permission for plugin to behave as a UDP server and accept client connections

#### `network.udp.outgoingdatagram` { data-since=0.1 }

Allows the plugin to send UDP datagrams to non-connected UDP socket (connectionless data sending)

### `network.loopback` { data-since=0.1 }

Only allows plugin to make requests to sockets on the loopback address (localhost)

### `network.outbound` { data-since=0.1 }

Allow plugin to make requests to any external IP or domain (full internet access)

> [!WARNING]
> It is recommended to **not** grant this permission unless the plugin has a legitimate usecase for this permission, as it allows the plugin to make uncontrolled requests to any device on the internet

## System permissions

### `sys.env` { data-since=0.1 }

Allow plugin to read any of the host's environment variables

### `sys.env.*` { data-since=0.1 }

This is a prefix that allows the plugin to specifically request permission to read only certain environment variables. An example use would be `sys.env.HOME` to read the user's home directory location, or `sys.env.TZ` to get the server's configured timezone

### `sys.info` { data-since=0.1 }

Allows plugin to access all system information (OS, CPU, RAM, Pumpkin version) from the `server.get_sys_info()` method

#### `sys.info.cpu` { data-since=0.1 }

Allow access to read specifically the CPU information

#### `sys.info.ram` { data-since=0.1 }

Allow access to read the memory information specifically

#### `sys.info.os` { data-since=0.1 }

Allow reading OS info specifically
