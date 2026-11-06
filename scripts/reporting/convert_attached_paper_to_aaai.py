"""Faithful LaTeX reformat of the specifically requested pre-supervisor paper.

No scientific text is generated. Pandoc parses the original Markdown counterpart;
layout transformations preserve its paragraphs, math, code, tables and figures.
"""
import copy
import hashlib
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'output/paper/pre_supervisor_review/RESEARCH_PAPER.md'
PDF_SOURCE = SOURCE.with_suffix('.pdf')
OUT = ROOT / 'output/aaai'
PANDOC = ROOT / 'tmp/latex-tools/pandoc.exe'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text(x):
    if isinstance(x, list):
        return ''.join(text(v) for v in x)
    if isinstance(x, dict):
        t, c = x['t'], x.get('c', '')
        if t == 'Str': return c
        if t in ('Space', 'SoftBreak', 'LineBreak'): return ' '
        if t in ('Code', 'Math'): return c[1]
        if t == 'Link': return text(c[1])
        return text(c)
    return ''


def esc(s):
    table = {'\\': r'\textbackslash{}', '&': r'\&', '%': r'\%', '$': r'\$',
             '#': r'\#', '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
             '^': r'\textasciicircum{}'}
    return ''.join(table.get(c, c) for c in s)


def inline(items):
    out = []
    for x in items:
        t, c = x['t'], x.get('c')
        if t == 'Str': out.append(esc(c))
        elif t in ('Space', 'SoftBreak'): out.append(' ')
        elif t == 'LineBreak': out.append(r'\newline ')
        elif t == 'Strong': out.append(r'\textbf{' + inline(c) + '}')
        elif t == 'Emph': out.append(r'\emph{' + inline(c) + '}')
        elif t == 'Code': out.append(r'\path|' + c[1] + '|')
        elif t == 'Math': out.append('$' + c[1] + '$')
        elif t == 'Link': out.append(inline(c[1]) + r' (\url|' + c[2][0] + '|)')
        elif t == 'Quoted': out.append('``' + inline(c[1]) + "''")
        elif t in ('Superscript', 'Subscript'):
            out.append(('\\textsuperscript{' if t == 'Superscript' else '\\textsubscript{') + inline(c) + '}')
        else: raise ValueError('Unhandled table inline: ' + t)
    return ''.join(out)


def celltex(cell):
    return '\\par '.join(inline(b['c']) for b in cell[4] if b['t'] in ('Plain', 'Para'))


def rawblock(s):
    return {'t': 'RawBlock', 'c': ['latex', s]}


def rawinline(s):
    return {'t': 'RawInline', 'c': ['latex', s]}


def parse_bib(source):
    refs = source.split('## References', 1)[1].split('## Appendix A.', 1)[0]
    lines = re.findall(r'^\d+\. (.+)$', refs, re.M)
    assert len(lines) == 55
    result = []
    # Only metadata literally present in the source is used; unknown names/years
    # are not completed from the web or guessed.
    for i, line in enumerate(lines, 1):
        m = re.match(r'(.+?) \((\d{4})\)\. (.+)', line)
        if not m:
            # The source's final entry is a group of regulations with no author
            # or year. Preserve it as its original context paragraph, not a
            # fabricated dated BibTeX record or an entry with ???? placeholders.
            continue
        authors, year, rest = m.groups()
        authors = authors.replace(', et al.', ' and others')
        authors = authors.replace(', & ', ' and ')
        authors = re.sub(r'(?<=\.), (?=[A-ZŻ][^,]+, )', ' and ', authors)
        # A title ends at the first sentence period, except "vs." and initials.
        # The exact remainder is retained as a note, including venue identifiers.
        title_end = re.search(r'(?<=[.?]) (?=(?:arXiv|ICLR|EMNLP|NeurIPS|ICML|MLSys|ACL|NAACL|Findings|KDD|AIITA|JMLR|Journal|Scandinavian|JASA|The American|Social|Psychometrika|Biometrika|British|Statistics|BMC|Cambridge|Wiley|KnowledgeNLP|https:))', rest)
        if title_end:
            title, note = rest[:title_end.start()].rstrip('.'), rest[title_end.end():]
        else:
            title, note = rest.rstrip('.'), ''
        fields = ['  author = {' + authors + '}', '  year = {' + year + '}',
                  '  title = {{' + esc(title) + '}}']
        if note:
            note = re.sub(r'https?://\S+', lambda m: r'\url{' + m[0].rstrip('.') + '}' + ('.' if m[0].endswith('.') else ''), esc(note))
            note = note.replace('`', '')
            fields.append('  note = {' + note + '}')
        result.append('@misc{source%02d,\n%s\n}' % (i, ',\n'.join(fields)))
    return '\n\n'.join(result) + '\n', lines


