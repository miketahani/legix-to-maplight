# link legix data to ML data via APIs
# mike tahani       m.tahani@gmail.com
# usage: linkdata.py JSON_FILE
import json, urllib, re, sys

MAPLIGHT_API_KEY = 'INSERT API KEY HERE'

def search(tree, key):
    for node in tree:
        if key in node:
            res = [ v['src'] for sec in node[key] for v in sec['versions'] ] 
            #yield [ url(urn) for urn in list(set(res)) ]
            yield list(set(res))
        else: search(node['levels'], key)
    return

def url(urn):
    ''' return resolve URL from a URN '''
    return "http://legix.info/resolve(%s:json)" % ( re.sub('\(.+?\)', '', urn) )

def legix_get(json_data):
    ''' get the relevant data from a legix json CODE doc '''
    levels = json_data['fragment']['content']['levels']
    result = search(levels, "sections")
    all_urns = list( set( [re.sub('\(.+?\)', '', urn) for res in result for urn in res] ) )
    bills = get_bill_data(all_urns)
    for bill in bills:
        if bill['prefix'] == 'ab' or bill['prefix'] == 'sb':
            print bill
            print "organizations:", maplight( urllib.urlencode(bill) )

def get_bill_data(all_urns):
    ''' get bill numbers from statutes '''
    statutes = json.load( open('../data/statuteslist.json') )
    reformatted_stats = filter(None, [statute_to_bill(urn) for urn in all_urns])
    for statute in reformatted_stats:
        # get bill from statuteslist.json:
        prefix, number = statutes[ statute['reformatted'] ].split('_') 
        session = statute['session']
        yield dict( zip( ['session', 'prefix', 'number'],
                         [ session, prefix, number ] ) )

def statute_to_bill(urn):
    ''' link statutes to bill numbers, skip legix entirely '''
    year_and_chapter = re.compile('(\d{4})[a-z\d]*?-chp(\d{4})')
    year, chapter = year_and_chapter.findall(urn)[0]
    chapter = re.sub('^0+', '', chapter)
    if int(year) > 2008:
        # maplight data only goes past 2009
        reformatted = "ch-%s_st_%s" % (chapter, year) # 1998-chp0931 -> ch-931_st_1998
        session = year
        if session == '2010':
            session = '2009'    # session number IS NOT year enacted
        return { 'session'     : session,
                 'reformatted' : reformatted }
    else:
        return

def load_json_from_url(url):
    ''' duh '''
    data = urllib.urlopen(url).read()
    #print data # debugging
    #return json.loads( data.encode('ascii','ignore') )
    return json.loads(data)
    
def resolver(url):
    ''' get bill data -> send to maplight '''
    jsond = load_json_from_url(url)
    hdrs = [ 'sessionYear', 'measureType', 'measureNum' ]
    #return dict( zip( hdrs, [ jsond['legInfo'][val] for val in hdrs ] ) )
    vars = [ 'session', 'prefix', 'number' ]
    vals = [ jsond['legInfo'][val] for val in hdrs ]
    #return '&'.join( [ "%s=%s" % (k,v) for k,v in zip(vars,vals) ] )
    return urllib.urlencode( zip(vars,vals) )

def maplight(url_suffix):
    ''' get bill position data from maplight's API '''
    url = "http://maplight.org/services_open_api/map.bill_positions_v1.json?"\
          "apikey=%s&jurisdiction=ca&%s" % (MAPLIGHT_API_KEY, url_suffix)
    jsond = load_json_from_url(url)
    return dict( [ (org['name'], org['disposition']) for org in jsond['bill']['organizations'] ] )

if __name__ == '__main__':
    d = open( sys.argv[-1] ).read()
    json_data = json.loads( d.decode('ascii','ignore') )
    legix_get(json_data)