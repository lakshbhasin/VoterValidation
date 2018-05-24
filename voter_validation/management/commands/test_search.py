"""
Tests searching for a voter by full name, residential address, or ZIP. Partial
searches are supported for full name and residential address.

Usage:
    python manage.py test_search -n "<name>" -a "<address>" -z <ZIP> \
        [-s <num_searches>]

To get more stable results for timing average search latency, it's recommended
to use -s 250 or so.
"""
import time

from django.core.management import BaseCommand, CommandError

from voter_validation.search import voter_search


class Command(BaseCommand):
    help = 'Searches for a specified Voter.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--name',
                            dest='name',
                            help="Voter's full name, or any part thereof.")
        parser.add_argument('-a', '--address',
                            dest='address',
                            help="Voter's residential address, or any part "
                                 "thereof.")
        parser.add_argument('-z', '--zip',
                            dest='zip',
                            help="Voter's 5-digit ZIP")
        parser.add_argument('-s', '--num_searches',
                            dest='num_searches',
                            type=int,
                            default=1,
                            help='Number of times to search the given query.')

    def print_results(self, results):
        for result in results:
            self.stdout.write('%s @ %s -- Score: %.2f. Name similarity: %.2f. '
                              'Address similarity: %.2f. '
                              'Exact address match: %.2f' %
                              (result['name'], result['address'],
                               result['search_score'],
                               result.get('name_similarity', 0),
                               result.get('addr_similarity', 0),
                               result.get('addr_exact_match', 0)))

    def handle(self, *args, **options):
        name = options['name']
        address = options['address']
        res_zip = options['zip']
        num_searches = int(options['num_searches'])

        self.stdout.write("Name: %s" % name)
        self.stdout.write("Address: %s" % address)
        self.stdout.write("ZIP: %s" % res_zip)
        self.stdout.write("Num searches: %d" % num_searches)

        self.stdout.write("\nIssuing same search %d times..." % num_searches)
        search_times = []
        results = None
        for i in range(num_searches):
            start_time = time.time()
            new_results = voter_search(name, address, res_zip, debug=True)
            end_time = time.time()

            # Results shouldn't change
            if results is not None:
                if results != new_results:
                    raise CommandError("FAILURE: Search results changed after "
                                       "re-issuing query.")
            else:
                results = new_results
            search_times.append(1000.0 * (end_time - start_time))

        ave_time = sum(search_times) / len(search_times)

        self.stdout.write(self.style.SUCCESS("\nSearch(es) successful!"))
        self.stdout.write("Average time per search: %.1f ms" % ave_time)
        self.stdout.write("\nResults: ")
        self.print_results(results)
