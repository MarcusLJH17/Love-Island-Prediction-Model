import { spawn } from "node:child_process";

const root = process.cwd();

function runPython(args: string[], input?: unknown) {
  return new Promise<void>((resolve, reject) => {
    const child = spawn("python", args, { cwd: root, shell: false });
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("close", (code) => {
      if (code === 0) {
        resolve();
      } else {
        reject(new Error(stderr || `python ${args.join(" ")} exited with ${code}`));
      }
    });
    if (input != null) {
      child.stdin.write(JSON.stringify(input));
    }
    child.stdin.end();
  });
}

export async function saveManualEntry(type: "tiktok" | "episode", payload: unknown) {
  const entry = payload as { date?: string; day?: number };
  await runPython(["scripts/save_manual_entry.py", "--type", type], payload);
  await runPython(["scripts/build_features.py", "--day", String(entry.day ?? 28), "--date", entry.date ?? todayId()]);
  await runPython(["scripts/export_predictions.py"]);
}

export function todayId() {
  return new Date().toISOString().slice(0, 10);
}
