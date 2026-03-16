// AgentForgeOS Tauri runtime
// Responsibilities:
// 1. Launch backend server
// 2. Load frontend UI
// 3. Package as desktop application

#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::{Command, Stdio};

#[tauri::command]
fn launch_backend() -> Result<(), String> {
    // Attempt to start the backend server using the engine entrypoint.
    // The command is intentionally simple and assumes Python is available in PATH.
    let mut cmd = Command::new("python");
    cmd.arg("-m")
        .arg("engine.main")
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|e| format!("Failed to start backend: {e}"))?;
    // Process is left detached; the user is responsible for shutdown via OS.
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![launch_backend])
        .setup(|_| {
            // Start backend automatically on app setup.
            if let Err(err) = launch_backend() {
                eprintln!("AgentForgeOS backend failed to start: {err}");
            }
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running AgentForgeOS desktop runtime");
}
