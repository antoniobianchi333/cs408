"""Build a dependency-light static handout from Markdown and checked baseline data."""
import argparse
import html
import json
import re
import shutil
from pathlib import Path

from markdown_it import MarkdownIt

HERE = Path(__file__).resolve().parent
SKELETON = HERE.parent / 'skeleton'


def replace_block(path, label, body):
    text = path.read_text()
    start, end = '<!-- baseline:{} -->'.format(label), '<!-- /baseline:{} -->'.format(label)
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError('Missing or duplicated baseline markers: ' + label)
    text = text[:text.index(start)+len(start)] + '\n' + body + '\n' + text[text.index(end):]
    if text != path.read_text():
        path.write_text(text)


def fraction(value):
    return '—' if value is None else '{:.4f}'.format(value).rstrip('0').rstrip('.')


def task_details(task):
    ir = task['type'] == 'IR'
    lines = ['### {} — {:.2f}/100'.format(task['title'], task['score']), '', task['description'], '',
             '**Task:** `{}` · **Checkpoints:** {} · **Faulty versions:** {}'.format(task['task'], len(task['checkpoints']), sum(g['variant_count'] for g in task['checkpoints'])), '',
             '```bash', 'python -m lab2 ' + task['task'], '```', '',
             '<details>', '<summary>Detailed selected vanilla score</summary>', '',
             '| Checkpoint | Max | V | ' + ('E | ' if ir else '') + 'K | Points |',
             '| --- | ---: | ---: | ' + ('---: | ' if ir else '') + '---: | ---: |']
    for g in task['checkpoints']:
        values = [g['label'], '{:.2f}'.format(g['max_points']), fraction(g['V'])]
        if ir:
            values.append(fraction(g['E']))
        values.extend([fraction(g['K']), '{:.2f}'.format(g['points'])])
        lines.append('| ' + ' | '.join(values) + ' |')
    lines += ['', '**Total: {:.2f}/100.** Each checkpoint is worth exactly `100/{}`; displayed values are rounded. The total uses unrounded values.'.format(task['score'], len(task['checkpoints'])), '',
              'Selected score record: `{}`. See `baselines.json` for the evidence hash and other eligible historical scores.'.format(task['source_score_file']), '', '</details>', '']
    return '\n'.join(lines)


def build(destination):
    data = json.loads((SKELETON / 'baselines.json').read_text())
    for kind in ['TW', 'IR']:
        replace_block(SKELETON / 'README.md', kind, '\n'.join(task_details(t) for t in data['tasks'] if t['type'] == kind))
    summary = ['| Part | Task | Selected vanilla minimum | Checkpoints |', '| --- | --- | ---: | ---: |']
    for task in data['tasks']:
        summary.append('| {} | {} | {:.2f}/100 | {} |'.format('Test Writing' if task['type'] == 'TW' else 'Issue Reproduction', task['title'], task['score'], len(task['checkpoints'])))
    summary += ['', '**Mean of these six selected minima: {:.2f}/100.** These are historical test-quality scores, not a prediction or a matched experiment.'.format(data['mean'])]
    replace_block(HERE / 'index.md', 'summary', '\n'.join(summary))
    md = MarkdownIt('commonmark', {'html': True}).enable('table')
    tokens = md.parse((HERE / 'index.md').read_text())
    nav, used = [], set()
    for i, token in enumerate(tokens):
        if token.type == 'heading_open':
            title = tokens[i+1].content
            slug = re.sub('[^a-z0-9]+', '-', title.lower()).strip('-')
            if slug in used:
                raise ValueError('Duplicate heading anchor: ' + slug)
            used.add(slug)
            token.attrSet('id', slug)
            if token.tag == 'h2':
                nav.append('<a href="#{}">{}</a>'.format(slug, html.escape(title)))
    body = md.renderer.render(tokens, md.options, {})
    template = (HERE / 'template.html').read_text()
    page = template.replace('<!-- NAVIGATION -->', '\n'.join(nav)).replace('<!-- ARTICLE -->', body)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'index.html').write_text(page)
    if destination.resolve() != HERE.resolve():
        shutil.copytree(HERE / 'assets', destination / 'assets', dirs_exist_ok=True)
    shutil.copyfile(SKELETON / 'baselines.json', destination / 'baselines.json')
    (destination / '.nojekyll').touch()
    return destination / 'index.html'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE)
    args = parser.parse_args()
    print(build(args.output))
