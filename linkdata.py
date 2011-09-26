# link legix data to ML data via APIs
# mike tahani       m.tahani@gmail.com
# usage: linkdata.py JSON_FILE
import json, urllib, re, sys

MAPLIGHT_API_KEY = 'INSERT API KEY HERE'

def search(tree, key):
    """ search a tree-like data structure (json/xml) for a key """
    for node in tree:
        if key in node:
            # in legix json data, find all instances of "sections" > "versions" > "src":
            res = [ v['src'] for sec in node[key] for v in sec['versions'] ] 
            #yield [ url(urn) for urn in list(set(res)) ]
            yield list(set(res))
        else: search(node['levels'], key)   # found multiple "levels"; keep searching the tree
    return

def url(urn):
    """ return a properly formatted legix API resolve() call from a URN """
    return "http://legix.info/resolve(%s:json)" % ( re.sub('\(.+?\)', '', urn) )

def legix_to_maplight(json_data):
    """
    get all URNs in a legix state code doc, then use the URNs to find
    corresponding data via maplight's API
    """
    levels = json_data['fragment']['content']['levels']
    result = search(levels, "sections")
    # get the base urns (strip out section information):
    all_urns = list( set( [re.sub('\(.+?\)', '', urn) for res in result for urn in res] ) )
    bills = get_bill_data(all_urns)
    for bill in bills:
        if bill['prefix'] == 'ab' or bill['prefix'] == 'sb':
            print bill
            # query maplight using data about the bill:
            print "organizations:", query_maplight( urllib.urlencode(bill) )

def get_bill_data(all_urns):
    """ translate CA statute chapter/year to a corresponding bill """
    statutes = json.load( open('../data/statuteslist.json') )
    # reformat all legix-formatted statute chapter/year data to statuteslist format
    reformatted_stats = filter(None, [reformat_statute_name(urn) for urn in all_urns])
    for statute in reformatted_stats:
        # look up bill prefix/number ('ab_1099') from statuteslist.json:
        prefix, number = statutes[ statute['reformatted'] ].split('_') 
        session = statute['session']
        yield dict( zip( ['session', 'prefix', 'number'],
                         [ session, prefix, number ] ) )

def reformat_statute_name(urn):
    """ format statute data for a lookup in statuteslist.json; get session """
    year_and_chapter = re.compile('(\d{4})[a-z\d]*?-chp(\d{4})')
    year, chapter = year_and_chapter.findall(urn)[0]
    chapter = re.sub('^0+', '', chapter)    # remove leading zeroes from chapter
    if int(year) > 2008:
        # maplight data only goes past 2009; ignore years prior to 2009
        reformatted = "ch-%s_st_%s" % (chapter, year) # e.g. '1998-chp0931' becomes 'ch-931_st_1998'
        session = year  # "year enacted" corresponds to a bill's session number
        if session == '2010':
            session = '2009'    # session number IS NOT year enacted; correct it
        return { 'session'     : session,
                 'reformatted' : reformatted }
    else:
        return

def load_json_from_url(url):
    """ helper function to load json from an url """
    data = urllib.urlopen(url).read()
    #return json.loads( data.encode('ascii','ignore') )
    return json.loads(data)
    
def resolver(url):
    """
    get bill data from a legix doc via API and format it for maplight API calls;
    no longer used, thanks to statuteslist.json
    """
    jsond = load_json_from_url(url)
    hdrs = [ 'sessionYear', 'measureType', 'measureNum' ]
    #return dict( zip( hdrs, [ jsond['legInfo'][val] for val in hdrs ] ) )
    vars = [ 'session', 'prefix', 'number' ]
    vals = [ jsond['legInfo'][val] for val in hdrs ]
    #return '&'.join( [ "%s=%s" % (k,v) for k,v in zip(vars,vals) ] )
    return urllib.urlencode( zip(vars,vals) )

def query_maplight(url_suffix):
    """
    get bill position data from maplight's API; called by legix_to_maplight();
    expects an url suffix containing session, prefix, & number for the ML API
    """
    url = "http://maplight.org/services_open_api/map.bill_positions_v1.json?"\
          "apikey=%s&jurisdiction=ca&%s" % (MAPLIGHT_API_KEY, url_suffix)
    jsond = load_json_from_url(url)
    return dict( [ (org['name'], org['disposition']) for org in jsond['bill']['organizations'] ] )

def main(filename):
    """ main """
    d = open( filename ).read()
    json_data = json.loads( d.decode('ascii','ignore') )
    legix_to_maplight(json_data)

if __name__ == '__main__':
    main( sys.argv[-1] )