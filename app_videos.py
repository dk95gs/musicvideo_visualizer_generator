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
USED_VIDEOS = []

# Text style presets for ImageMagick
TEXT_STYLE_PRESETS = [
    {
        "name": "Neon Cyan Glow",
        "fill": "cyan",
        "stroke": "#0066CC",
        "strokewidth": 4,
        "shadow_color": "cyan",
        "shadow_opacity": 80,
        "shadow_sigma": 5,
        "brightness": "light"
    },
    {
        "name": "Hot Pink Neon",
        "fill": "#FF1493",
        "stroke": "#8B0045",
        "strokewidth": 5,
        "shadow_color": "#FF1493",
        "shadow_opacity": 85,
        "shadow_sigma": 6,
        "brightness": "light"
    },
    {
        "name": "Electric Green",
        "fill": "#39FF14",
        "stroke": "#0D5302",
        "strokewidth": 4,
        "shadow_color": "#39FF14",
        "shadow_opacity": 80,
        "shadow_sigma": 5,
        "brightness": "light"
    },
    {
        "name": "Golden Shine",
        "fill": "#FFD700",
        "stroke": "#8B6914",
        "strokewidth": 6,
        "shadow_color": "#FFD700",
        "shadow_opacity": 75,
        "shadow_sigma": 4,
        "brightness": "light"
    },
    {
        "name": "Purple Haze",
        "fill": "#9D00FF",
        "stroke": "#4B0082",
        "strokewidth": 5,
        "shadow_color": "#9D00FF",
        "shadow_opacity": 80,
        "shadow_sigma": 6,
        "brightness": "medium"
    },
    {
        "name": "Fiery Orange",
        "fill": "#FF4500",
        "stroke": "#8B2500",
        "strokewidth": 4,
        "shadow_color": "#FF4500",
        "shadow_opacity": 85,
        "shadow_sigma": 5,
        "brightness": "light"
    },
    {
        "name": "Ice Blue",
        "fill": "#00CED1",
        "stroke": "#003D40",
        "strokewidth": 5,
        "shadow_color": "#00CED1",
        "shadow_opacity": 80,
        "shadow_sigma": 5,
        "brightness": "light"
    },
    {
        "name": "Magenta Burst",
        "fill": "#FF00FF",
        "stroke": "#8B008B",
        "strokewidth": 6,
        "shadow_color": "#FF00FF",
        "shadow_opacity": 85,
        "shadow_sigma": 6,
        "brightness": "light"
    },
    {
        "name": "Lime Punch",
        "fill": "#7FFF00",
        "stroke": "#2E5902",
        "strokewidth": 4,
        "shadow_color": "#7FFF00",
        "shadow_opacity": 80,
        "shadow_sigma": 5,
        "brightness": "light"
    },
    {
        "name": "Ruby Red",
        "fill": "#E0115F",
        "stroke": "#8B0A3B",
        "strokewidth": 5,
        "shadow_color": "#E0115F",
        "shadow_opacity": 85,
        "shadow_sigma": 6,
        "brightness": "medium"
    },
    {
        "name": "Pure White Glow",
        "fill": "white",
        "stroke": "#CCCCCC",
        "strokewidth": 5,
        "shadow_color": "white",
        "shadow_opacity": 90,
        "shadow_sigma": 6,
        "brightness": "light"
    },
    {
        "name": "Deep Black Shadow",
        "fill": "black",
        "stroke": "#333333",
        "strokewidth": 6,
        "shadow_color": "white",
        "shadow_opacity": 95,
        "shadow_sigma": 8,
        "brightness": "dark"
    },
    {
        "name": "Silver Chrome",
        "fill": "#C0C0C0",
        "stroke": "#404040",
        "strokewidth": 5,
        "shadow_color": "#E0E0E0",
        "shadow_opacity": 85,
        "shadow_sigma": 5,
        "brightness": "light"
    }
]

