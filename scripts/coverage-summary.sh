#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_SUMMARY="$ROOT_DIR/frontend/coverage/unit/coverage-summary.json"
BACKEND_XML="$ROOT_DIR/backend/coverage/backend-coverage.xml"
BASELINE_FILE="$ROOT_DIR/AI/truth/test-plan/coverage-baseline.json"
WRITE_BASELINE=false

for arg in "$@"; do
  case "$arg" in
    --write-baseline)
      WRITE_BASELINE=true
      ;;
    *)
      echo "Unknown argument: $arg"
      echo "Usage: scripts/coverage-summary.sh [--write-baseline]"
      exit 2
      ;;
  esac
done

if [[ ! -f "$FRONTEND_SUMMARY" ]]; then
  echo "Missing frontend coverage summary at $FRONTEND_SUMMARY"
  echo "Run: cd frontend && npm run test:unit:coverage"
  exit 1
fi

if [[ ! -f "$BACKEND_XML" ]]; then
  echo "Missing backend coverage report at $BACKEND_XML"
  echo "Run: scripts/backend-coverage.sh"
  exit 1
fi

frontend_json="$(node -e "const fs=require('fs');const data=JSON.parse(fs.readFileSync('$FRONTEND_SUMMARY','utf8'));process.stdout.write(JSON.stringify({lines:data.total.lines.pct,statements:data.total.statements.pct,functions:data.total.functions.pct,branches:data.total.branches.pct}));")"
backend_json="$(node -e "const fs=require('fs');const xml=fs.readFileSync('$BACKEND_XML','utf8');const line=Number((xml.match(/line-rate=\\\"([0-9.]+)\\\"/)||[])[1]||0)*100;const branch=Number((xml.match(/branch-rate=\\\"([0-9.]+)\\\"/)||[])[1]||0)*100;process.stdout.write(JSON.stringify({lines:line,branches:branch}));")"

node - "$frontend_json" "$backend_json" "$BASELINE_FILE" "$WRITE_BASELINE" <<'NODE'
const [frontendRaw, backendRaw, baselineFile, writeBaselineRaw] = process.argv.slice(2);
const frontend = JSON.parse(frontendRaw);
const backend = JSON.parse(backendRaw);
const fs = require('fs');
const writeBaseline = writeBaselineRaw === 'true';

const current = {
  timestamp: new Date().toISOString(),
  frontend,
  backend,
};

function fmt(n) {
  return Number(n).toFixed(2);
}

console.log('Current coverage:');
console.log(`  frontend lines: ${fmt(frontend.lines)}%`);
console.log(`  frontend statements: ${fmt(frontend.statements)}%`);
console.log(`  frontend functions: ${fmt(frontend.functions)}%`);
console.log(`  frontend branches: ${fmt(frontend.branches)}%`);
console.log(`  backend lines: ${fmt(backend.lines)}%`);
console.log(`  backend branches: ${fmt(backend.branches)}%`);

if (fs.existsSync(baselineFile)) {
  const baseline = JSON.parse(fs.readFileSync(baselineFile, 'utf8'));
  const fd = baseline.frontend || {};
  const bd = baseline.backend || {};
  console.log('Delta vs baseline:');
  console.log(`  frontend lines: ${fmt(frontend.lines - (fd.lines || 0))}%`);
  console.log(`  frontend statements: ${fmt(frontend.statements - (fd.statements || 0))}%`);
  console.log(`  frontend functions: ${fmt(frontend.functions - (fd.functions || 0))}%`);
  console.log(`  frontend branches: ${fmt(frontend.branches - (fd.branches || 0))}%`);
  console.log(`  backend lines: ${fmt(backend.lines - (bd.lines || 0))}%`);
  console.log(`  backend branches: ${fmt(backend.branches - (bd.branches || 0))}%`);
} else {
  console.log('No baseline file found; run with --write-baseline to establish baseline.');
}

if (writeBaseline) {
  fs.writeFileSync(baselineFile, JSON.stringify(current, null, 2));
  console.log(`Wrote baseline: ${baselineFile}`);
}
NODE
