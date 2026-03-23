const path = require("path");
const fs = require("fs");

const packager = require("electron-packager");
const { createWindowsInstaller } = require("electron-winstaller");


async function main() {
  const projectDir = __dirname;
  const outDir = path.join(projectDir, "release-squirrel");
  const appName = "AgentForgeOS";

  const backendExe = path.join(projectDir, "backend.exe");
  if (!fs.existsSync(backendExe)) {
    throw new Error(`Missing backend.exe at ${backendExe}`);
  }

  const appPaths = await packager({
    dir: projectDir,
    out: outDir,
    name: appName,
    platform: "win32",
    arch: "x64",
    overwrite: true,
    prune: true,
    asar: false,
  });

  const appDirectory = appPaths[0];
  const outputDirectory = path.join(outDir, "installer");

  await createWindowsInstaller({
    appDirectory,
    outputDirectory,
    exe: `${appName}.exe`,
    setupExe: `${appName}Setup.exe`,
    authors: "AgentForgeOS",
    description: "AgentForgeOS desktop application",
    noMsi: true,
  });
}


main().catch((err) => {
  process.stderr.write(String(err && err.stack ? err.stack : err) + "\n");
  process.exit(1);
});
