import os
import subprocess
import sys
import re
import random
import atexit
import signal
from tqdm import tqdm

random.seed()  # Initialize with system time
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
VIDEOS_DIR = os.path.join(INPUT_DIR, "videos")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IS_WINDOWS = sys.platform.startswith('win')

# Track temp files for cleanup
TEMP_FILES = []
CURRENT_PROCESS = None

# Modern waveform style presets
# Modern waveform style presets - 15 Bar Styles
WAVEFORM_PRESETS = [
    {
        "name": "Electric Blue Bars",
        "color": "0x00FFFF",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 8,
        "win_size": 1024,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Neon Pink Equalizer",
        "color": "0xFF1493",
        "mode": "bar",
        "scale": "log",
        "split_channels": False,
        "thickness": 10,
        "win_size": 512,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Lime Green Spectrum",
        "color": "0x39FF14",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 6,
        "win_size": 2048,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Blazing Orange Bars",
        "color": "0xFF4500",
        "mode": "bar",
        "scale": "cbrt",
        "split_channels": False,
        "thickness": 12,
        "win_size": 1024,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Royal Purple Waves",
        "color": "0x9D00FF",
        "mode": "bar",
        "scale": "log",
        "split_channels": False,
        "thickness": 9,
        "win_size": 768,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Golden Frequency Bars",
        "color": "0xFFD700",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 7,
        "win_size": 1536,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Crimson Red Spectrum",
        "color": "0xDC143C",
        "mode": "bar",
        "scale": "lin",
        "split_channels": False,
        "thickness": 11,
        "win_size": 512,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Turquoise Dream Bars",
        "color": "0x40E0D0",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 8,
        "win_size": 1024,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Violet Storm Equalizer",
        "color": "0x8A2BE2",
        "mode": "bar",
        "scale": "log",
        "split_channels": False,
        "thickness": 10,
        "win_size": 896,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Coral Reef Bars",
        "color": "0xFF7F50",
        "mode": "bar",
        "scale": "cbrt",
        "split_channels": False,
        "thickness": 9,
        "win_size": 1280,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Aqua Marine Spectrum",
        "color": "0x00CED1",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 7,
        "win_size": 2048,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Hot Magenta Bars",
        "color": "0xFF00FF",
        "mode": "bar",
        "scale": "log",
        "split_channels": False,
        "thickness": 12,
        "win_size": 640,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Chartreuse Pulse",
        "color": "0x7FFF00",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 8,
        "win_size": 1024,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Sapphire Blue Equalizer",
        "color": "0x0F52BA",
        "mode": "bar",
        "scale": "cbrt",
        "split_channels": False,
        "thickness": 11,
        "win_size": 1152,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    },
    {
        "name": "Ruby Red Spectrum",
        "color": "0xE0115F",
        "mode": "bar",
        "scale": "log",
        "split_channels": False,
        "thickness": 9,
        "win_size": 768,
        "glow": True,
        "position": "bottom",
        "type": "bars"
    }
]


def cleanup_all_temp_files():
    """Clean up all tracked temp files and kill running process"""
    global CURRENT_PROCESS

    # Kill running FFmpeg process
    if CURRENT_PROCESS:
        try:
            CURRENT_PROCESS.terminate()
            CURRENT_PROCESS.wait(timeout=3)
        except:
            try:
                CURRENT_PROCESS.kill()
            except:
                pass
        CURRENT_PROCESS = None

    # Clean up temp files
    for f in TEMP_FILES:
        try:
            if os.path.exists(f):
                os.remove(f)
        except Exception as e:
            pass  # File might be locked, will be overwritten next run


def cleanup_startup_temp_files():
    """Remove any leftover temp files from previous runs"""
    temp_patterns = ['_tmp_audio.wav', '_tmp_*.wav', '_tmp_*.mp4']

    cleaned = 0
    for pattern in temp_patterns:
        if '*' in pattern:
            # Handle wildcards
            import glob
            for temp_file in glob.glob(os.path.join(OUTPUT_DIR, pattern)):
                try:
                    os.remove(temp_file)
                    cleaned += 1
                except:
                    pass  # File might be locked, FFmpeg will overwrite
        else:
            temp_file = os.path.join(OUTPUT_DIR, pattern)
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    cleaned += 1
                except:
                    pass

    if cleaned > 0:
        print(f"[*] Cleaned up {cleaned} leftover temp file(s)")


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    print("\n\n[!] Interrupted! Cleaning up...")
    cleanup_all_temp_files()
    sys.exit(0)


# Register cleanup handlers
atexit.register(cleanup_all_temp_files)
signal.signal(signal.SIGINT, signal_handler)
if hasattr(signal, 'SIGTERM'):
    signal.signal(signal.SIGTERM, signal_handler)


