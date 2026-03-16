#![cfg_attr(
    all(not(debug_assertions), target_os = "windows"),
    windows_subsystem = "windows"
)]

use std::process::{Child, Command, Stdio};
use std::sync::Mutex;
use tauri::{Manager, State, WindowEvent};

#[derive(Default)]
struct BackendProcess {
    handle: Mutex<Option<Child>>,
}

impl BackendProcess {
    fn set(&self, child: Child) {
        let mut slot = self.handle.lock().expect("backend mutex poisoned");
        if let Some(mut existing) = slot.take() {
            let _ = existing.kill();
        }
        *slot = Some(child);
    }

    fn terminate(&self) {
        if let Some(mut child) = self.handle.lock().expect("backend mutex poisoned").take() {
            let _ = child.kill();
        }
    }
}

#[tauri::command]
fn launch_backend(state: State<BackendProcess>) -> Result<(), String> {
    let child = Command::new("python")
        .arg("-m")
        .arg("engine.main")
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|e| format!("Failed to start backend: {e}"))?;
    state.set(child);
    Ok(())
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![launch_backend])
        .setup(|app| {
            app.manage(BackendProcess::default());
            let state = app.state::<BackendProcess>();
            if let Err(err) = launch_backend(state) {
                eprintln!("AgentForgeOS backend failed to start: {err}");
            }
            Ok(())
        })
        .on_window_event(|event| {
            if matches!(event.event(), WindowEvent::CloseRequested { .. }) {
                let state = event.window().state::<BackendProcess>();
                state.terminate();
            }
        })
        .run(tauri::generate_context!())
        .expect("error while running AgentForgeOS desktop runtime");
}
