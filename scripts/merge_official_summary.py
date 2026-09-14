#!/usr/bin/env python3
import csv, json, re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "data" / "official-summary.csv"
AUTO = ROOT / "auto-data.js"
STATUS = ROOT / "data" / "fetch-status.json"

VALID = {"AMARPATAN","MAIHAR","RAMNAGAR","MAJHGAWAN","NAGOD","RAMPUR BAGHELAN","SATNA","UNCHAHARA"}
NUMFIELDS = ["totalGP","musterGP","dysfunctionalGP","labourAll","mrAll","noEkyc","mrs","ongoingAll",
             "labourIndividual","mrIndividual","labourCommunity","mrCommunity",
             "pmayLabour","pmayOngoing","pmayMR","ekLabour","ekOngoing","ekMR"]

# Verified R6.12 work-level master counts dated 13-09-2026.
# These three ongoing denominators must remain stable in the Official Janpad Daily Report.
# Today's live labour/MR values still come from the official daily source.
R612_VERIFIED = {
    "AMARPATAN":       {"ongoingAll":1383, "pmayOngoing":865,  "ekOngoing":109},
    "MAIHAR":          {"ongoingAll":2482, "pmayOngoing":1512, "ekOngoing":86},
    "MAJHGAWAN":       {"ongoingAll":2204, "pmayOngoing":1255, "ekOngoing":85},
    "NAGOD":           {"ongoingAll":2311, "pmayOngoing":1637, "ekOngoing":99},
    "RAMNAGAR":        {"ongoingAll":1166, "pmayOngoing":910,  "ekOngoing":105},
    "RAMPUR BAGHELAN": {"ongoingAll":3264, "pmayOngoing":2713, "ekOngoing":75},
    "SATNA":           {"ongoingAll":1048, "pmayOngoing":422,  "ekOngoing":94},
    "UNCHAHARA":       {"ongoingAll":1829, "pmayOngoing":1185, "ekOngoing":102},
}

def num(v):
    try: return float(str(v).replace(",", "").strip() or 0)
    except Exception: return 0.0

def load_auto():
    s=AUTO.read_text(encoding="utf-8").strip()
    s=re.sub(r"^window\.AUTO_REPORT\s*=\s*","",s).rstrip(";")
    return json.loads(s)

def main():
    with CSV.open(encoding="utf-8-sig", newline="") as f:
        rows=list(csv.DictReader(f))
    got={str(r.get("janpad","")).strip().upper() for r in rows}
    if got != VALID:
        raise SystemExit(f"Official summary validation failed: {sorted(got)}")

    clean=[]
    for r in rows:
        z={"janpad":str(r["janpad"]).strip().upper()}
        for k in NUMFIELDS: z[k]=num(r.get(k,0))
        if z["totalGP"]<=0 or z["musterGP"]<=0:
            raise SystemExit(f"Invalid Screen-2 row: {z['janpad']}")
        fixed=R612_VERIFIED[z["janpad"]]
        z["ongoingAll"]=fixed["ongoingAll"]
        z["pmayOngoing"]=fixed["pmayOngoing"]
        z["ekOngoing"]=fixed["ekOngoing"]
        clean.append(z)

    a=int(sum(x["ongoingAll"] for x in clean))
    p=int(sum(x["pmayOngoing"] for x in clean))
    e=int(sum(x["ekOngoing"] for x in clean))
    if (a,p,e)!=(15687,10499,755):
        raise SystemExit(f"R6.12 VERIFY FAILED Ongoing={a} PMAY={p} EK={e}")

    data=load_auto()
    new_daily=[{
        "janpad":o["janpad"],"totalGP":o["totalGP"],"gpsProgress":o["musterGP"],"dysfunctionalGP":o["dysfunctionalGP"],
        "labour":o["labourAll"],"worksMR":o["mrAll"],"ongoing":o["ongoingAll"],"mrs":o["mrs"],
        "labourIndividual":o["labourIndividual"],"mrIndividual":o["mrIndividual"],
        "labourCommunity":o["labourCommunity"],"mrCommunity":o["mrCommunity"],
        "pmayLabour":o["pmayLabour"],"pmayOngoing":o["pmayOngoing"],"pmayMR":o["pmayMR"],
        "ekLabour":o["ekLabour"],"ekOngoing":o["ekOngoing"],"ekMR":o["ekMR"]
    } for o in clean]

    before=json.dumps({"official":data.get("official",[]),"daily":data.get("daily",[])},ensure_ascii=False,sort_keys=True,separators=(",",":"))
    after=json.dumps({"official":clean,"daily":new_daily},ensure_ascii=False,sort_keys=True,separators=(",",":"))
    changed=before!=after
    data["official"]=clean
    data["daily"]=new_daily
    meta=data.setdefault("meta",{})
    meta.update({"mode":"auto","status":"ok","source":"Official VB-G RAM G live + verified R6.12 ongoing master",
                 "officialSummaryRows":8,"screen2Matched":True,"r612VerifiedOngoing":True,
                 "r612Totals":{"ongoingAll":15687,"pmayOngoing":10499,"ekOngoing":755}})
    if changed or not meta.get("updatedAt"): meta["updatedAt"]=datetime.now(timezone.utc).isoformat()
    meta["dataChangedOnLastFetch"]=changed
    try:
        st=json.loads(STATUS.read_text(encoding="utf-8"))
        if st.get("officialDate"): meta.setdefault("sourceDates",{})["OfficialSummary"]=st["officialDate"]
    except Exception: pass
    AUTO.write_text("window.AUTO_REPORT="+json.dumps(data,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    print("AUTO MERGE OK | Ongoing=%d | PMAY Ongoing=%d | Ek Bagiya Ongoing=%d | R6.12 verified" % (a,p,e))

if __name__=="__main__":
    main()
