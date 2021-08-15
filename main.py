import sys
from hcva.scraper.main import scraper
from hcva.parser.main import parser
from hcva.elastic.v7.main import elastic

if __name__ == '__main__':
    functions = {1: scraper,
                 2: parser,
                 3: elastic,
                 }

    if len(sys.argv) > 1:
        choice = int(sys.argv[1])
    else:
        choice = int(input("Enter which function you want to run:\n"
                           "1: Scraper\n"
                           "2: Parser\n"
                           "3: Elastic\n"
                           ))

    if len(functions) >= choice > 0:
        func = functions[choice]
        func()


print('DONE')
