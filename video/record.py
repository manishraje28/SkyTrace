"""Records the narrated SkyTrace demo video -> video/SkyTrace_Demo.mp4
Needs: pip install playwright edge-tts ; python -m playwright install chromium ; ffmpeg on PATH."""
import asyncio, json, os, subprocess, sys, time, shutil
import edge_tts
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = os.path.join(ROOT, "video"); B = os.path.join(V, "_build")
VOICE, PORT = "en-IN-NeerjaNeural", 8799
SCENES = "file:///" + os.path.join(V, "scenes.html").replace("\\", "/")
DASH = f"http://localhost:{PORT}/"

SEG = [
 ("title", "Hi! This is SkyTrace, our Big Data and Social Media Analytics micro project. It is about flight trajectory analysis, and it is linked to the UN Sustainable Development Goal 9: Industry, Innovation and Infrastructure."),
 ("what", "So, what is this project? Every aeroplane sends out its position every second, like a GPS ping. If we join these points, we get the path of the flight, called a trajectory. We study where and when the sky is crowded. Think of it as Google Maps traffic, but for the sky."),
 ("why", "Why do we need this? Airports like Delhi and Mumbai get packed in the morning and evening rush. When the runway is full, planes have to circle in the air and wait. Planes also fly bent routes instead of straight lines. Fifteen minutes of circling can burn five to six hundred kilograms of extra fuel for just one plane. Our data shows where new runways and better routes are needed, which is exactly what SDG 9 is about."),
 ("arch", "Here is how it works. We take real flight data from the OpenSky Network and store it in Hadoop HDFS. MapReduce and Spark process it to find busy areas and rebuild each flight's path. MongoDB stores the flight paths, so we can search them by location. Then a graph of airports finds regional groups and hub airports. Finally, everything is shown on a web dashboard."),
 ("hadoop", "All the Hadoop work runs in Google Colab. We upload the data into HDFS with the put command, and run two MapReduce jobs. The first job divides India's map into small boxes and counts the planes in each box every hour. The second job joins each plane's points and compares the distance it really flew with the straight line distance. In this real output, Pune to Mumbai flights flew almost three times the straight distance, because they had to circle near Mumbai."),
 ("d_kpi", "Now, the live demo. This is the SkyTrace dashboard. At the top are the key numbers: about sixty seven thousand position records, nine hundred flights, four point one percent extra distance, and around one hundred and thirty six tonnes of carbon dioxide that could be saved every day."),
 ("d_map", "This map shows every flight over India. Green means low, yellow means medium, and blue means high altitude. When I switch on the heatmap, we can clearly see the crowded areas around Delhi and Mumbai. The red boxes are the busiest hotspots, found by our MapReduce job."),
 ("d_hour", "This slider filters flights by the hour. At eight in the morning, the sky is busy. At seven in the evening, it is busy again. Now let me show only the planes that circled before landing, and zoom into Mumbai. You can see the circular holding patterns near the airport."),
 ("d_time", "The temporal analysis tab shows traffic by hour. There are two clear peaks: six to ten in the morning, and five to nine in the evening. On the right, we can see that all the holding happens at Delhi and Mumbai."),
 ("d_route", "The route efficiency tab shows which routes waste the most distance, and how much carbon dioxide that causes. Below is the list of flights with the most extra distance, straight from our MapReduce output."),
 ("d_net", "This is the network tab. Every airport is a dot, and every route is a line. The Louvain algorithm found four regional groups: north, west, south and east. Bigger dots are more important hubs according to PageRank. Delhi and Mumbai come out on top, just like influencers in a social network."),
 ("d_arch", "The architecture tab sums up the full pipeline, and which syllabus experiment each part comes from."),
 ("uses", "So, who can use this? The Airports Authority of India can plan direct routes. Airports can see when a new runway is needed, like the new Navi Mumbai and Noida airports. Airlines can choose better times to save fuel. The government can track pollution. And passengers get fewer delays."),
 ("end", "To conclude, SkyTrace turns raw flight data into useful decisions for better infrastructure. In future, we can add live data with Kafka, delay prediction with machine learning, and weather data. Thank you for watching!"),
]
CAP = {"d_kpi": "Live demo · Key numbers", "d_map": "Airspace map · altitude colours, heatmap, hotspots",
       "d_hour": "Spatio-temporal filter · flights by hour · holding patterns", "d_time": "Temporal analysis · rush hours",
       "d_route": "Route efficiency · extra distance & CO₂", "d_net": "Louvain communities · PageRank hubs",
       "d_arch": "Architecture & syllabus mapping"}


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", f]).decode())


async def tts():
    out = []
    for i, (sid, txt) in enumerate(SEG):
        f = os.path.join(B, f"{i:02d}_{sid}.mp3")
        if not os.path.exists(f):
            await edge_tts.Communicate(txt, VOICE, rate="+8%").save(f)
        out.append((sid, f, dur(f)))
    return out


