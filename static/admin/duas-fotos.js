// Registra imagem responsiva e duas fotos. Compatível com o formato anterior
// de duas fotos identificado pelos comentários rms:duas-fotos.
(() => {
  const quote = (value = '') => JSON.stringify(String(value));
  const decodeHTML = (value = '') => {
    const el = document.createElement('textarea');
    el.innerHTML = value;
    return el.value;
  };
  const photoBlock = (src = '', alt = '', layout = 'inteira') =>
    `{% <foto_responsiva src=${quote(src)} alt=${quote(alt)} layout="${layout}"> %}{% </foto_responsiva> %}`;
  const photoPattern = /^\{% <foto_responsiva src=("(?:\\.|[^"\\])*") alt=("(?:\\.|[^"\\])*") layout="(inteira|metade|terco)"> %\}\{% <\/foto_responsiva> %\}$/;
  const oldPhotoPattern = /^<img src="([^"]*)" alt="([^"]*)">$/;
  const parsePhoto = (line) => {
    const modern = line.match(photoPattern);
    if (modern) return { src: JSON.parse(modern[1]), alt: JSON.parse(modern[2]), layout: modern[3] };
    const old = line.match(oldPhotoPattern);
    if (old) return { src: decodeHTML(old[1]), alt: decodeHTML(old[2]) };
    return { src: '', alt: '' };
  };
  const previewImage = (src, alt, getAsset) => {
    const img = document.createElement('img');
    if (src) img.src = getAsset?.(src)?.url ?? src;
    img.alt = alt;
    img.style.cssText = 'max-width:100%;height:auto';
    return img;
  };

  CMS.registerEditorComponent({
    id: 'foto-responsiva',
    label: 'Foto responsiva',
    icon: 'image',
    trigger: 'button',
    fields: [
      { name: 'src', label: 'Imagem', widget: 'image' },
      { name: 'alt', label: 'Texto alternativo', widget: 'string', required: false },
    ],
    pattern: /^\{% <foto_responsiva src=("(?:\\.|[^"\\])*") alt=("(?:\\.|[^"\\])*") layout="inteira"> %\}\{% <\/foto_responsiva> %\}$/m,
    fromBlock(match) { return parsePhoto(match[0]); },
    toBlock({ src = '', alt = '' }) { return photoBlock(src, alt); },
    toPreview({ src = '', alt = '' }, getAsset) { return previewImage(src, alt, getAsset); },
  });

  CMS.registerEditorComponent({
    id: 'duas-fotos',
    label: 'Duas fotos lado a lado',
    icon: 'view_column',
    trigger: 'button',
    fields: [
      { name: 'foto1', label: 'Primeira foto', widget: 'image' },
      { name: 'alt1', label: 'Descrição da primeira foto', widget: 'string', required: false },
      { name: 'foto2', label: 'Segunda foto', widget: 'image' },
      { name: 'alt2', label: 'Descrição da segunda foto', widget: 'string', required: false },
    ],
    // Captura linhas individuais, sem atravessar outros blocos de conteúdo.
    pattern: /^<!-- rms:duas-fotos -->\r?\n\{% <columns> %\}\r?\n\{% <column ratio=\{50\.0\}> %\}\r?\n(<img src="[^"]*" alt="[^"]*">|\{% <foto_responsiva src="(?:\\.|[^"\\])*" alt="(?:\\.|[^"\\])*" layout="metade"> %\}\{% <\/foto_responsiva> %\})\r?\n\{% <\/column> %\}\r?\n\{% <column ratio=\{50\.0\}> %\}\r?\n(<img src="[^"]*" alt="[^"]*">|\{% <foto_responsiva src="(?:\\.|[^"\\])*" alt="(?:\\.|[^"\\])*" layout="metade"> %\}\{% <\/foto_responsiva> %\})\r?\n\{% <\/column> %\}\r?\n\{% <\/columns> %\}\r?\n<!-- \/rms:duas-fotos -->$/m,
    fromBlock(match) {
      const a = parsePhoto(match[1]);
      const b = parsePhoto(match[2]);
      return { foto1: a.src, alt1: a.alt, foto2: b.src, alt2: b.alt };
    },
    toBlock({ foto1 = '', alt1 = '', foto2 = '', alt2 = '' }) {
      return `<!-- rms:duas-fotos -->
{% <columns> %}
{% <column ratio={50.0}> %}
${photoBlock(foto1, alt1, 'metade')}
{% </column> %}
{% <column ratio={50.0}> %}
${photoBlock(foto2, alt2, 'metade')}
{% </column> %}
{% </columns> %}
<!-- /rms:duas-fotos -->`;
    },
    toPreview({ foto1 = '', alt1 = '', foto2 = '', alt2 = '' }, getAsset) {
      const div = document.createElement('div');
      div.style.cssText = 'display:flex;gap:12px;align-items:flex-start';
      for (const [src, alt] of [[foto1, alt1], [foto2, alt2]]) {
        const img = previewImage(src, alt, getAsset);
        img.style.cssText = 'width:calc(50% - 6px);height:auto';
        div.appendChild(img);
      }
      return div;
    },
  });

  CMS.registerEditorComponent({
    id: 'tres-fotos',
    label: 'Três fotos lado a lado',
    icon: 'view_column',
    trigger: 'button',
    fields: [
      { name: 'foto1', label: 'Primeira foto', widget: 'image' },
      { name: 'alt1', label: 'Descrição da primeira foto', widget: 'string', required: false },
      { name: 'foto2', label: 'Segunda foto', widget: 'image' },
      { name: 'alt2', label: 'Descrição da segunda foto', widget: 'string', required: false },
      { name: 'foto3', label: 'Terceira foto', widget: 'image' },
      { name: 'alt3', label: 'Descrição da terceira foto', widget: 'string', required: false },
    ],
    pattern: /^<!-- rms:tres-fotos -->\r?\n\{% <columns> %\}\r?\n\{% <column ratio=\{33\.33\}> %\}\r?\n(\{% <foto_responsiva src="(?:\\.|[^"\\])*" alt="(?:\\.|[^"\\])*" layout="terco"> %\}\{% <\/foto_responsiva> %\})\r?\n\{% <\/column> %\}\r?\n\{% <column ratio=\{33\.33\}> %\}\r?\n(\{% <foto_responsiva src="(?:\\.|[^"\\])*" alt="(?:\\.|[^"\\])*" layout="terco"> %\}\{% <\/foto_responsiva> %\})\r?\n\{% <\/column> %\}\r?\n\{% <column ratio=\{33\.33\}> %\}\r?\n(\{% <foto_responsiva src="(?:\\.|[^"\\])*" alt="(?:\\.|[^"\\])*" layout="terco"> %\}\{% <\/foto_responsiva> %\})\r?\n\{% <\/column> %\}\r?\n\{% <\/columns> %\}\r?\n<!-- \/rms:tres-fotos -->$/m,
    fromBlock(match) {
      const a = parsePhoto(match[1]);
      const b = parsePhoto(match[2]);
      const c = parsePhoto(match[3]);
      return { foto1: a.src, alt1: a.alt, foto2: b.src, alt2: b.alt, foto3: c.src, alt3: c.alt };
    },
    toBlock({ foto1 = '', alt1 = '', foto2 = '', alt2 = '', foto3 = '', alt3 = '' }) {
      return `<!-- rms:tres-fotos -->
{% <columns> %}
{% <column ratio={33.33}> %}
${photoBlock(foto1, alt1, 'terco')}
{% </column> %}
{% <column ratio={33.33}> %}
${photoBlock(foto2, alt2, 'terco')}
{% </column> %}
{% <column ratio={33.33}> %}
${photoBlock(foto3, alt3, 'terco')}
{% </column> %}
{% </columns> %}
<!-- /rms:tres-fotos -->`;
    },
    toPreview({ foto1 = '', alt1 = '', foto2 = '', alt2 = '', foto3 = '', alt3 = '' }, getAsset) {
      const div = document.createElement('div');
      div.style.cssText = 'display:flex;gap:12px;align-items:flex-start';
      for (const [src, alt] of [[foto1, alt1], [foto2, alt2], [foto3, alt3]]) {
        const img = previewImage(src, alt, getAsset);
        img.style.cssText = 'width:calc((100% - 24px) / 3);height:auto';
        div.appendChild(img);
      }
      return div;
    },
  });
})();
