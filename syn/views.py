from syn import do_it_all, tagged
from django.http import HttpResponse
from json import dumps
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def home(request):
    p = request.POST
    r = request.REQUEST
    if "s" in p:
        res = do_it_all(p["s"])
        return HttpResponse(res)
    elif "t" in r:
        res = tagged(r['t'])
        return HttpResponse(res)
    else:
        return HttpResponse(status=404)
