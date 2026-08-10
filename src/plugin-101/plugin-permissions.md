# Plugin permissions

Pumpkin plugins run in a WASM sandbox, meaning that they don't by default have permission to access anything on the host system. This is great for safety/security, but limits plugin functionality quite a bit. For this reason it is possible for plugins to request access to specific server resources through the permissions list.

When a plugin is first added to the server, or when a plugin is updated, the server will prompt the server admin with a list of permissions that each plugin requests and ask for them to approve these permissions. The admin can either approve use of all requested permissions, or deny all permissions (which then prevents the plugin from loading).

> [!NOTE]
> All permission groups **besides `sys.info.*`** control access to official `wasi:*` extensions. These are usually implemented by the language natively and Pumpkin doesn't re-expose an API for them. For example to use the `fs.read.data` permission to read a file, you should use your language's native file reading API (like `fs::read()` in Rust or `open()` in Python)

## File system permissions

### `fs.read.data`

Allows a plugin to read data in the plugin's dedicated data folder. This folder is generally located at `./plugins/data/<plugin_name>` relative to the server's working directory, however this path can differ in some situations, so plugins should use `context.get_data_folder()` to get the full path to the folder they should use. This permission applies to sub-directories as well.

### `fs.write.data`

Allows a plugin to write data in the plugin's dedicated data folder. This folder is generally located at `./plugins/data/<plugin_name>` relative to the server's working directory, however this path can differ in some situations, so plugins should use `context.get_data_folder()` to get the full path to the folder they should use. This permission applies to sub-directories as well.

## HTTP

### `http.outbound`

This permission allows the plugin to access the `wasi:http` extension and make outbound http requests. Note: This permission is separate from the `network.*` group which instead allows access to the more powerful `wasi:socket` extension.

## Networking permissions

All the permissions listed below control access level to the `wasi:socket` API.

### `network.dns`

Allows plugin to perform DNS resolution (required if you plan on sending requests to servers by domain name instead of IP)

### `network.tcp`

Allows working with TCP requests

#### `network.tcp.connect`

Permission for plugin to behave as a TCP client and connect to an existing TCP server

#### `network.tcp.bind`

Permission for plugin to behave as a TCP server and accept client connections

### `network.udp`

Allows working with UDP requests

#### `network.udp.connect`

Permission for plugin to behave as a UDP client and connect to an existing TCP server

#### `network.udp.bind`

Permission for plugin to behave as a UDP server and accept client connections

#### `network.udp.outgoingdatagram`

Allows the plugin to send UDP datagrams to non-connected UDP socket (connectionless data sending)

### `network.loopback`

Only allows plugin to make requests to sockets on the loopback address (localhost)

### `network.outbound`

Allow plugin to make requests to any external IP or domain (full internet access)

> [!WARNING]
> It is recommended to **not** grant this permission unless the plugin has a legitimate usecase for this permission, as it allows the plugin to make uncontrolled requests to any device on the internet

## System permissions

### `sys.env`

Allow plugin to read any of the host's environment variables

### `sys.env.*`

This is a prefix that allows the plugin to specifically request permission to read only certain environment variables. An example use would be `sys.env.HOME` to read the user's home directory location, or `sys.env.TZ` to get the server's configured timezone

### `sys.info`

Allows plugin to access all system information (OS, CPU, RAM, Pumpkin version) from the `server.get_sys_info()` method

#### `sys.info.cpu`

Allow access to read specifically the CPU information

#### `sys.info.ram`

Allow access to read the memory information specifically

#### `sys.info.os`

Allow reading OS info specifically
