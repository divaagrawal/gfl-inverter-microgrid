"""Run every declared synthetic operating case and save reproducible tables."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import pandas as pd
from src.simulator import CASES,metrics,simulate
out=ROOT/'results'/'tables';out.mkdir(parents=True,exist_ok=True)
frames=[]; summaries=[]
for case in CASES:
    try:
        frame=simulate(case); frames.append(frame); summaries.append(metrics(frame))
    except Exception as exc:  # preserve a failed case rather than silently dropping it
        summaries.append({'case':case,'status':'failed','error':str(exc)})
if frames:
    pd.concat(frames,ignore_index=True).to_csv(out/'event_traces.csv',index=False)
pd.DataFrame(summaries).to_csv(out/'event_summary.csv',index=False)
failures=sum(item['status'] == 'failed' for item in summaries)
print(f'wrote {len(summaries)} synthetic event cases; failures: {failures}')
