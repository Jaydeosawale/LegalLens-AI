import unittest
from rag.retrievers.query_rewriter import QueryRewriter


class QueryNormalizationTest(unittest.TestCase):
    def test_equivalent_definition_questions_use_same_search(self):
        for question in ('income tax', 'what is income tax', 'What is income tax?',
                         '  Please explain   Income Tax! ', 'Define income tax'):
            self.assertEqual(QueryRewriter.rewrite(question), 'income tax')

    def test_preserves_legal_qualifiers(self):
        self.assertEqual(QueryRewriter.rewrite('What is not taxable under section 10 in 2025?'),
                         'not taxable under section 10 in 2025')
        self.assertEqual(QueryRewriter.rewrite('How is income tax calculated for non-residents?'),
                         'how is income tax calculated for non-residents')

    def test_does_not_produce_empty_search(self):
        self.assertEqual(QueryRewriter.rewrite('What is?'), 'what is')
