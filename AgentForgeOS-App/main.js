const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');
const net = require('net');

let backendProcess;

function waitForBackend(port, callback) {
    const check = () => {
        http.get(`http://127.0.0.1:${port}/health`, () => {
            callback();
        }).on('error', () => {
            setTimeout(check, 500);
        });
    };
    check();
}

function findFreePort(startPort, endPort) {
    return new Promise((resolve, reject) => {
        let port = startPort;
        const tryNext = () => {
            if (port > endPort) {
                reject(new Error(`No free port found in range ${startPort}-${endPort}`));
                return;
            }
            const server = net.createServer();
            server.unref();
            server.on('error', () => {
                port += 1;
                tryNext();
            });
            server.listen(port, '127.0.0.1', () => {
                server.close(() => resolve(port));
            });
        };
        tryNext();
    });
}

function isPortAvailable(port) {
    return new Promise((resolve) => {
        const server = net.createServer();
        server.unref();
        server.on('error', () => resolve(false));
        server.listen(port, '127.0.0.1', () => {
            server.close(() => resolve(true));
        });
    });
}

function createWindow(port) {
    const win = new BrowserWindow({
        width: 1400,
        height: 900,
        show: false
    });

    win.loadURL(`data:text/html,
        <html>
            <body style="background:#0b0b0b;color:white;display:flex;align-items:center;justify-content:center;">
                <h2>Starting AgentForgeOS...</h2>
            </body>
        </html>
    `);

    waitForBackend(port, async () => {
        try {
            await win.webContents.session.clearCache();
        } catch (e) {
        }
        const cacheBust = Date.now();
        win.loadURL(`http://127.0.0.1:${port}/?v=${app.getVersion()}-${cacheBust}`);
        win.show();
    });
}

app.whenReady().then(async () => {
    const backendPath = app.isPackaged
        ? path.join(process.resourcesPath, 'backend.exe')
        : path.join(__dirname, '..', 'dist_backend2', 'backend.exe');
    const desiredPort = Number.parseInt(process.env.AGENTFORGE_PORT || "", 10);
    const desiredValid = Number.isInteger(desiredPort) && desiredPort > 0 && desiredPort < 65536;
    const port = (desiredValid && await isPortAvailable(desiredPort))
        ? desiredPort
        : await findFreePort(8000, 8099);
    backendProcess = spawn(backendPath, [], {
        windowsHide: true,
        env: { ...process.env, AGENTFORGE_PORT: String(port), AGENTFORGE_ENV: 'production' },
    });

    createWindow(port);
});

app.on('window-all-closed', () => {
    if (backendProcess) backendProcess.kill();
    app.quit();
});