UNICODE = {
    '−': r'\ensuremath{-}', '×': r'\ensuremath{\times}', '÷': r'\ensuremath{\div}',
    '≤': r'\ensuremath{\leq}', '≈': r'\ensuremath{\approx}',
    '→': r'\ensuremath{\rightarrow}', '←': r'\ensuremath{\leftarrow}',
    '↔': r'\ensuremath{\leftrightarrow}', '↓': r'\ensuremath{\downarrow}',
    'Δ': r'\ensuremath{\Delta}', 'χ': r'\ensuremath{\chi}', 'α': r'\ensuremath{\alpha}',
    'λ': r'\ensuremath{\lambda}', 'κ': r'\ensuremath{\kappa}', '∧': r'\ensuremath{\wedge}',
    '·': r'\ensuremath{\cdot}',
    '⁻': r'\textsuperscript{-}', '⁰': r'\textsuperscript{0}', '¹': r'\textsuperscript{1}',
    '²': r'\textsuperscript{2}', '³': r'\textsuperscript{3}', '⁴': r'\textsuperscript{4}',
    '⁵': r'\textsuperscript{5}', '⁶': r'\textsuperscript{6}', '⁷': r'\textsuperscript{7}',
    '⁸': r'\textsuperscript{8}', '⁹': r'\textsuperscript{9}',
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ast = json.loads(subprocess.check_output([str(PANDOC), str(SOURCE), '-f', 'markdown', '-t', 'json']))
    original = copy.deepcopy(ast)
    source = SOURCE.read_text(encoding='utf-8')
    bib, original_refs = parse_bib(source)
    (OUT / 'references.bib').write_text(bib, encoding='utf-8')
    # Save provenance without modifying either of the user's source files.
    title = text(ast['blocks'][0]['c'][2])
    blocks, abstract, front = [], [], []
    phase, heading, table_index, figure_index = 'front', '', 0, 0
    table_audit, figures = [], []

    def write_table(b):
        nonlocal table_index
        table_index += 1
        c = b['c']
        heads = c[3][1][0][1]
        rows = [r for body in c[4] for r in body[3]]
        n = len(heads)
        # Very wide statistical tables are split into horizontal panels with
        # their first identifying columns repeated. No cell is dropped/rounded.
        if n > 8:
            repeat = 3 if n >= 10 else 1
            groups = [list(range(repeat)) + list(range(i, min(i + 4, n))) for i in range(repeat, n, 4)]
        else:
            groups = [list(range(n))]
        table_audit.append({'source_table': table_index, 'columns': n, 'rows': len(rows),
                            'source_cells': [[text(cell[4]) for cell in row[1]] for row in rows],
                            'panels': groups})
        chunks = [rows[i:i+10] for i in range(0, len(rows), 10)]
        output = []
        for gi, indices in enumerate(groups):
            for ri, chunk in enumerate(chunks):
                wide = True
                env = 'table*' if wide else 'table'
                width = 504 if wide else 238.5
                # tabcolsep is the one table-spacing adjustment explicitly
                # permitted by the author kit; body and captions stay 10 pt.
                usable = width - 6 * (len(indices) - 1)
                weights = []
                for col in indices:
                    length = max([len(text(heads[col][4]))] + [min(100, len(text(row[1][col][4]))) for row in chunk])
                    weights.append(max(1, math.sqrt(length)) * (1.25 if col == 0 else 1))
                colwidths = [usable * w / sum(weights) for w in weights]
                spec = '@{}' + ''.join('>{\\raggedright\\arraybackslash}p{%.2fpt}' % w for w in colwidths) + '@{}'
                out = ['\\begin{' + env + '}[tbp]', '\\centering', '\\setlength{\\tabcolsep}{3pt}',
                       '\\begin{tabular}{' + spec + '}', '\\toprule']
                out.append(' & '.join(r'\textbf{' + celltex(heads[i]) + '}' for i in indices) + r' \\')
                out.append(r'\midrule')
                out.extend(' & '.join(celltex(row[1][i]) for i in indices) + r' \\' for row in chunk)
                caption = re.sub(r'^\d+(?:\.\d+)*\.?\s*', '', heading)
                if len(groups) > 1: caption += ' (column panel %d of %d)' % (gi+1, len(groups))
                if len(chunks) > 1: caption += ' (rows %d-%d)' % (ri*10+1, ri*10+len(chunk))
                out += [r'\bottomrule', r'\end{tabular}', r'\caption{' + esc(caption) + '}', r'\end{' + env + '}']
                output.append(rawblock('\n'.join(out)))
        return output

    def walk(x):
        if isinstance(x, list): return [walk(v) for v in x]
        if not isinstance(x, dict): return x
        t, c = x.get('t'), x.get('c')
        if t == 'OrderedList' and len(c[1]) >= 10:
            # Keep the same numbered items without a hanging two-digit marker
            # protruding into the AAAI left margin.
            paragraphs = []
            for number, item in enumerate(c[1], c[0][0]):
                item = copy.deepcopy(item)
                item[0]['c'] = [{'t': 'Str', 'c': str(number) + '.'}, {'t': 'Space'}] + item[0]['c']
                paragraphs.extend(walk(item))
            return {'t': 'Div', 'c': [['', [], []], paragraphs]}
        if t == 'Code':
            # Allow line breaks in paths and machine IDs without adding links.
            delimiter = '|' if '|' not in c[1] else '!'
            return rawinline(r'\path' + delimiter + c[1] + delimiter)
        if t == 'Link':
            # AAAI disallows hyperlinks. Retain displayed text and the actual URL.
            label = text(c[1])
            return rawinline(r'\url|' + c[2][0] + '|' if label == c[2][0] else inline(c[1]) + r' (\url|' + c[2][0] + '|)')
        if t == 'Math' and c[0]['t'] == 'DisplayMath':
            mathtext = c[1]
            # Long displayed formulae become full-width floats. Terms stay exact.
            if len(mathtext) > 120 or r'\qquad' in mathtext:
                mathtext = mathtext.replace(r'\qquad', r'\\').replace(r'\quad', r'\;')
                return {'t': 'Math', 'c': [c[0], mathtext]}
        result = dict(x)
        if 'c' in result: result['c'] = walk(c)
        return result

    for b in ast['blocks'][1:]:
        t, c = b['t'], b.get('c')
        if t == 'Header':
            h = text(c[2])
            if h == 'Abstract': phase = 'abstract'; continue
            if h == 'References':
                phase = 'references'
                blocks.append(rawblock(r'\nocite{*}' + '\n' + r'\bibliography{references}'))
                blocks.append(rawblock(r'\paragraph{Regulatory context.} ' + esc(original_refs[-1])))
                continue
            if h.startswith('Appendix A.'):
                phase = 'body'
                blocks.append(rawblock(r'\appendix'))
            if phase in ('front', 'abstract'): phase = 'body'
            heading = h
            c[0] -= 1
            prefix = r'^Appendix [A-Z]\.\s*' if h.startswith('Appendix ') else r'^\d+(?:\.\d+)*\.?\s*'
            clean = re.sub(prefix, '', h)
            c[2] = [{'t': 'Str', 'c': clean}]
            blocks.append(b)
            continue
        if t == 'HorizontalRule': continue
        if phase == 'front':
            front.append(b); continue
        if phase == 'references':
            # Preserve the original bibliographic note, not the original numbered
            # list (its 55 entries are formatted by the unmodified AAAI bst).
            if t == 'Para' and text(c).startswith('Bibliographic note:'):
                blocks.append(walk(b))
            continue
        if phase == 'abstract':
            if t == 'Para' and text(c).startswith('Keywords:'):
                front.append(b)
            else: abstract.append(b)
            continue
        if t == 'Table': blocks.extend(write_table(b)); continue
        if t == 'CodeBlock':
            code = c[1]
            if 'shared, identical for both arms' in code:
                # Reflow the source's box-drawing diagram using its existing
                # labels, instead of squeezing 113 monospace columns to fit.
                blocks.append(rawblock(r'''\begin{figure*}[tbp]
\centering
\begin{tabular}{p{238pt}p{238pt}}
\multicolumn{2}{p{488pt}}{\centering Shared, identical for both arms: question $\rightarrow$ public evidence packet (lexical IDF top-8 source units + quantity catalog A000\ldots A0nn)} \\
\midrule
SAS (one 14B Q4 model) & MAS (three resident F16 models) \\
\midrule
Analysis $\leq$128 tok & 1.5B extractor: select source IDs \\
Program JSON: ANSWER/INSUFFICIENT + steps & 3B drafter: analysis $\leq$128 tok; program JSON \\
\midrule
\multicolumn{2}{p{488pt}}{\centering Deterministic executor: copies catalog values, applies add/subtract/multiply/divide, checks spans} \\
\midrule
14B review: PASS/FAIL/UNKNOWN & 0.5B verifier: PASS/FAIL/UNKNOWN \\
\midrule
\multicolumn{2}{p{488pt}}{\centering Deliver if ANSWER $\wedge$ executable $\wedge$ PASS, else withhold (repair-ablation profile: one full re-plan + re-review)} \\
\midrule
\multicolumn{2}{p{488pt}}{\centering Score: reported-answer convention and raw-execution convention $\rightarrow$ C / W / H} \\
\end{tabular}
\end{figure*}'''))
                continue
            # Actual code/examples retain every character; listings soft-wrap
            # them in the column and can break naturally across pages.
            listing = '\\begin{lstlisting}\n' + code + '\n\\end{lstlisting}'
            blocks.append(rawblock(listing))
            continue
        if t == 'Figure' or (t == 'Para' and len(c) == 1 and c[0]['t'] == 'Image'):
            figure_index += 1
            image_node = c[2][0]['c'][0] if t == 'Figure' else c[0]
            _, caption, target = image_node['c']
            path = target[0]
            src = ROOT / path
            dst = OUT / path
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            figures.append({'path': path, 'sha256': sha(src), 'caption': text(caption)})
            blocks.append(rawblock('\\begin{figure*}[tbp]\n\\centering\n'
                + r'\includegraphics[width=\textwidth,height=0.43\textheight,keepaspectratio]{' + path + '}\n'
                + r'\caption{' + inline(caption) + '}\n' + r'\label{fig:source-' + str(figure_index) + '}\n\\end{figure*}'))
            continue
        blocks.append(walk(b))

    def convert(bs):
        doc = {'pandoc-api-version': ast['pandoc-api-version'], 'meta': {}, 'blocks': bs}
        return subprocess.check_output([str(PANDOC), '-f', 'json', '-t', 'latex', '--wrap=none'], input=json.dumps(doc).encode('utf-8')).decode('utf-8').replace('\r\n', '\n')

    # Body and abstract have exactly the source words; only the top-level author
    # and project strings move into the template's author/affiliations fields.
    abstract_text = convert(walk(abstract))
    front_text = convert(walk(front[1:]))  # skip the author line already in title block
    body_text = convert(blocks)
    # Pandoc display math may contain explicit soft line breaks for long formulas.
    def display_layout(match):
        formula = match[1]
        if '\\\\' not in formula and len(formula) <= 120:
            return match[0]
        formatted = '\\[\\begin{gathered}' + formula + '\\end{gathered}\\]'
        if max(map(len, formula.split('\\\\'))) > 120:
            return '\\begin{figure*}[tbp]\n' + formatted + '\n\\end{figure*}'
        return formatted
    body_text = re.sub(r'\\\[(.*?)\\\]', display_layout, body_text, flags=re.S)
    preamble = r'''\documentclass[letterpaper]{article}
\usepackage[preprint]{aaai2027}
\usepackage[hyphens]{url}
\usepackage{graphicx}
\urlstyle{rm}
\def\UrlFont{\rm}
\usepackage{natbib}
\usepackage{caption}
\frenchspacing
\usepackage{booktabs}
\usepackage{array}
\usepackage{amsmath,amssymb}
\usepackage{listings}
\lstset{basicstyle=\footnotesize\ttfamily,breaklines=true,breakatwhitespace=false,columns=fullflexible,keepspaces=true,showstringspaces=false}
\providecommand{\tightlist}{}
\pdfminorversion=5
\pdfinfo{/TemplateVersion (2027.1)}
\setcounter{secnumdepth}{2}
'''
    for char, tex in UNICODE.items():
        preamble += r'\DeclareUnicodeCharacter{' + '%04X' % ord(char) + '}{' + tex + '}\n'
    # Listing-only glyph substitutions retain the original diagram/operator text.
    literate = {'─': '-', '│': '|', '┌': '+', '┐': '+', '┘': '+', '└': '+',
                '►': r'$\triangleright$', '◄': r'$\triangleleft$', '▼': r'$\triangledown$',
                '→': r'$\rightarrow$', '↓': r'$\downarrow$', '≤': r'$\leq$',
                '∧': r'$\wedge$', '…': r'\ldots', '×': r'$\times$',
                '—': r'\textemdash', '–': r'\textendash'}
    for char, replacement in UNICODE.items():
        literate.setdefault(char, replacement)
    preamble += '\\lstset{literate=' + ' '.join('{' + c + '}{{' + v + '}}1' for c,v in literate.items()) + '}\n'
    tex = preamble + '\\title{' + esc(title) + '}\n' + r'\author{Mutasim ur Rehman and Ahmad Raza}' + '\n' + r'\affiliations{Project Agere}' + '\n'
    tex += '\\begin{document}\n\\maketitle\n\\begin{abstract}\n' + abstract_text + '\\end{abstract}\n' + front_text + body_text + '\n\\end{document}\n'
    (OUT / 'main.tex').write_text(tex, encoding='utf-8')
    assert figure_index == 20
    audit = {'source_markdown': str(SOURCE.relative_to(ROOT)), 'source_markdown_sha256': sha(SOURCE),
             'source_pdf': str(PDF_SOURCE.relative_to(ROOT)), 'source_pdf_sha256': sha(PDF_SOURCE),
             'new_research_claims': 0, 'new_experiments': 0,
             'figures': figures, 'original_table_count': table_index, 'tables': table_audit,
             'original_reference_count': len(original_refs), 'bibtex_reference_count': 54,
             'undated_regulatory_context_entries_preserved': 1, 'original_reference_entries': original_refs,
             'style_source': 'https://github.com/tabbycat7/aaai_2027_latex',
             'style_download_note': 'aaai.org author-kit URLs returned 403; style and bst retrieved from a mirror; not edited.',
             'style_sha256': sha(OUT / 'aaai2027.sty'), 'bst_sha256': sha(OUT / 'aaai2027.bst'),
             'layout_only_changes': ['Author/project moved to template fields; no new affiliation or email',
                 'AAAI-27 preprint option preserves named authors without asserting AAAI copyright/acceptance',
                 'All original prose and abstract retained; no conference page-limit condensation',
                 'Horizontal statistical panels and row chunks preserve all original cells',
                 'Existing references reformatted via AAAI bst; missing metadata not invented',
                 'Long equations placed at full width where required; code examples soft-wrap in columns',
                 'Original box-drawing architecture reflowed with the same stage/model/decision labels in native LaTeX']}
    (OUT / 'conversion_audit.json').write_text(json.dumps(audit, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')
    print('Created main.tex, references.bib and conversion audit:', figure_index, 'figures,', table_index, 'source tables,', len(original_refs), 'references')


if __name__ == '__main__':
    main()
