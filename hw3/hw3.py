# I collaborated with other students for this homework : Huilan You

# ========================================================================
# Copyright 2018 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========================================================================

import codecs
import bibtexparser
import re
import os
import glob
from collections import Counter
from types import SimpleNamespace
import tldextract

# Task 1

def load_map(map_file):
    """
    :param map_file: bib_map.tsv
    :return: a dictionary where the key is the conference/journal ID and the value is a namespace of (weight, series).
    """
    fin = open(map_file)
    d = {}

    for i, line in enumerate(fin):
        l = line.strip().split('\t')
        if len(l) == 3:
            key = l[0]
            d[key] = SimpleNamespace(weight=float(l[1]), series=l[2])

    return d


def get_entry_dict(bib_map, bib_dir):
    """
    :param bib_map: the output of load_map().
    :param bib_dir: the input directory where the bib files are stored.
    :return: a dictionary where the key is the publication ID (e.g., 'P17-1000') and the value is its bib entry.
    """
    re_pages = re.compile('(\d+)-{1,2}(\d+)')

    def parse_name(name):
        if ',' in name:
            n = name.split(',')
            if len(n) == 2: return n[1].strip() + ' ' + n[0].strip()
        return name

    def get(entry, weight, series):
        entry['author'] = [parse_name(name) for name in entry['author'].split(' and ')]
        entry['weight'] = weight
        entry['series'] = series
        return entry['ID'], entry

    def valid(entry, weight):
        if weight == 1.0:
            if 'pages' in entry:
                m = re_pages.search(entry['pages'])
                return m and int(m.group(2)) - int(m.group(1)) > 4
            return False

        return 'author' in entry

    bibs = {}
    for k, v in bib_map.items():
        fin = open(os.path.join(bib_dir, k+'.bib'), encoding='utf-8')
        bib = bibtexparser.loads(fin.read())
        bibs.update([get(entry, v.weight, v.series) for entry in bib.entries if valid(entry, v.weight)])

    return bibs


def get_email_dict(txt_dir):
    """
    :param txt_dir: the input directory containing all text files.
    :return: a dictionary where the key is the publication ID and the value is the list of authors' email addresses.
    """
    def chunk(text_file, page_limit=2000):
        fin = codecs.open(text_file, encoding='utf-8')
        doc = []
        n = 0

        for line in fin:
            line = line.strip().lower()
            if line:
                doc.append(line)
                n += len(line)
                if n > page_limit: break

        return ' '.join(doc)

    re_email = re.compile(
        '[({\[]?\s*([a-z0-9\.\-_]+(?:\s*[,;|]\s*[a-z0-9\.\-_]+)*)\s*[\]})]?\s*@\s*([a-z0-9\.\-_]+\.[a-z]{2,})')
    email_dict_new = {}

    for txt_file in glob.glob(os.path.join(txt_dir, '*.txt')):
        try:
            doc = chunk(txt_file)
        except UnicodeDecodeError:
            continue
        emails = []

        pattern1 = ['lastname.firstname']
        pattern2 = ['initial.last', 'initial.surname']
        pattern3 = ['surname','lastname']

        for m in re_email.findall(doc):

            ids = m[0].replace(';', ',').replace('|', ',')
            domain = m[1]

            ## Consider different patterns of emails

            if ids in pattern1:
                name1 = []
                key = os.path.basename(txt_file)[:-4]
                if key in entry_dict:

                    for k in entry_dict[key]['author']:
                        first = k.split(' ')[0].lower()
                        last = k.split(' ')[1].lower()
                        name1.append(last + '.' + first)

                    ids = ','.join(name1)

                if ',' in ids:
                    for ID in ids.split(','):
                        if ID.strip() in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            continue
                        emails.append(ID.strip() + '@' + domain)



                break

            elif ids in pattern2:
                name2 = []
                key = os.path.basename(txt_file)[:-4]
                if key in entry_dict:

                    for k in entry_dict[key]['author']:
                        initial = k.split(' ')[0][1].lower()
                        last = k.split(' ')[1].lower()
                        name2.append(initial + '.' + last)

                    ids = ','.join(name2)

                if ',' in ids:
                    for ID in ids.split(','):
                        if ID.strip() in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            continue
                        emails.append(ID.strip() + '@' + domain)



                break

            elif ids in pattern3:
                name3 = []
                key = os.path.basename(txt_file)[:-4]
                if key in entry_dict:

                    for k in entry_dict[key]['author']:
                        last = k.split(' ')[1].lower()
                        name3.append(last)

                    ids = ','.join(name3)

                if ',' in ids:
                    for ID in ids.split(','):
                        if ID.strip() in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            continue
                        emails.append(ID.strip() + '@' + domain)



                break

            else:
                if ',' in ids:
                    for ID in ids.split(','):
                        if ID.strip() in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            continue
                        emails.append(ID.strip() + '@' + domain)
                else:
                    emails.append(ids + '@' + domain)

        if emails:
            key = os.path.basename(txt_file)[:-4]
            email_dict_new[key] = emails


    return email_dict_new

