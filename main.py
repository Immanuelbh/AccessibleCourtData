import sys
from hcva.elastic.v7.Elastic import main as elastic_main
from hcva.parser.parser import main as parser_main
from hcva.utils.sync import uploadSync, downloadSync
from hcva.scraper.scrapers.SupremeCourt_Scraper import main as scraper_main

if __name__ == '__main__':
    functions = {1: scraper_main,
                 2: parser_main,
                 3: elastic_main,
                 4: uploadSync,
                 5: downloadSync
                 }

    if len(sys.argv) > 1:
        choice = int(sys.argv[1])
    else:
        choice = int(input("Enter which function you want to run:\n"
                           "1: Supreme Court Scraper\n"
                           "2: Parser\n"
                           "3: Elastic\n"
                           "4: Upload Sync\n"
                           "5: Download Sync\n"
                           ))

    if len(functions) >= choice > 0:
        func = functions[choice]
        func()


print('DONE')
