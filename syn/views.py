from syn import do_it_all, tagged, filtered_for_syn
from django.http import HttpResponse
from json import dumps
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def home(request):
    r = request.REQUEST
    if "sent" in r:
        res = do_it_all(r["sent"])
        return HttpResponse(res)
    elif "tag" in r:
        res = tagged(r['tag'])
        return HttpResponse(res)
    elif 'syn' in r:
        res = filtered_for_syn(tagged(r["syn"]),r['p']) if 'p' in r else  filtered_for_syn(tagged(r["syn"]))
        return HttpResponse(res)
    else:
        return HttpResponse(status=404)
