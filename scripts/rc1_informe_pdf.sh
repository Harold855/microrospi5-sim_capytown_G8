#!/usr/bin/env bash
# Genera informe.pdf (1 pagina A4) desde informe.md. Requiere pandoc y Node con playwright (chromium).
set -e
cd "$(dirname "$0")/.."
pandoc informe.md -f markdown+raw_html -s --metadata pagetitle="RC-1 Informe Grupo 8" --css docs/rc1_g8/informe.css -o /tmp/informe_rc1.html --embed-resources 2>/dev/null || pandoc informe.md -f markdown+raw_html -s --metadata pagetitle="RC-1 Informe Grupo 8" --css docs/rc1_g8/informe.css -o /tmp/informe_rc1.html --self-contained
node -e '
const {chromium}=require("playwright");
(async()=>{const b=await chromium.launch();const p=await b.newPage();
await p.goto("file:///tmp/informe_rc1.html");
await p.pdf({path:"informe.pdf",format:"A4",printBackground:true,preferCSSPageSize:true});
await b.close();})();'
echo "informe.pdf generado"
