from ncis import route, api_response, api_error, request, ncis_weakrefs
import sys
import platform
import inspect
import gc

__version__ = "0.1"
__author__ = "Mathieu Virbel <mat@kivy.org>"

@route("/version")
def version():
    vi = sys.version_info
    un = platform.uname()
    return api_response({
        "version": sys.version,
        "version_info": {
            "major": vi.major,
            "minor": vi.minor,
            "micro": vi.micro,
            "releaselevel": vi.releaselevel,
            "serial": vi.serial
        },
        "platform": {
            "system": un.system,
            "node": un.node,
            "release": un.release,
            "version": un.version,
            "machine": un.machine,
            "processor": un.processor
        }
    })


@route("/modules")
def modules():
    return api_response(list(sys.modules.keys()))


@route("/exec", methods=["POST"])
def _exec():
    cmd = request.form.get("cmd")
    if not cmd:
        return api_response(None)
    try:
        exec(cmd, globals(), globals())
        return api_response()
    except Exception as e:
        return api_error(repr(e))


@route("/eval", methods=["POST"])
def _eval():
    cmd = request.form.get("cmd")
    if not cmd:
        return api_response(None)
    try:
        result = eval(cmd, globals(), globals())
        return api_response(result)
    except Exception as e:
        return api_error(repr(e))


@route("/inspect/<refid>", methods=["GET"])
def _inspect(refid):
    refid = int(refid)
    try:
        obj = ncis_weakrefs.get(refid)
        if obj is None:
            return api_response(None)
        obj = obj()
        if obj is None:
            ncis_weakrefs.pop(refid, None)
            return api_response(None)
        result = inspect.getmembers(obj)
        return api_response(result)
    except Exception as e:
        import traceback; traceback.print_exc()
        ncis_weakrefs.pop(refid, None)
        return api_response(None)


@route("/inspect", methods=["POST"])
def _inspect_by_eval():
    cmd = request.form.get("cmd")
    if not cmd:
        return api_error("cmd is empty")
    try:
        obj = eval(cmd, globals(), globals())
        return api_response(inspect.getmembers(obj))
    except Exception as e:
        import traceback; traceback.print_exc()
        return api_response(None)


@route("/gc")
def gc_state():
    return api_response({
        "enabled": gc.isenabled()
    })


@route("/gc/enable")
def gc_enable():
    gc.enable()
    return api_response()


@route("/gc/disable")
def gc_disable():
    gc.disable()
    return api_response()


@route("/gc/stats")
def gc_stats():
    return api_response(gc.stats())


@route("/gc/counts")
def gc_count():
    return api_response(gc.count())