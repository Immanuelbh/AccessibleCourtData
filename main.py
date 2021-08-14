import sys
from hcva.elastic.v7.elastic import main as elastic
from hcva.parser.parser import main as parser
from hcva.parser.enricher.main import normalize
from hcva.scraper.app import main as scraper

if __name__ == '__main__':
    functions = {1: scraper,
                 2: parser,
                 3: normalize,
                 4: elastic,
                 }

    if len(sys.argv) > 1:
        choice = int(sys.argv[1])
    else:
        choice = int(input("Enter which function you want to run:\n"
                           "1: Scraper\n"
                           "2: Parser\n"
                           "3: Enricher\n"
                           "4: Elastic\n"
                           ))

    if len(functions) >= choice > 0:
        func = functions[choice]
        func()


print('DONE')