# Modern waveform style presets - 15 Bar Styles
WAVEFORM_PRESETS = [
    {
        "name": "Electric Blue Bars",
        "color": "0x00FFFF",
        "mode": "bar",
        "scale": "sqrt",
        "split_channels": False,
        "thickness": 8,
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
        "win_size": 2048,
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
            pass


def cleanup_startup_temp_files():
    """Remove any leftover temp files from previous runs"""
    temp_patterns = ['_tmp_audio.wav', '_tmp_*.wav', '_tmp_*.mp4', '_tmp_*.png']

    cleaned = 0
    for pattern in temp_patterns:
        if '*' in pattern:
            import glob
            for temp_file in glob.glob(os.path.join(OUTPUT_DIR, pattern)):
                try:
                    os.remove(temp_file)
                    cleaned += 1
                except:
                    pass
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

    pbar = None
    if duration and desc:
        pbar = tqdm(total=100, desc=desc, unit="%", leave=False,
                    bar_format='{l_bar}{bar}| {n:.0f}% [{elapsed}<{remaining}]')

    stderr_output = []
    time_pattern = re.compile(r'time=(\d+):(\d+):(\d+\.\d+)')

    try:
        while True:
            line = CURRENT_PROCESS.stderr.readline()
            if not line:
                break
            stderr_output.append(line)

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
        print(f"\n[!] Command error (exit code {returncode}):")
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


def get_video_brightness(video_path):
    """Analyze video to determine if it's predominantly dark or light"""
    try:
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", "select=eq(n\\,50),signalstats",
            "-f", "null", "-"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )

        output = result.stderr

        import re
        match = re.search(r'lavfi\.signalstats\.YAVG=(\d+\.?\d*)', output)

        if match:
            avg_luminance = float(match.group(1))
            if avg_luminance < 100:
                return "dark"
            elif avg_luminance > 155:
                return "light"
            else:
                return "medium"

        return "medium"

    except Exception as e:
        return "medium"


def pick_contrasting_text_style(video_path):
    """Pick a text style that contrasts with the video's brightness"""
    brightness = get_video_brightness(video_path)

    if brightness == "dark":
        suitable_styles = [s for s in TEXT_STYLE_PRESETS if s["brightness"] == "light"]
    elif brightness == "light":
        suitable_styles = [s for s in TEXT_STYLE_PRESETS if s["brightness"] in ["dark", "medium"]]
        if not suitable_styles:
            suitable_styles = TEXT_STYLE_PRESETS
    else:
        suitable_styles = TEXT_STYLE_PRESETS

    return random.choice(suitable_styles)


def get_random_video():
    """Get random video from videos folder, avoiding repeats"""
    global USED_VIDEOS
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

        available = [v for v in videos if v not in USED_VIDEOS]

        if not available:
            USED_VIDEOS.clear()
            available = videos

        chosen = random.choice(available)
        USED_VIDEOS.append(chosen)

        return os.path.join(VIDEOS_DIR, chosen)
    except Exception as e:
        print(f"[!] Error accessing videos folder: {e}")
        return None


def find_imagemagick():
    """Find ImageMagick executable on the system"""
    import shutil

    commands = ["magick", "convert", "magick.exe", "convert.exe"]

    for cmd in commands:
        if shutil.which(cmd):
            return cmd

    if IS_WINDOWS:
        import glob
        possible_paths = [
            r"C:\Program Files\ImageMagick-*\magick.exe",
            r"C:\Program Files (x86)\ImageMagick-*\magick.exe",
            r"C:\ImageMagick\magick.exe",
        ]

        for pattern in possible_paths:
            matches = glob.glob(pattern)
            if matches:
                return matches[0]

    return None


def create_text_overlay(text, style_preset, output_path, width=1920, height=1080):
    """Create stylized text overlay using ImageMagick"""
    try:
        magick_cmd = find_imagemagick()

        if not magick_cmd:
            print("[!] ImageMagick not found. Please install it:")
            print("    Windows: Download from https://imagemagick.org/")
            print("    Make sure to check 'Add to PATH' during installation")
            print("    Then restart your terminal/IDE")
            return False

        cmd = [
            magick_cmd,
            "-size", f"{width}x{height}",
            "xc:none",
            "-font", "Arial-Bold",
            "-pointsize", "120",
            "-fill", style_preset["fill"],
            "-stroke", style_preset["stroke"],
            "-strokewidth", str(style_preset["strokewidth"]),
            "-gravity", "center",
            "-annotate", "+0+0", text,
            "(",
            "+clone",
            "-background", style_preset["shadow_color"],
            "-shadow", f"{style_preset['shadow_opacity']}x{style_preset['shadow_sigma']}+0+0",
            ")",
            "+swap",
            "-background", "none",
            "-layers", "merge",
            "+repage",
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"[!] ImageMagick error: {result.stderr}")
            return False

        return True

    except subprocess.TimeoutExpired:
        print("[!] ImageMagick timed out")
        return False
    except Exception as e:
        print(f"[!] Error creating text overlay: {e}")
        return False


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
    """Generate audio visualizer video from random video and audio with stylized text"""
    preset = random.choice(WAVEFORM_PRESETS)
    video_path = get_random_video()

    if not video_path:
        print("[!] No video available, skipping")
        return False

    text_style = pick_contrasting_text_style(video_path)

    song_name = os.path.splitext(os.path.basename(audio_path))[0]

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
    tmp_text_overlay = os.path.join(OUTPUT_DIR, f"_tmp_text_{os.getpid()}.png")
    TEMP_FILES.extend([tmp_audio, tmp_text_overlay])

    print(f"\n📝 Processing: {song_name} ({duration:.1f}s)")
    print(f"   🎨 Waveform: {preset['name']} ({preset['type']})")
    print(f"   ✨ Text Style: {text_style['name']}")
    print(f"   🎬 Video: {os.path.basename(video_path)}")

    print("  ├─ Creating text overlay")
    if not create_text_overlay(song_name, text_style, tmp_text_overlay, width, height):
        print("[!] Failed to create text overlay, continuing without text...")
        tmp_text_overlay = None

    if not run_with_progress([
        "ffmpeg", "-y", "-i", audio_path,
        "-ac", "2", "-ar", "44100", "-acodec", "pcm_s16le",
        tmp_audio
    ], "  ├─ Converting audio", duration):
        return False

    filter_parts = []
    input_index = 0

    filter_parts.append(
        f"[{input_index}:v]scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},setsar=1[bg]"
    )
    input_index += 1

    current_layer = "[bg]"

    if preset["type"] in ["circular", "bars", "vector"]:
        waveform_height = wave_height
    else:
        waveform_height = wave_height // 2

    waveform_filter = build_waveform_filter(preset, wave_width, waveform_height)
    waveform_filter = waveform_filter.replace("[AUDIO_INPUT]", f"[{input_index}:a]")
    filter_parts.append(waveform_filter)

    if preset["position"] == "center":
        overlay_pos = f"(W-w)/2:(H-h)/2"
    else:
        overlay_pos = "0:H-h"

    filter_parts.append(f"{current_layer}[wave]overlay={overlay_pos}[v_with_wave]")
    current_layer = "[v_with_wave]"

    if tmp_text_overlay and os.path.exists(tmp_text_overlay):
        input_index += 1
        filter_parts.append(
            f"[{input_index}:v]format=rgba,colorchannelmixer=aa=0.9[text]"
        )
        filter_parts.append(f"{current_layer}[text]overlay=(W-w)/2:(H-h)/2,format=yuv420p[v]")
    else:
        filter_parts.append(f"{current_layer}format=yuv420p[v]")

    filter_graph = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1",
        "-i", video_path,
        "-i", tmp_audio,
    ]

    if tmp_text_overlay and os.path.exists(tmp_text_overlay):
        cmd.extend(["-loop", "1", "-i", tmp_text_overlay])

    cmd.extend([
        "-filter_complex", filter_graph,
        "-map", "[v]",
        "-map", "1:a",
        "-t", f"{duration:.2f}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-r", str(fps),
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ])

    if not run_with_progress(cmd, "  └─ Composing final video", duration):
        return False

    for tmp_file in [tmp_audio, tmp_text_overlay]:
        try:
            if tmp_file and os.path.exists(tmp_file):
                os.remove(tmp_file)
                if tmp_file in TEMP_FILES:
                    TEMP_FILES.remove(tmp_file)
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
    print("🎵 Music Visualizer Generator with Stylized Text")
    print("=" * 60)

    cleanup_startup_temp_files()

    try:
        batch_generate()
    except KeyboardInterrupt:
        print("\n[!] Process interrupted")
    finally:
        cleanup_all_temp_files()

    print("=" * 60)
    print("✅ Done — check your output/ folder")