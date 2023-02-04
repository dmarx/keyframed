import re
from keyframed import Curve

def deforum_parse(string, prompt_parser=None):
    # because math functions (i.e. sin(t)) can utilize brackets 
    # it extracts the value in form of some stuff
    # which has previously been enclosed with brackets and
    # with a comma or end of line existing after the closing one
    pattern = r'((?P<frame>[0-9]+):[\s]*\((?P<param>[\S\s]*?)\)([,][\s]?|[\s]?$))'
    frames = dict()
    for match_object in re.finditer(pattern, string):
        frame = int(match_object.groupdict()['frame'])
        param = match_object.groupdict()['param']
        if prompt_parser:
            frames[frame] = prompt_parser(param)
        else:
            frames[frame] = param
    if frames == {} and len(string) != 0:
        raise RuntimeError('Key Frame string not correctly formatted')
    return frames

def curve_from_cn_string(cn_string):
    d = {k:float(v) for k,v in deforum_parse(cn_string).items()}
    if 0 not in d:
        start_frame = min(d.keys())
        d[0] = d[start_frame]
    curve = Curve(d, default_interpolation='linear')
    return curve