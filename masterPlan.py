import httplib2
from bs4 import BeautifulSoup, SoupStrainer
import cProfile




http = httplib2.Http()
pilar_urls = ['https://univis.fau.de/form?__s=2&dsc=anew/modules&tdir=__mod/fau/techfa/inform_6/'
              'master/wahlpf/sulede_1&autoexports=modules_pversion&anonymous=1&camefrom=__sat/'
              'studie/inform&modules_oldsem=2019w&modules_pordnrtitle=079%2365%23H&modules_pversion'
              '=079%2365%23H%232010&ref=tumstud&sem=2019w&__e=294',
              'https://univis.fau.de/form?__s=2&dsc=anew/modules&tdir=__mod/fau/techfa/inform_6/'
              'master/wahlpf/sulede&autoexports=modules_pversion&anonymous=1&camefrom=__sat/studie/'
              'inform&modules_oldsem=2019w&modules_pordnrtitle=079%2365%23H&modules_pversion='
              '079%2365%23H%232010&ref=tumstud&sem=2019w&__e=297',
              'https://univis.fau.de/form?__s=2&dsc=anew/modules&tdir=__mod/fau/techfa/inform_6/'
              'master/wahlpf/sulede_3&autoexports=modules_pversion&anonymous=1&camefrom=__sat/'
              'studie/inform&modules_oldsem=2019w&modules_pordnrtitle=079%2365%23H&modules_pversion'
              '=079%2365%23H%232010&ref=tumstud&sem=2019w&__e=297',
              'https://univis.fau.de/form?__s=2&dsc=anew/modules&tdir=__mod/fau/techfa/inform_6/'
              'master/wahlpf/sulede_2&autoexports=modules_pversion&anonymous=1&camefrom=__sat/'
              'studie/inform&modules_oldsem=2019w&modules_pordnrtitle=079%2365%23H&modules_pversion'
              '=079%2365%23H%232010&ref=tumstud&sem=2019w&__e=297'


]

def scrape_modules(url):
    status, response = http.request(url)
    modules = []
    for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
        if link.has_attr('href'):
            # module links contain this, lectures don't
            if "amod_view" in link['href']:
                url = 'https://univis.fau.de/'+link['href']
                _, resp = http.request(url)
                # Vertiefungsrichtungs modules contain this tag, use b because resp is bytes
                if b"<h3>Vertiefungsrichtung" in resp:
                    continue
                module_specialisations = []
                module_ects = None
                module_soup = BeautifulSoup(resp,'html.parser')
                module_name = module_soup.body.h3.contents[0].string
                
                dds = module_soup.find_all('dd')
                for dd in dds:
                    if 'Leistungspunkte'  in (dd.contents[0]):
                        module_ects = float(dd.contents[0].split()[-2])
                        
                spans = (module_soup.body.find_all('span'))
                for span in spans:
                    if span.has_attr('class') and  'smalltext' in span['class'] :
                        if  'Informatik (Master of Science)' in  span.text:
                            module_specialisations.append(span.text.split('|')[5])
                modules.append(Module(module_name, module_specialisations, module_ects))
    return modules



class Module:
    def __init__(self, name, specialisations, ects):
        self._name = name
        self._specialisations = specialisations
        self._ects = ects
        

def pilar_from_specialisation(specialisation):
    if(specialisation in [" Vertiefungsrichtung Theoretische Informatik ",
                          " Vertiefungsrichtung Systemsimulation ",
                          " Vertiefungsrichtung Diskrete Simulation ",
                          " Vertiefungsrichtung Kryptographie "]):
        return "Theorie"
    if(specialisation in [" Vertiefungsrichtung Programmiersysteme ", 
                          " Vertiefungsrichtung Datenbanksysteme ",
                          " Vertiefungsrichtung Künstliche Intelligenz ",
                          " Vertiefungsrichtung Software Engineering "]):
        return "Software"
    if(specialisation in [" Vertiefungsrichtung Rechnerarchitektur ",
                          " Vertiefungsrichtung Verteilte Systeme und Betriebssysteme ",
                          " Vertiefungsrichtung Kommunikationssysteme ",
                          " VertiefungsrichtungHardware-Software-Co-Design ",
                          " Vertiefungsrichtung IT-Sicherheit "]):
        return "System"
    if(specialisation in [" Vertiefungsrichtung Mustererkennung ",
                         " Vertiefungsrichtung Graphische Datenverarbeitung ",
                         " Vertiefungsrichtung Elektronik und Informationstechnik ", 
                         " Vertiefungsrichtung Medizinische Informatik ",
                         " Vertiefungsrichtung Medieninformatik ",
                         " Vertiefungsrichtung Informatik in der Bildung "]):
        return "Anwendung"
    return "ERROR"

def main():
    all_modules = []
    for url in pilar_urls:
        
        all_modules.extend(scrape_modules(url))
    for module in all_modules:
        print(module._name)
        for spec in module._specialisations:
            print("{0}: {1}".format(spec, pilar_from_specialisation(spec)))

main()