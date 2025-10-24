

(function () {
  const els = {
    ceaserIn: document.getElementById('ceaser_in'),
    ceaserShift: document.getElementById('ceaser_shift'),
    ceaserBtn: document.getElementById('ceaser_btn'),
    ceaserOut: document.getElementById('ceaser_out'),

    monoIn: document.getElementById('mono_in'),
    monoKey: document.getElementById('mono_key'),
    monoBtn: document.getElementById('mono_btn'),
    monoOut: document.getElementById('mono_out'),

    transIn: document.getElementById('transposition_in'),
    transKey: document.getElementById('transposition_key'),
    transBtn: document.getElementById('transposition_btn'),
    transOut: document.getElementById('transposition_out'),
  };

  let pyodideReadyPromise = null;

  async function initPy() {
    const pyodide = await loadPyodide({
      stdout: () => {},
      stderr: () => {},
    });


    const resp = await fetch('decrypters.py');
    if (!resp.ok) throw new Error('Failed to fetch decrypters.py');
    const src = await resp.text();
    pyodide.FS.writeFile('decrypters.py', src);

    return pyodide;
  }

  pyodideReadyPromise = initPy();

  async function callDecrypter(funcName, args) {
    const pyodide = await pyodideReadyPromise;
    const jsonArgs = JSON.stringify(args);
    const code = [
      "import json",
      "import decrypters as d",
      `args = json.loads(${JSON.stringify(jsonArgs)})`,
      `res = getattr(d, '${funcName}')(*args)`,
      "res",
    ].join("\n");
    return await pyodide.runPythonAsync(code);
  }

  function parseTranspositionKey(str) {
    const digits = (str || '').trim();
    if (!/^[0-9]+$/.test(digits)) return null;
    return digits.split('').map(d => parseInt(d, 10));
  }


  els.ceaserBtn?.addEventListener('click', async () => {
    els.ceaserBtn.disabled = true;
    try {
      const msg = els.ceaserIn.value || '';
      const k = parseInt(els.ceaserShift.value || '0', 10) || 0;
      const out = await callDecrypter('ceaser', [msg, k]);
      els.ceaserOut.textContent = out;
    } catch (e) {
      els.ceaserOut.textContent = String(e);
    } finally {
      els.ceaserBtn.disabled = false;
    }
  });


  els.monoBtn?.addEventListener('click', async () => {
    els.monoBtn.disabled = true;
    try {
      const msg = els.monoIn.value || '';
      const key = els.monoKey.value || '';
      const out = await callDecrypter('mono', [msg, key]);
      els.monoOut.textContent = out;
    } catch (e) {
      els.monoOut.textContent = String(e);
    } finally {
      els.monoBtn.disabled = false;
    }
  });


  els.transBtn?.addEventListener('click', async () => {
    els.transBtn.disabled = true;
    try {
      const msg = els.transIn.value || '';
      const key = parseTranspositionKey(els.transKey.value);
      if (!key) throw new Error('Key must be digits like 1324');
      const out = await callDecrypter('transposition_block', [msg, key]);
      els.transOut.textContent = out;
    } catch (e) {
      els.transOut.textContent = String(e);
    } finally {
      els.transBtn.disabled = false;
    }
  });


  if (els.monoKey && !els.monoKey.value) {
    els.monoKey.value = 'abcdefghijklmnopqrstuvwxyz';
  }

})();