def print_emails(entry_dict, email_dict_new, email_file, weights_dict):
    """
    :param entry_dict: the output of get_entry_dict().
    :param email_dict: the output of get_email_dict().
    :param email_file: the output file in the TSV format, where each column contains
                       (publication ID, the total number of authors, list of email addresses) for each paper.
    """
    fout = open(email_file, 'w')

    for k, v in sorted(entry_dict.items()):
        n = len(v['author'])
        l = [k, str(n)]
        if k in email_dict_new:
            emails = [';'.join(email_dict_new[k][:n])]
            if k in weights_dict:
                l = [k, str(n), str(emails), str(weights_dict[k])]

        fout.write('\t'.join(l) + '\n')
    fout.close()


def print_mismatch(entry_dict, email_dict_new, email_mismatch):

    fout = open(email_mismatch, 'w')

    for k, v in sorted(entry_dict.items()):
        n = len(v['author'])

        if k in email_dict_new:
            e_count = len(email_dict_new[k])
            if e_count != n:
                l = [k, str(n), str(e_count), str(email_dict_new[k])]
                fout.write('\t'.join(l) + '\n')


    fout.close()


# Task 2

def get_domains(email_dict_new):

    domain = {}

    for k, v in email_dict_new.items():
        domains = []
        for z in email_dict_new[k]:
            domains.append(str(z.split('@')[1]))

        domain[k] = domains

    return domain

def get_weights(domain):
    weights = {}

    for k, v in domain.items():
        num_dom = len(v)
        dom = []
        w = Counter([t for t in v])
        y = len(Counter([t for t in v]))
        doms = {}

        if y >= 1:
            for k1, v1 in w.items():
                ext = tldextract.extract(k1)
                main = '.'.join(ext[1:3])
                doms[main] = doms.get(main, 0) + v1


            for k2, v2 in doms.items():
                #                 print(k2)
                weigh = int(v2) / int(num_dom)
                weigh = round(weigh, 2)
                dom.append((' ' + str(k2) + ":" + str(weigh)).strip())

            weights[k] = ';'.join(dom)

    return weights

if __name__ == '__main__':
    BIB_DIR ='/Users/huilanyou/PycharmProjects/qtm385/hw3/nlp-ranking-master/bib/'
    MAP_FILE = '/Users/huilanyou/PycharmProjects/qtm385/hw3/nlp-ranking-master/dat/bib_map.tsv'

    bib_map = load_map(MAP_FILE)
    entry_dict = get_entry_dict(bib_map, BIB_DIR)

    TXT_DIR = '/Users/huilanyou/PycharmProjects/qtm385/hw3/nlp-ranking-m'
    email_dict_new = get_email_dict(TXT_DIR)
    print(email_dict_new)

    EMAIL_MISMATCH = 'you_mismatch.tsv'
    print_mismatch(entry_dict, email_dict_new, EMAIL_MISMATCH)

    # Task 2: Institution Weighting
    domains_dict = get_domains(email_dict_new)
    weights_dict = get_weights(domains_dict)

    EMAIL_FILE = '/Users/huilanyou/PycharmProjects/qtm385/hw3/nlp-ranking-master/dat/email_map.tsv'
    print_emails(entry_dict, email_dict_new, EMAIL_FILE, weights_dict)