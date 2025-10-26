      const els = {
        runBtn: document.getElementById('runBtn'),
        status: document.getElementById('status'),
        output: document.getElementById('output'),
        cipher: document.getElementById('cipher'),

        cbCaesar: document.getElementById('cb_caesar'),
        cbBlock: document.getElementById('cb_block'),
        cbColumnar: document.getElementById('cb_columnar'),
        cbMono: document.getElementById('cb_mono'),
        cbVig: document.getElementById('cb_vig'),
        cbHill: document.getElementById('cb_hill'),
        cbRail: document.getElementById('cb_rail'),
      };

      let pyodideReadyPromise = null;

      function setStatus(text) { els.status.textContent = text; }
      function setBusy(b) {
        els.output.setAttribute('aria-busy', String(!!b));
        els.runBtn.disabled = !!b;
      }

      async function initPy() {
        setStatus('PLEASE WORK PLEASE I BEG DINGALINGALING ');
        const pyodide = await loadPyodide({
          stdout: () => {},
          stderr: () => {},
        });

        // Write a tiny 'colorama' shim so your code can import it without changes.
        const coloramaShim = [
          'class Fore:\n',
          '    CYAN=""\n',
          '    GREEN=""\n',
          '    RED=""\n',
          '    YELLOW=""\n',
          'class Style:\n',
          '    RESET_ALL=""\n',
          'def init(autoreset=False):\n',
          '    pass\n',
        ].join('');
        pyodide.FS.writeFile('colorama.py', coloramaShim);

        // Fetch project files from the same directory and place them into Pyodide FS.
        async function fetchText(path) {
          const res = await fetch(path);
          if (!res.ok) throw new Error('stupid ass failed to fetch' + path);
          return await res.text();
        }
        async function fetchBinary(path) {
          const res = await fetch(path);
          if (!res.ok) throw new Error('stupid ass failed to fetch' + path);
          const buf = await res.arrayBuffer();
          return new Uint8Array(buf);
        }

        setStatus('WWWW THIS WORKS TY EVERYTHINGTHAT I DO PRAISE THE LORD');
        // Python sources
        const [crackerSrc, scorerSrc, vignereSrc] = await Promise.all([
          fetchText('cracker.py'),
          fetchText('scorer.py'),
          fetchText('NEWvignere.py'),
        ]);
        pyodide.FS.writeFile('cracker.py', crackerSrc);
        pyodide.FS.writeFile('scorer.py', scorerSrc);
        pyodide.FS.writeFile('NEWvignere.py', vignereSrc);

        // Data files
        const [quadgrams, bigrams] = await Promise.all([
          fetchBinary('quadgrams.gz'),
          fetchText('bigrams.json'),
        ]);
        pyodide.FS.writeFile('quadgrams.gz', quadgrams);
        pyodide.FS.writeFile('bigrams.json', bigrams);

        setStatus('Ready');
        els.output.textContent = 'loaded this works 100% no joke';
        return pyodide;
      }

      // Kick off loading immediately
      pyodideReadyPromise = initPy().catch(err => {
        setStatus('failed cuz im stupid pls check error');
        els.output.textContent = String(err);
        throw err;
      });

      async function runCracker() {
        const pyodide = await pyodideReadyPromise;
        const ciphertext = els.cipher.value || '';
        const lines = ciphertext.split(/\r?\n/);
        // multiLineInput ends on a line 'p' — we auto-append it.
        lines.push('p');

        const flags = {
          RUN_CAESAR: !!els.cbCaesar?.checked,
          RUN_BLOCK: !!els.cbBlock?.checked,
          RUN_COLUMNAR: !!els.cbColumnar?.checked,
          RUN_MONO: !!els.cbMono?.checked,
          RUN_VIG: !!els.cbVig?.checked,
          RUN_HILL: !!els.cbHill?.checked,
          RUN_RAIL: !!els.cbRail?.checked,
        };

        const py = `\n` +
`import sys, io, builtins, runpy\n` +
`buf = io.StringIO()\n` +
`sys.stdout = buf\n` +
`sys.stderr = buf\n` +
`import os, json\n` +
`_flags = json.loads(${JSON.stringify(JSON.stringify(flags))})\n` +
`for k,v in _flags.items(): os.environ[str(k)] = '1' if v else '0'\n` +
`_lines = ${JSON.stringify(lines)}\n` +
`_it = iter(_lines)\n` +
`builtins.input = lambda: next(_it)\n` +
`try:\n` +
`    runpy.run_module('cracker', run_name='__main__')\n` +
`except SystemExit:\n` +
`    pass\n` +
`except Exception as e:\n` +
`    import traceback; traceback.print_exc()\n` +
`buf.getvalue()\n`;

        setBusy(true);
        setStatus('its running now scripts running be patient');
        els.output.textContent = '';
        try {
          const out = await pyodide.runPythonAsync(py);
          els.output.textContent = out;
          setStatus('done');
        } catch (err) {
          els.output.textContent = String(err);
          setStatus('error AHHHHHHHHHH');
        } finally {
          setBusy(false);
        }
      }

      els.runBtn.addEventListener('click', runCracker);