def run_with_progress(cmd, desc=None, duration=None):
    """Execute FFmpeg command with progress tracking"""
    global CURRENT_PROCESS

    if IS_WINDOWS:
        CURRENT_PROCESS = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
        )
    else:
        import shlex
        cmd_str = " ".join(shlex.quote(str(c)) for c in cmd)
        CURRENT_PROCESS = subprocess.Popen(
            cmd_str,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )

    # Create progress bar if we have duration info
    pbar = None
    if duration and desc:
        pbar = tqdm(total=100, desc=desc, unit="%", leave=False,
                    bar_format='{l_bar}{bar}| {n:.0f}% [{elapsed}<{remaining}]')

    stderr_output = []
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')

    # Read stderr line by line
    try:
        while True:
            line = CURRENT_PROCESS.stderr.readline()
            if not line:
                break
            stderr_output.append(line)

            # Parse progress from FFmpeg output
            if pbar and duration:
                match = time_pattern.search(line)
                if match:
                    hours = int(match.group(1))
                    minutes = int(match.group(2))
                    seconds = float(match.group(3))
                    current_time = hours * 3600 + minutes * 60 + seconds
                    progress = min((current_time / duration) * 100, 100)
                    pbar.n = progress
                    pbar.refresh()
    except KeyboardInterrupt:
        if pbar:
            pbar.close()
        raise

    CURRENT_PROCESS.wait()
    returncode = CURRENT_PROCESS.returncode
    CURRENT_PROCESS = None

    if pbar:
        if returncode == 0:
            pbar.n = 100
            pbar.refresh()
        pbar.close()

    if returncode != 0:
        print(f"\n[!] FFmpeg error (exit code {returncode}):")
        print("".join(stderr_output[-20:]))
        return False

    return True


def get_duration(path):
    """Get duration of media file in seconds"""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            capture_output=True,
            text=True,
            timeout=10
        )
        duration = float(result.stdout.strip())
        return duration if duration > 0 else 30.0
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"[!] Could not get duration for {os.path.basename(path)}, using 30s default")
        return 30.0


def get_random_video():
    """Get random video from videos folder"""
    video_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm')

    try:
        if not os.path.exists(VIDEOS_DIR):
            print(f"[!] Videos directory not found: {VIDEOS_DIR}")
            print(f"[!] Please create '{VIDEOS_DIR}' and add video files")
            return None

        videos = [f for f in os.listdir(VIDEOS_DIR)
                  if f.lower().endswith(video_extensions)]

        if not videos:
            print(f"[!] No videos found in {VIDEOS_DIR}")
            return None

        return os.path.join(VIDEOS_DIR, random.choice(videos))
    except Exception as e:
        print(f"[!] Error accessing videos folder: {e}")
        return None


def build_waveform_filter(preset, wave_width, wave_height):
    """Build FFmpeg filter string based on preset style"""
    color = preset["color"]
    mode = preset["mode"]
    scale = preset["scale"]
    split = preset["split_channels"]
    wave_type = preset["type"]

    if wave_type == "circular":
        wave_filter = (
            f"showfreqs=s={wave_width}x{wave_height}:mode=line:colors={color}:"
            f"fscale=log:ascale=sqrt"
        )
        filter_chain = f"[AUDIO_INPUT]{wave_filter}[wave]"
    elif wave_type == "bars":
        win_size = preset.get("win_size", 2048)
        wave_filter = (
            f"showfreqs=s={wave_width}x{wave_height}:mode=bar:colors={color}:"
            f"fscale=log:ascale={scale}:win_size={win_size}"
        )
        filter_chain = f"[AUDIO_INPUT]{wave_filter}[wave]"
    elif wave_type == "vector":
        wave_filter = (
            f"avectorscope=s={wave_width}x{wave_height}:mode={mode}:draw=line:"
            f"scale={scale}"
        )
        filter_chain = f"[AUDIO_INPUT]{wave_filter}[wave]"
    elif wave_type == "spectrum":
        wave_filter = (
            f"showspectrum=s={wave_width}x{wave_height}:mode={mode}:color={color}:"
            f"scale={scale}:slide=scroll"
        )
        filter_chain = f"[AUDIO_INPUT]{wave_filter}[wave]"
    else:
        wave_filter = (
            f"showwaves=s={wave_width}x{wave_height}:mode={mode}:colors={color}:"
            f"scale={scale}:draw=scale"
        )
        if split:
            wave_filter += ":split_channels=1"
        filter_chain = f"[AUDIO_INPUT]{wave_filter}[wave]"

    if preset.get("glow"):
        filter_chain += ";[wave]split[wave1][wave2];[wave2]boxblur=3:1[glow];[wave1][glow]overlay[wave]"

    if preset.get("mirror"):
        filter_chain += ";[wave]split[w1][w2];[w2]vflip[w2flip];[w1][w2flip]vstack[wave]"

    if preset.get("shadow"):
        filter_chain += ";[wave]split[wave1][wave2];[wave2]boxblur=5:1,colorchannelmixer=aa=0.3[shadow];[shadow][wave1]overlay[wave]"

    return filter_chain


