"""Build the narrated evidence walkthrough on macOS; no cloud calls or secrets."""
import argparse
import json
from pathlib import Path
import re
import subprocess

from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storyboard", type=Path, default=Path("docs/demo/storyboard.json"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.storyboard.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    font_dir = Path("/System/Library/Fonts/Supplemental")
    def font(size, bold=False):
        return ImageFont.truetype(str(font_dir / ("Arial Bold.ttf" if bold else "Arial.ttf")), size)
    bg, panel, white, muted, accent = "#0b1726", "#13273c", "#eef4f7", "#a4b8c9", "#58e0bd"
    clips, transcript, captions = [], [], []
    total = 0
    def wrap(draw, words, f, width):
        lines, line = [], ""
        for word in words.split():
            candidate = (line + " " + word).strip()
            if draw.textlength(candidate, font=f) > width and line:
                lines.append(line)
                line = word
            else:
                line = candidate
        return lines + ([line] if line else [])
    def stamp(seconds):
        ms = round(seconds * 1000)
        return f"{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02}.{ms%1000:03}"
    for index, slide in enumerate(data["slides"]):
        number = index + 1
        image = Image.new("RGB", (1280,720), bg)
        d = ImageDraw.Draw(image)
        d.text((56,35), "SKYFLOW", font=font(23,True), fill=accent)
        d.text((880,40), "VERIFIED PORTFOLIO / NOV 2026", font=font(16), fill=muted)
        d.line((56,83,1224,83), fill="#294055", width=2)
        d.text((56,109), slide["eyebrow"].upper(), font=font(17,True), fill=accent)
        d.text((56,147), slide["title"], font=font(46,True), fill=white)
        d.rounded_rectangle((56,229,1224,564), radius=18, fill=panel)
        y=258
        for heading, body in slide["rows"]:
            d.text((82,y), heading, font=font(28,True), fill=accent)
            lines = wrap(d,body,font(23),790)
            for line_number,line in enumerate(lines):
                d.text((380,y+line_number*30),line,font=font(23),fill=white)
            y += max(76,len(lines)*30+15)
        if y > 577:
            raise ValueError(f"Slide {number} overflows its evidence panel")
        for line_number,line in enumerate(wrap(d, slide["note"],font(18),1160)):
            d.text((58,589+line_number*24),line,font=font(18),fill=muted)
        d.text((56,671),"Captured results • Synthetic airline data • Computer-generated narration",font=font(15),fill=muted)
        d.text((1140,667),f"{number:02} / {len(data['slides']):02}",font=font(19,True),fill=accent)
        d.rectangle((0,712,round(1280*number/len(data["slides"])),719),fill=accent)
        png=args.output/f"chapter-{number:02}.png"
        image.save(png)
        narration=args.output/f"chapter-{number:02}.txt"
        narration.write_text(slide["narration"])
        audio=args.output/f"chapter-{number:02}.aiff"
        subprocess.run(["say","-v","Samantha","-r","150","-f",str(narration),"-o",str(audio)],check=True)
        info=subprocess.run([ffmpeg,"-i",str(audio)],capture_output=True,text=True)
        match=re.search(r"Duration: (\d+):(\d+):([\d.]+)",info.stderr)
        if not match:
            raise RuntimeError("Could not measure generated narration")
        duration=int(match[1])*3600+int(match[2])*60+float(match[3])+1
        clip=args.output/f"chapter-{number:02}.mp4"
        subprocess.run([ffmpeg,"-y","-loglevel","error","-loop","1","-framerate","10","-i",str(png),
            "-i",str(audio),"-af","apad=pad_dur=1","-t",str(duration),"-c:v","libx264","-preset","fast",
            "-tune","stillimage","-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",str(clip)],check=True)
        clips.append(clip)
        transcript.append(f"## {stamp(total)} — {slide['title']}\n\n{slide['narration']}\n")
        captions.append(f"{stamp(total)} --> {stamp(total+duration)}\n{slide['title']}\n")
        total+=duration
        print(f"Rendered chapter {number}: {duration:.1f}s",flush=True)
    concat=args.output/"clips.txt"
    concat.write_text("".join("file '"+str(p.resolve()).replace("'", "'\\''")+"'\n" for p in clips))
    video=args.output/"SkyFlow-demo.mp4"
    subprocess.run([ffmpeg,"-y","-loglevel","error","-f","concat","-safe","0","-i",str(concat),
                    "-c","copy","-movflags","+faststart",str(video)],check=True)
    (args.output/"SkyFlow-demo-transcript.md").write_text("# SkyFlow narrated evidence demo\n\n"+"\n".join(transcript))
    (args.output/"SkyFlow-demo-chapters.vtt").write_text("WEBVTT\n\n"+"\n".join(captions))
    (args.output/"video-metadata.json").write_text(json.dumps({"duration_seconds":round(total,2),"width":1280,"height":720,
        "chapters":len(clips),"narration":"macOS Samantha computer-generated voice","format":"narrated evidence walkthrough, not a screen recording"},indent=2))
    print(f"Finished {video} ({total:.1f} seconds)")


if __name__ == "__main__":
    main()
