from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from tier8_v2_fresh_development import select

class FreshSelectionTests(unittest.TestCase):
    def test_excludes_entire_seen_reports_and_duplicate_groups(self):
        rows=[{'id':s} for s in ['A/2010/page_1.pdf-1','A/2010/page_2.pdf-1','B/2011/page_1.pdf-1','B/2011/page_2.pdf-1','C/2012/page_1.pdf-1']]
        chosen=select(rows,set(),{'A/2010'},2)
        self.assertEqual([r['id'] for r in chosen],['B/2011/page_1.pdf-1','C/2012/page_1.pdf-1'])
    def test_labels_do_not_change_selection(self):
        ids=['A/2010/page_1.pdf-1','B/2011/page_1.pdf-1']
        a=select([{'id':s,'qa':{'answer':'correct'}} for s in ids],set(),set(),2)
        b=select([{'id':s,'qa':{'answer':'different'}} for s in ids],set(),set(),2)
        self.assertEqual([r['id'] for r in a],[r['id'] for r in b])
    def test_insufficient_groups_refused(self):
        with self.assertRaises(ValueError):select([{'id':'A/2010/page_1.pdf-1'}],set(),{'A/2010'},1)

if __name__=='__main__':unittest.main()
