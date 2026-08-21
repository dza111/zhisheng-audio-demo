from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from local_agent.automation.song_structure import read_song_tracks, target_track_indexes
from local_agent.automation.studio_one_automation import StudioOneAutomation, select_formal_song


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="local_agent/config.json")
    parser.add_argument("--full-demo", action="store_true")
    parser.add_argument("--track-only", action="store_true", help="Click both configured tracks and capture visual evidence only")
    parser.add_argument("--next-track-only", action="store_true", help="Run internal First Track then Next Track macros only")
    parser.add_argument("--next-track-probe", action="store_true", help="Run Next Track probe macro, capture mute evidence, then undo")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        settings = config["studio_one"]
        accompaniment = Path(config["test_accompaniment"])
        vocal = Path(config["test_vocal"])
        configured_song = Path(settings["song_path"])
        song = select_formal_song(configured_song.parent, configured_song.name)
        output = Path(settings["result_path"])

        print("ACCOMPANIMENT_PATH:", accompaniment)
        print("VOCAL_PATH:", vocal)
        print("SONG_PATH:", song)
        print("OUTPUT_PATH:", output)
        paths = (accompaniment, vocal, song, output)
        if any("?" in str(path) for path in paths):
            raise RuntimeError("Configured path contains a question-mark character")
        if not accompaniment.is_file(): raise RuntimeError("accompaniment file missing")
        if not vocal.is_file(): raise RuntimeError("vocal file missing")
        if not song.is_file() or song.suffix.lower() != ".song": raise RuntimeError("formal .song missing")
        if not output.parent.is_dir(): raise RuntimeError("output directory missing")
        print("PASS accompaniment exists")
        print("PASS vocal exists")
        print("PASS song exists")
        print("PASS song is .song")
        print("PASS autosave excluded")
        print("PASS output directory exists")

        automation = StudioOneAutomation(settings)
        ready, message = automation.healthcheck()
        if not ready: raise RuntimeError(message)
        tracks = read_song_tracks(song)
        targets = target_track_indexes(song)
        if targets != {"accompaniment": 1, "vocal": 2}: raise RuntimeError(f"unexpected template targets: {targets}")
        print("PASS song structure readable")
        print("PASS Stereo track found")
        print("PASS Mono track found")
        if args.track_only or args.next_track_only or args.next_track_probe:
            diagnostics = Path(r"C:\ZhishengMixJobs\diagnostics")
            diagnostics.mkdir(parents=True, exist_ok=True)
            def capture(name: str) -> Path:
                target = diagnostics / f"track_selection_{name}.png"
                script = (
                    "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; "
                    "$b=New-Object Drawing.Bitmap([Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,[Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); "
                    "$g=[Drawing.Graphics]::FromImage($b); $g.CopyFromScreen(0,0,0,0,$b.Size); "
                    f"$b.Save('{target}',[Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $b.Dispose()"
                )
                subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)
                return target
            automation.open_song(song)
            automation.wait_until_ready()
            window = automation._window()
            if not window:
                raise RuntimeError("Studio One main window not found")
            print("NEXT_TRACK_PROBE_TEST" if args.next_track_probe else ("NEXT_TRACK_TEST" if args.next_track_only else "TRACK_SELECTION_TEST"))
            print(f"Studio One foreground hwnd = {window[0]}")
            print(f"Studio One window title = {window[1]}")
            before = capture("before")
            if args.next_track_probe:
                automation.run_next_track_probe()
                time.sleep(0.8)
                first = capture("next_track_probe")
                print("NEXT_TRACK_PROBE_COMMAND_SENT")
                # Ctrl+Z is Studio One's reversible undo for the temporary Track/Mute action.
                automation._activate()
                automation._send_keys("^z")
                time.sleep(0.8)
                second = capture("next_track_probe_after_undo")
                print("PROBE_UNDO_SENT")
            elif args.next_track_only:
                try:
                    automation.select_first_track()
                    print("FIRST_TRACK_PASS")
                except Exception as exc:
                    print("FIRST_TRACK_FAILED")
                    print("FIRST_TRACK_REASON:", exc)
                    return 1
                time.sleep(0.5)
                first = capture("after_first_track_macro")
                try:
                    automation.select_next_track()
                    print("NEXT_TRACK_COMMAND_SENT")
                except Exception as exc:
                    print("NEXT_TRACK_FAILED")
                    print("NEXT_TRACK_REASON:", exc)
                    return 1
                time.sleep(0.5)
                second = capture("after_next_track_macro")
                print(f"first track macro virtual key = {settings['first_track_macro_vk']}")
                print(f"next track macro virtual key = {settings['next_track_macro_vk']}")
            else:
                automation.click_track("accompaniment")
                time.sleep(0.5)
                first = capture("after_track_1")
                automation.click_track("vocal")
                time.sleep(0.5)
                second = capture("after_track_2")
                print(f"track 1 click: X,Y = {settings['track_click_points']['accompaniment']}")
                print(f"track 2 click: X,Y = {settings['track_click_points']['vocal']}")
            print(f"screenshot before = {before}")
            print(f"screenshot after track 1 = {first}")
            print(f"screenshot after track 2 = {second}")
            if args.next_track_probe:
                print(f"PROBE_SCREENSHOT: {first}")
                print(f"PROBE_AFTER_UNDO_SCREENSHOT: {second}")
                print("PROBE_REQUIRES_VISUAL_REVIEW")
            elif args.next_track_only:
                print("NEXT_TRACK_SELECTION_REQUIRES_VISUAL_REVIEW")
            else:
                print("TRACK_SELECTION_REQUIRES_VISUAL_REVIEW")
            return 0
        if not args.full_demo:
            print("PASS preflight complete")
            return 0

        before = automation.snapshot_mixdown(output.parent) if 'automation' in locals() else {}
        automation.open_song(song)
        automation.wait_until_ready()
        print("[1/10] Studio One activated")
        automation.select_first_track()
        print("[2/10] First Stereo track selected")
        automation.import_audio_to_selected_track(accompaniment)
        print("[3/10] Accompaniment imported")
        automation.select_next_track()
        print("[4/10] Vocal Mono track selected")
        automation.import_audio_to_selected_track(vocal)
        print("[5/10] Vocal imported")
        automation.align_event_to_start()
        automation.export_mixdown("mp3")
        print("[6/10] Export dialog opened")
        print("[7/10] VK_RETURN sent")
        result = automation.wait_for_export(output, before)
        print("[8/10] Mixdown detected")
        print("[9/10] File stable:", result)
        print("[10/10] REAL_STUDIO_ONE_MIX_PASS")
        return 0
    except Exception as exc:
        print("STUDIO_ONE_MIX_FAILED")
        print("FAILED_STEP: full demo")
        print("FAILED_REASON:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
