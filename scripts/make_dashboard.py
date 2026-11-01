"""Create a self-contained, interactive dashboard from saved study tables."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from plotly.offline import get_plotlyjs

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
OUT = ROOT / "results" / "dashboard.html"


def build_payload(traces: pd.DataFrame, summary: pd.DataFrame) -> dict:
    rows: dict[str, dict] = {}
    frames = {case: frame for case, frame in traces.groupby("case", sort=False)}
    for record in summary.to_dict("records"):
        case = record["case"]
        rows[case] = {"summary": record, "available": case in frames}
    for case, frame in traces.groupby("case", sort=False):
        rows[case].update({column: frame[column].round(6).tolist() for column in frame.columns if column != "case"})
    return rows


def main() -> None:
    traces = pd.read_csv(TABLES / "event_traces.csv")
    summary = pd.read_csv(TABLES / "event_summary.csv")
    payload = json.dumps(build_payload(traces, summary), separators=(",", ":"))
    plotly_js = get_plotlyjs()
    html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>GFM Microgrid Event Recorder</title>
<style>
:root{{--ink:#eaf2ff;--muted:#9bb0ca;--ground:#07111f;--panel:#0c192a;--panel2:#0f2035;--line:#21354d;--cyan:#38d7c3;--blue:#69aaff;--amber:#f6bd60;--red:#ff6b82;--mono:"SFMono-Regular",Consolas,"Liberation Mono",monospace;--sans:"Avenir Next",Avenir,"Helvetica Neue",Arial,sans-serif}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--ground);color:var(--ink);font-family:var(--sans);min-width:320px}}
main{{position:relative;max-width:1480px;margin:auto;padding:28px 32px 52px}} .topline{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:20px;gap:16px}} .brand{{display:flex;gap:14px;align-items:center}} .mark{{width:31px;height:31px;border:1px solid var(--cyan);display:grid;place-items:center;color:var(--cyan);font:700 14px var(--mono)}} h1{{font-size:18px;margin:0;font-weight:650}} .sub{{font:12px var(--mono);color:var(--muted);margin-top:4px}} .synthetic{{white-space:nowrap;border:1px solid #76592b;color:var(--amber);padding:7px 9px;font:12px var(--mono)}}
.hero{{display:grid;grid-template-columns:1.28fr .72fr;border-bottom:1px solid var(--line)}} .lead{{padding:38px 38px 31px 0}} .kicker{{color:var(--cyan);font:12px var(--mono)}} h2{{font-size:clamp(30px,4vw,54px);line-height:1.02;max-width:770px;letter-spacing:-.045em;margin:12px 0 17px}} .lead p{{color:var(--muted);line-height:1.55;max-width:700px;margin:0;font-size:15px}} .control{{border-left:1px solid var(--line);padding:38px 0 30px 31px}} .label{{font:12px var(--mono);color:var(--muted);margin-bottom:12px}} .case-selector{{display:grid;gap:6px}} button{{cursor:pointer;text-align:left;border:1px solid var(--line);color:#a9bbd0;background:transparent;padding:11px 12px;font:12px var(--mono);transition:background .18s,border-color .18s,color .18s}} button:hover,button.active{{background:#142b46;border-color:var(--blue);color:#fff}} button:disabled{{cursor:not-allowed;border-color:#593240;color:#b17280;background:transparent}} .method{{border-top:1px solid var(--line);margin-top:25px;padding-top:17px;color:var(--muted);font-size:12px;line-height:1.5}} .method strong{{color:var(--ink);font-weight:600}}
.events{{padding:23px 0 25px;border-bottom:1px solid var(--line)}} .event-head{{display:flex;justify-content:space-between;align-items:baseline;gap:15px}} .event-head h3{{font:600 12px var(--mono);margin:0}} .cursor-readout{{font:12px var(--mono);color:var(--cyan)}} .rail{{display:grid;grid-template-columns:4fr 6fr 12fr 13fr 13fr 12fr;min-height:75px;margin-top:14px;border:1px solid var(--line)}} .stage{{position:relative;padding:11px;border-right:1px solid var(--line);font:12px var(--mono);color:var(--muted)}} .stage:last-child{{border:0}} .stage b{{display:block;color:var(--ink);font-weight:600;margin-bottom:6px}} .stage.danger b{{color:var(--red)}} .stage.warn b{{color:var(--amber)}} .event-cursor{{position:absolute;z-index:3;width:2px;top:0;height:100%;background:var(--cyan);left:0;pointer-events:none}}
.readout{{display:grid;grid-template-columns:1.1fr 1.1fr 1.1fr 1.5fr;border-bottom:1px solid var(--line)}} .reading{{padding:19px 18px 17px 0;border-right:1px solid var(--line);margin-right:18px}} .reading:last-child{{border:0}} .reading .name{{font:12px var(--mono);color:var(--muted)}} .reading .value{{font:700 26px var(--mono);letter-spacing:-.05em;margin-top:5px}} .reading .unit{{font:12px var(--mono);color:var(--muted);margin-left:4px}} .reading .note{{font-size:12px;color:var(--muted);margin-top:6px}}
.plots{{display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--line);border:1px solid var(--line);margin-top:27px}} .plot{{background:var(--panel);min-height:295px;padding:13px 10px 5px}} .plot-title{{padding:0 8px;color:var(--muted);font:12px var(--mono)}} .chart{{height:253px}} .foot{{color:var(--muted);font-size:12px;line-height:1.6;padding-top:17px}} .foot a{{color:var(--blue)}}
@media(max-width:800px){{main{{padding:18px 17px 38px}}.hero{{grid-template-columns:1fr}}.lead{{padding:30px 0 25px}}.control{{border-left:0;border-top:1px solid var(--line);padding:25px 0}}.rail{{grid-template-columns:1fr 1fr 1fr;min-height:150px}}.stage:nth-child(3){{border-right:0}}.stage:nth-child(-n+3){{border-bottom:1px solid var(--line)}}.readout{{grid-template-columns:1fr 1fr}}.reading:nth-child(2){{border-right:0}}.plots{{grid-template-columns:1fr}}.topline{{align-items:flex-start}}.synthetic{{font-size:12px}}}}
</style></head><body><main>
<header class="topline"><div class="brand"><div class="mark">GF</div><div><h1>MICROGRID EVENT RECORDER</h1><div class="sub">BESS-01 / 500 kVA notional base / 50 Hz</div></div></div><div class="synthetic">SYNTHETIC BENCHMARK · NOT A DESIGN</div></header>
<section class="hero"><div class="lead"><div class="kicker">GRID-FORMING INVERTER CONTROL STUDY</div><h2>Can the inverter hold an island when the grid disappears?</h2><p>A transparent reduced-order event replay of black start, intentional islanding, a load step, and grid reconnection. Compare the controller modes without mistaking a portfolio simulation for field validation.</p></div><aside class="control"><div class="label">SELECT CONTROL MODE</div><div class="case-selector"><button class="active" data-case="grid_following">01 / GRID-FOLLOWING (GFL)</button><button data-case="gfm_droop">02 / GRID-FORMING — DROOP</button><button data-case="gfm_vsm">03 / GRID-FORMING — VSM</button></div><div class="method"><strong>Model boundary.</strong> Per-unit synthetic traces, fixed load/PV profile, simplified current cap. No feeder impedance, protection coordination, PLL dynamics, or certification claim.</div></aside></section>
<section class="events"><div class="event-head"><h3>EVENT SEQUENCE / 0–60 s</h3><span class="cursor-readout" id="cursor">cursor 0.0 s · black start</span></div><div class="rail" id="rail"><i class="event-cursor" id="eventCursor"></i><div class="stage"><b>00–04 s</b>BLACK START</div><div class="stage"><b>04–10 s</b>GRID PARALLEL</div><div class="stage danger"><b>10–22 s</b>ISLANDING</div><div class="stage warn"><b>22–35 s</b>LOAD STEP</div><div class="stage danger"><b>35–48 s</b>ISLANDING</div><div class="stage"><b>48–60 s</b>RECONNECT</div></div></section>
<section class="readout"><div class="reading"><div class="name">FREQUENCY NADIR</div><div class="value" id="freq">—</div></div><div class="reading"><div class="name">VOLTAGE NADIR</div><div class="value" id="volt">—</div></div><div class="reading"><div class="name">MIN. LOAD SERVED</div><div class="value" id="served">—</div></div><div class="reading"><div class="name">CURRENT-LIMIT EXPOSURE</div><div class="value" id="limit">—</div><div class="note">During the 10–48 s islanding window</div></div></section>
<section class="plots"><article class="plot"><div class="plot-title">FREQUENCY / Hz</div><div class="chart" id="frequency"></div></article><article class="plot"><div class="plot-title">VOLTAGE / pu</div><div class="chart" id="voltage"></div></article><article class="plot"><div class="plot-title">BATTERY POWER / pu</div><div class="chart" id="power"></div></article><article class="plot"><div class="plot-title">LOAD SERVED / %</div><div class="chart" id="servedchart"></div></article></section>
<footer class="foot">All cases and parameters are synthetic and reproducible from saved CSV tables. Educational comparison only. Conceptual basis: <a href="https://www.energy.gov/cmei/systems/solar-integration-inverters-and-grid-services-basics">U.S. DOE inverter overview</a>.</footer>
</main><script>{plotly_js}</script><script>
const data={payload}; const colors={{grid_following:'#ff6b82',gfm_droop:'#f6bd60',gfm_vsm:'#38d7c3'}}; let selected=Object.keys(data).find(c=>data[c].available);
const phase=t=>t<4?'black start':t<10?'grid parallel':t<22?'islanded':t<35?'load step':t<48?'islanded':'reconnected';
const layout=(label,range)=>({{paper_bgcolor:'#0c192a',plot_bgcolor:'#0c192a',margin:{{l:44,r:12,t:8,b:34}},font:{{family:'SFMono-Regular,Consolas,monospace',color:'#8ba0bb',size:10}},xaxis:{{title:'TIME / s',color:'#8ba0bb',gridcolor:'#20354d',zeroline:false,fixedrange:true}},yaxis:{{title:label,color:'#8ba0bb',gridcolor:'#20354d',zeroline:false,fixedrange:true,range}},showlegend:false,shapes:[{{type:'rect',x0:10,x1:48,y0:0,y1:1,yref:'paper',fillcolor:'rgba(255,107,130,.055)',line:{{width:0}}}},{{type:'rect',x0:22,x1:35,y0:0,y1:1,yref:'paper',fillcolor:'rgba(246,189,96,.07)',line:{{width:0}}}}]}});
function trace(x,y){{return [{{x,y,type:'scatter',mode:'lines',line:{{color:colors[selected],width:2}},hovertemplate:'%{{x:.2f}} s · %{{y:.3f}}<extra></extra>'}}]}}
function draw(){{const d=data[selected]; if(!d || !d.available) return; const s=d.summary, x=d.time_s; document.querySelectorAll('[data-case]').forEach(b=>{{b.disabled=!data[b.dataset.case]?.available;b.classList.toggle('active',b.dataset.case===selected)}}); document.querySelector('#freq').innerHTML=s.frequency_nadir_hz+'<span class="unit">Hz</span>';document.querySelector('#volt').innerHTML=s.voltage_nadir_pu+'<span class="unit">pu</span>';document.querySelector('#served').innerHTML=(s.minimum_served_fraction*100).toFixed(0)+'<span class="unit">%</span>';document.querySelector('#limit').innerHTML=s.current_limit_seconds+'<span class="unit">s</span>'; const frequencyRange=Math.min(...d.frequency_hz)<10?[-1,52]:[48.8,50.4]; Plotly.react('frequency',trace(x,d.frequency_hz),layout('Hz',frequencyRange),{{responsive:true,displayModeBar:false}});Plotly.react('voltage',trace(x,d.voltage_pu),layout('pu',[0,1.12]),{{responsive:true,displayModeBar:false}});Plotly.react('power',trace(x,d.battery_power_pu),layout('pu',[-.5,.5]),{{responsive:true,displayModeBar:false}});Plotly.react('servedchart',trace(x,d.served_fraction.map(v=>v*100)),layout('%',[-2,105]),{{responsive:true,displayModeBar:false}})}}
function moveCursor(t){{document.querySelector('#eventCursor').style.left=(t/60*100)+'%';document.querySelector('#cursor').textContent='cursor '+t.toFixed(1)+' s · '+phase(t)}}
document.querySelectorAll('[data-case]').forEach(b=>b.onclick=()=>{{selected=b.dataset.case;draw()}});document.querySelector('#rail').addEventListener('mousemove',e=>{{const r=e.currentTarget.getBoundingClientRect();moveCursor(Math.max(0,Math.min(60,(e.clientX-r.left)/r.width*60)))}});document.querySelector('#rail').addEventListener('mouseleave',()=>moveCursor(0));draw();moveCursor(0);
</script></body></html>'''
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