def make_visualizer(audio_path, output_path):
    """Generate audio visualizer video from random video and audio"""
    preset = random.choice(WAVEFORM_PRESETS)
    video_path = get_random_video()

    if not video_path:
        print("[!] No video available, skipping")
        return False

    wave_width = 1920
    if preset["type"] == "circular":
        wave_height = 1080
    elif preset["type"] == "bars":
        wave_height = 800
    elif preset["type"] == "vector":
        wave_height = 300
    else:
        wave_height = 300

    width = 1920
    height = 1080
    fps = 30
    duration = get_duration(audio_path)

    tmp_audio = os.path.join(OUTPUT_DIR, "_tmp_audio.wav")
    TEMP_FILES.append(tmp_audio)

    print(f"\n📝 Processing: {os.path.basename(audio_path)} ({duration:.1f}s)")
    print(f"   🎨 Style: {preset['name']} ({preset['type']})")
    print(f"   🎬 Video: {os.path.basename(video_path)}")

    # Step 1: Normalize audio
    if not run_with_progress([
        "ffmpeg", "-y", "-i", audio_path,
        "-ac", "2", "-ar", "44100", "-acodec", "pcm_s16le",
        tmp_audio
    ], "  ├─ Converting audio", duration):
        return False

    # Step 2: Build filter graph with looping video
    filter_parts = []

    # Scale and loop the video to match audio duration
    filter_parts.append(
        f"[0:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1[bg]"
    )

    current_layer = "[bg]"

    # Build waveform filter
    if preset["type"] in ["circular", "bars", "vector"]:
        waveform_height = wave_height
    else:
        waveform_height = wave_height // 2

    waveform_filter = build_waveform_filter(preset, wave_width, waveform_height)
    waveform_filter = waveform_filter.replace("[AUDIO_INPUT]", "[1:a]")
    filter_parts.append(waveform_filter)

    # Position waveform
    if preset["position"] == "center":
        overlay_pos = f"(W-w)/2:(H-h)/2"
    else:
        overlay_pos = "0:H-h"

    filter_parts.append(f"{current_layer}[wave]overlay={overlay_pos},format=yuv420p[v]")

    filter_graph = ";".join(filter_parts)

    # Build FFmpeg command with looping video
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",  # Loop video indefinitely
        "-i", video_path,
        "-i", tmp_audio,
        "-filter_complex", filter_graph,
        "-map", "[v]",
        "-map", "1:a",
        "-t", f"{duration:.2f}",  # Cut to audio duration
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]

    if not run_with_progress(cmd, "  └─ Composing final video", duration):
        return False

    # Clean up temp file immediately after successful completion
    try:
        if os.path.exists(tmp_audio):
            os.remove(tmp_audio)
            TEMP_FILES.remove(tmp_audio)
    except:
        pass

    print(f"  ✅ Complete: {os.path.basename(output_path)}")
    return True


def batch_generate():
    """Process all audio files in input directory"""
    audio_extensions = ('.wav', '.mp3', '.m4a', '.flac', '.ogg', '.aac')

    try:
        files = [f for f in os.listdir(INPUT_DIR)
                 if f.lower().endswith(audio_extensions)]
    except FileNotFoundError:
        print(f"[!] Input directory not found: {INPUT_DIR}")
        print("[!] Please create an 'input' folder and add your files")
        return

    if not files:
        print("[!] No audio files found in input/ directory")
        print(f"[!] Supported formats: {', '.join(audio_extensions)}")
        return

    # Check if videos folder exists
    if not os.path.exists(VIDEOS_DIR):
        print(f"[!] Videos directory not found: {VIDEOS_DIR}")
        print(f"[!] Please create 'input/videos' folder and add video files")
        return

    print(f"[*] Found {len(files)} audio file(s) to process\n")

    success_count = 0
    for idx, audio_file in enumerate(files, 1):
        print(f"{'=' * 60}")
        print(f"File {idx}/{len(files)}")

        name, _ = os.path.splitext(audio_file)
        audio_path = os.path.join(INPUT_DIR, audio_file)
        output_path = os.path.join(OUTPUT_DIR, f"{name}.mp4")

        try:
            if make_visualizer(audio_path, output_path):
                success_count += 1
        except KeyboardInterrupt:
            print("\n[!] Interrupted by user")
            raise

    print(f"\n{'=' * 60}")
    print(f"[*] Successfully processed {success_count}/{len(files)} file(s)")


if __name__ == "__main__":
    print("🎵 Music Visualizer Generator (Video Background)")
    print("=" * 60)

    # Clean up any leftover temp files from previous runs
    cleanup_startup_temp_files()

    try:
        batch_generate()
    except KeyboardInterrupt:
        print("\n[!] Process interrupted")
    finally:
        cleanup_all_temp_files()

    print("=" * 60)
    print("✅ Done — check your output/ folder")