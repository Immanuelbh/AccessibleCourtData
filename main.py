import sys
from hcva.elastic.v7.elastic import main as elastic
from hcva.parser.parser import main as parser
from hcva.utils.sync import upload_sync, download_sync
from hcva.scraper.app import main as scraper

if __name__ == '__main__':
    functions = {1: scraper,
                 2: parser,
                 3: elastic,
                 4: upload_sync,
                 5: download_sync,
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