async def act(page, sid, d):
    """Run the on-screen actions for one segment, spread over its duration d (seconds)."""
    ev = page.evaluate
    w = lambda s: page.wait_for_timeout(int(s * 1000))
    if sid == "d_kpi":
        await w(d * .5); await page.mouse.move(400, 260); await w(1)
    elif sid == "d_map":
        await ev("window.scrollTo({top: document.querySelector('#t-map').offsetTop - 10, behavior: 'smooth'})")
        await w(d * .35); await page.click("#lyHeat"); await w(d * .3); await page.click("#lyTraj")
        await w(d * .2); await page.click("#lyTraj"); await page.click("#lyHeat")
    elif sid == "d_hour":
        for h in (8, 19):
            await ev(f"(()=>{{const s=document.querySelector('#hour');s.value={h};s.dispatchEvent(new Event('input'))}})()")
            await w(d * .22)
        await ev("(()=>{const s=document.querySelector('#hour');s.value=-1;s.dispatchEvent(new Event('input'))})()")
        await page.click("#lyHold"); await w(1.2)
        await ev("void map.flyTo([19.3,72.9],8,{duration:2})"); await w(d * .3)
    elif sid in ("d_time", "d_route", "d_net", "d_arch"):
        tab = {"d_time": "t-time", "d_route": "t-route", "d_net": "t-net", "d_arch": "t-arch"}[sid]
        if sid == "d_time":  # reset map state quietly
            await page.click("#lyHold"); await ev("void map.setView([22,81],5)")
        await ev("window.scrollTo({top: 0, behavior: 'smooth'})")
        await page.click(f"[data-t={tab}]"); await w(d * .45)
        await page.mouse.wheel(0, 500 if sid != "d_net" else 250); await w(d * .3)
        await page.mouse.wheel(0, -900)


async def main():
    os.makedirs(B, exist_ok=True)
    segs = await tts()
    term = "\n".join(l for l in open(os.path.join(V, "terminal.txt")).read().splitlines()
                     if not l.startswith(("$ hdfs", "-rw")))
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--directory", os.path.join(ROOT, "web")],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    vdir = os.path.join(B, "raw"); shutil.rmtree(vdir, ignore_errors=True)
    starts = []
    try:
        async with async_playwright() as p:
            br = await p.chromium.launch()
            ctx = await br.new_context(viewport={"width": 1600, "height": 900}, device_scale_factor=1,
                                       record_video_dir=vdir, record_video_size={"width": 1280, "height": 720})
            page = await ctx.new_page(); t0 = time.monotonic()
            await page.goto(SCENES); await page.wait_for_timeout(1500)
            lead = time.monotonic() - t0
            cur = "scenes"
            for sid, f, d in segs:
                dash = sid.startswith("d_")
                if dash and cur != "dash":
                    await page.goto(DASH); await page.wait_for_load_state("networkidle"); await page.wait_for_timeout(800)
                    await page.add_style_tag(content="#cap{position:fixed;left:50%;bottom:22px;transform:translateX(-50%);"
                        "background:#000c;color:#fff;padding:10px 22px;border-radius:30px;font:600 18px 'Space Grotesk';"
                        "border:1px solid #4cc9f0;z-index:9999}")
                    await page.evaluate("document.body.insertAdjacentHTML('beforeend','<div id=cap></div>')")
                    cur = "dash"
                elif not dash and cur != "scenes":
                    await page.goto(SCENES); await page.wait_for_timeout(600); cur = "scenes"
                ts = time.monotonic() - t0; starts.append(ts)
                if dash:
                    await page.evaluate(f"document.getElementById('cap').textContent={json.dumps(CAP[sid])}")
                    await act(page, sid, d)
                else:
                    n = await page.evaluate(f"document.querySelectorAll('#{sid} li,#{sid} .box').length")
                    await page.evaluate(f"window.TERM={json.dumps(term)};window.STAGGER={int(d * 1000 / (n + 1)) if n else 1000};show('{sid}')")
                left = ts + d + 0.5 - (time.monotonic() - t0)
                if left > 0: await page.wait_for_timeout(int(left * 1000))
            await page.wait_for_timeout(1500)
            await ctx.close(); await br.close()
    finally:
        srv.terminate()
    raw = os.path.join(vdir, os.listdir(vdir)[0])
    trim = max(lead - 0.3, 0)
    inputs, filt = ["-ss", f"{trim:.2f}", "-i", raw], []
    for i, ((sid, f, d), ts) in enumerate(zip(segs, starts)):
        inputs += ["-i", f]; ms = int((ts - trim) * 1000)
        filt.append(f"[{i + 1}:a]adelay={ms}|{ms}[a{i}]")
    filt.append("".join(f"[a{i}]" for i in range(len(segs))) + f"amix=inputs={len(segs)}:normalize=0[aout]")
    out = os.path.join(V, "SkyTrace_Demo.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "0:v", "-map", "[aout]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", out], check=True)
    print("video:", out, f"{dur(out):.1f}s")


if __name__ == "__main__":
    asyncio.run(main())
