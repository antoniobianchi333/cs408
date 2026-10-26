(() => {
  'use strict';
  const toggle = document.querySelector('.nav-toggle');
  const contents = document.getElementById('contents');
  toggle.addEventListener('click', () => {
    const opened = contents.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(opened));
  });
  const links = [...contents.querySelectorAll('nav a')];
  links.forEach(link => link.addEventListener('click', () => {
    contents.classList.remove('open');
    toggle.setAttribute('aria-expanded', 'false');
  }));
  const headings = [...document.querySelectorAll('article > h2')];
  const update = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    document.getElementById('reading-progress').style.width = `${max > 0 ? window.scrollY / max * 100 : 0}%`;
    const active = headings.filter(h => h.getBoundingClientRect().top <= 145).at(-1);
    links.forEach(link => {
      const selected = !!active && link.hash === `#${active.id}`;
      link.classList.toggle('active', selected);
      if (selected) link.setAttribute('aria-current', 'location'); else link.removeAttribute('aria-current');
    });
  };
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  update();
  document.querySelectorAll('table').forEach(table => {
    const wrapper = document.createElement('div');
    wrapper.className = 'table-wrap';
    table.before(wrapper);
    wrapper.append(table);
  });
  document.querySelectorAll('pre').forEach(pre => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-code';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code block');
    button.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(pre.querySelector('code').textContent);
        button.textContent = 'Copied';
      } catch (_) {
        const selection = window.getSelection(), range = document.createRange();
        range.selectNodeContents(pre.querySelector('code'));
        selection.removeAllRanges();
        selection.addRange(range);
        button.textContent = 'Selected';
      }
      setTimeout(() => { button.textContent = 'Copy'; }, 1800);
    });
    pre.prepend(button);
  });
  const values = ['v', 'e', 'k'].map(id => document.getElementById(`score-${id}`));
  const kind = document.getElementById('score-type');
  const calculate = () => {
    const fractions = values.map((input, i) => {
      document.getElementById(`value-${['v', 'e', 'k'][i]}`).textContent = `${input.value}%`;
      return Number(input.value) / 100;
    });
    const ir = kind.value === 'IR';
    document.getElementById('label-e').hidden = !ir;
    document.getElementById('score-e').disabled = !ir;
    const score = 20 * fractions[0] * (ir ? fractions[1] : 1) * fractions[2];
    document.getElementById('score-value').textContent = `${score.toFixed(2)} / 20`;
  };
  values.forEach(input => input.addEventListener('input', calculate));
  kind.addEventListener('change', calculate);
  calculate();
})();
