#!/usr/bin/env python3
"""Executable checks of the published specification, not production behavior.

Run from any directory: python3 test/documentation/verify_specification.py
Add --with-hazard after the hazard-analysis PR is present in the stack.
Boolean guards and TP/FP/FN membership predicates are read from SRS.tex so
changing the document changes the cases evaluated here.
"""
import ast
import itertools
import re
import sys
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if '--root' in sys.argv:
    position = sys.argv.index('--root')
    ROOT = Path(sys.argv[position + 1]).resolve()
    del sys.argv[position:position + 2]
SRS = (ROOT / 'docs/SRS/SRS.tex').read_text()
WITH_HAZARD = '--with-hazard' in sys.argv
SRS_OVERRIDE = None
if '--srs' in sys.argv:
    position = sys.argv.index('--srs')
    SRS_OVERRIDE = Path(sys.argv[position + 1])
    del sys.argv[position:position + 2]
    SRS = SRS_OVERRIDE.read_text()
if WITH_HAZARD:
    sys.argv.remove('--with-hazard')


def predicate(source):
    """Translate only the small Boolean language used by these SRS tables."""
    source = source.replace(r'\neg', ' not ').replace(r'\land', ' and ')
    source = source.replace(r'\lor', ' or ').replace(r'\ne', ' != ')
    source = source.replace(r'\hat o_i', 'o').replace('y_i', 'y')
    source = re.sub(r'([cdeav])\(r\)', r'\1', source)
    source = re.sub(r'(?<!!)=', ' == ', source).strip()
    tree = ast.parse(source, mode='eval')
    allowed = (ast.Expression, ast.BoolOp, ast.UnaryOp, ast.And, ast.Or,
               ast.Not, ast.Name, ast.Load, ast.Compare, ast.Eq, ast.NotEq)
    if any(not isinstance(node, allowed) for node in ast.walk(tree)):
        raise ValueError('Unexpected expression in published specification')
    code = compile(tree, '<SRS predicate>', 'eval')
    return lambda **env: eval(code, {'__builtins__': {}}, env)


def guards():
    table = SRS.split(r'\textbf{Disjoint condition on a pending request}', 1)[1]
    table = table.split(r'\end{array}', 1)[0]
    return [(predicate(condition), status) for condition, status in re.findall(
        r'^\s*(.+?)\s*&\s*\\texttt\{(\w+)\}\\\\', table, re.M)]


def membership(name):
    # Acceptance counts must range over I (all eligible examples), never A.
    match = re.search(
        r'\\mathrm\{' + name + r'\}_c&=\|\\\{i\\in I:(.+?)\\\}\|', SRS)
    if not match:
        raise ValueError('Missing full-population ' + name + ' predicate')
    return predicate(match.group(1))


MEMBERSHIP = {name: membership(name) for name in ['TP', 'FP', 'FN']}


def score(truth, outcomes):
    f1 = []
    for c in [0, 1]:
        counts = {name: sum(rule(y=y, o=o, c=c)
                           for y, o in zip(truth, outcomes))
                  for name, rule in MEMBERSHIP.items()}
        denominator = 2 * counts['TP'] + counts['FP'] + counts['FN']
        f1.append(Fraction(2 * counts['TP'], denominator) if denominator else 0)
    return sum(f1) / 2


class SpecificationExamples(unittest.TestCase):
    def test_guard_partition_is_disjoint_and_complete(self):
        rows = guards()
        self.assertEqual(len(rows), 5)
        for values in itertools.product([False, True], repeat=5):
            env = dict(zip('cdeav', values))
            matches = [status for rule, status in rows if rule(**env)]
            self.assertEqual(len(matches), 1, env)

    def transition(self, **overrides):
        env = dict.fromkeys('cdeav', False)
        env.update(overrides)
        return [status for rule, status in guards() if rule(**env)][0]

    def test_waiting_for_analysis_stays_pending(self):
        self.assertEqual(self.transition(), 'pending')
        self.assertEqual(self.transition(a=True), 'inconclusive')
        self.assertEqual(self.transition(a=True, v=True), 'completed')

    def test_simultaneous_events_have_documented_precedence(self):
        self.assertEqual(self.transition(d=True, a=True, v=True), 'failed')
        self.assertEqual(self.transition(e=True, a=True, v=True), 'failed')
        self.assertEqual(self.transition(c=True, d=True, e=True, a=True,
                                         v=True), 'cancelled')

    def test_full_population_diagnostic_exposes_sparse_predictions(self):
        truth = [0] * 500 + [1] * 500
        for withheld in ['inconclusive', 'failed']:
            outcomes = [0] * 5 + [withheld] * 495
            outcomes += [1] * 5 + [withheld] * 495
            self.assertEqual(score(truth, outcomes), Fraction(2, 101))
            self.assertLess(score(truth, outcomes), Fraction(4, 5))

    def test_full_population_diagnostic_for_withheld_and_perfect_runs(self):
        truth = [0, 0, 1, 1]
        for withheld in ['inconclusive', 'failed']:
            self.assertEqual(score(truth, [withheld] * 4), 0)
        self.assertEqual(score(truth, truth), 1)

    def test_more_abstention_cannot_improve_full_population_diagnostic(self):
        # Replacing a correct prediction with abstention must cost credit.
        truth = [0, 0, 1, 1]
        self.assertLess(score(truth, [0, 'inconclusive', 1, 1]),
                        score(truth, truth))

    def test_coverage_floor_counts_abstentions_and_errors(self):
        literal = SRS.replace(r'\allowbreak{}', '')
        match = re.search(r'const:MIN_COVERAGE\}.*?& \$([0-9.]+)\\%\$', literal)
        self.assertIsNotNone(match)
        floor = Fraction(match.group(1)) / 100
        self.assertEqual(floor, Fraction(7, 10))
        for withheld in ['inconclusive', 'failed']:
            outcomes = [0, 1] + [withheld] * 8
            coverage = Fraction(sum(o in [0, 1] for o in outcomes), len(outcomes))
            self.assertLess(coverage, floor)
        self.assertGreaterEqual(Fraction(7, 10), floor)

    @unittest.skipUnless(WITH_HAZARD, 'hazard PR not required for SRS-only check')
    def test_shared_safety_requirements_match(self):
        ha = (ROOT / 'docs/HazardAnalysis/HazardAnalysis.tex').read_text()
        for number in range(1, 10):
            tag = 'SR' + str(number)
            block = SRS.split(r'\label{' + tag + '}', 1)[1]
            statement = block.split(r'\textbf{Statement:} ', 1)[1]
            statement = statement.split(r'\newline', 1)[0]
            other = ha.split(r'\label{' + tag + '}', 1)[1]
            other = other.split(r'\newline', 1)[1].split('\n\n', 1)[0]
            self.assertEqual(' '.join(statement.replace(r'\allowbreak{}', '').split()),
                             ' '.join(other.replace(r'\allowbreak{}', '').split()), tag)


if __name__ == '__main__':
    unittest.main(verbosity=2)
