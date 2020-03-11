from dateutil.parser import parse

strd1 = "2019-07-19T11:07:00"
strdlimite = "2019-07-10"

d1 = parse(strd1)
d2 = parse(strdlimite)

if d1 > d2:
    print "data >"
if strd1 > strdlimite:
    print "coco"
else:
    print 'vv'