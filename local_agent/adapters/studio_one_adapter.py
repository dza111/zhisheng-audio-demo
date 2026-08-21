from __future__ import annotations

from pathlib import Path

try:
    from ..automation.song_structure import SongStructureError, target_track_indexes
    from ..automation.studio_one_automation import StudioOneAutomation, StudioOneAutomationError
    from ..studio_one_adapter import AdapterHealth, MixResult
except ImportError:
    from automation.song_structure import SongStructureError, target_track_indexes
    from automation.studio_one_automation import StudioOneAutomation, StudioOneAutomationError
    from studio_one_adapter import AdapterHealth, MixResult


class StudioOneAdapterImpl:
    """Fixed competition workflow: accompaniment -> Stereo, vocal -> Mono."""

    def __init__(self, config: dict):
        self.settings = config.get("studio_one", config)
        self.automation = StudioOneAutomation(self.settings)
        self.cancelled: set[str] = set()

    def healthcheck(self) -> AdapterHealth:
        ready, message = self.automation.healthcheck()
        if not ready:
            return AdapterHealth(False, message)
        try:
            targets = target_track_indexes(Path(self.settings["song_path"]))
        except (KeyError, SongStructureError) as exc:
            return AdapterHealth(False, f"Studio One template preflight failed: {exc}")
        return AdapterHealth(True, f"Studio One template ready: {targets}")

    def process(self, job: dict, workspace: Path, progress_callback) -> MixResult:
        source_song = Path(self.settings["song_path"])
        result_path = Path(self.settings["result_path"])
        roles = {entry.get("role") for entry in job.get("inputs", [])}
        if roles != {"accompaniment", "vocal"}:
            raise StudioOneAutomationError("job must contain exactly accompaniment and vocal")
        if not result_path.parent.is_dir():
            raise StudioOneAutomationError(f"Mixdown directory does not exist: {result_path.parent}")
        try:
            target_track_indexes(source_song)
        except SongStructureError as exc:
            raise StudioOneAutomationError(str(exc)) from exc

        before = self.automation.snapshot_mixdown(result_path.parent)
        progress_callback("preparing", "Preparing Studio One")
        self.automation.open_song(source_song)
        self.automation.wait_until_ready()
        for role in ("accompaniment", "vocal"):
            item = next(entry for entry in job["inputs"] if entry["role"] == role)
            track_number = 1 if role == "accompaniment" else 2
            progress_callback("studio_processing", f"[{track_number}/10] Selecting {role} track")
            if role == "accompaniment":
                self.automation.select_first_track()
            else:
                self.automation.select_next_track()
            self.automation.import_audio_to_selected_track(Path(item["local_path"]))
            progress_callback("studio_processing", f"[{track_number + 2}/10] {role} import completed")
        progress_callback("studio_processing", "Aligning both audio events to 00:00:00")
        self.automation.align_event_to_start()
        progress_callback("exporting", "Exporting the saved Studio One MP3 mixdown")
        self.automation.export_mixdown("mp3")
        exported = self.automation.wait_for_export(result_path, before)
        return MixResult(exported, "studio_one")

    def cancel(self, job_id: str) -> bool:
        self.cancelled.add(job_id)
        return True
