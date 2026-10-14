import json
r=json.load(open('out/qa_report.json'))
for i in r: print(i['kind'],i['a'][:24],i['b'][:24],i['t0'],i['t1'],round(i['worst'],3))
