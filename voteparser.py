from json import loads
from itertools import combinations
from sys import stderr, argv, exit
from dateutil import parser

meps = {}

vote_types = ('For', 'Against', 'Abstain')

def parse(outprefix, from_date, to_date=None, ep_refs=None):
    with open('ep_votes.json') as infile:
        infile.seek(1)
        line = infile.readline().strip()
        i = 0
        while line:
            if line in (',', ']'):
                i += 1
                try:
                    line = infile.readline().strip()
                except:
                    break
                continue
            vote_data = loads(line)
            vote_date = parser.parse(vote_data['ts'])
            if vote_date < from_date\
               or (to_date and vote_date > to_date)\
               or (ep_refs and vote_data.get('epref') not in ep_refs):
                i += 1
                try:
                    line = infile.readline().strip()
                except:
                    break
                continue
            stderr.write('.'); stderr.flush()
            for vid,vote_type in enumerate(vote_types):
                if vote_type not in vote_data:
                    continue
                for groups in vote_data[vote_type]['groups']:
                    for vote in groups['votes']:
                        if type(vote) != dict:
                            continue
                        meps.setdefault(vote['id'], [set(),set(),set()])[vid].add(i)
            i += 1
            try:
                line = infile.readline().strip()
            except:
                break

    stderr.write('[parsing done]\n')

    with open(outprefix+'_vote_counts.csv', 'w') as outfile:
        outfile.write('mep\tvote_count\n')
        for mep in meps:
            outfile.write('{0}\t{1}\n'.format(mep, sum(len(x) for x in meps[mep])))

    stderr.write('[vote counts done]\n')

    with open(outprefix+'_same_votes.csv', 'w') as outfile:
        outfile.write('mep1\tmep2\tsame_vote_count\n')
        for mep1, mep2 in combinations(meps.keys(), 2):
            same_votes = 0
            for cid,categ in enumerate(meps[mep1]):
                for vote in categ:
                    if vote in meps[mep2][cid]:
                        same_votes += 1
            outfile.write('{0}\t{1}\t{2}\n'.format(mep1,mep2,same_votes))

    stderr.write('[same votes done]\n')


if __name__ == '__main__':
    if len(argv) not in (4, 5):
        print('''[Error] wrong parameters
run
 python voteparser.py <output prefix> <from-date> <end-date>
or
python voteparser.py <output prefix> <from-date> <end-date> <reference list file>''')
        exit(1)

    prefix = argv[1]
    from_date = parser.parse(argv[2])
    to_date = parser.parse(argv[3])
    prefix += '_{0}_-_{1}'.format(argv[2].replace('/', '-'), argv[3].replace('/', '-'))
    print(prefix)
    if len(argv) == 5:
        ep_refs = set(map(str.strip, open(argv[4]).readlines()))
    else:
        ep_refs = None

    parse(prefix, from_date, to_date, ep_refs)
