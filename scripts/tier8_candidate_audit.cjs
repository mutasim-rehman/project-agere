// Retrospective audit of the matched 8 GB development runs.
const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');

const root = path.join(__dirname, '../research/tier8_v2/runs');
function read(condition) {
  const dir = path.join(root, `finqa-mas-3b-${condition}-direct-dev24-01`);
  return fs.readFileSync(path.join(dir, 'cases.jsonl'), 'utf8').trim()
    .split(/\r?\n/).map(JSON.parse);
}

const baseline = read('unadapted');
const adapted = read('adapted');
assert.equal(baseline.length, 24);
assert.deepEqual(baseline.map(row => row.case_id), adapted.map(row => row.case_id));
assert.equal(new Set(adapted.map(row => row.case_id)).size, 24);
const reports = new Set(adapted.map(row => row.case_id.split('/').slice(0, 2).join('/')));

function summarize(rows, metric) {
  const counts = { refused: 0, executable: 0, correctCandidates: 0,
    correctRejected: 0, wrongDelivered: 0, correctDelivered: 0, withheld: 0 };
  for (const row of rows) {
    assert.equal(row.repair, 'none');
    assert.deepEqual(row.initial_score, row.score);
    const executable = row.initial_execution?.value != null;
    const correct = row.initial_score[metric] === true;
    counts.refused += Number(row.initial_plan?.decision === 'INSUFFICIENT');
    counts.executable += Number(executable);
    assert.ok(!correct || executable);
    assert.ok(!row.delivered || executable);
    counts.correctCandidates += Number(correct);
    counts.correctRejected += Number(correct && !row.delivered);
    counts.correctDelivered += Number(correct && row.delivered);
    counts.wrongDelivered += Number(!correct && row.delivered);
    counts.withheld += Number(!row.delivered);
  }
  return counts;
}

const result = { cases: adapted.length, reports: reports.size };
for (const metric of ['case_success', 'raw_execution_match']) {
  result[metric] = { baseline: summarize(baseline, metric), adapted: summarize(adapted, metric) };
}
console.log(JSON.stringify(result, null, 2));
